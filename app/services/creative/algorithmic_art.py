"""
ONI Creative Engine - Algorithmic Art Generator
Produces scalable vector graphics (SVG) based on mathematical patterns.
"""
import random
import structlog
from app.services.creative.theme_factory import ThemeFactory, ColorPalette

logger = structlog.get_logger()

class AlgorithmicArt:
    """Generates generative art SVGs."""
    
    def __init__(self, theme_factory: ThemeFactory):
        self.theme_factory = theme_factory

    def generate_svg(self, width: int = 1920, height: int = 1080, style: str = "geometric", mood: str = "cyberpunk") -> str:
        """Generate an SVG string."""
        palette = self.theme_factory.generate_palette(mood)
        
        header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background-color:{palette.background}">'
        footer = '</svg>'
        
        body = ""
        if style == "geometric":
            body = self._generate_geometric(width, height, palette)
        elif style == "grid":
            body = self._generate_grid(width, height, palette)
        else:
            body = self._generate_random_shapes(width, height, palette)
            
        return header + body + footer

    def _generate_geometric(self, w: int, h: int, p: ColorPalette) -> str:
        elements = []
        center_x, center_y = w // 2, h // 2
        
        # Concentric circles
        for r in range(500, 50, -50):
            color = random.choice([p.primary, p.secondary, p.accent])
            opacity = random.uniform(0.1, 0.5)
            elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{r}" stroke="{color}" stroke-width="2" fill="none" opacity="{opacity}" />')
            
        # Lines
        for _ in range(20):
            x1, y1 = random.randint(0, w), random.randint(0, h)
            x2, y2 = random.randint(0, w), random.randint(0, h)
            color = p.accent
            elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1" opacity="0.3" />')
            
        return "\n".join(elements)

    def _generate_grid(self, w: int, h: int, p: ColorPalette) -> str:
        elements = []
        step = 50
        for x in range(0, w, step):
            for y in range(0, h, step):
                if random.random() > 0.7:
                    color = random.choice([p.primary, p.secondary])
                    size = random.randint(5, 20)
                    elements.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{color}" opacity="0.4" />')
        return "\n".join(elements)

    def _generate_random_shapes(self, w: int, h: int, p: ColorPalette) -> str:
        elements = []
        for _ in range(50):
            shape_type = random.choice(["circle", "rect"])
            x, y = random.randint(0, w), random.randint(0, h)
            size = random.randint(10, 100)
            color = random.choice([p.primary, p.secondary, p.accent, p.text])
            opacity = random.uniform(0.1, 0.8)
            
            if shape_type == "circle":
                elements.append(f'<circle cx="{x}" cy="{y}" r="{size//2}" fill="{color}" opacity="{opacity}" />')
            else:
                 elements.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{color}" opacity="{opacity}" />')
        return "\n".join(elements)
