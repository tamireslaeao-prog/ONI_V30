
import math
import time
import random
import numpy as np
import pyautogui
import structlog
from typing import Tuple, List, Optional

# CRITICAL: Disable ALL pyautogui delays for maximum speed
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0

logger = structlog.get_logger(__name__)


class QuantumMouseController:
    """
    Advanced mouse controller for ONI ArtMaster v5.2.
    Implements 'Human-Like' Bezier movements, velocity profiling, and Win32 direct access.
    """
    def __init__(self, use_win32: bool = True):
        """
        Initialize mouse controller.
        
        Args:
            use_win32: If True, use Win32 API for ultra-fast movements (Windows only)
        """
        self._win32 = None
        self._use_win32 = use_win32
        
        # Try to load Win32 controller
        if use_win32:
            try:
                from app.infrastructure.actuation.win32_input import Win32InputController
                self._win32 = Win32InputController()
                logger.info("win32_mouse_enabled")
            except Exception as e:
                logger.warning("win32_mouse_unavailable", error=str(e))
                self._use_win32 = False
        
        self.modes = {
            "SURGICAL": self.surgical_precision,
            "TECHNICAL": self.technical_linear,
            "HUMAN": self.natural_bezier,
            "ARTISTIC": self.gestural_flow,
            "TURBO": self.instant_teleport,
            "FAST": self.fast_direct,
            "WIN32": self.fast_direct_win32  # NEW: Ultra-fast Win32 API
        }
        
        # Safety: PyAutoGUI fail-safe
        pyautogui.FAILSAFE = True
        self.current_pos = pyautogui.position()

    def move(self, start: Tuple[int, int], end: Tuple[int, int], mode: str = "FAST"):
        """Execute move from start to end using specified mode."""
        if mode not in self.modes:
            mode = "FAST"
        self.modes[mode](start, end)
        self.current_pos = end

    def fast_direct(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        FAST mode: Direct movement with NO intermediate steps.
        Best for continuous drawing without dotting.
        """
        pyautogui.moveTo(end[0], end[1], _pause=False)

    def fast_direct_win32(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        WIN32 mode: Ultra-fast movement using Win32 API directly.
        Bypasses PyAutoGUI for maximum speed. Falls back to FAST if Win32 unavailable.
        """
        if self._win32:
            self._win32.set_cursor_position(end[0], end[1])
        else:
            # Fallback to pyautogui
            pyautogui.moveTo(end[0], end[1], _pause=False)

    def instant_teleport(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Instant movement - alias for fast_direct_win32 if available."""
        if self._win32:
            self._win32.set_cursor_position(end[0], end[1])
        else:
            pyautogui.moveTo(end[0], end[1], _pause=False)

    def technical_linear(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Straight line, constant speed. Good for technical drawing."""
        pyautogui.moveTo(start[0], start[1])
        pyautogui.dragTo(end[0], end[1], duration=0.5, button='left')

    def surgical_precision(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        Simulates sub-pixel precision.
        """
        distance = math.dist(start, end)
        steps = int(distance * 5)
        if steps == 0: return

        for i in range(steps + 1):
            t = i / steps
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            pyautogui.moveTo(int(x), int(y))
            time.sleep(0.002)

    def natural_bezier(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        Simulates human hand movement using Cubic Bezier curves with randomized control points.
        """
        dist = math.dist(start, end)
        
        # Don't curvify extremely short lines
        if dist < 5:
            self.surgical_precision(start, end)
            return

        # Random control points to simulate arch/hand movement
        offset_var = min(dist * 0.3, 50)
        
        # Midpoint drift
        mid_x = (start[0] + end[0]) / 2 + random.uniform(-offset_var, offset_var)
        mid_y = (start[1] + end[1]) / 2 + random.uniform(-offset_var, offset_var)
        
        # Control points
        ctrl1_x = (start[0] + mid_x) / 2
        ctrl1_y = (start[1] + mid_y) / 2
        
        ctrl2_x = (mid_x + end[0]) / 2
        ctrl2_y = (mid_y + end[1]) / 2
        
        steps = max(int(dist / 2), 10)
        
        for i in range(steps + 1):
            t = i / steps
            # Easing
            t_ease = self._ease_in_out_cubic(t)
            
            # Simple Quadratic for now, simpler calc
            # P = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
            x = (1-t_ease)**2 * start[0] + 2*(1-t_ease)*t_ease * mid_x + t_ease**2 * end[0]
            y = (1-t_ease)**2 * start[1] + 2*(1-t_ease)*t_ease * mid_y + t_ease**2 * end[1]
            
            pyautogui.moveTo(int(x), int(y))
            
            # Velocity profile: fast in middle, slow at ends
            # Sleep less in middle
            base_sleep = 0.002
            velocity_mod = 1.0 - (math.sin(t * math.pi) * 0.5) # 0.5 at peak speed
            time.sleep(base_sleep * velocity_mod)

    def gestural_flow(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        Artistic ease-in-out movement with tremor (noise).
        """
        dist = math.dist(start, end)
        steps = max(int(dist), 10) # High density
        
        for i in range(steps + 1):
            t_raw = i / steps
            t = self._ease_in_out_cubic(t_raw)
            
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            
            # Artistic noise (tremor)
            noise_x = random.gauss(0, 0.8)
            noise_y = random.gauss(0, 0.8)
            
            pyautogui.moveTo(int(x + noise_x), int(y + noise_y))
            # Fast drawing
            time.sleep(0.001)

    def _ease_in_out_cubic(self, t):
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
