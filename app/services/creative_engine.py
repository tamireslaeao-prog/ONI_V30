"""
ONI Creative Engine Service
Exposes creative generation capabilities to the Agent.
"""
from typing import Dict, Any
import structlog
from app.services.creative.theme_factory import ThemeFactory
from app.services.creative.algorithmic_art import AlgorithmicArt

logger = structlog.get_logger()

class CreativeEngineService:
    """
    The heart of ONI's creative capabilities.
    """
    def __init__(self):
        self.theme_factory = ThemeFactory()
        self.art_generator = AlgorithmicArt(self.theme_factory)
        logger.info("creative_engine_initialized")

    def generate_theme_assets(self, mood: str = "cyberpunk", style: str = "geometric") -> Dict[str, Any]:
        """
        Generate a complete theme package.
        """
        palette = self.theme_factory.generate_palette(mood)
        svg_bg = self.art_generator.generate_svg(style=style, mood=mood)
        
        return {
            "palette": palette,
            "background_svg": svg_bg,
            "css_vars": palette.to_css_vars()
        }

    def get_palette(self, mood: str) -> Dict[str, str]:
        """Get just a palette dict."""
        p = self.theme_factory.generate_palette(mood)
        return {
            "primary": p.primary,
            "secondary": p.secondary,
            "accent": p.accent,
            "background": p.background,
            "text": p.text
        }
