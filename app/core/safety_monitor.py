
import threading
import time
import structlog
import keyboard
from typing import Optional

logger = structlog.get_logger(__name__)

class SafetyMonitor:
    """
    Monitors global safety triggers (Kill Switch).
    Singleton.
    """
    _instance = None
    _abort_flag = False
    _listening = False
    _thread: Optional[threading.Thread] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SafetyMonitor, cls).__new__(cls)
        return cls._instance

    @classmethod
    def start_listening(cls):
        """Start the background listener for safety keys."""
        if cls._listening:
            return

        cls._listening = True
        cls._thread = threading.Thread(target=cls._monitor_loop, daemon=True)
        cls._thread.start()
        logger.info("safety_monitor_started", key="SPACE")

    @classmethod
    def _monitor_loop(cls):
        """Background loop to check for kill switch."""
        logger.info("safety_monitor_loop_active")
        
        # Register the hotkey directly with the keyboard library
        # This is non-blocking in modern versions, but we keep it simple
        try:
            while cls._listening:
                # Check for SPACEBAR
                if keyboard.is_pressed('space'):
                    if not cls._abort_flag:
                        logger.critical("KILL_SWITCH_ACTIVATED", reason="User pressed SPACE")
                        cls._abort_flag = True
                
                # Sleep to prevent high CPU usage
                time.sleep(0.05)
        except Exception as e:
            logger.error("safety_monitor_crashed", error=str(e))
            cls._listening = False

    @classmethod
    def is_abort_requested(cls) -> bool:
        """Check if abort has been triggered."""
        return cls._abort_flag

    @classmethod
    def reset(cls):
        """Reset the abort flag (e.g. at start of new heavy task)."""
        cls._abort_flag = False
        logger.info("safety_monitor_reset")

    @classmethod
    def stop(cls):
        """Stop the monitor."""
        cls._listening = False
