"""
ONI v2.0 - Vision Module
"""
# Use try/except for optional imports
try:
    from app.infrastructure.vision.capture import ScreenCapture
except ImportError:
    ScreenCapture = None

try:
    from app.infrastructure.vision.preprocessing import ImagePreprocessor
except ImportError:
    ImagePreprocessor = None

try:
    from app.infrastructure.vision.semantic_locator import SemanticLocator
except ImportError:
    SemanticLocator = None

__all__ = ["ScreenCapture", "ImagePreprocessor", "SemanticLocator"]
