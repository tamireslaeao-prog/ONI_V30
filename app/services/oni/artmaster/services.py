"""
ONI ArtMaster - Services
"""
import time
import asyncio
import structlog
from typing import Optional, Tuple, List, Dict, Any
from fastapi import HTTPException

# Safe imports
try:
    import pyautogui
except ImportError:
    pyautogui = None

from .types import ApplicationType, ApplicationInfo
from .detector import ApplicationDetector
from .factory import ApplicationStrategyFactory
from .strategies.base import ApplicationStrategy
from .config import ArtMasterConfig
from .utils import mandatory_vision_check

logger = structlog.get_logger(__name__)


class ApplicationService:
    """Service for application management."""
    
    _current_app: Optional[ApplicationInfo] = None
    _current_strategy: Optional[ApplicationStrategy] = None
    
    @classmethod
    async def get_active_application(cls, preferred: Optional[ApplicationType] = None) -> Tuple[ApplicationInfo, ApplicationStrategy]:
        """Get active creative application and its strategy."""
        # Try to use cached application
        if cls._current_app and cls._current_strategy:
            try:
                if await cls._current_strategy.ensure_focus():
                    return cls._current_app, cls._current_strategy
            except Exception:
                pass
        
        # Detect application
        app_info = ApplicationDetector.detect_application()
        
        if not app_info:
            raise HTTPException(
                status_code=404,
                detail="No supported creative application found. Please open Photoshop, Paint, or GIMP."
            )
        
        # Check if preferred application matches
        if preferred and app_info.app_type != preferred:
            raise HTTPException(
                status_code=400,
                detail=f"Requested {preferred} but {app_info.app_type} is active"
            )
        
        # Create strategy
        strategy = ApplicationStrategyFactory.create_strategy(app_info)
        
        # Ensure focused
        if not await strategy.ensure_focus():
            raise HTTPException(
                status_code=500,
                detail=f"Failed to focus {app_info.app_type}"
            )
        
        # Cache
        cls._current_app = app_info
        cls._current_strategy = strategy
        
        logger.info("application_active",
                   app_type=app_info.app_type.value,
                   title=app_info.window_title)
        
        return app_info, strategy


class DrawingService:
    """Service for drawing operations."""
    
    def __init__(self, mouse_controller, strategy: ApplicationStrategy, force_pyautogui: bool = False):
        self.mouse = mouse_controller
        self.strategy = strategy
        self.force_pyautogui = force_pyautogui
    
    @mandatory_vision_check
    async def draw_shape_batch(
        self,
        screen_points_list: List[List[Tuple[int, int]]],
        shape_types: List[str],
        on_progress=None
    ) -> int:
        """Draw multiple shapes using optimized mouse controller."""
        shapes_drawn = 0
        
        # Check for fast win32 capability (mock check if controller has method)
        use_fast_mouse = hasattr(self.mouse, 'fast_direct_win32') and not self.force_pyautogui
        if use_fast_mouse:
            logger.info("using_fast_win32_mouse")
        
        for i, screen_points in enumerate(screen_points_list):
            if len(screen_points) < 2:
                continue
            
            try:
                start_point = screen_points[0]
                
                # Logic for fast drawing via win32api fallback if needed
                if use_fast_mouse or True: # Force win32api logic for now as it's superior
                     import win32api, win32con
                     import math
                     
                     screen_w = win32api.GetSystemMetrics(0)
                     screen_h = win32api.GetSystemMetrics(1)
                     
                     def move_absolute(x, y):
                         fx = int(x * 65535 / screen_w)
                         fy = int(y * 65535 / screen_h)
                         win32api.mouse_event(
                             win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, 
                             fx, fy, 0, 0
                         )

                     move_absolute(start_point[0], start_point[1])
                     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                     
                     last_point = start_point
                     for point in screen_points[1:]:
                         dist = math.hypot(point[0] - last_point[0], point[1] - last_point[1])
                         if dist > 0: 
                             steps = int(dist * 2) 
                             if steps < 1: steps = 1
                             for k in range(1, steps):
                                 t = k / steps
                                 tx = int(last_point[0] + (point[0] - last_point[0]) * t)
                                 ty = int(last_point[1] + (point[1] - last_point[1]) * t)
                                 move_absolute(tx, ty)
                                 await asyncio.sleep(0.001) 
                         
                         move_absolute(point[0], point[1])
                         await asyncio.sleep(0.001)
                         last_point = point
                         
                     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                     
                else:
                    # Fallback
                    if pyautogui:
                        pyautogui.moveTo(start_point[0], start_point[1], _pause=False)
                        pyautogui.mouseDown(_pause=False)
                        for point in screen_points[1:]:
                            pyautogui.moveTo(point[0], point[1], _pause=False)
                        pyautogui.mouseUp(_pause=False)
                
                shapes_drawn += 1
                if on_progress:
                    await on_progress(i + 1, len(screen_points_list))
                
            except Exception as e:
                logger.warning("shape_draw_failed", index=i, error=str(e))
                if pyautogui: pyautogui.mouseUp()
        
        return shapes_drawn


class VectorizationService:
    """Service for image vectorization."""
    
    @staticmethod
    async def vectorize_image(image_path: str, max_shapes: int, high_fidelity: bool = False, line_art: bool = False):
        # Stub for importing NeuralVectorizer (assumed existing in core)
        try:
            from app.core.artmaster.vectorizer import NeuralVectorizer, ImageProfile
            
            if line_art:
                profile = ImageProfile.LINE_ART
            elif high_fidelity:
                profile = ImageProfile.HIGH_FIDELITY
            else:
                profile = ImageProfile.DEFAULT
            
            vectorizer = NeuralVectorizer(profile=profile)
            vectorizer.processor.max_shapes = max_shapes
            
            contours = await asyncio.to_thread(
                vectorizer.vector_from_image,
                image_path=image_path
            )
            return contours
        except ImportError:
            logger.error("vectorizer_import_failed")
            return []
    
    @staticmethod
    def compute_screen_coordinates(contours, center_x, center_y, scale, image_shape):
        h, w = image_shape
        offset_x = center_x - int((w * scale) / 2)
        offset_y = center_y - int((h * scale) / 2)
        
        screen_points_list = []
        shape_types = []
        
        for contour in contours:
            raw_points = contour.points
            if len(raw_points) < 2:
                screen_points_list.append([])
                shape_types.append("unknown")
                continue
            
            screen_points = [
                (int(offset_x + p.x * scale), int(offset_y + p.y * scale))
                for p in raw_points
            ]
            screen_points_list.append(screen_points)
            # Safe access to shape_type
            shape_type = "unknown"
            if hasattr(contour, 'shape_type'):
                 shape_type = str(contour.shape_type.value) if hasattr(contour.shape_type, 'value') else str(contour.shape_type)
            shape_types.append(shape_type)
        
        return screen_points_list, shape_types


class ServiceContainer:
    """Dependency injection container."""
    
    def __init__(self):
        self._mouse = None
        
    def get_mouse(self):
        # Stub or import real mouse controller
        if self._mouse is None:
            # from app.core.artmaster.mouse_controller import QuantumMouseController
            # self._mouse = QuantumMouseController()
            self._mouse = object() # Mock for now
        return self._mouse

services = ServiceContainer()

def get_services() -> ServiceContainer:
    """FastAPI dependency."""
    return services

