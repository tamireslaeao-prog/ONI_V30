"""
ONI v2.0 - Screen Capture
High-performance screen capture with DXcam and MSS fallback
"""
import asyncio
import time
from collections.abc import Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import structlog
from PIL import Image

from app.core.config import settings
from app.core.exceptions import CaptureError

logger = structlog.get_logger()

# Constants
DEFAULT_FALLBACK_WIDTH = 1920
DEFAULT_FALLBACK_HEIGHT = 1080
CAPTURE_WORKER_THREADS = 2
MIN_FRAME_INTERVAL = 0.001  # 1ms minimum


@dataclass
class CaptureResult:
    """Result of screen capture."""
    image: np.ndarray
    width: int
    height: int
    capture_time_ms: float
    backend: str
    timestamp: float


class ScreenCapture:
    """
    High-performance screen capture.
    
    Features:
    - Primary: DXcam (DirectX, Windows only, 60+ FPS)
    - Fallback: MSS (cross-platform, 30+ FPS)
    - Async wrapper for non-blocking capture
    - Region-based capture support
    - Multi-monitor support
    """
    
    def __init__(
        self,
        backend: Literal["dxcam", "mss", "auto"] = "auto",
        target_fps: int | None = None,
    ) -> None:
        """
        Initialize screen capture.
        
        Args:
            backend: Capture backend ("dxcam", "mss", or "auto")
            target_fps: Target frames per second
        """
        self._backend = backend
        self._target_fps = target_fps or settings.vision.capture_fps
        self._executor = ThreadPoolExecutor(
            max_workers=CAPTURE_WORKER_THREADS,
            thread_name_prefix="capture"
        )
        
        self._dxcam_camera: Any = None
        self._active_backend: str | None = None
        
        self._frame_interval = max(1.0 / self._target_fps, MIN_FRAME_INTERVAL)
        self._last_capture_time = 0.0
        self._screen_size_cache: tuple[int, int] | None = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize capture backend."""
        if self._initialized:
            return
            
        if self._backend == "auto":
            try:
                await self._init_dxcam()
                self._active_backend = "dxcam"
                logger.info("capture_backend_initialized", backend="dxcam")
            except Exception as e:
                logger.warning("dxcam_init_failed_using_mss", error=str(e))
                await self._init_mss()
                self._active_backend = "mss"
        elif self._backend == "dxcam":
            await self._init_dxcam()
            self._active_backend = "dxcam"
        else:
            await self._init_mss()
            self._active_backend = "mss"
        
        self._initialized = True
    
    async def _init_dxcam(self) -> None:
        """Initialize DXcam capture."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._init_dxcam_sync)
    
    def _init_dxcam_sync(self) -> None:
        """Synchronous DXcam initialization."""
        try:
            import dxcam
            self._dxcam_camera = dxcam.create(output_color="BGR")
            if self._dxcam_camera is None:
                raise CaptureError("DXcam.create() returned None")
        except ImportError:
            raise CaptureError("DXcam not installed")
        except Exception as e:
            raise CaptureError(f"DXcam initialization failed: {e}")
    
    async def _init_mss(self) -> None:
        """Initialize MSS capture."""
        try:
            import mss
            # Verify MSS is importable (actual instance created per-thread)
            logger.info("capture_backend_initialized", backend="mss")
        except ImportError:
            raise CaptureError("MSS not installed")
        except Exception as e:
            raise CaptureError(f"MSS initialization failed: {e}")
    
    def _validate_region(self, region: tuple[int, int, int, int]) -> None:
        """Validate capture region parameters."""
        if len(region) != 4:
            raise ValueError("Region must be (x, y, width, height)")
        
        x, y, w, h = region
        if w <= 0 or h <= 0:
            raise ValueError(f"Invalid region dimensions: width={w}, height={h}")
        if x < 0 or y < 0:
            raise ValueError(f"Invalid region position: x={x}, y={y}")
    
    async def capture(
        self,
        region: tuple[int, int, int, int] | None = None,
    ) -> CaptureResult:
        """
        Capture screen.
        
        Args:
            region: Optional region (x, y, width, height)
            
        Returns:
            Capture result with image data
            
        Raises:
            ValueError: If region parameters are invalid
            CaptureError: If capture fails
        """
        if not self._initialized:
            await self.initialize()
        
        if region is not None:
            self._validate_region(region)
        
        # Rate limiting
        now = time.perf_counter()
        elapsed = now - self._last_capture_time
        if elapsed < self._frame_interval:
            await asyncio.sleep(self._frame_interval - elapsed)
        
        start_time = time.perf_counter()
        
        loop = asyncio.get_event_loop()
        if self._active_backend == "dxcam":
            image = await loop.run_in_executor(
                self._executor,
                self._capture_dxcam,
                region
            )
        else:
            image = await loop.run_in_executor(
                self._executor,
                self._capture_mss,
                region
            )
        
        capture_time = (time.perf_counter() - start_time) * 1000
        self._last_capture_time = time.perf_counter()
        
        return CaptureResult(
            image=image,
            width=image.shape[1],
            height=image.shape[0],
            capture_time_ms=capture_time,
            backend=self._active_backend or "unknown",
            timestamp=time.time(),
        )
    
    def _capture_dxcam(
        self,
        region: tuple[int, int, int, int] | None = None,
    ) -> np.ndarray:
        """Capture using DXcam."""
        if self._dxcam_camera is None:
            raise CaptureError("DXcam not initialized")
        
        try:
            if region:
                # DXcam uses (left, top, right, bottom)
                x, y, w, h = region
                frame = self._dxcam_camera.grab(region=(x, y, x + w, y + h))
            else:
                frame = self._dxcam_camera.grab()
            
            if frame is None:
                raise CaptureError("DXcam returned None frame")
            
            return frame
            
        except Exception as e:
            raise CaptureError(f"DXcam capture failed: {e}")
    
    def _capture_mss(
        self,
        region: tuple[int, int, int, int] | None = None,
    ) -> np.ndarray:
        """
        Capture using MSS.
        
        Note: MSS uses thread-local storage, so we create a fresh instance
        in each worker thread rather than reusing a shared instance.
        """
        try:
            import mss
            
            with mss.mss() as sct:
                if region:
                    x, y, w, h = region
                    monitor = {"left": x, "top": y, "width": w, "height": h}
                else:
                    # monitors[0] = full virtual desktop (all monitors)
                    # monitors[1] = primary monitor only
                    monitor = sct.monitors[0]
                
                screenshot = sct.grab(monitor)
                
                # Convert BGRA to BGR
                image = np.array(screenshot)[:, :, :3]
                
                return image
            
        except Exception as e:
            raise CaptureError(f"MSS capture failed: {e}")
    
    async def capture_pil(
        self,
        region: tuple[int, int, int, int] | None = None,
    ) -> Image.Image:
        """
        Capture screen and return as PIL Image.
        
        Args:
            region: Optional region
            
        Returns:
            PIL Image in RGB format
        """
        result = await self.capture(region)
        # Convert BGR to RGB
        rgb_image = result.image[:, :, ::-1]
        return Image.fromarray(rgb_image)
    
    def get_screen_size(self) -> tuple[int, int]:
        """
        Get primary screen dimensions.
        
        Returns cached value after first call for performance.
        """
        if self._screen_size_cache is not None:
            return self._screen_size_cache
        
        try:
            import mss
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                size = (monitor["width"], monitor["height"])
                self._screen_size_cache = size
                return size
                
        except Exception as e:
            logger.warning(
                "get_screen_size_failed_using_fallback",
                error=str(e),
                fallback=f"{DEFAULT_FALLBACK_WIDTH}x{DEFAULT_FALLBACK_HEIGHT}"
            )
            return DEFAULT_FALLBACK_WIDTH, DEFAULT_FALLBACK_HEIGHT
    
    async def start_continuous_capture(
        self,
        callback: Callable[[CaptureResult], Awaitable[None]],
        fps: int | None = None,
    ) -> None:
        """
        Start continuous capture loop.
        
        Args:
            callback: Async function to call with each frame
            fps: Override target FPS
        """
        frame_interval = max(1.0 / (fps or self._target_fps), MIN_FRAME_INTERVAL)
        
        while True:
            try:
                result = await self.capture()
                await callback(result)
                
                # Maintain frame rate
                elapsed = time.perf_counter() - self._last_capture_time
                if elapsed < frame_interval:
                    await asyncio.sleep(frame_interval - elapsed)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("continuous_capture_error", error=str(e))
                await asyncio.sleep(0.1)
    
    async def cleanup(self) -> None:
        """Clean up capture resources."""
        if self._dxcam_camera is not None:
            try:
                del self._dxcam_camera
            except Exception as e:
                logger.warning("dxcam_cleanup_error", error=str(e))
            finally:
                self._dxcam_camera = None
        
        self._executor.shutdown(wait=False)
        self._screen_size_cache = None
        self._initialized = False
        logger.debug("capture_cleanup_complete")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return False
