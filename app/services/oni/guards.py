"""
ONI Guard Services
Ensures proper screenshot/action sequencing and undo limits.
Enforces barriers B1-B5 via code blocking.
"""

import time
import math
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class ActionGuardService:
    """
    Action Guard Service (v8.1)
    Enforces ONI barriers (B2, B3, B5) via code blocking.
    Prevents the agent from executing actions if protocols are not followed.
    """
    
    # State tracking
    _last_screenshot_time: float = 0.0
    _last_active_window_check_time: float = 0.0
    _last_move_time: float = 0.0
    _last_move_coords: tuple[int, int] = (0, 0)
    
    # Configuration (Strictness)
    _max_time_since_screenshot: float = 20.0  # B3: Screenshot must be recent
    _max_time_since_window_check: float = 15.0 # B2: Must verify window recently
    _max_time_since_move: float = 10.0         # B5: Move must optionally be recent
    _move_click_dist_threshold: int = 100      # B5: Click must be near last move (pixels)
    
    _enabled: bool = True
    
    # Legacy support
    _screenshot_count_before_action: int = 0
    _action_awaiting_verification: Optional[str] = None

    @classmethod
    def record_screenshot(cls):
        """Record that a FRESH screenshot was captured (B3 compliance)."""
        cls._last_screenshot_time = time.time()
        cls._screenshot_count_before_action += 1
        
        # Clear awaiting verification
        if cls._action_awaiting_verification:
            logger.info("guard_verified", action=cls._action_awaiting_verification, class_id=str(id(cls)))
            cls._action_awaiting_verification = None
        else:
             logger.debug("guard_screenshot_recorded", class_id=str(id(cls)))

    @classmethod
    def record_active_window_check(cls):
        """Record that active window was checked (B2 compliance)."""
        cls._last_active_window_check_time = time.time()
        logger.debug("guard_window_check_recorded", class_id=str(id(cls)))

    @classmethod
    def record_move(cls, x: int, y: int):
        """Record a mouse move (B5 compliance)."""
        cls._last_move_time = time.time()
        cls._last_move_coords = (x, y)

    @classmethod
    def can_execute_action(cls, action_name: str, **kwargs) -> tuple[bool, str]:
        """
        Check if an action can be executed based on barriers.
        Returns: (allowed: bool, reason: str)
        """
        if not cls._enabled:
            return True, "Guard disabled"

        now = time.time()

        # --- B2: ACTIVE WINDOW CHECK ---
        # Critical for ALL input actions
        if action_name in ["click", "keys", "type", "drag", "scroll"]:
            time_since_window = now - cls._last_active_window_check_time
            if cls._last_active_window_check_time == 0.0 or time_since_window > cls._max_time_since_window_check:
                return False, f"⛔ BLOQUEIO B2: Use /api/active-window antes de '{action_name}'! (Último check: {round(time_since_window, 1)}s atrás)"

        # --- B3: SCREENSHOT FRESHNESS ---
        # Critical for visual actions
        if action_name in ["click", "drag", "move", "pixel_color"]:
            time_since_shot = now - cls._last_screenshot_time
            if cls._last_screenshot_time == 0.0 or time_since_shot > cls._max_time_since_screenshot:
                return False, f"⛔ BLOQUEIO B3: Screenshot antigo/inexistente! Use /api/screenshot?nocache=... (Último: {round(time_since_shot, 1)}s atrás)"

        # --- B5: MOVE BEFORE CLICK ---
        # Critical for clicks to ensure coordinates are verified
        if action_name == "click":
            target_x = kwargs.get("x")
            target_y = kwargs.get("y")
            
            if target_x is not None and target_y is not None:
                # 1. Check if we moved recently
                time_since_move = now - cls._last_move_time
                if cls._last_move_time == 0.0:
                     return False, "⛔ BLOQUEIO B5: NUNCA cique sem MOVER antes! Use /api/do?action=move... para verificar posição."
                
                # 2. Check distance (did we move TO the target?)
                last_x, last_y = cls._last_move_coords
                dist = math.sqrt((target_x - last_x)**2 + (target_y - last_y)**2)
                
                if dist > cls._move_click_dist_threshold:
                    return False, f"⛔ BLOQUEIO B5: Movimento longe do clique! Moveu p/ ({last_x},{last_y}), quer clicar em ({target_x},{target_y}). Dist: {int(dist)}px. Mova para o alvo primeiro!"

        # Warning for unverified previous actions (Legacy)
        if cls._action_awaiting_verification:
            logger.warning("guard_unverified_action_stacking", 
                          previous=cls._action_awaiting_verification,
                          new=action_name)

        return True, "OK"

    @classmethod
    def record_action(cls, action_name: str):
        """Record that an action was executed."""
        cls._action_awaiting_verification = action_name
        cls._screenshot_count_before_action = 0
        logger.info("guard_action_recorded", action=action_name, class_id=str(id(cls)))

    @classmethod
    def set_enabled(cls, enabled: bool):
        cls._enabled = enabled
        logger.info("guard_toggled", enabled=enabled)

    @classmethod
    def get_status(cls) -> dict:
        """Retornar status atual do guarda para debug."""
        now = time.time()
        return {
            "class_id": str(id(cls)),
            "enabled": cls._enabled,
            "last_active_window_check_ago": round(now - cls._last_active_window_check_time, 1) if cls._last_active_window_check_time > 0 else -1,
            "last_screenshot_ago": round(now - cls._last_screenshot_time, 1) if cls._last_screenshot_time > 0 else -1,
            "last_move_ago": round(now - cls._last_move_time, 1) if cls._last_move_time > 0 else -1,
            "last_move_coords": cls._last_move_coords,
            "rule": "B2, B3, B5 Enforced via Code Blocking",
            "module": __name__
        }

# Alias for backwards compatibility
ScreenshotGuardService = ActionGuardService 


class UndoGuardService:
    """
    Undo Guard Service (v1.0) - REGRA 6: 1-Undo-1-Check
    Previne múltiplos undos cegos consecutivos.
    """
    
    _consecutive_undos: int = 0
    _max_blind_undos: int = 1
    _last_undo_time: float = 0.0
    _enabled: bool = True
    
    @classmethod
    def record_undo(cls) -> dict:
        """Registrar undo executado."""
        if not cls._enabled:
            return {"blocked": False}
            
        cls._consecutive_undos += 1
        cls._last_undo_time = time.time()
        
        if cls._consecutive_undos > cls._max_blind_undos:
            return {
                "blocked": True,
                "warning": f"⚠️ REGRA 6: {cls._consecutive_undos} undos seguidos!",
                "consecutive_undos": cls._consecutive_undos,
                "solution": "Chame /api/active-window ou /api/screenshot primeiro"
            }
        
        return {
            "blocked": False,
            "consecutive_undos": cls._consecutive_undos,
            "warning": f"Undo {cls._consecutive_undos}/{cls._max_blind_undos}"
        }
    
    @classmethod
    def record_verification(cls):
        """Registrar que verificação foi feita."""
        cls._consecutive_undos = 0
    
    @classmethod
    def set_enabled(cls, enabled: bool):
        cls._enabled = enabled
    
    @classmethod
    def is_undo_keys(cls, keys: list) -> bool:
        """Detectar se combinação de teclas é undo."""
        keys_lower = [k.lower() for k in keys]
        return "ctrl" in keys_lower and "z" in keys_lower
