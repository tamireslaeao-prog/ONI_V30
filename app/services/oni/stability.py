"""
ONI Stability Service
Prevents actions during animations/loading states.
"""

import asyncio
from collections import deque
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

try:
    import cv2
except ImportError:
    cv2 = None


class StabilityService:
    """
    Temporal Stability Service (v5.2).
    Prevents actions during animations/loading states.
    """
    _frame_buffer = deque(maxlen=5)
    _last_stable_time = 0.0
    
    @classmethod
    async def push_frame(cls, frame_bgr):
        """Add frame to temporal buffer."""
        import time
        cls._frame_buffer.append((frame_bgr, time.time()))
        
    @classmethod
    def is_stable(cls, threshold=5000) -> bool:
        """Check if screen is stable (no heavy animation)."""
        if len(cls._frame_buffer) < 2 or cv2 is None:
            return True
            
        recent, t1 = cls._frame_buffer[-1]
        oldest, t2 = cls._frame_buffer[0]
        
        gray1 = cv2.cvtColor(recent, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(oldest, cv2.COLOR_BGR2GRAY)
        
        small1 = cv2.resize(gray1, (64, 64))
        small2 = cv2.resize(gray2, (64, 64))
        
        diff = cv2.absdiff(small1, small2)
        score = np.sum(diff)
        
        return score < threshold

    @classmethod
    async def wait_until_stable(cls, vision_service, timeout=2.0, check_interval=0.2):
        """Block until screen stabilizes."""
        import time
        start = time.time()
        
        while (time.time() - start) < timeout:
            capture = await vision_service.capture()
            if capture:
                await cls.push_frame(capture.image)
            
            if cls.is_stable():
                return True
                
            await asyncio.sleep(check_interval)
            
        logger.warning("stability_timeout", timeout=timeout)
        return False
