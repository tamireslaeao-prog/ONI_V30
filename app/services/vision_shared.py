"""
ONI v2.0 - Shared Vision Service
Centralized frame caching to avoid duplicate captures.

This service ensures that multiple WebSocket connections (Antigravity + Dashboard)
don't all capture screens independently, wasting CPU/GPU resources.
"""
import asyncio
import base64
import hashlib
import io
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, List

import cv2
import numpy as np
import structlog
from PIL import Image

from app.core.dependencies import container

logger = structlog.get_logger()


@dataclass
class CachedFrame:
    """A cached frame with metadata."""
    image_bgr: np.ndarray
    timestamp: float
    frame_number: int
    hash: str
    resolution: tuple[int, int]
    
    # Derived formats (lazy computed)
    _image_rgb: Optional[np.ndarray] = None
    _image_gray: Optional[np.ndarray] = None
    _jpeg_bytes: Optional[bytes] = None
    _jpeg_b64: Optional[str] = None
    
    # Fix P27: TTL (Time To Live)
    ttl: float = 2.0  # Seconds before frame is considered stale
    
    @property
    def is_expired(self) -> bool:
        """Check if frame is expired."""
        return time.time() - self.timestamp > self.ttl
    
    @property
    def image_rgb(self) -> np.ndarray:
        """Get RGB version (cached)."""
        if self._image_rgb is None:
            self._image_rgb = self.image_bgr[:, :, ::-1]
        return self._image_rgb
    
    @property
    def image_gray(self) -> np.ndarray:
        """Get grayscale version (cached)."""
        if self._image_gray is None:
            self._image_gray = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2GRAY)
            self._image_gray = cv2.GaussianBlur(self._image_gray, (21, 21), 0)
        return self._image_gray
    
    def get_jpeg(self, quality: int = 70) -> bytes:
        """Get JPEG encoded bytes (cached)."""
        if self._jpeg_bytes is None or quality != 70:
            img = Image.fromarray(self.image_rgb)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            if quality == 70:  # Only cache default quality
                self._jpeg_bytes = buffer.getvalue()
            return buffer.getvalue()
        return self._jpeg_bytes
    
    def get_jpeg_b64(self, quality: int = 70) -> str:
        """Get base64 JPEG (cached)."""
        if self._jpeg_b64 is None or quality != 70:
            jpeg_bytes = self.get_jpeg(quality)
            if quality == 70:
                self._jpeg_b64 = base64.b64encode(jpeg_bytes).decode('utf-8')
                return self._jpeg_b64
            return base64.b64encode(jpeg_bytes).decode('utf-8')
        return self._jpeg_b64


@dataclass
class FrameSubscriber:
    """A subscriber to frame updates."""
    name: str
    callback: Callable[[CachedFrame], None]
    fps_limit: float = 30.0  # Max FPS this subscriber wants
    last_frame_time: float = field(default_factory=time.time)
    
    def should_receive_frame(self) -> bool:
        """Check if enough time has passed for this subscriber's FPS limit."""
        if self.fps_limit <= 0:
            return True
        
        min_interval = 1.0 / self.fps_limit
        elapsed = time.time() - self.last_frame_time
        return elapsed >= min_interval
    
    def mark_received(self):
        """Mark that frame was received."""
        self.last_frame_time = time.time()


