"""
ONI v3.0 - Grounding Layer
Hybrid grounding system combining UI-TARS and OCR-based semantic locator.
"""
from .ui_tars import UITarsGrounding, GroundingResult, GroundingError
from .hybrid import HybridGrounding

# Import SemanticLocator from original location for compatibility
try:
    from app.infrastructure.vision.semantic_locator import SemanticLocator, LocatorMatch
except ImportError:
    SemanticLocator = None
    LocatorMatch = None

__all__ = [
    "UITarsGrounding",
    "GroundingResult",
    "GroundingError",
    "HybridGrounding",
    "SemanticLocator",
    "LocatorMatch",
]
