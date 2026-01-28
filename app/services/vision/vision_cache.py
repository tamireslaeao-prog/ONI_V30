import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """A cache entry for vision inference results."""
    frame_hash: str
    elements: List[Dict[str, Any]]
    timestamp: float = field(default_factory=time.time)

class VisionInferenceCache:
    """
    Cache for expensive vision inference results.
    Prevents re-running YOLO/OCR on identical or nearly identical frames.
    """
    def __init__(self, max_size: int = 50, ttl: float = 300.0):
        self._max_size = max_size
        self._ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []

    def get(self, frame_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached elements for a given frame hash."""
        if frame_hash in self._cache:
            entry = self._cache[frame_hash]
            
            # Check TTL
            if time.time() - entry.timestamp > self._ttl:
                del self._cache[frame_hash]
                if frame_hash in self._access_order:
                    self._access_order.remove(frame_hash)
                return None
            
            # Update access order (LRU)
            if frame_hash in self._access_order:
                self._access_order.remove(frame_hash)
            self._access_order.append(frame_hash)
            
            return entry.elements
        return None

    def set(self, frame_hash: str, elements: List[Dict[str, Any]]):
        """Store inference results in cache."""
        # Evict LRU if full
        if len(self._cache) >= self._max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
            
        self._cache[frame_hash] = CacheEntry(
            frame_hash=frame_hash,
            elements=elements,
            timestamp=time.time()
        )
        
        if frame_hash in self._access_order:
            self._access_order.remove(frame_hash)
        self._access_order.append(frame_hash)

    def clear(self):
        """Clear the cache."""
        self._cache.clear()
        self._access_order.clear()

# Global singleton for easy access
_global_vision_cache = VisionInferenceCache()

def get_vision_cache() -> VisionInferenceCache:
    return _global_vision_cache
