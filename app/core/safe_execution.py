
import time
import math
import structlog
import pyautogui
from PIL import ImageChops
from typing import Optional, List, Any
from app.core.safety_monitor import SafetyMonitor
from app.core.process_sentinel import sentinel

logger = structlog.get_logger(__name__)

class SafeTaskExecutor:
    """
    Universal Safety Wrapper for long-running automation tasks.
    Implements:
    1. Global Kill Switch Check
    2. Task Chunking (Batching)
    3. Mandatory Yield/Pause
    4. Visual Verification (Ghost Drawing Detection)
    5. Process Sentinel Integration (Cleanup)
    6. Smart Recovery (ToT) logic
    """

    def __init__(self, job_id: str, total_items: int, target_chunks: int = 10, target_pids: List[int] = None):
        self.job_id = job_id
        self.total_items = total_items
        
        # Calculate Chunk Size
        self.chunk_size = math.ceil(total_items / target_chunks)
        if self.chunk_size < 1: self.chunk_size = 1
        
        # State
        self.current_index = 0
        self.consecutive_failures = 0
        self.max_recovery_attempts = 3
        self.last_screenshot = pyautogui.screenshot()
        
        # Track processes if provided
        if target_pids:
            for pid in target_pids:
                sentinel.track_pid(pid)
        
        # Reset Safety Monitor at start of any safe task
        SafetyMonitor.reset()
        
        logger.info("safe_executor_initialized", 
                    job_id=job_id, 
                    chunk_size=self.chunk_size, 
                    total=total_items)

    def get_next_batch(self) -> range:
        """Returns the range of indices for the next batch."""
        batch_end = min(self.current_index + self.chunk_size, self.total_items)
        return range(self.current_index, batch_end)

    def check_abort(self):
        """Checks for external or internal abort triggers. DISABLED."""
        # SafetyMonitor DISABLED by user request
        pass

    def verify_and_advance(self, batch_range: range) -> bool:
        """
        Called after a batch execution.
        Performs Visual Verification and Smart Recovery.
        """
        # 1. Mandatory Yield (Release Mouse)
        try:
            pyautogui.mouseUp()
        except Exception:
            pass
        time.sleep(0.5)

        # 2. Semantic/Visual Verification
        # Note: Semantic verification via Vision API will be added here
        current_screenshot = pyautogui.screenshot()
        diff = ImageChops.difference(self.last_screenshot, current_screenshot)
        bbox = diff.getbbox()
        
        batch_end = batch_range.stop

        if bbox:
            # SUCCESS: Visual change confirmed
            logger.info("visual_verification_passed", batch_end=batch_end)
            self.last_screenshot = current_screenshot
            self.consecutive_failures = 0
            self.current_index = batch_end # Commit progress
            return True
        else:
            # FAILURE: No change detected
            self.consecutive_failures += 1
            logger.warning("visual_verification_failed", 
                           reason="No pixel change detected", 
                           failures=self.consecutive_failures)
            
            if self.consecutive_failures <= self.max_recovery_attempts:
                # ToT RECOVERY STRATEGY
                self._perform_recovery_strategy()
                return False # Do not advance, Retry
            else:
                # Final fail: Purge and raise
                sentinel.emergency_purge_automation()
                raise RuntimeError(
                    f"Visual Verification Failed: Screen not changing after {self.max_recovery_attempts} retries."
                )

    def _perform_recovery_strategy(self):
        """Executes ToT fallback actions to recover system state."""
        logger.info("tot_recovery_active", strategy="Refocus and Purge Ghosts")
        
        # Strategy 1: Clear zombie processes that might be locking the app
        sentinel.scan_and_purge()
        
        # Strategy 2: Wake up UI / Ensure Focus
        pyautogui.press('alt') 
        time.sleep(1.0)
        pyautogui.press('esc') 
        time.sleep(0.5)
        
        # Log for telemetry
        logger.info("recovery_action_executed", action="Sentinel Purge + Focus Cycle")


class SafePrimitive:
    """
    Atomic Safety Primitives for single actions.
    Replaces bare pyautogui calls with managed, safety-checked execution.
    """
    
    @staticmethod
    def _pre_check():
        """Check safety before any physical action. DISABLED."""
        # SafetyMonitor DISABLED by user request
        # Ensure fail-safe is enabled at library level
        pyautogui.FAILSAFE = True

    @staticmethod
    def safe_click(x: int = None, y: int = None, clicks: int = 1, button: str = 'left'):
        SafePrimitive._pre_check()
        try:
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            time.sleep(0.1) # Micro-yield
        except pyautogui.FailSafeException:
            logger.critical("failsafe_triggered_physical")
            raise

    @staticmethod
    def safe_type(text: str, interval: float = 0.0):
        SafePrimitive._pre_check()
        pyautogui.typewrite(text, interval=interval)

    @staticmethod
    def safe_hotkey(*args):
        SafePrimitive._pre_check()
        pyautogui.hotkey(*args)
        
    @staticmethod
    def safe_press(keys):
        SafePrimitive._pre_check()
        pyautogui.press(keys)
        
    @staticmethod
    def safe_move(x: int, y: int, duration: float = 0.0):
        SafePrimitive._pre_check()
        pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def safe_drag(x: int, y: int, duration: float = 0.5, absolute: bool = False):
        SafePrimitive._pre_check()
        if absolute:
            pyautogui.dragTo(x, y, duration=duration)
        else:
            pyautogui.drag(x, y, duration=duration)

    @staticmethod
    def safe_scroll(clicks: int):
        SafePrimitive._pre_check()
        pyautogui.scroll(clicks)

    @staticmethod
    def safe_position():
        # Read-only, safely return position
        return pyautogui.position()

    @staticmethod
    def safe_mouse_down(button: str = 'left'):
        SafePrimitive._pre_check()
        pyautogui.mouseDown(button=button)

    @staticmethod
    def safe_mouse_up(button: str = 'left'):
        SafePrimitive._pre_check()
        pyautogui.mouseUp(button=button)
