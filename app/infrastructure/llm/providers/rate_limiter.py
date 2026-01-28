"""
ONI LLM - Intelligent Rate Limiter
Extracted from providers.py for modularity.
"""
import asyncio
import time
from typing import List, Optional
import structlog

logger = structlog.get_logger()


class IntelligentRateLimiter:
    """Rate limiter that learns and prevents 429 errors."""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.request_timestamps: List[float] = []
        self.cooldown_until: Optional[float] = None
        self.adaptive_delay = 1.0
        self.min_delay = 0.5
        self.max_delay = 30.0
    
    async def wait_if_needed(self) -> None:
        """Smart wait before making a request."""
        now = time.time()
        
        if self.cooldown_until and now < self.cooldown_until:
            wait_time = self.cooldown_until - now
            logger.info("rate_limiter_cooldown", wait_seconds=round(wait_time, 1))
            await asyncio.sleep(wait_time)
            self.cooldown_until = None
            return
        
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        
        if len(self.request_timestamps) >= self.requests_per_minute:
            oldest = self.request_timestamps[0]
            wait_time = 60 - (now - oldest) + 1
            if wait_time > 0:
                logger.info("rate_limiter_throttle", wait_seconds=round(wait_time, 1))
                await asyncio.sleep(wait_time)
        
        if self.adaptive_delay > self.min_delay:
            await asyncio.sleep(self.adaptive_delay)
        
        self.request_timestamps.append(time.time())
    
    def on_429_error(self) -> None:
        """Increase delay when receiving 429."""
        self.adaptive_delay = min(self.max_delay, self.adaptive_delay * 2)
        self.cooldown_until = time.time() + 30
        logger.warning("rate_limiter_429", cooldown_seconds=30, new_delay=round(self.adaptive_delay, 1))
    
    def on_success(self) -> None:
        """Gradually reduce delay after success."""
        self.adaptive_delay = max(self.min_delay, self.adaptive_delay * 0.9)
    
    def reset(self) -> None:
        """Reset rate limiter state."""
        self.request_timestamps = []
        self.cooldown_until = None
        self.adaptive_delay = 1.0
