"""
ONI v5.0 - Routines Base Module
Common base class and utilities for all routine modules.
"""

import asyncio
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class RoutinesBase:
    """Base class for all routine modules with common functionality."""
    
    def __init__(self, actuation: Any):
        """
        Initialize routines base.
        
        Args:
            actuation: Actuation service with keyboard and mouse
        """
        self._actuation = actuation
        self._keyboard = actuation.keyboard if actuation else None
        self._mouse = actuation.mouse if actuation else None
    
    async def press_keys(self, *keys: str) -> bool:
        """Press one or more keys as a hotkey combination."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.hotkey(*keys)
            return True
        except Exception as e:
            logger.error("routine_press_keys_failed", keys=keys, error=str(e))
            return False
    
    async def type_text(self, text: str, interval: float = 0.0) -> bool:
        """Type text character by character."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.type_text(text, interval=interval)
            return True
        except Exception as e:
            logger.error("routine_type_text_failed", error=str(e))
            return False
    
    async def click(self, x: int = None, y: int = None, button: str = "left") -> bool:
        """Click at position or current cursor location."""
        if not self._mouse:
            return False
        try:
            if x is not None and y is not None:
                await self._mouse.move(x, y)
            await self._mouse.click(button=button)
            return True
        except Exception as e:
            logger.error("routine_click_failed", error=str(e))
            return False
    
    async def double_click(self, x: int = None, y: int = None) -> bool:
        """Double-click at position."""
        if not self._mouse:
            return False
        try:
            if x is not None and y is not None:
                await self._mouse.move(x, y)
            await self._mouse.double_click()
            return True
        except Exception as e:
            logger.error("routine_double_click_failed", error=str(e))
            return False
    
    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """Drag from start to end position."""
        if not self._mouse:
            return False
        try:
            await self._mouse.drag(start_x, start_y, end_x, end_y)
            return True
        except Exception as e:
            logger.error("routine_drag_failed", error=str(e))
            return False
    
    async def scroll(self, amount: int) -> bool:
        """Scroll mouse wheel (positive = up, negative = down)."""
        if not self._mouse:
            return False
        try:
            await self._mouse.scroll(amount)
            return True
        except Exception as e:
            logger.error("routine_scroll_failed", error=str(e))
            return False
    
    async def key_down(self, key: str) -> bool:
        """Press and hold a key."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.key_down(key)
            return True
        except Exception as e:
            logger.error("routine_key_down_failed", error=str(e))
            return False
    
    async def key_up(self, key: str) -> bool:
        """Release a held key."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.key_up(key)
            return True
        except Exception as e:
            logger.error("routine_key_up_failed", error=str(e))
            return False
