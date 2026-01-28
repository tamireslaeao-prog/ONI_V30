"""
ONI Creative Engine - Theme Factory
Generates harmonious color palettes and design tokens procedurally.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple
import colorsys
import random
import structlog

logger = structlog.get_logger()

@dataclass
class ColorPalette:
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    mood: str
    
    def to_css_vars(self) -> str:
        return f"""
        --primary: {self.primary};
        --secondary: {self.secondary};
        --accent: {self.accent};
        --background: {self.background};
        --text: {self.text};
        """

class ThemeFactory:
    """Generates design themes and color palettes."""
    
    def __init__(self):
        self._presets = {
            "cyberpunk": {"h_range": (280, 340), "s_min": 0.8, "l_base": 0.1},
            "nature": {"h_range": (80, 160), "s_min": 0.4, "l_base": 0.9},
            "corporate": {"h_range": (200, 240), "s_min": 0.5, "l_base": 0.95},
            "dark_mode": {"h_range": (0, 360), "s_min": 0.0, "l_base": 0.05}
        }

    def generate_palette(self, mood: str = "cyberpunk") -> ColorPalette:
        """Generate a palette based on mood."""
        # Normalize mood
        mood_key = mood.lower() if mood.lower() in self._presets else "cyberpunk"
        settings = self._presets[mood_key]
        
        # Base Hue
        base_h = random.randint(*settings["h_range"]) / 360.0
        
        # Primary Color
        primary = self._hsl_to_hex(base_h, settings["s_min"], 0.5)
        
        # Complementary/Analogous logic
        sec_h = (base_h + 0.5) % 1.0 # Complementary
        secondary = self._hsl_to_hex(sec_h, settings["s_min"] * 0.8, 0.4)
        
        # Accent (Triadic)
        acc_h = (base_h + 0.33) % 1.0
        accent = self._hsl_to_hex(acc_h, 1.0, 0.6)
        
        # Background & Text
        is_dark = settings["l_base"] < 0.5
        bg_l = settings["l_base"]
        text_l = 0.9 if is_dark else 0.1
        
        background = self._hsl_to_hex(base_h, 0.1, bg_l)
        text = self._hsl_to_hex(base_h, 0.05, text_l)
        
        palette = ColorPalette(
            name=f"{mood.title()} Generated",
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            text=text,
            mood=mood
        )
        
        logger.info("palette_generated", mood=mood, primary=primary)
        return palette

    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
