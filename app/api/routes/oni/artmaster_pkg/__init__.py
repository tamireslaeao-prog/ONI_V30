"""
ONI ArtMaster Package
Modular application-specific strategies for creative automation.

Usage:
    from app.api.routes.oni.artmaster import (
        ApplicationDetector,
        ApplicationType,
        ApplicationInfo,
        PhotoshopStrategy,
        PaintStrategy,
        GimpStrategy,
    )
"""

from .detector import ApplicationDetector, ApplicationType, ApplicationInfo
from .base_strategy import ApplicationStrategy, PYAUTOGUI_AVAILABLE
from .photoshop_strategy import PhotoshopStrategy
from .paint_strategy import PaintStrategy
from .gimp_strategy import GimpStrategy

__all__ = [
    "ApplicationDetector",
    "ApplicationType",
    "ApplicationInfo",
    "ApplicationStrategy",
    "PhotoshopStrategy",
    "PaintStrategy",
    "GimpStrategy",
    "PYAUTOGUI_AVAILABLE",
]
