"""
ONI Shape Executor - Types
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

class ShapeType(str, Enum):
    """Tipos de formas suportadas."""
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    SQUARE = "square"
    LINE = "line"
    BEZIER = "bezier"
    POLYGON = "polygon"
    TRIANGLE = "triangle"


@dataclass
class ShapeCommand:
    """Comando de forma universal."""
    shape_type: ShapeType
    params: Dict[str, Any]
    fill_color: Optional[str] = None  # Hex color
    stroke_color: Optional[str] = "#000000"
    stroke_width: int = 2
    
    @classmethod
    def circle(cls, center_x: int, center_y: int, radius: int, fill: str = None):
        return cls(
            shape_type=ShapeType.CIRCLE,
            params={"center_x": center_x, "center_y": center_y, "radius": radius},
            fill_color=fill
        )
    
    @classmethod
    def rectangle(cls, x: int, y: int, width: int, height: int, fill: str = None):
        return cls(
            shape_type=ShapeType.RECTANGLE,
            params={"x": x, "y": y, "width": width, "height": height},
            fill_color=fill
        )
    
    @classmethod
    def line(cls, x1: int, y1: int, x2: int, y2: int):
        return cls(
            shape_type=ShapeType.LINE,
            params={"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        )
    
    @classmethod
    def ellipse(cls, center_x: int, center_y: int, width: int, height: int, fill: str = None):
        return cls(
            shape_type=ShapeType.ELLIPSE,
            params={"center_x": center_x, "center_y": center_y, "width": width, "height": height},
            fill_color=fill
        )
