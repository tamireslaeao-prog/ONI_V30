"""
ONI ArtMaster - Configuration
"""
import os
from pathlib import Path

class ArtMasterConfig:
    """Centralized configuration."""
    
    MAX_SHAPES_LIMIT = 1000
    DEFAULT_MAX_SHAPES = 100
    MAX_IMAGE_SIZE_MB = 50
    CACHE_TTL_SECONDS = 3600
    
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60
    
    DRAW_TIMEOUT_SECONDS = 300
    APPLICATION_FOCUS_TIMEOUT = 5.0
    
    DEFAULT_SCALE = 0.8
    MIN_SCALE = 0.1
    MAX_SCALE = 10.0
    
    VERIFICATION_SETTLE_TIME = 0.5
    SSIM_THRESHOLD = 0.7
    
    TEMP_DIR = Path(os.getenv("TEMP", "/tmp"))
    PREVIEW_DIR = TEMP_DIR / "oni_previews"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ArtMasterConfig.ensure_directories()
