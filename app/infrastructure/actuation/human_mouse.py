"""
ONI v5.0 - Human Mouse (The Specialist)
Advanced mouse controller with NumPy-based Bezier curves and speed profiles.
"""
import asyncio
import random
import time
from typing import Literal, Optional, Tuple, Union
from app.soul.types import ValidatedCoordinate

import numpy as np
import structlog

from app.core.config import settings
from app.infrastructure.actuation.win32_input import Win32InputController

logger = structlog.get_logger()

class HumanMouse:
    """
    Advanced human-like mouse controller using NumPy for fluid Bezier paths.
    
    Ported from 'vetorizador_improved_v6.py' and enhanced for ONI v5.0 Server.
    """
    
    def __init__(self, use_win32: bool = True):
        self._use_win32 = use_win32
        self._win32 = Win32InputController() if use_win32 else None
        
        # Speed profiles (pixels per second, roughly)
        self.speeds = {
            "precise": 0.5,   # Slow, high precision
            "balanced": 1.0,  # Normal usage
            "fast": 1.5,      # Quick actions
            "zero_latency": 10.0 # Machine speed
        }
        self.current_speed = "balanced"
        self._screen_res = (1920, 1080) # Cache, update on usage if needed
        
    def set_speed(self, mode: Literal["precise", "balanced", "fast", "zero_latency"]):
        """Set the movement speed profile."""
        if mode in self.speeds:
            self.current_speed = mode
            
    def _get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if self._win32:
            return self._win32.get_cursor_position()
        from app.core.safe_execution import SafePrimitive
        # Note: pyautogui.position() is a read operation, technically safe, but good to wrap or just leave if read-only.
        # SafePrimitive doesn't have read ops yet. Leaving position() raw is acceptible as it's not an ACTION.
        import pyautogui
        return pyautogui.position()

    def _check_bounds(self, x: int, y: int) -> Tuple[int, int]:
        """Validate and clamp coordinates to monitor bounds."""
        try:
            import mss
            with mss.mss() as sct:
                # Check if point is in any monitor
                for m in sct.monitors[1:]: 
                    if (m['left'] <= x < m['left'] + m['width'] and 
                        m['top'] <= y < m['top'] + m['height']):
                        return x, y
                
                # Clamp to primary if outside
                primary = sct.monitors[1]
                safe_x = max(primary['left'], min(x, primary['left'] + primary['width'] - 1))
                safe_y = max(primary['top'], min(y, primary['top'] + primary['height'] - 1))
                return safe_x, safe_y
        except Exception:
            return x, y

    def _bezier_curve(self, p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, num_points: int) -> np.ndarray:
        """
        Generate cubic Bezier curve points using NumPy.
        p0: Start [x, y]
        p1: Control 1 [x, y]
        p2: Control 2 [x, y]
        p3: End [x, y]
        """
        t = np.linspace(0, 1, num_points).reshape(-1, 1)
        t_matrix = np.hstack([
            (1-t)**3,           # (1-t)^3
            3*(1-t)**2 * t,     # 3(1-t)^2 * t
            3*(1-t) * t**2,     # 3(1-t) * t^2
            t**3                # t^3
        ])
        points_matrix = np.vstack([p0, p1, p2, p3])
        return t_matrix @ points_matrix

    def _ease_out_cubic(self, x: np.ndarray) -> np.ndarray:
        """Ease out cubic function for smoother arrival."""
        return 1 - np.power(1 - x, 3)

    async def move_to(self, target_x: Union[int, ValidatedCoordinate], target_y: int = None, duration: Optional[float] = None):
        """
        Human-like mouse movement to target.
        Accepts ValidatedCoordinate (Soul Safe) or raw ints (Unsafe).
        """
        from app.core.config import settings
        from app.soul.exceptions import AxiomViolationError

        if isinstance(target_x, ValidatedCoordinate):
            x, y = target_x.x, target_x.y
            logger.debug("soul_safe_move", source=target_x.source.value)
        else:
            x, y = target_x, target_y
            if settings.safety.enforce_axioms:
                raise AxiomViolationError("Blind movement attempted (No ValidatedCoordinate)", axiom_id=3)
            # STARTUP WARN: Blind movement detected
            logger.warning("unsafe_movement_warning", x=x, y=y)

        start_x, start_y = self._get_position()
        target_x, target_y = self._check_bounds(x, y)
        
        # Distance calculation
        dist = np.hypot(target_x - start_x, target_y - start_y)
        
        # Check for zero distance
        if dist < 3:
            return

        # Calculate duration based on speed profile if not provided
        speed_factor = self.speeds[self.current_speed]
        if duration is None:
            # Fitts's Law approximation: T = a + b * log2(D/W + 1)
            # Simplified: Base time + (Distance / SpeedConstant)
            base_duration = 0.15
            calculated_duration = base_duration + (dist / 1500.0) / speed_factor
            duration = max(0.1, min(calculated_duration, 2.0))
            
        # Machine speed shortcut
        if self.current_speed == "zero_latency" or duration < 0.05:
            await self._direct_move(target_x, target_y)
            return

        # Bezier Control Points
        # Randomize control points to create arcs (human behavior)
        # Control point 1: closer to start, deviated
        offset_var = min(dist * 0.2, 100)
        
        p0 = np.array([start_x, start_y])
        p3 = np.array([target_x, target_y])
        
        # Perpendicular vector for arc
        direction = p3 - p0
        perp = np.array([-direction[1], direction[0]])
        perp = perp / (np.linalg.norm(perp) + 1e-6)
        
        # Arc bias
        arc_scale = random.uniform(-1, 1) * offset_var
        
        p1 = p0 + direction * 0.3 + perp * arc_scale
        p2 = p0 + direction * 0.7 + perp * arc_scale
        
        # Add jitter to control points
        p1 += np.random.uniform(-20, 20, 2)
        p2 += np.random.uniform(-20, 20, 2)
        
        # Generate points
        hz = 60 # Updates per second
        num_steps = max(5, int(duration * hz))
        
        curve = self._bezier_curve(p0, p1, p2, p3, num_steps)
        
        # Apply easing to time steps (not path) to simulate acceleration/deceleration
        start_time = time.perf_counter()
        
        for i in range(1, len(curve)):
            # Determine when this point should be reached
            progress = i / num_steps
            # Easing: We want to be at 'progress' distance at 'eased_progress' time? 
            # Actually, standard bezier t is spatial. 
            # We just iterate and wait appropriate time.
            
            point = curve[i]
            x, y = int(point[0]), int(point[1])
            
            await self._direct_move(x, y)
            
            # Sleep management
            expected_elapsed = duration * progress
            actual_elapsed = time.perf_counter() - start_time
            sleep_needed = expected_elapsed - actual_elapsed
            
            if sleep_needed > 0:
                await asyncio.sleep(sleep_needed)

    async def _direct_move(self, x: int, y: int):
        """Internal low-level move."""
        if self._win32:
            self._win32.set_cursor_position(x, y)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_move(x, y)

    async def click(self, x: Union[int, ValidatedCoordinate] = None, y: int = None, button: str = "left", double: bool = False):
        """Click at position."""
        if isinstance(x, ValidatedCoordinate):
             await self.move_to(x)
        elif x is not None and y is not None:
             await self.move_to(x, y)
        
        # Pause before click
        await asyncio.sleep(random.uniform(0.02, 0.05))
        
        if self._win32:
            self._win32.click(button=button)
            if double:
                await asyncio.sleep(random.uniform(0.05, 0.1))
                self._win32.click(button=button)
        else:
            from app.core.safe_execution import SafePrimitive
            clicks = 2 if double else 1
            SafePrimitive.safe_click(clicks=clicks, button=button)
            
    async def double_click(self, x: int = None, y: int = None):
        """Double click (compatibility alias)."""
        await self.click(x, y, double=True)

    async def drag(self, start_x: Union[int, ValidatedCoordinate], start_y: int = None, end_x: Union[int, ValidatedCoordinate] = None, end_y: int = None, duration: float = 0.5, use_fallback: bool = True):
        """
        Human-like drag operation.
        
        Args:
            start_x: Start position (int or ValidatedCoordinate)
            start_y: Start Y (if start_x is int)
            end_x: End position (int or ValidatedCoordinate)
            end_y: End Y (if end_x is int)
            duration: Drag duration in seconds
            use_fallback: If True, use fallback mouse library for reliable drag
        """
        # Resolve coordinates
        if isinstance(start_x, ValidatedCoordinate):
            sx, sy = start_x.x, start_x.y
        else:
            sx, sy = start_x, start_y
            
        if isinstance(end_x, ValidatedCoordinate):
            ex, ey = end_x.x, end_x.y
        else:
            ex, ey = end_x, end_y
            
        if use_fallback:
            # Use fallback mouse library for reliable drag
            from app.infrastructure.actuation.mouse import drag as fallback_drag
            fallback_drag(sx, sy, ex, ey, absolute=True, duration=duration)
            return
            
        # Legacy human-like implementation (fallback)
        await self.move_to(sx, sy)
        await asyncio.sleep(0.1)
        
        if self._win32:
            self._win32.key_down("left")
        else:
            import pyautogui
            pyautogui.mouseDown() # TODO: Add SafePrimitive.safe_mouse_down
            
        await asyncio.sleep(0.1)
        
        # Drag is slower than move
        old_speed = self.current_speed
        self.current_speed = "precise" # Dragging requires precision/force
        await self.move_to(ex, ey)
        self.current_speed = old_speed
        
        await asyncio.sleep(0.1)
        
        if self._win32:
            self._win32.key_up("left")
        else:
            import pyautogui
            pyautogui.mouseUp()

