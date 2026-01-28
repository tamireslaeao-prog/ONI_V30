"""
ONI Vectorizer Package
Modularized from vectorizer.py (52KB) in Phase 5.
"""
from .constants import ProcessingConstants
from .enums import ShapeType, DrawStrategy, ImageProfile
from .models import (
    Point, BoundingBox, ColorInfo, Region, 
    Contour, Stroke, ProcessingMetrics, ProfileConfig
)
