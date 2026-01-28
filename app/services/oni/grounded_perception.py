"""
ONI v11.0 - Grounded Perception Service
Unified anti-hallucination pipeline combining multiple grounding providers.

Pipeline:
1. OmniParser V2 → detect ALL elements (ground truth)
2. UI-TARS → natural language grounding
3. Qwen-VL → verification (optional)
4. Consensus check → only return if providers agree
5. Calibration → fix coordinates before action
"""

import base64
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple
import structlog

from app.services.oni.consensus_engine import ConsensusEngine, ConsensusResult
from app.services.oni.calibration_service import CalibrationService

logger = structlog.get_logger(__name__)


@dataclass
class GroundedElement:
    """A verified, grounded UI element."""
    label: str
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    confidence: float = 0.0
    element_type: str = "unknown"
    verified_by: List[str] = field(default_factory=list)


@dataclass
class PerceptionResult:
    """Result from grounded perception pipeline."""
    query: str
    found: bool
    element: Optional[GroundedElement] = None
    all_elements: List[GroundedElement] = field(default_factory=list)
    consensus: Optional[ConsensusResult] = None
    calibrated_coords: Optional[Tuple[int, int]] = None
    pipeline_stages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class GroundedPerceptionService:
    """
    Complete anti-hallucination perception pipeline.
    
    Combines multiple grounding methods to ensure UI elements are real:
    1. Detection (OmniParser) - Find ALL elements as ground truth
    2. Grounding (UI-TARS) - Locate specific element by description
    3. Verification (Qwen-VL or secondary) - Cross-check location
    4. Consensus - Require provider agreement
    5. Calibration - Fix coordinates for accurate clicking
    
    Example:
        service = GroundedPerceptionService(
            consensus_engine=engine,
            calibration_service=calibrator,
            omniparser=omni,
            uitars=uitars
        )
        
        result = await service.perceive(screenshot, "Save button")
        if result.found and result.element:
            click(result.calibrated_coords)
    """
    
    def __init__(
        self,
        consensus_engine: Optional[ConsensusEngine] = None,
        calibration_service: Optional[CalibrationService] = None,
        omniparser=None,
        uitars=None,
        qwen_vl=None,
        require_consensus: bool = True,
    ):
        """
        Initialize Grounded Perception Service.
        
        Args:
            consensus_engine: ConsensusEngine instance
            calibration_service: CalibrationService instance
            omniparser: OmniParser provider (detection)
            uitars: UI-TARS provider (grounding)
            qwen_vl: Qwen-VL provider (verification, optional)
            require_consensus: Require multi-provider consensus
        """
        self._consensus = consensus_engine or ConsensusEngine()
        self._calibration = calibration_service or CalibrationService()
        self._omniparser = omniparser
        self._uitars = uitars
        self._qwen_vl = qwen_vl
        self._require_consensus = require_consensus
        
        # Register providers with consensus engine
        if omniparser:
            self._consensus.register_provider("omniparser", omniparser)
        if uitars:
            self._consensus.register_provider("uitars", uitars)
        if qwen_vl:
            self._consensus.register_provider("qwenvl", qwen_vl)
        
        logger.info(
            "grounded_perception_init",
            has_omniparser=omniparser is not None,
            has_uitars=uitars is not None,
            has_qwenvl=qwen_vl is not None
        )
    
    async def perceive(
        self,
        screenshot: bytes,
        query: str,
        screen_size: Tuple[int, int] = (1920, 1080),
        calibration_source: Literal["screen", "vlm"] = "vlm",
    ) -> PerceptionResult:
        """
        Perceive and locate element using full anti-hallucination pipeline.
        
        Args:
            screenshot: PNG screenshot bytes
            query: Natural language description of element
            screen_size: Screen dimensions
            calibration_source: Source type for calibration
            
        Returns:
            PerceptionResult with verified element and calibrated coordinates
        """
        result = PerceptionResult(query=query, found=False, pipeline_stages=[])
        
        # 0. Compute Frame Hash for caching across providers
        from app.utils.vision_utils import compute_dhash
        frame_hash = compute_dhash(screenshot)
        
        # Stage 1: Detection with OmniParser (ground truth)
        all_elements = []
        if self._omniparser:
            try:
                result.pipeline_stages.append("omniparser_detection")
                # Pass frame_hash to enable caching in OmniParser
                all_elements = await self._detect_all_elements(screenshot, screen_size, frame_hash=frame_hash)
                result.all_elements = all_elements
                logger.debug("omniparser_detected", count=len(all_elements))
            except Exception as e:
                result.errors.append(f"OmniParser: {e}")
                logger.warning("omniparser_failed", error=str(e))
        
        # Stage 2: Consensus grounding (anti-hallucination)
        if self._require_consensus:
            try:
                result.pipeline_stages.append("consensus_grounding")
                # Consolidation: pass frame_hash to consensus engine too
                consensus = await self._consensus.locate(
                    query, screenshot, screen_size, frame_hash=frame_hash
                )
                result.consensus = consensus
                
                if consensus.hallucination_check == "PASSED":
                    element = GroundedElement(
                        label=query,
                        x=consensus.x,
                        y=consensus.y,
                        confidence=consensus.confidence,
                        verified_by=[r.provider for r in consensus.provider_results if r.found]
                    )
                    result.element = element
                    result.found = True
                    logger.info(
                        "consensus_grounding_passed",
                        query=query,
                        coords=(consensus.x, consensus.y),
                        variance=consensus.variance_px
                    )
                else:
                    logger.warning(
                        "consensus_grounding_failed",
                        query=query,
                        check=consensus.hallucination_check
                    )
                    
            except Exception as e:
                result.errors.append(f"Consensus: {e}")
                logger.error("consensus_failed", error=str(e))
        
        # Stage 3: Fallback to single provider if consensus not required or failed
        if not result.found and not self._require_consensus:
            result.found = await self._fallback_grounding(result, screenshot, query, screen_size)
        
        # Stage 4: Calibrate coordinates
        if result.found and result.element:
            try:
                result.pipeline_stages.append("calibration")
                cal_result = self._calibration.calibrate(
                    result.element.x,
                    result.element.y,
                    source=calibration_source
                )
                result.calibrated_coords = (cal_result.calibrated_x, cal_result.calibrated_y)
                logger.debug(
                    "coordinates_calibrated",
                    original=(result.element.x, result.element.y),
                    calibrated=result.calibrated_coords
                )
            except Exception as e:
                result.errors.append(f"Calibration: {e}")
                # Use uncalibrated coords as fallback
                result.calibrated_coords = (result.element.x, result.element.y)
        
        return result
    
    async def _detect_all_elements(
        self,
        screenshot: bytes,
        screen_size: Tuple[int, int],
        frame_hash: Optional[str] = None
    ) -> List[GroundedElement]:
        """Detect all elements using OmniParser."""
        elements = []
        
        if not self._omniparser:
            return elements
        
        try:
            b64 = base64.b64encode(screenshot).decode()
            # Pass frame_hash to the provider
            parse_result = await self._omniparser.parse_screenshot(b64, screen_size, frame_hash=frame_hash)
            
            if parse_result:
                for elem in parse_result.elements:
                    elements.append(GroundedElement(
                        label=elem.label,
                        x=elem.x,
                        y=elem.y,
                        width=elem.width,
                        height=elem.height,
                        confidence=0.8,
                        element_type=elem.element_type,
                        verified_by=["omniparser"]
                    ))
        except Exception as e:
            logger.error("element_detection_failed", error=str(e))
        
        return elements
    
    async def _fallback_grounding(
        self,
        result: PerceptionResult,
        screenshot: bytes,
        query: str,
        screen_size: Tuple[int, int],
    ) -> bool:
        """Fallback to single provider grounding."""
        result.pipeline_stages.append("fallback_grounding")
        
        # Try UI-TARS first
        if self._uitars:
            try:
                grounding_result = await self._uitars.find_element(
                    screenshot, query, screen_size
                )
                if grounding_result:
                    result.element = GroundedElement(
                        label=query,
                        x=grounding_result.x,
                        y=grounding_result.y,
                        confidence=grounding_result.confidence,
                        verified_by=["uitars"]
                    )
                    return True
            except Exception as e:
                result.errors.append(f"UI-TARS fallback: {e}")
        
        # Try Qwen-VL
        if self._qwen_vl:
            try:
                grounding_result = await self._qwen_vl.find_element(
                    screenshot, query, screen_size
                )
                if grounding_result:
                    result.element = GroundedElement(
                        label=query,
                        x=grounding_result.x,
                        y=grounding_result.y,
                        confidence=grounding_result.confidence,
                        verified_by=["qwenvl"]
                    )
                    return True
            except Exception as e:
                result.errors.append(f"Qwen-VL fallback: {e}")
        
        return False
    
    async def verify_element_exists(
        self,
        screenshot: bytes,
        query: str,
        expected_coords: Tuple[int, int],
        tolerance_px: int = 30,
    ) -> bool:
        """
        Verify an element exists at expected coordinates.
        
        Useful for pre-click verification.
        """
        result = await self.perceive(screenshot, query)
        
        if not result.found or not result.element:
            return False
        
        # Check if found coordinates are within tolerance
        dx = abs(result.element.x - expected_coords[0])
        dy = abs(result.element.y - expected_coords[1])
        distance = (dx**2 + dy**2)**0.5
        
        return distance <= tolerance_px
    
    def get_stats(self) -> Dict:
        """Get perception statistics."""
        return {
            "consensus_stats": self._consensus.get_stats(),
            "calibration_dpi": self._calibration.dpi_scale,
            "providers_registered": len(self._consensus._providers),
        }


# Global singleton
_grounded_perception: Optional[GroundedPerceptionService] = None


def get_grounded_perception_service() -> GroundedPerceptionService:
    """Get or create GroundedPerceptionService singleton."""
    global _grounded_perception
    if _grounded_perception is None:
        from app.services.oni.consensus_engine import get_consensus_engine
        from app.services.oni.calibration_service import get_calibration_service
        
        _grounded_perception = GroundedPerceptionService(
            consensus_engine=get_consensus_engine(),
            calibration_service=get_calibration_service(),
        )
    return _grounded_perception
