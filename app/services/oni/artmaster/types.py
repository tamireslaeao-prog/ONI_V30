"""
ONI ArtMaster - Types
"""
from enum import Enum
from typing import Dict, Optional, Tuple
from pydantic import BaseModel

class ApplicationType(str, Enum):
    """Supported creative applications."""
    PHOTOSHOP = "photoshop"
    PAINT = "paint"
    PAINT_NET = "paint_net"
    GIMP = "gimp"
    KRITA = "krita"
    UNKNOWN = "unknown"


class ApplicationInfo(BaseModel):
    """Information about detected application."""
    app_type: ApplicationType
    window_title: str
    version: Optional[str] = None
    window_bounds: Dict[str, int]
    canvas_center: Tuple[int, int]
    is_active: bool
