"""
ONI Canvas Bounds Service v1.0
Detects and manages canvas/work area boundaries in graphic applications.

Features:
- Hybrid detection (app hints + visual analysis)
- Bounds caching per application
- Coordinate validation and clamping
- Center calculation for centered drawing
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple
import structlog
import numpy as np

logger = structlog.get_logger(__name__)


@dataclass
class CanvasBounds:
    """Represents the boundaries of a work area/canvas."""
    x: int  # Left edge
    y: int  # Top edge  
    width: int
    height: int
    app_name: str = ""
    detected_at: float = field(default_factory=time.time)
    method: str = "manual"  # "manual", "hints", "visual", "hybrid"
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    @property
    def center_x(self) -> int:
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        return self.y + self.height // 2
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.center_x, self.center_y)
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is within bounds."""
        return self.x <= x <= self.right and self.y <= y <= self.bottom
    
    def clamp(self, x: int, y: int, margin: int = 10) -> Tuple[int, int]:
        """Clamp coordinates to stay within bounds with optional margin."""
        clamped_x = max(self.x + margin, min(self.right - margin, x))
        clamped_y = max(self.y + margin, min(self.bottom - margin, y))
        return (clamped_x, clamped_y)
    
    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "right": self.right,
            "bottom": self.bottom,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "app_name": self.app_name,
            "method": self.method
        }


# Application-specific hints for canvas detection
# Format: {process_name: {offset hints}}
APP_CANVAS_HINTS = {
    "Photoshop.exe": {
        "toolbar_left": 74,      # Left toolbar width
        "header_top": 105,       # Top menu/options height
        "palette_right": 300,    # Right palettes width
        "status_bottom": 25,     # Bottom status bar
        "description": "Adobe Photoshop"
    },
    "CorelDRW.exe": {
        "toolbar_left": 32,      # Left toolbar width  
        "header_top": 95,        # Top menu/toolbars height
        "palette_right": 25,     # Right palette width
        "status_bottom": 80,     # Bottom (includes docker)
        "ruler_offset": 10,      # Ruler width
        "description": "CorelDRAW"
    },
    "PHOTO-PAINT.exe": {
        "toolbar_left": 32,
        "header_top": 95,
        "palette_right": 25,
        "status_bottom": 60,
        "description": "Corel PHOTO-PAINT"
    },
    "illustrator.exe": {
        "toolbar_left": 60,
        "header_top": 100,
        "palette_right": 280,
        "status_bottom": 25,
        "description": "Adobe Illustrator"
    },
    "AfterFX.exe": {
        "toolbar_left": 0,
        "header_top": 150,
        "palette_right": 400,
        "status_bottom": 300,
        "description": "Adobe After Effects (Composition Panel)"
    },
    "mspaint.exe": {
        "toolbar_left": 0,
        "header_top": 135,
        "palette_right": 0,
        "status_bottom": 50,
        "description": "Microsoft Paint"
    },
}


