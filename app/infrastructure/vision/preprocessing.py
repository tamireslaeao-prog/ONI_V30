"""
ONI v2.0 - Image Preprocessing
Image enhancement pipeline for better OCR and detection
"""
from dataclasses import dataclass
from typing import Literal

import cv2
import numpy as np
import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class PreprocessingConfig:
    """Configuration for image preprocessing."""
    denoise: bool = True
    denoise_strength: int = 10
    contrast_enhance: bool = True
    clahe_clip_limit: float = 2.0
    clahe_grid_size: tuple[int, int] = (8, 8)
    sharpen: bool = True
    sharpen_amount: float = 0.5
    resize_factor: float = 1.0
    grayscale: bool = False


@dataclass
class PreprocessingResult:
    """Result of preprocessing."""
    image: np.ndarray
    original_shape: tuple[int, ...]
    processed_shape: tuple[int, ...]
    processing_time_ms: float
    operations_applied: list[str]


class ImagePreprocessor:
    """
    Image preprocessing pipeline for vision tasks.
    
    Features:
    - Noise reduction (Non-local Means Denoising)
    - Contrast enhancement (CLAHE)
    - Sharpening (Unsharp Mask)
    - Color space conversion
    - Resize/upscale
    """
    
    def __init__(self, config: PreprocessingConfig | None = None) -> None:
        """
        Initialize preprocessor.
        
        Args:
            config: Preprocessing configuration
        """
        self._config = config or PreprocessingConfig()
    
    def process(
        self,
        image: np.ndarray,
        config: PreprocessingConfig | None = None,
    ) -> PreprocessingResult:
        """
        Apply preprocessing pipeline to image.
        
        Args:
            image: Input image (BGR format)
            config: Optional config override
            
        Returns:
            Preprocessing result
        """
        import time
        start_time = time.perf_counter()
        
        cfg = config or self._config
        original_shape = image.shape
        operations = []
        
        result = image.copy()
        
        # Resize if needed
        if cfg.resize_factor != 1.0:
            result = self._resize(result, cfg.resize_factor)
            operations.append(f"resize_{cfg.resize_factor}x")
        
        # Convert to grayscale if needed
        if cfg.grayscale:
            result = self._to_grayscale(result)
            operations.append("grayscale")
        
        # Denoise
        if cfg.denoise:
            result = self._denoise(result, cfg.denoise_strength)
            operations.append("denoise")
        
        # Contrast enhancement
        if cfg.contrast_enhance:
            result = self._enhance_contrast(
                result,
                cfg.clahe_clip_limit,
                cfg.clahe_grid_size
            )
            operations.append("clahe")
        
        # Sharpen
        if cfg.sharpen:
            result = self._sharpen(result, cfg.sharpen_amount)
            operations.append("sharpen")
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return PreprocessingResult(
            image=result,
            original_shape=original_shape,
            processed_shape=result.shape,
            processing_time_ms=processing_time,
            operations_applied=operations,
        )
    
    def _resize(self, image: np.ndarray, factor: float) -> np.ndarray:
        """Resize image by factor."""
        if factor == 1.0:
            return image
        
        width = int(image.shape[1] * factor)
        height = int(image.shape[0] * factor)
        
        interpolation = cv2.INTER_CUBIC if factor > 1 else cv2.INTER_AREA
        return cv2.resize(image, (width, height), interpolation=interpolation)
    
    def _to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale."""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _denoise(self, image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Apply Non-local Means Denoising.
        
        This is slower but more effective than Gaussian blur.
        """
        if len(image.shape) == 2:
            return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
    
    def _enhance_contrast(
        self,
        image: np.ndarray,
        clip_limit: float = 2.0,
        grid_size: tuple[int, int] = (8, 8),
    ) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        
        if len(image.shape) == 2:
            return clahe.apply(image)
        
        # Convert to LAB, apply CLAHE to L channel
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    def _sharpen(self, image: np.ndarray, amount: float = 0.5) -> np.ndarray:
        """
        Apply Unsharp Mask sharpening.
        """
        # Create blurred version
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        
        # Unsharp mask: original + amount * (original - blurred)
        sharpened = cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
        return sharpened
    
    # =========================================================================
    # Specialized Preprocessing Methods
    # =========================================================================
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Optimize image for OCR.
        
        Returns grayscale, denoised, high-contrast image.
        """
        config = PreprocessingConfig(
            denoise=True,
            denoise_strength=10,
            contrast_enhance=True,
            clahe_clip_limit=3.0,
            sharpen=True,
            sharpen_amount=0.3,
            grayscale=True,
        )
        result = self.process(image, config)
        return result.image
    
    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Optimize image for object detection.
        
        Returns color image with enhanced contrast.
        """
        config = PreprocessingConfig(
            denoise=False,
            contrast_enhance=True,
            clahe_clip_limit=2.0,
            sharpen=False,
            grayscale=False,
        )
        result = self.process(image, config)
        return result.image
    
    def preprocess_for_template_matching(self, image: np.ndarray) -> np.ndarray:
        """
        Optimize image for template matching.
        """
        config = PreprocessingConfig(
            denoise=True,
            denoise_strength=5,
            contrast_enhance=False,
            sharpen=False,
            grayscale=True,
        )
        result = self.process(image, config)
        return result.image
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def extract_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        padding: int = 0,
    ) -> np.ndarray:
        """
        Extract a region from the image.
        
        Args:
            image: Source image
            x, y: Top-left corner
            width, height: Region size
            padding: Extra pixels around region
            
        Returns:
            Cropped region
        """
        # Apply padding with bounds checking
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + width + padding)
        y2 = min(image.shape[0], y + height + padding)
        
        return image[y1:y2, x1:x2].copy()
    
    def binarize(
        self,
        image: np.ndarray,
        method: Literal["otsu", "adaptive", "simple"] = "otsu",
        threshold: int = 127,
    ) -> np.ndarray:
        """
        Convert image to binary (black and white).
        
        Args:
            image: Input image
            method: Binarization method
            threshold: Threshold for simple method
            
        Returns:
            Binary image
        """
        gray = self._to_grayscale(image)
        
        if method == "otsu":
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "adaptive":
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        else:
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        return binary
