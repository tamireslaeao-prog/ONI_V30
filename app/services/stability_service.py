import asyncio
import time
import numpy as np
import cv2
import structlog
from typing import Optional, List, Tuple
from app.services.vision_shared import get_shared_vision, CachedFrame

logger = structlog.get_logger()

class StabilityService:
    """
    Temporal Intelligence Service.
    Ensures UI is stable (not animating/loading) before allowing actions.
    """
    
    def __init__(self):
        self.vision = get_shared_vision()
        self._frame_buffer: List[CachedFrame] = []
        self._buffer_size = 5  # Keep last 5 frames (~150-300ms history)
        self._stability_threshold = 0.01  # 1% pixel change allowed (noise)
        self._lock = asyncio.Lock()

    async def _update_buffer(self) -> CachedFrame:
        """Fetch latest frame and update buffer."""
        frame = await self.vision.get_current_frame()
        if not frame:
            # Force a capture if cache is empty (rare but possible on startup)
            # Using internal verify mechanism or just waiting
            await asyncio.sleep(0.1)
            frame = await self.vision.get_current_frame()
            
        if frame:
            async with self._lock:
                # Avoid duplicates
                if not self._frame_buffer or self._frame_buffer[-1].hash != frame.hash:
                    self._frame_buffer.append(frame)
                    if len(self._frame_buffer) > self._buffer_size:
                        self._frame_buffer.pop(0)
                        
        return frame

    def _calculate_visual_flux(self, roi: Optional[Tuple[int, int, int, int]] = None) -> float:
        """
        Calculate visual change rate (Optical Flow proxy) across buffered frames.
        Returns:
            Float 0.0 (static) to 1.0 (chaotic)
        """
        if len(self._frame_buffer) < 2:
            return 0.0 # Insufficient data, assume stable (or potentially risky?)

        # Compare first and last frame in buffer for gross movement
        f1 = self._frame_buffer[0].image_gray
        f2 = self._frame_buffer[-1].image_gray

        if roi:
            x, y, w, h = roi
            # Clamp ROI to image bounds
            h_img, w_img = f1.shape
            x = max(0, min(x, w_img))
            y = max(0, min(y, h_img))
            w = max(0, min(w, w_img - x))
            h = max(0, min(h, h_img - y))
            
            if w <= 0 or h <= 0: return 0.0
            
            f1 = f1[y:y+h, x:x+w]
            f2 = f2[y:y+h, x:x+w]

        # Calculate difference
        delta = cv2.absdiff(f1, f2)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        non_zero = np.count_nonzero(thresh)
        return non_zero / delta.size

    async def wait_until_stable(self, 
                              roi: Optional[Tuple[int, int, int, int]] = None, 
                              timeout: float = 5.0,
                              min_stable_frames: int = 3) -> bool:
        """
        Block until the specified ROI (or full screen) is stable.
        
        Args:
            roi: Tuple (x, y, w, h) or None for full screen.
            timeout: Max time to wait in seconds.
            min_stable_frames: Number of consecutive frames required to be stable.
            
        Returns:
            True if stable, False if timed out (unstable).
        """
        start_time = time.time()
        stable_streak = 0
        
        logger.info("stability_check_start", roi=roi, timeout=timeout)

        while (time.time() - start_time) < timeout:
            # 1. Update View
            await self._update_buffer()
            
            # 2. Measure Flux
            flux = self._calculate_visual_flux(roi)
            
            # 3. Assess Stability
            if flux <= self._stability_threshold:
                stable_streak += 1
            else:
                stable_streak = 0 # Reset streak if movement detected
                
            if stable_streak >= min_stable_frames:
                logger.info("stability_achieved", flux=flux, duration=time.time()-start_time)
                return True
                
            await asyncio.sleep(0.1) # Check every 100ms

        logger.warning("stability_timeout", last_flux=flux)
        return False

# Singleton
_stability_service = None

def get_stability_service():
    global _stability_service
    if not _stability_service:
        _stability_service = StabilityService()
    return _stability_service
