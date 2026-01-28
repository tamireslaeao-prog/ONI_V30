"""
ONI v5.0 - Routines Package
Modular keyboard routines for Windows, CorelDRAW, and Photoshop.

Usage:
    from app.agent.routines import WindowsRoutines, CorelRoutines, PhotoshopRoutines
    
    # Or use the unified class for backward compatibility:
    from app.agent.routines import UnifiedRoutines
"""

from typing import Any

from .base import RoutinesBase
from .windows import WindowsRoutines
from .corel import CorelRoutines
from .photoshop import PhotoshopRoutines


class UnifiedRoutines(WindowsRoutines, CorelRoutines, PhotoshopRoutines):
    """
    Unified routines class combining all modules.
    
    Provides backward compatibility with the original WindowsRoutines class
    by inheriting from all specialized routine modules.
    
    For new code, prefer using the specialized classes directly:
    - WindowsRoutines: System operations, file management
    - CorelRoutines: CorelDRAW-specific shortcuts
    - PhotoshopRoutines: Photoshop-specific shortcuts
    """
    
    def __init__(self, actuation: Any):
        """Initialize unified routines with all capabilities."""
        # Call parent __init__ (RoutinesBase handles the actuation)
        super().__init__(actuation)


# Backward compatibility alias
WindowsRoutines_Legacy = UnifiedRoutines


# Singleton pattern (backward compatible)
_routines: UnifiedRoutines | None = None


def get_routines(actuation: Any = None) -> UnifiedRoutines:
    """Get or create the unified routines singleton."""
    global _routines
    if _routines is None and actuation is not None:
        _routines = UnifiedRoutines(actuation)
    return _routines


# Export all classes
__all__ = [
    "RoutinesBase",
    "WindowsRoutines", 
    "CorelRoutines",
    "PhotoshopRoutines",
    "UnifiedRoutines",
    "get_routines",
]
