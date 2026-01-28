"""
ONI v2.0 - Working Memory
Fast in-memory storage using Redis for active session data
"""
import asyncio
import json
from datetime import datetime
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class WorkingMemory:
    """
    Working memory implementation using Redis.
    
    Features:
    - Fast key-value storage
    - TTL-based expiration
    - Session-scoped data
    - JSON serialization
    """
    
    def __init__(
        self,
        redis_url: str | None = None,
        ttl: int | None = None,
    ) -> None:
        """
        Initialize working memory.
        
        Args:
            redis_url: Redis connection URL
            ttl: Default TTL in seconds
        """
        self._redis_url = redis_url or settings.memory.redis_url
        self._default_ttl = ttl or settings.memory.working_memory_ttl
        self._redis: Any = None
        self._fallback: dict[str, tuple[Any, float]] = {}  # Fallback if Redis unavailable
        self._use_fallback = False
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(self._redis_url)
            await self._redis.ping()
            logger.info("working_memory_connected", url=self._redis_url)
        except Exception as e:
            logger.warning("redis_unavailable_using_fallback", error=str(e))
            self._use_fallback = True
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """
        Store a value.
        
        Args:
            key: Storage key
            value: Value to store (will be JSON serialized)
            ttl: Time-to-live in seconds
        """
        ttl = ttl or self._default_ttl
        serialized = json.dumps(value, default=str)
        
        if self._use_fallback:
            expire_at = datetime.now().timestamp() + ttl
            self._fallback[key] = (value, expire_at)
            return
        
        try:
            await self._redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error("working_memory_set_failed", key=key, error=str(e))
    
    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None
        """
        if self._use_fallback:
            if key in self._fallback:
                value, expire_at = self._fallback[key]
                if datetime.now().timestamp() < expire_at:
                    return value
                del self._fallback[key]
            return None
        
        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("working_memory_get_failed", key=key, error=str(e))
            return None
    
    async def delete(self, key: str) -> None:
        """Delete a value."""
        if self._use_fallback:
            self._fallback.pop(key, None)
            return
        
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.error("working_memory_delete_failed", key=key, error=str(e))
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._use_fallback:
            if key in self._fallback:
                _, expire_at = self._fallback[key]
                return datetime.now().timestamp() < expire_at
            return False
        
        try:
            return bool(await self._redis.exists(key))
        except Exception:
            return False
    
    async def set_hash(self, key: str, mapping: dict[str, Any]) -> None:
        """Store a hash (dict) value."""
        if self._use_fallback:
            await self.set(key, mapping)
            return
        
        try:
            serialized = {k: json.dumps(v, default=str) for k, v in mapping.items()}
            await self._redis.hset(key, mapping=serialized)
            await self._redis.expire(key, self._default_ttl)
        except Exception as e:
            logger.error("working_memory_hset_failed", key=key, error=str(e))
    
    async def get_hash(self, key: str) -> dict[str, Any] | None:
        """Retrieve a hash value."""
        if self._use_fallback:
            return await self.get(key)
        
        try:
            data = await self._redis.hgetall(key)
            if data:
                return {k.decode(): json.loads(v) for k, v in data.items()}
            return None
        except Exception as e:
            logger.error("working_memory_hget_failed", key=key, error=str(e))
            return None
    
    async def push(self, key: str, value: Any) -> None:
        """Push value to a list."""
        serialized = json.dumps(value, default=str)
        
        if self._use_fallback:
            existing = await self.get(key) or []
            existing.append(value)
            await self.set(key, existing)
            return
        
        try:
            await self._redis.rpush(key, serialized)
            await self._redis.expire(key, self._default_ttl)
        except Exception as e:
            logger.error("working_memory_push_failed", key=key, error=str(e))
    
    async def get_list(self, key: str, limit: int = 100) -> list[Any]:
        """Get list values."""
        if self._use_fallback:
            existing = await self.get(key) or []
            return existing[-limit:]
        
        try:
            data = await self._redis.lrange(key, -limit, -1)
            return [json.loads(item) for item in data]
        except Exception as e:
            logger.error("working_memory_list_failed", key=key, error=str(e))
            return []
    
    # =========================================================================
    # Session-specific methods
    # =========================================================================
    
    async def set_goal(self, goal: str) -> None:
        """Store current goal."""
        await self.set("oni:current_goal", goal)
    
    async def get_goal(self) -> str | None:
        """Get current goal."""
        return await self.get("oni:current_goal")
    
    async def add_action(self, action: dict[str, Any]) -> None:
        """Add action to history."""
        action["timestamp"] = datetime.now().isoformat()
        await self.push("oni:action_history", action)
    
    async def get_recent_actions(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent actions."""
        return await self.get_list("oni:action_history", limit)
    
    async def clear_session(self) -> None:
        """Clear all session data."""
        keys = ["oni:current_goal", "oni:action_history", "oni:context"]
        for key in keys:
            await self.delete(key)
        logger.info("session_cleared")
