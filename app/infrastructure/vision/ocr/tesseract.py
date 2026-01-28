"""
ONI v2.0 - Tesseract OCR Engine
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import structlog

from app.core.config import settings
from app.core.exceptions import OCRError

logger = structlog.get_logger()


@dataclass
class OCRBox:
    """OCR bounding box result."""
    text: str
    confidence: float
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


@dataclass
class OCRResult:
    """Complete OCR result."""
    boxes: list[OCRBox] = field(default_factory=list)
    full_text: str = ""
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    engine: str = "unknown"


class TesseractOCR:
    """
    Tesseract 5 OCR Engine.
    
    Features:
    - LSTM-based recognition
    - Multiple language support
    - Page segmentation modes
    - Word and character level boxes
    """
    
    def __init__(
        self,
        languages: list[str] | None = None,
        config: str = "",
    ) -> None:
        """
        Initialize Tesseract OCR.
        
        Args:
            languages: OCR languages (e.g., ["eng", "por"])
            config: Additional Tesseract config
        """
        self._languages = languages or settings.vision.ocr_languages
        self._config = config
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tesseract")
        self._tesseract: Any = None
    
    async def initialize(self) -> None:
        """Initialize Tesseract."""
        try:
            import pytesseract
            self._tesseract = pytesseract
            # Test that tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("tesseract_initialized", languages=self._languages)
        except Exception as e:
            raise OCRError(f"Tesseract initialization failed: {e}")
    
    async def extract(
        self,
        image: np.ndarray,
        psm: int = 3,
    ) -> OCRResult:
        """
        Extract text from image (Cached).
        """
        if self._tesseract is None:
            await self.initialize()
            
        import time
        import hashlib
        from functools import lru_cache
        
        # 1. Compute Hash of the image (Smart Cache)
        # Use simple bytes hash for speed
        img_hash = hashlib.sha256(image.tobytes()).hexdigest()
        
        # Check internal cache (We inject a simple dict cache here if not exists)
        if not hasattr(self, "_ocr_cache"):
            self._ocr_cache = {}
            
        if img_hash in self._ocr_cache:
            # CACHE HIT
            return self._ocr_cache[img_hash]
        
        start_time = time.perf_counter()
        
        # 2. Run OCR (Cache Miss)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            lambda: self._extract_sync(image, psm)
        )
        
        result.processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        # 3. Store in Cache (Limit size to avoid OOM - simple mechanism)
        if len(self._ocr_cache) > 1000:
             self._ocr_cache.clear() # Primitive LRU alternative
             
        self._ocr_cache[img_hash] = result
        
        return result
    
    def _extract_sync(self, image: np.ndarray, psm: int) -> OCRResult:
        """Synchronous OCR extraction."""
        import pytesseract
        from PIL import Image
        
        # Convert to PIL Image
        if len(image.shape) == 3:
            # BGR to RGB
            pil_image = Image.fromarray(image[:, :, ::-1])
        else:
            pil_image = Image.fromarray(image)
        
        lang_str = "+".join(self._languages)
        config = f"--psm {psm} {self._config}"
        
        try:
            # Get detailed data
            data = pytesseract.image_to_data(
                pil_image,
                lang=lang_str,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            boxes = []
            total_conf = 0
            valid_count = 0
            
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                conf = int(data["conf"][i])
                
                if text and conf > 0:
                    box = OCRBox(
                        text=text,
                        confidence=conf / 100.0,
                        x=data["left"][i],
                        y=data["top"][i],
                        width=data["width"][i],
                        height=data["height"][i],
                    )
                    boxes.append(box)
                    total_conf += conf
                    valid_count += 1
            
            # Get full text
            full_text = pytesseract.image_to_string(
                pil_image,
                lang=lang_str,
                config=config
            ).strip()
            
            avg_conf = (total_conf / valid_count / 100.0) if valid_count > 0 else 0.0
            
            return OCRResult(
                boxes=boxes,
                full_text=full_text,
                confidence=avg_conf,
                engine="tesseract",
            )
            
        except Exception as e:
            raise OCRError(f"Tesseract extraction failed: {e}")
    
    async def extract_text_only(self, image: np.ndarray) -> str:
        """
        Extract only text (faster, no boxes).
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if self._tesseract is None:
            await self.initialize()
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._extract_text_sync(image)
        )
    
    def _extract_text_sync(self, image: np.ndarray) -> str:
        """Synchronous text-only extraction."""
        import pytesseract
        from PIL import Image
        
        if len(image.shape) == 3:
            pil_image = Image.fromarray(image[:, :, ::-1])
        else:
            pil_image = Image.fromarray(image)
        
        lang_str = "+".join(self._languages)
        return pytesseract.image_to_string(pil_image, lang=lang_str).strip()
