"""
ONI v5.0 - Routines (DEPRECATED - Use app.agent.routines package)

This file is maintained for backward compatibility only.
New code should import from the modular package:

    from app.agent.routines import WindowsRoutines, CorelRoutines, PhotoshopRoutines
    
Or for the unified class:

    from app.agent.routines import UnifiedRoutines, get_routines
"""

# Re-export everything from the new package for backward compatibility
from app.agent.routines import (
    RoutinesBase,
    WindowsRoutines,
    CorelRoutines, 
    PhotoshopRoutines,
    UnifiedRoutines,
    get_routines,
)

# Backward compatibility: WindowsRoutines was the original class name
# but it actually contained all routines
__all__ = [
    "RoutinesBase",
    "WindowsRoutines",
    "CorelRoutines",
    "PhotoshopRoutines", 
    "UnifiedRoutines",
    "get_routines",
]
