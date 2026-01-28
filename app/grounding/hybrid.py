"""
ONI v3.0 - Hybrid Grounding System
Combines UI-TARS visual grounding with OCR-based semantic locator.
Uses UI-TARS for complex visual elements, falls back to OCR for text.
"""
import asyncio
from dataclasses import dataclass
from typing import Any, Literal

import structlog

from app.grounding.ui_tars import UITarsGrounding, GroundingResult, GroundingError
from app.infrastructure.vision.semantic_locator import SemanticLocator

logger = structlog.get_logger()


class HybridGrounding:
    """
    Intelligent grounding that selects the best strategy per query.
    
    Strategy selection:
    1. Text queries (exact phrases) → OCR + SemanticLocator (faster)
    2. Visual queries (icons, buttons by appearance) → UI-TARS (more accurate)
    3. Fallback chain: UI-TARS → OCR → Error
    
    Example:
        grounding = HybridGrounding(
            ui_tars=UITarsGrounding(...),
            semantic_locator=SemanticLocator(),
        )
        
        # Text query - uses OCR
        result = await grounding.locate("Save", screenshot, ocr_boxes)
        
        # Visual query - uses UI-TARS
        result = await grounding.locate(
            "the blue download button with arrow icon", 
            screenshot
        )
    """
    
    # Keywords that suggest visual/icon-based locating
    VISUAL_KEYWORDS = [
        "icon", "button", "image", "logo", "picture", "thumbnail",
        "arrow", "checkbox", "radio", "toggle", "slider", "color",
        "blue", "red", "green", "yellow", "white", "black", "gray",
        "left", "right", "top", "bottom", "corner", "center",
        "next to", "below", "above", "beside", "near",
    ]
    
    def __init__(
        self,
        ui_tars: UITarsGrounding | None = None,
        semantic_locator: SemanticLocator | None = None,
        prefer_ui_tars: bool = False,
        fallback_enabled: bool = True,
    ) -> None:
        """
        Initialize hybrid grounding.
        
        Args:
            ui_tars: UI-TARS grounding instance
            semantic_locator: Semantic locator for OCR-based matching
            prefer_ui_tars: Always try UI-TARS first
            fallback_enabled: Enable fallback to other method on failure
        """
        self._ui_tars = ui_tars
        self._semantic_locator = semantic_locator or SemanticLocator()
        self._prefer_ui_tars = prefer_ui_tars
        self._fallback_enabled = fallback_enabled
        
        # Stats for adaptive routing
        self._ui_tars_successes = 0
        self._ui_tars_failures = 0
        self._ocr_successes = 0
        self._ocr_failures = 0
    
    @property
    def ui_tars_available(self) -> bool:
        """Check if UI-TARS is configured."""
        return self._ui_tars is not None and self._ui_tars.is_available
    
    async def locate(
        self,
        query: str,
        screenshot: bytes,
        ocr_boxes: list[Any] | None = None,
        strategy: Literal["auto", "ui_tars", "ocr"] = "auto",
    ) -> GroundingResult:
        """
        Locate element using hybrid strategy.
        
        Args:
            query: Natural language description of element
            screenshot: PNG screenshot as bytes
            ocr_boxes: Pre-computed OCR boxes (optional)
            strategy: Force specific strategy or auto-detect
            
        Returns:
            GroundingResult with coordinates
            
        Raises:
            GroundingError: If all strategies fail
        """
        # Determine strategy
        if strategy == "auto":
            use_ui_tars_first = self._should_use_ui_tars(query)
        elif strategy == "ui_tars":
            use_ui_tars_first = True
        else:
            use_ui_tars_first = False
        
        # Override if UI-TARS not available
        if use_ui_tars_first and not self.ui_tars_available:
            logger.debug("ui_tars_not_available_fallback_to_ocr")
            use_ui_tars_first = False
        
        # Execute strategy with fallback
        if use_ui_tars_first:
            return await self._try_ui_tars_then_ocr(query, screenshot, ocr_boxes)
        else:
            return await self._try_ocr_then_ui_tars(query, screenshot, ocr_boxes)
    
    def _should_use_ui_tars(self, query: str) -> bool:
        """
        Determine if query should use UI-TARS.
        
        Uses keyword matching to detect visual queries.
        """
        if self._prefer_ui_tars:
            return True
        
        query_lower = query.lower()
        
        # Check for visual keywords
        visual_score = sum(
            1 for keyword in self.VISUAL_KEYWORDS
            if keyword in query_lower
        )
        
        # If query has visual descriptors, prefer UI-TARS
        if visual_score >= 2:
            return True
        
        # If query is a short exact phrase, prefer OCR
        if len(query.split()) <= 3 and visual_score == 0:
            return False
        
        # Default to UI-TARS for complex queries
        return len(query.split()) > 5
    
    async def _try_ui_tars_then_ocr(
        self,
        query: str,
        screenshot: bytes,
        ocr_boxes: list[Any] | None,
    ) -> GroundingResult:
        """Try UI-TARS first, fallback to OCR."""
        try:
            result = await self._ui_tars.locate(query, screenshot)
            self._ui_tars_successes += 1
            return result
        except GroundingError as e:
            self._ui_tars_failures += 1
            logger.warning("ui_tars_failed_trying_ocr", error=str(e))
            
            if not self._fallback_enabled:
                raise
        
        # Fallback to OCR
        return await self._locate_with_ocr(query, screenshot, ocr_boxes)
    
    async def _try_ocr_then_ui_tars(
        self,
        query: str,
        screenshot: bytes,
        ocr_boxes: list[Any] | None,
    ) -> GroundingResult:
        """Try OCR first, fallback to UI-TARS."""
        try:
            return await self._locate_with_ocr(query, screenshot, ocr_boxes)
        except GroundingError as e:
            self._ocr_failures += 1
            logger.warning("ocr_failed_trying_ui_tars", error=str(e))
            
            if not self._fallback_enabled or not self.ui_tars_available:
                raise
        
        # Fallback to UI-TARS
        result = await self._ui_tars.locate(query, screenshot)
        self._ui_tars_successes += 1
        return result
    
    async def _locate_with_ocr(
        self,
        query: str,
        screenshot: bytes,
        ocr_boxes: list[Any] | None,
    ) -> GroundingResult:
        """Locate element using OCR + SemanticLocator."""
        # If no pre-computed boxes, run OCR on the screenshot
        if ocr_boxes is None:
            try:
                import io
                import numpy as np
                from PIL import Image
                from app.infrastructure.vision.ocr.tesseract import TesseractOCR
                
                # Convert PNG bytes to numpy array
                pil_image = Image.open(io.BytesIO(screenshot))
                np_image = np.array(pil_image)
                
                # Run OCR
                ocr = TesseractOCR()
                await ocr.initialize()
                result = await ocr.extract(np_image)
                ocr_boxes = result.boxes
                logger.debug("ocr_ran_internally", boxes_found=len(ocr_boxes))
            except Exception as e:
                raise GroundingError(f"Failed to run OCR: {e}")
        
        if not ocr_boxes:
            raise GroundingError(f"No text found on screen for: {query}")
        
        # Use semantic locator to find match
        match = self._semantic_locator.find(query, ocr_boxes)
        
        if match is None:
            raise GroundingError(f"Could not find element matching: {query}")
        
        self._ocr_successes += 1
        
        return GroundingResult(
            x=match.center_x,
            y=match.center_y,
            confidence=match.confidence,
            method="ocr",
            raw_response=f"Found: {match.text}",
        )
    
    def get_stats(self) -> dict[str, int]:
        """Get grounding statistics."""
        return {
            "ui_tars_successes": self._ui_tars_successes,
            "ui_tars_failures": self._ui_tars_failures,
            "ocr_successes": self._ocr_successes,
            "ocr_failures": self._ocr_failures,
        }
