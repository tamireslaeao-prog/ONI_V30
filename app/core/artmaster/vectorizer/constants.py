"""
ONI Vectorizer - Constants
"""

class ProcessingConstants:
    """Central location for all processing constants."""
    
    MIN_IMAGE_SIZE = 10
    MAX_IMAGE_SIZE = 10000
    MAX_FILE_SIZE_MB = 50
    BRIGHTNESS_DARK = 80
    BRIGHTNESS_BRIGHT = 180
    COLOR_SIMILARITY_RGB = 15
    CANNY_LOW_DEFAULT = (20, 60)
    CANNY_MED_DEFAULT = (40, 120)
    CANNY_HIGH_DEFAULT = (60, 180)
    MORPH_KERNEL_SIZE_SMALL = 2
    MORPH_KERNEL_SIZE_DEFAULT = 3
    CACHE_HASH_BYTES = 8192
    CACHE_DEFAULT_TTL_SECONDS = 3600
