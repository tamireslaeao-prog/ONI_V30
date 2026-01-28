"""
ONI v2.0 - EasyOCR Engine
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np
import structlog

from app.core.config import settings
from app.core.exceptions import OCRError
from app.infrastructure.vision.ocr.tesseract import OCRBox, OCRResult

logger = structlog.get_logger()


class EasyOCREngine:
    """
    EasyOCR Engine.
    
    Features:
    - Deep learning based (better for complex backgrounds)
    - Handles rotated text well
    - Multiple language support
    - GPU acceleration
    """
    
    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = True,
    ) -> None:
        """
        Initialize EasyOCR.
        
        Args:
            languages: OCR languages
            gpu: Use GPU acceleration
        """
        self._languages = languages or settings.vision.ocr_languages
        self._gpu = gpu
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="easyocr")
        self._reader: Any = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize EasyOCR reader."""
        if self._initialized:
            return
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._init_sync)
        self._initialized = True
    
    def _init_sync(self) -> None:
        """Synchronous initialization."""
        try:
            import easyocr
            self._reader = easyocr.Reader(
                self._languages,
                gpu=self._gpu,
                verbose=False,
            )
            logger.info("easyocr_initialized", languages=self._languages, gpu=self._gpu)
        except Exception as e:
            raise OCRError(f"EasyOCR initialization failed: {e}")
    
    async def extract(
        self,
        image: np.ndarray,
        paragraph: bool = False,
    ) -> OCRResult:
        """
        Extract text from image.
        
        Args:
            image: Input image
            paragraph: Merge text into paragraphs
            
        Returns:
            OCR result
        """
        if not self._initialized:
            await self.initialize()
        
        import time
        start_time = time.perf_counter()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            lambda: self._extract_sync(image, paragraph)
        )
        
        result.processing_time_ms = (time.perf_counter() - start_time) * 1000
        return result
    
    def _extract_sync(self, image: np.ndarray, paragraph: bool) -> OCRResult:
        """Synchronous extraction."""
        try:
            # EasyOCR expects BGR or RGB
            results = self._reader.readtext(
                image,
                paragraph=paragraph,
                detail=1,
            )
            
            boxes = []
            texts = []
            total_conf = 0
            
            for detection in results:
                # detection format: (bbox, text, confidence)
                bbox, text, conf = detection
                
                # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                x1 = int(min(p[0] for p in bbox))
                y1 = int(min(p[1] for p in bbox))
                x2 = int(max(p[0] for p in bbox))
                y2 = int(max(p[1] for p in bbox))
                
                box = OCRBox(
                    text=text,
                    confidence=float(conf),
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1,
                )
                boxes.append(box)
                texts.append(text)
                total_conf += conf
            
            avg_conf = total_conf / len(boxes) if boxes else 0.0
            
            return OCRResult(
                boxes=boxes,
                full_text=" ".join(texts),
                confidence=avg_conf,
                engine="easyocr",
            )
            
        except Exception as e:
            raise OCRError(f"EasyOCR extraction failed: {e}")
