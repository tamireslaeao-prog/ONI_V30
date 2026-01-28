"""
ONI Core Module
Classes base, dependências e utilitários compartilhados.
"""

import time
import asyncio
from typing import Optional, Dict, Any, List
from functools import lru_cache, wraps
from collections import deque

from fastapi import HTTPException, Query, Depends
from pydantic import BaseModel, Field
from enum import Enum
import structlog

from app.core.dependencies import container

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ActionType(str, Enum):
    """Supported action types."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    TYPEWRITE = "typewrite"
    HOTKEY = "hotkey"
    PRESS = "press"
    MOVE = "move"
    DRAG = "drag"
    SCROLL = "scroll"
    WAIT = "wait"
    MOUSE_RESET = "mouse_reset"
    NEURAL_DRAW = "neural_draw"


class MouseButton(str, Enum):
    """Mouse button types."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ImageFormat(str, Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ActionRequest(BaseModel):
    """Request body for executing an action."""
    action: ActionType
    params: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None

    class Config:
        use_enum_values = True


class ActionResponse(BaseModel):
    """Response from action execution."""
    success: bool
    action: str
    message: str
    execution_time_ms: Optional[float] = None
    timestamp: Optional[str] = None


class ScreenshotRequest(BaseModel):
    """Request parameters for screenshot."""
    format: ImageFormat = ImageFormat.JPEG
    quality: int = Field(default=85, ge=1, le=100)
    draw_cursor: bool = True
    save_to_disk: bool = True


class ScreenshotResponse(BaseModel):
    """Screenshot response with metadata."""
    image: str  # base64 encoded
    resolution: str
    format: str
    saved_path: Optional[str] = None
    file_size_kb: Optional[float] = None
    capture_time_ms: float


class OCRWord(BaseModel):
    """Word detected by OCR."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float


# =============================================================================
# WINDOW MANAGER
# =============================================================================

class WindowManager:
    """Encapsulates window management operations."""
    
    @staticmethod
    async def get_active_window_info() -> Optional[Dict]:
        """Get detailed information about active window (Cross-Platform)."""
        import platform
        system = platform.system()
        
        if system == "Windows":
            return await WindowManager._get_windows_info()
        elif system == "Linux":
            return {"title": "Linux Window", "process_name": "unknown", "x": 0, "y": 0, "width": 1920, "height": 1080}
        else:
            return {"title": "Unknown OS", "process_name": "unknown", "x": 0, "y": 0, "width": 1920, "height": 1080}

    @staticmethod
    async def _get_windows_info() -> Optional[Dict]:
        try:
            import win32gui
            import win32process
            import win32con
            import psutil
            
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y
            
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                process = psutil.Process(process_id)
                process_name = process.name()
            except:
                process_name = "unknown"
            
            placement = win32gui.GetWindowPlacement(hwnd)
            is_maximized = placement[1] == win32con.SW_SHOWMAXIMIZED
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            screen_area = 1920 * 1080
            window_area = width * height
            screen_coverage = (window_area / screen_area) * 100 if screen_area > 0 else 0
            
            # Record active window check for ActionGuard
            from app.services.oni.guards import ActionGuardService
            ActionGuardService.record_active_window_check()
            
            return {
                'hwnd': hwnd,
                'title': title,
                'process_name': process_name,
                'process_id': process_id,
                'x': x, 'y': y,
                'width': width, 'height': height,
                'is_maximized': is_maximized,
                'is_minimized': is_minimized,
                'is_active': True,
                'screen_coverage_percent': round(screen_coverage, 2)
            }
            
        except Exception as e:
            logger.error("get_window_info_failed", error=str(e))
            return None


# =============================================================================
# OCR SERVICE
# =============================================================================

class OCRService:
    """Service for OCR text extraction."""
    
    @staticmethod
    def _compute_dhash(pil_image):
        """Compute dHash for caching."""
        try:
            import cv2
            import numpy as np
            
            img_arr = np.array(pil_image)
            if len(img_arr.shape) == 3:
                gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_arr
            
            resized = cv2.resize(gray, (9, 8))
            diff = resized[:, 1:] > resized[:, :-1]
            return sum([2**i for i, v in enumerate(diff.flatten()) if v])
        except Exception:
            return None

    @staticmethod
    async def extract_text(img, region: Optional[str] = None, languages: str = "por+eng"):
        """Extract text using Tesseract OCR."""
        import pytesseract
        from time import perf_counter
        
        start_time = perf_counter()
        
        try:
            ocr_img = img
            if region:
                parts = [int(p) for p in region.split(",")]
                if len(parts) == 4:
                    rx, ry, rw, rh = parts
                    ocr_img = img.crop((rx, ry, rx + rw, ry + rh))
            
            ocr_text = pytesseract.image_to_string(ocr_img, lang=languages)
            
            ocr_words = []
            try:
                data = pytesseract.image_to_data(ocr_img, lang=languages, output_type=pytesseract.Output.DICT)
                for i in range(len(data['text'])):
                    if data['text'][i].strip() and data['conf'][i] > 0:
                        ocr_words.append(OCRWord(
                            text=data['text'][i],
                            x=data['left'][i],
                            y=data['top'][i],
                            width=data['width'][i],
                            height=data['height'][i],
                            confidence=float(data['conf'][i])
                        ))
            except Exception as e:
                logger.warning("ocr_word_extraction_failed", error=str(e))
            
            ocr_time_ms = (perf_counter() - start_time) * 1000
            
            return ocr_text, ocr_words, ocr_time_ms
            
        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return f"OCR_ERROR: {str(e)}", [], 0


# =============================================================================
# RATE LIMITER
# =============================================================================

_rate_limit_cache: Dict[str, List[float]] = {}

def rate_limit(limit: int = 10, window: int = 1):
    """Rate limiter decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}"
            now = time.time()
            
            if key not in _rate_limit_cache:
                _rate_limit_cache[key] = []
            
            _rate_limit_cache[key] = [t for t in _rate_limit_cache[key] if now - t < window]
            
            if len(_rate_limit_cache[key]) >= limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            _rate_limit_cache[key].append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# DEPENDENCIES
# =============================================================================

async def get_vision_service():
    """Dependency to get vision service."""
    vision = container.get("vision")
    if not vision:
        raise HTTPException(status_code=503, detail="Vision system not available")
    return vision


async def get_mouse_service():
    """Dependency to get mouse service."""
    return container.get("mouse")


async def get_keyboard_service():
    """Dependency to get keyboard service."""
    return container.get("keyboard")
