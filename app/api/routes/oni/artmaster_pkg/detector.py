"""
ONI ArtMaster - Application Detection Module
Detects and identifies creative applications on the desktop.
"""

from enum import Enum
from typing import Optional, Dict, Tuple
from pydantic import BaseModel

import structlog

logger = structlog.get_logger(__name__)

# Module-level imports
try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    gw = None
    PYGETWINDOW_AVAILABLE = False


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


class ApplicationDetector:
    """Detect and identify creative applications."""
    
    # Application signatures (window title keywords)
    SIGNATURES = {
        ApplicationType.PHOTOSHOP: [
            "photoshop", "adobe photoshop", "ps cc", "ps 2020", "ps 2021",
            "ps 2022", "ps 2023", "ps 2024", "ps 2025", " @ ", "(rgb/", "(cmyk/"
        ],
        ApplicationType.PAINT: [
            "paint", "mspaint", "pintura"
        ],
        ApplicationType.PAINT_NET: [
            "paint.net", "paintdotnet"
        ],
        ApplicationType.GIMP: [
            "gimp", "gnu image manipulation"
        ],
        ApplicationType.KRITA: [
            "krita"
        ]
    }
    
    @classmethod
    def detect_application(cls) -> Optional[ApplicationInfo]:
        """
        Detect which creative application is currently active.
        
        Returns:
            ApplicationInfo if detected, None otherwise
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.warning("detection_unavailable", message="pygetwindow not installed")
            return None
            
        try:
            # Get all windows
            all_windows = gw.getAllWindows()
            
            # Check active window first
            active_window = gw.getActiveWindow()
            if active_window:
                app_info = cls._identify_window(active_window, is_active=True)
                if app_info:
                    return app_info
            
            # Check all windows for creative apps
            for window in all_windows:
                if not window.title:
                    continue
                    
                app_info = cls._identify_window(window, is_active=False)
                if app_info and app_info.app_type != ApplicationType.UNKNOWN:
                    return app_info
            
            return None
            
        except Exception as e:
            logger.error("application_detection_failed", error=str(e))
            return None
    
    @classmethod
    def _identify_window(cls, window, is_active: bool) -> Optional[ApplicationInfo]:
        """Identify application type from window."""
        title_lower = window.title.lower()
        
        for app_type, keywords in cls.SIGNATURES.items():
            if any(kw in title_lower for kw in keywords):
                try:
                    return ApplicationInfo(
                        app_type=app_type,
                        window_title=window.title,
                        version=cls._extract_version(window.title),
                        window_bounds={
                            "left": window.left,
                            "top": window.top,
                            "width": window.width,
                            "height": window.height
                        },
                        canvas_center=(
                            window.left + window.width // 2,
                            window.top + window.height // 2
                        ),
                        is_active=is_active
                    )
                except Exception:
                    continue
        
        return None
    
    @staticmethod
    def _extract_version(title: str) -> Optional[str]:
        """Extract version from window title."""
        import re
        
        # Common patterns: "2024", "CC 2024", "v24.0"
        patterns = [
            r'(20\d{2})',  # Year: 2020, 2024, etc.
            r'CC\s*(20\d{2})',  # CC 2024
            r'v?(\d+\.\d+)',  # v24.0, 24.0
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        return None
