"""
ONI Rollback Service
Maintains action checkpoints and enables undo via Ctrl+Z.
"""

import time
import asyncio
import hashlib
from collections import deque
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

try:
    import cv2
except ImportError:
    cv2 = None


class RollbackService:
    """
    Rollback Service (v6.0).
    Maintains action checkpoints and enables undo via Ctrl+Z.
    """
    _checkpoints = deque(maxlen=10)
    _last_action = None
    
    @classmethod
    async def create_checkpoint(cls, vision_service, action_name: str, window_title: str = ""):
        """Save current screen state and window context before action."""
        if cv2 is None:
            return False
            
        try:
            capture = await vision_service.capture()
            if capture:
                gray = cv2.cvtColor(capture.image, cv2.COLOR_BGR2GRAY)
                small = cv2.resize(gray, (64, 64))
                frame_hash = hashlib.md5(small.tobytes()).hexdigest()
                
                cls._checkpoints.append({
                    "action": action_name,
                    "timestamp": time.time(),
                    "frame_hash": frame_hash,
                    "frame_data": small,
                    "window_title": window_title
                })
                cls._last_action = action_name
                logger.debug("checkpoint_created", action=action_name)
                return True
        except Exception as e:
            logger.error("checkpoint_failed", error=str(e))
        return False
    
    @classmethod
    async def should_rollback(cls, vision_service, current_window_title: str = "") -> bool:
        """Check if current state indicates failure (visual or semantic)."""
        if not cls._checkpoints or cv2 is None:
            return False
            
        try:
            capture = await vision_service.capture()
            if not capture:
                return False
                
            gray = cv2.cvtColor(capture.image, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(gray, (64, 64))
            
            last_checkpoint = cls._checkpoints[-1]
            
            # Semantic Check 1: Unexpected Application Switch (if title provided)
            # If we were in "Photoshop" and suddenly we are in "Error", that's bad.
            # But if we were in "Save As" and now "Photoshop", that's good (dialog closed).
            if current_window_title and last_checkpoint.get("window_title"):
                old_title = last_checkpoint["window_title"].lower()
                new_title = current_window_title.lower()
                
                # Detect crash/freeze/error dialogs
                critical_keywords = ["not responding", "error", "erro", "crash", "parou de funcionar"]
                for kw in critical_keywords:
                    if kw in new_title and kw not in old_title:
                        logger.warning("rollback_triggered_semantic", reason="error_keyword_in_title")
                        return True

            # Visual Check (Legacy)
            diff = cv2.absdiff(small, last_checkpoint["frame_data"])
            change_score = np.sum(diff)
            
            return change_score < 1000
        except Exception as e:
            logger.error("rollback_check_failed", error=str(e))
        return False
    
    @classmethod
    async def execute_rollback(cls, keyboard_service=None):
        """Execute Ctrl+Z to undo last action."""
        try:
            import pyautogui
            pyautogui.hotkey('ctrl', 'z')
            await asyncio.sleep(0.3)
            logger.info("rollback_executed", action=cls._last_action)
            return True
        except Exception as e:
            logger.error("rollback_failed", error=str(e))
        return False
