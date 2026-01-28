"""
ONI v7.0 - Dual Verification Service
Multi-model verification using Claude (implicit) + Gemini.
"""

import base64
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class VerificationModel(str, Enum):
    """Available verification models."""
    GEMINI_FLASH = "google/gemini-2.0-flash-exp:free"
    NEMO_VLM = "nvidia/nemotron-nano-12b-v2-vl:free"


@dataclass
class ModelResult:
    """Result from a single model verification."""
    model: str
    approved: bool
    confidence: float
    reason: str
    raw_response: str = ""


@dataclass
class DualVerificationResult:
    """Result from dual model verification."""
    approved: bool
    consensus: float
    confidence: float
    primary_result: ModelResult
    secondary_result: ModelResult
    conflict: bool = False


class DualVerificationService:
    """
    Dual Model Verification Service.
    
    Uses two VLMs to verify visual results:
    - Primary: Claude (implicit via user interaction)
    - Secondary: Gemini 2.0 Flash (via OpenRouter)
    """
    
    SECONDARY_MODEL = VerificationModel.GEMINI_FLASH
    
    @classmethod
    def _encode_image(cls, image_path: str) -> Optional[str]:
        """Encode image to base64."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error("image_not_found", path=image_path)
                return None
            
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error("image_encode_failed", error=str(e))
            return None
    
    @classmethod
    async def verify_with_secondary(
        cls,
        image_path: str,
        expected_result: str,
        task_context: str = ""
    ) -> ModelResult:
        """
        Verify with secondary model (Gemini 1.5 Flash via SDK).
        """
        try:
            from app.services.vision.gemini_flash_provider import GeminiFlashProvider
            provider = GeminiFlashProvider()
            
            prompt = f"Verify if '{expected_result}' is visible/achieved. Context: {task_context}"
            
            result = provider.verify_image(image_path, prompt)
            
            return ModelResult(
                model=result["model"],
                approved=result["approved"],
                confidence=result["confidence"],
                reason=result["reason"],
                raw_response=result.get("raw_response", "")
            )
            
        except Exception as e:
            logger.error("secondary_verification_exception", error=str(e))
            return ModelResult(
                model="gemini-flash-error",
                approved=True,
                confidence=0.5,
                reason=f"Exception: {str(e)}"
            )
    
    @classmethod
    async def dual_verify(
        cls,
        image_path: str,
        expected_result: str,
        primary_approved: bool,
        primary_reason: str = "",
        primary_confidence: float = 0.8,
        task_context: str = ""
    ) -> DualVerificationResult:
        """
        Perform dual verification with primary (Claude) and secondary (Gemini).
        
        Args:
            image_path: Path to screenshot
            expected_result: What should be visible
            primary_approved: Claude's verdict
            primary_reason: Claude's reasoning
            primary_confidence: Claude's confidence
            task_context: Additional context
            
        Returns:
            DualVerificationResult with consensus
        """
        # Primary result (from Claude - passed in)
        primary = ModelResult(
            model="claude",
            approved=primary_approved,
            confidence=primary_confidence,
            reason=primary_reason
        )
        
        # Secondary result (from Gemini)
        secondary = await cls.verify_with_secondary(
            image_path, expected_result, task_context
        )
        
        # Calculate consensus
        agreement = primary.approved == secondary.approved
        
        if agreement:
            # Both agree
            consensus = 1.0
            final_approved = primary.approved
            # Combine confidences (higher when both agree)
            confidence = (primary.confidence + secondary.confidence) / 2 + 0.1
        else:
            # Disagreement
            consensus = 0.5
            # Use higher confidence result
            if primary.confidence >= secondary.confidence:
                final_approved = primary.approved
            else:
                final_approved = secondary.approved
            confidence = max(primary.confidence, secondary.confidence) * 0.8
        
        confidence = min(0.95, confidence)
        
        result = DualVerificationResult(
            approved=final_approved,
            consensus=consensus,
            confidence=round(confidence, 2),
            primary_result=primary,
            secondary_result=secondary,
            conflict=not agreement
        )
        
        logger.info("dual_verification_complete",
                   approved=result.approved,
                   consensus=result.consensus,
                   conflict=result.conflict)
        
        return result
    
    @classmethod
    async def verify(
        cls,
        image_path: str,
        expected_result: str,
        task_context: str = ""
    ) -> Dict[str, Any]:
        """
        Simplified verification endpoint.
        
        Uses secondary model only (for API use).
        Returns dict for JSON serialization.
        """
        result = await cls.verify_with_secondary(image_path, expected_result, task_context)
        
        return {
            "approved": result.approved,
            "confidence": result.confidence,
            "reason": result.reason,
            "model": result.model
        }