class SharedVisionService:
    """
    Centralized vision service that captures once and distributes to all subscribers.
    
    Benefits:
    - Single capture instead of N captures for N connections
    - Shared cache reduces memory
    - Subscribers get frames at their desired FPS
    - Automatic cleanup of stale subscribers
    """
    
    def __init__(self):
        self._current_frame: Optional[CachedFrame] = None
        self._previous_frame: Optional[CachedFrame] = None
        self._frame_number = 0
        self._subscribers: List[FrameSubscriber] = []
        self._lock = asyncio.Lock()
        self._capture_task: Optional[asyncio.Task] = None
        self._running = False
        self._capture_fps = 30.0  # Master capture rate
        
    async def start(self, sentinel_mode: bool = False):
        """
        Start the capture loop.
        
        Args:
            sentinel_mode: If True, captures frames even without subscribers (Always-On Vision).
        """
        if self._running:
            logger.warning("shared_vision_already_running")
            # Update mode if changed
            self._sentinel_mode = sentinel_mode
            return
        
        self._running = True
        self._sentinel_mode = sentinel_mode
        self._capture_task = asyncio.create_task(self._capture_loop())
        logger.info("shared_vision_started", fps=self._capture_fps, sentinel=sentinel_mode)
        
    async def stop(self):
        """Stop the capture loop."""
        self._running = False
        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass
        logger.info("shared_vision_stopped")

    async def get_fresh_frame(self, max_age: float = 0.2) -> Optional[CachedFrame]:
        """
        Get the current frame ONLY if it is fresh enough.
        If stale, it waits for the next immediate capture.
        
        Args:
            max_age: Maximum age in seconds.
            
        Returns:
            CachedFrame or None if capture fails.
        """
        # 1. Check current cache
        current = self._current_frame
        if current and not current.is_expired and (time.time() - current.timestamp < max_age):
            return current
            
        # 2. If stale, ensure we are running
        if not self._running:
            logger.warning("vision_not_running_starting_temporary")
            await self.start(sentinel_mode=True)
            
        # 3. Wait for next frame (subscribe loosely)
        future = asyncio.get_running_loop().create_future()
        
        def _callback(frame):
            if not future.done():
                future.set_result(frame)
                
        # Inject temporary subscriber
        sub = await self.subscribe("temp_fresh_request", _callback, fps_limit=60)
        
        try:
            return await asyncio.wait_for(future, timeout=2.0)
        except asyncio.TimeoutError:
            logger.error("fresh_frame_timeout")
            return None
        finally:
            await self.unsubscribe(sub)

        
    async def subscribe(
        self, 
        name: str, 
        callback: Callable[[CachedFrame], None],
        fps_limit: float = 30.0
    ) -> FrameSubscriber:
        """
        Subscribe to frame updates.
        
        Args:
            name: Subscriber name (for logging)
            callback: Async function to call with new frames
            fps_limit: Maximum FPS this subscriber wants
            
        Returns:
            FrameSubscriber instance
        """
        async with self._lock:
            subscriber = FrameSubscriber(
                name=name,
                callback=callback,
                fps_limit=fps_limit
            )
            self._subscribers.append(subscriber)
            
            logger.info("subscriber_added", 
                       name=name, 
                       fps_limit=fps_limit,
                       total_subscribers=len(self._subscribers))
            
            return subscriber
    
    async def unsubscribe(self, subscriber: FrameSubscriber):
        """Remove a subscriber."""
        async with self._lock:
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)
                logger.info("subscriber_removed", 
                           name=subscriber.name,
                           total_subscribers=len(self._subscribers))
    
    async def get_current_frame(self) -> Optional[CachedFrame]:
        """Get the most recent frame (cached)."""
        return self._current_frame
    
    async def get_previous_frame(self) -> Optional[CachedFrame]:
        """Get the previous frame for comparison."""
        return self._previous_frame
    
    def calculate_frame_diff(
        self, 
        frame1: CachedFrame, 
        frame2: CachedFrame
    ) -> float:
        """
        Calculate visual difference between two frames.
        
        Returns:
            Change ratio (0.0 = identical, 1.0 = completely different)
        """
        delta = cv2.absdiff(frame1.image_gray, frame2.image_gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        non_zero = np.count_nonzero(thresh)
        return non_zero / delta.size
    
    async def _capture_loop(self):
        """Main capture loop."""
        vision = container.get("vision")
        # Retry getting vision container if not immediately ready on startup
        # Fix P25: Exponential Backoff for Retry
        retry_delay = 0.5
        for i in range(5):
             if vision: break
             vision = container.get("vision")
             logger.warning("vision_service_wait", attempt=i+1, delay=retry_delay)
             await asyncio.sleep(retry_delay)
             retry_delay *= 2  # 0.5 -> 1.0 -> 2.0 -> 4.0 -> 8.0

        if not vision:
            logger.error("vision_service_not_available")
            return
        
        logger.info("capture_loop_started")
        
        try:
            while self._running:
                start_time = time.perf_counter()
                
                # Skip capture if no subscribers AND not in sentinel mode
                if not self._subscribers and not getattr(self, '_sentinel_mode', False):
                    await asyncio.sleep(0.5)
                    continue
                
                # Capture frame
                try:
                    capture_result = await vision.capture()
                    if not capture_result or capture_result.image is None:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Create cached frame
                    image_bgr = capture_result.image
                    
                    # Fix P26: Unified dHash optimization
                    from app.utils.vision_utils import compute_dhash
                    frame_hash = compute_dhash(image_bgr)
                    
                    # Skip if identical to last frame
                    if self._current_frame and frame_hash == self._current_frame.hash:
                        await asyncio.sleep(self._get_sleep_time())
                        continue
                    
                    self._frame_number += 1
                    
                    new_frame = CachedFrame(
                        image_bgr=image_bgr,
                        timestamp=time.time(),
                        frame_number=self._frame_number,
                        hash=frame_hash,
                        resolution=(image_bgr.shape[1], image_bgr.shape[0])
                    )
                    
                    # Update frame pointers
                    self._previous_frame = self._current_frame
                    self._current_frame = new_frame
                    
                    # Notify subscribers (async)
                    await self._notify_subscribers(new_frame)
                    
                except Exception as e:
                    logger.error("capture_error", error=str(e))
                    await asyncio.sleep(1.0)
                    continue
                
                # Maintain target FPS
                elapsed = time.perf_counter() - start_time
                sleep_time = max(0, self._get_sleep_time() - elapsed)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("capture_loop_cancelled")
        except Exception as e:
            logger.error("capture_loop_error", error=str(e), exc_info=True)
    
    async def _notify_subscribers(self, frame: CachedFrame):
        """Notify all subscribers of new frame in parallel."""
        if not self._subscribers:
            return

        async def _safe_notify(subscriber: FrameSubscriber):
            # Check if subscriber wants this frame based on FPS limit
            if not subscriber.should_receive_frame():
                return None
            
            try:
                # Call subscriber callback
                if asyncio.iscoroutinefunction(subscriber.callback):
                    # Parallel notification with timeout
                    await asyncio.wait_for(subscriber.callback(frame), timeout=3.0)
                else:
                    # Run sync callback in thread to avoid blocking loop
                    await asyncio.to_thread(subscriber.callback, frame)
                
                subscriber.mark_received()
                return None
            except asyncio.TimeoutError:
                logger.warning("subscriber_callback_timeout", subscriber=subscriber.name)
                return subscriber
            except Exception as e:
                logger.error("subscriber_callback_error", 
                           subscriber=subscriber.name,
                           error=str(e))
                return subscriber

        # Notify everyone in parallel
        results = await asyncio.gather(*[_safe_notify(s) for s in self._subscribers])
        
        # Collect dead subscribers (those that returned themselves instead of None)
        dead_subscribers = [r for r in results if r is not None]
        
        # Remove dead subscribers
        if dead_subscribers:
            async with self._lock:
                for sub in dead_subscribers:
                    if sub in self._subscribers:
                        self._subscribers.remove(sub)
                logger.info("dead_subscribers_removed", count=len(dead_subscribers))
    
    def _get_sleep_time(self) -> float:
        """Get sleep time to maintain target FPS."""
        return 1.0 / self._capture_fps if self._capture_fps > 0 else 0.033
    
    def set_capture_fps(self, fps: float):
        """
        Set the master capture FPS.
        """
        self._capture_fps = max(1.0, min(60.0, fps))
        logger.info("capture_fps_updated", fps=self._capture_fps)


# =============================================================================
# GLOBAL SHARED INSTANCE
# =============================================================================

_shared_vision: Optional[SharedVisionService] = None

def get_shared_vision() -> SharedVisionService:
    """Get or create the global shared vision service."""
    global _shared_vision
    if _shared_vision is None:
        _shared_vision = SharedVisionService()
    return _shared_vision


async def initialize_shared_vision():
    """Initialize and start the shared vision service."""
    service = get_shared_vision()
    await service.start()
    logger.info("shared_vision_initialized")


async def shutdown_shared_vision():
    """Shutdown the shared vision service."""
    global _shared_vision
    if _shared_vision:
        await _shared_vision.stop()
        _shared_vision = None
    logger.info("shared_vision_shutdown")
