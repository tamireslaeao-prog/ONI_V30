"""
ONI Vectorizer - Enums
"""
from enum import Enum


class ShapeType(str, Enum):
    """Identified shape types."""
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    STAR = "star"
    CURVE = "curve"
    TEXT = "text"
    COMPLEX = "complex"


class DrawStrategy(str, Enum):
    """Drawing strategies based on complexity."""
    ULTRA_PRECISE = "ultra_precise"
    PRECISE = "precise"
    BALANCED = "balanced"
    FAST = "fast"
    ULTRA_FAST = "ultra_fast"


class ImageProfile(str, Enum):
    """Pre-configured profiles for different image types."""
    LINE_ART = "line_art"
    HIGH_FIDELITY = "high_fidelity"
    LOGO = "logo"
    PHOTO = "photo"
    DEFAULT = "default"