class CanvasBoundsService:
    """
    Manages canvas/work area detection and validation.
    
    Usage:
        # Detect canvas automatically
        bounds = await CanvasBoundsService.detect_canvas("CorelDRW.exe", window_info)
        
        # Get center for drawing
        center_x, center_y = bounds.center
        
        # Validate coordinates
        if bounds.contains(x, y):
            execute_action()
        
        # Clamp coordinates to stay within bounds
        safe_x, safe_y = bounds.clamp(x, y)
    """
    
    _bounds_cache: Dict[str, CanvasBounds] = {}
    _cache_ttl: float = 300.0  # 5 minutes cache TTL
    
    @classmethod
    def get_app_hints(cls, process_name: str) -> Optional[dict]:
        """Get canvas hints for a specific application."""
        return APP_CANVAS_HINTS.get(process_name)
    
    @classmethod
    def set_bounds(cls, app_name: str, bounds: CanvasBounds):
        """Manually set canvas bounds for an application."""
        bounds.app_name = app_name
        cls._bounds_cache[app_name] = bounds
        logger.info("canvas_bounds_set", app=app_name, bounds=bounds.to_dict())
    
    @classmethod
    def get_bounds(cls, app_name: str) -> Optional[CanvasBounds]:
        """Get cached bounds for an application."""
        bounds = cls._bounds_cache.get(app_name)
        if bounds:
            # Check TTL
            if time.time() - bounds.detected_at < cls._cache_ttl:
                return bounds
            else:
                # Expired, remove from cache
                del cls._bounds_cache[app_name]
        return None
    
    @classmethod
    async def detect_canvas(
        cls,
        process_name: str,
        window_x: int,
        window_y: int, 
        window_width: int,
        window_height: int,
        use_visual: bool = True
    ) -> CanvasBounds:
        """
        Detect canvas bounds using hybrid approach (Visual > Hints > Default).
        """
        
        # Check cache first
        cached = cls.get_bounds(process_name)
        if cached:
            return cached

        # 1. Try Visual Detection (White Rectangle)
        if use_visual:
            try:
                import pyautogui
                import numpy as np
                import cv2
                
                # Take screenshot of the window area
                # clamp regions
                sx = max(0, window_x)
                sy = max(0, window_y)
                sw = max(100, window_width)
                sh = max(100, window_height)
                
                screenshot = pyautogui.screenshot(region=(sx, sy, sw, sh))
                img_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                visual_bounds = await cls.detect_canvas_visual(img_bgr, sx, sy)
                
                if visual_bounds:
                    visual_bounds.app_name = process_name
                    # Sanity check: Visual bounds should be reasonable size
                    if visual_bounds.width > 50 and visual_bounds.height > 50:
                        cls._bounds_cache[process_name] = visual_bounds
                        logger.info("canvas_detected_visual", bounds=visual_bounds.to_dict())
                        return visual_bounds
            except Exception as e:
                logger.warning("visual_detection_failed_fallback", error=str(e))

        # 2. Fallback to Hints
        hints = cls.get_app_hints(process_name)
        if hints:
            toolbar_left = hints.get("toolbar_left", 0)
            header_top = hints.get("header_top", 0)
            palette_right = hints.get("palette_right", 0)
            status_bottom = hints.get("status_bottom", 0)
            
            canvas_x = window_x + toolbar_left
            canvas_y = window_y + header_top
            canvas_width = window_width - toolbar_left - palette_right
            canvas_height = window_height - header_top - status_bottom
            
            bounds = CanvasBounds(
                x=canvas_x, y=canvas_y, width=canvas_width, height=canvas_height,
                app_name=process_name, method="hints"
            )
            cls.set_bounds(process_name, bounds)
            return bounds

        # 3. Last Resort: Estimate
        margin_x = int(window_width * 0.1)
        margin_y = int(window_height * 0.15)
        bounds = CanvasBounds(
            x=window_x + margin_x,
            y=window_y + margin_y,
            width=int(window_width * 0.8),
            height=int(window_height * 0.7),
            app_name=process_name,
            method="estimate"
        )
        cls.set_bounds(process_name, bounds)
        return bounds
    
    @classmethod
    async def detect_canvas_visual(
        cls,
        image_bgr: np.ndarray,
        window_x: int,
        window_y: int
    ) -> Optional[CanvasBounds]:
        """
        Detect canvas using visual analysis.
        Looks for the largest bright rectangular area.
        """
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Threshold for white/bright areas (canvas usually white)
            # Increased from 200 to 245 to avoid light-gray UI areas
            _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find largest rectangle-like contour
            largest_area = 0
            best_rect = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area and area > 10000:  # Minimum area
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Canvas should be roughly rectangular (aspect between 0.5 and 2.0)
                    if 0.3 < aspect_ratio < 3.0:
                        largest_area = area
                        best_rect = (x, y, w, h)
            
            if best_rect:
                x, y, w, h = best_rect
                return CanvasBounds(
                    x=window_x + x,
                    y=window_y + y,
                    width=w,
                    height=h,
                    method="visual"
                )
            
            return None
            
        except Exception as e:
            logger.error("visual_canvas_detection_failed", error=str(e))
            return None
    
    @classmethod
    def validate_coords(cls, app_name: str, x: int, y: int) -> Tuple[bool, str]:
        """
        Validate if coordinates are within cached canvas bounds.
        
        Returns: (is_valid, message)
        """
        bounds = cls.get_bounds(app_name)
        
        if not bounds:
            return True, "No bounds cached, allowing action"
        
        if bounds.contains(x, y):
            return True, "Coordinates within canvas"
        else:
            return False, f"Coordinates ({x},{y}) outside canvas bounds {bounds.to_dict()}"
    
    @classmethod
    def get_safe_coords(
        cls, 
        app_name: str, 
        x: int, 
        y: int,
        margin: int = 10
    ) -> Tuple[int, int]:
        """
        Get coordinates clamped to stay within canvas bounds.
        Returns original coordinates if no bounds cached.
        """
        bounds = cls.get_bounds(app_name)
        
        if not bounds:
            return (x, y)
        
        return bounds.clamp(x, y, margin)
    
    @classmethod
    def get_center(cls, app_name: str) -> Optional[Tuple[int, int]]:
        """Get the center point of the cached canvas."""
        bounds = cls.get_bounds(app_name)
        return bounds.center if bounds else None
    
    @classmethod
    def clear_cache(cls, app_name: str = None):
        """Clear bounds cache for an app or all apps."""
        if app_name:
            cls._bounds_cache.pop(app_name, None)
        else:
            cls._bounds_cache.clear()
        logger.info("canvas_cache_cleared", app=app_name or "all")
    
    @classmethod
    def get_all_cached(cls) -> Dict[str, dict]:
        """Get all cached bounds as dictionaries."""
        return {k: v.to_dict() for k, v in cls._bounds_cache.items()}
