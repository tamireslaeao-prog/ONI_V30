"""
ONI LLM - API Key Pool
Manages pool of API keys with rotation on failure.
"""
import time
from dataclasses import dataclass, field
from typing import List, Optional
import structlog

logger = structlog.get_logger()


@dataclass
class APIKeyPool:
    """Manages a pool of API keys with rotation on failure."""
    keys: List[str] = field(default_factory=list)
    current_index: int = 0
    failed_keys: dict = field(default_factory=dict)
    cooldown_seconds: int = 60
    
    def add_key(self, key: str) -> None:
        """Add a key to the pool if not empty."""
        if key and key not in self.keys:
            self.keys.append(key)
    
    def get_current_key(self) -> Optional[str]:
        """Get the current active key, skipping failed ones."""
        if not self.keys:
            return None
        
        now = time.time()
        attempts = 0
        
        while attempts < len(self.keys):
            key = self.keys[self.current_index]
            
            if key in self.failed_keys:
                if now - self.failed_keys[key] > self.cooldown_seconds:
                    del self.failed_keys[key]
                else:
                    self._rotate()
                    attempts += 1
                    continue
            
            return key
        
        return self.keys[0] if self.keys else None
    
    def mark_failed(self, key: str) -> None:
        """Mark a key as failed and rotate to next."""
        self.failed_keys[key] = time.time()
        self._rotate()
        logger.warning("api_key_failed_rotating", failed_keys=len(self.failed_keys), total_keys=len(self.keys))
    
    def _rotate(self) -> None:
        """Move to the next key."""
        if self.keys:
            self.current_index = (self.current_index + 1) % len(self.keys)
    
    @property
    def has_keys(self) -> bool:
        return len(self.keys) > 0
    
    @property
    def all_keys_exhausted(self) -> bool:
        """Check if all keys are currently in cooldown."""
        if not self.keys:
            return True
        now = time.time()
        return all(
            key in self.failed_keys and (now - self.failed_keys[key]) < self.cooldown_seconds
            for key in self.keys
        )
