"""
ONI Vectorizer - Data Models
"""
import math
import colorsys
import cv2
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from .constants import ProcessingConstants
from .enums import ShapeType, DrawStrategy, ImageProfile


@dataclass
class Point:
    """2D point with utility methods."""
    x: int
    y: int
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y}
    
    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class BoundingBox:
    """Rectangle bounding box."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Point:
        return Point(self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 1.0
    
    @property
    def area(self) -> int:
        return self.width * self.height

    def intersects(self, other: 'BoundingBox') -> bool:
        return not (self.x + self.width < other.x or other.x + other.width < self.x or
                    self.y + self.height < other.y or other.y + other.height < self.y)
    
    def contains_point(self, point: Point) -> bool:
        return (self.x <= point.x <= self.x + self.width and self.y <= point.y <= self.y + self.height)


@dataclass
class ColorInfo:
    """Color information in multiple formats."""
    rgb: Tuple[int, int, int]
    hsv: Tuple[float, float, float]
    hex: str
    is_grayscale: bool
    
    @staticmethod
    def from_rgb(rgb: Tuple[int, int, int]) -> 'ColorInfo':
        r, g, b = rgb
        hsv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        is_gray = (abs(r - g) < ProcessingConstants.COLOR_SIMILARITY_RGB and 
                   abs(g - b) < ProcessingConstants.COLOR_SIMILARITY_RGB and 
                   abs(r - b) < ProcessingConstants.COLOR_SIMILARITY_RGB)
        return ColorInfo(rgb=rgb, hsv=(hsv[0]*360, hsv[1]*100, hsv[2]*100), hex=hex_color, is_grayscale=is_gray)


@dataclass
class Region:
    """Represents a filled region/area in an image."""
    contour: List[Tuple[int, int]]
    fill_color: Tuple[int, int, int]
    area: int
    centroid: Tuple[int, int]
    bounding_box: Tuple[int, int, int, int]
    is_background: bool = False
    hierarchy_level: int = 0
    
    @property
    def is_large(self) -> bool:
        return self.area > 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {"centroid": self.centroid, "fill_color": self.fill_color, "area": self.area, 
                "bounding_box": self.bounding_box, "is_background": self.is_background, "point_count": len(self.contour)}


@dataclass
class Contour:
    """Advanced Contour Representation."""
    points: List[Point]
    area: float
    perimeter: float
    bbox: BoundingBox
    complexity: float
    shape_type: ShapeType
    color_info: Optional[ColorInfo] = None
    circularity: float = 0.0
    solidity: float = 0.0
    aspect_ratio: float = 1.0
    
    @property
    def center(self) -> Point:
        if not self.points: return Point(0, 0)
        avg_x = sum(p.x for p in self.points) // len(self.points)
        avg_y = sum(p.y for p in self.points) // len(self.points)
        return Point(avg_x, avg_y)

    @property
    def recommended_strategy(self) -> DrawStrategy:
        if self.shape_type in [ShapeType.CIRCLE, ShapeType.ELLIPSE, ShapeType.RECTANGLE]:
            return DrawStrategy.FAST
        if self.complexity > 0.85: return DrawStrategy.ULTRA_PRECISE
        elif self.complexity > 0.65: return DrawStrategy.PRECISE
        elif self.complexity < 0.25: return DrawStrategy.ULTRA_FAST
        elif self.complexity < 0.45: return DrawStrategy.FAST
        return DrawStrategy.BALANCED


@dataclass
class Stroke:
    """Represents a continuous line stroke."""
    points: List[Tuple[int, int]]
    thickness: int = 2
    color: Tuple[int, int, int] = (0, 0, 0)
    
    @property
    def length(self) -> int:
        return len(self.points)
    
    @property
    def is_valid(self) -> bool:
        return len(self.points) >= 2
    
    @property
    def pixel_length(self) -> float:
        if len(self.points) < 2: return 0
        total = 0
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return total


@dataclass
class ProcessingMetrics:
    """Metrics for processing performance."""
    total_time_ms: float = 0
    preprocessing_time_ms: float = 0
    detection_time_ms: float = 0
    classification_time_ms: float = 0
    shapes_found: int = 0
    shapes_filtered: int = 0
    memory_used_mb: float = 0


@dataclass
class ProfileConfig:
    """Configuration for image processing profile."""
    min_area: int
    min_perimeter: int
    max_shapes: int
    duplicate_threshold: int
    approx_epsilon: float
    use_line_art_mode: bool = False
    retrieval_mode: int = cv2.RETR_EXTERNAL
    denoise_strength: int = 10
    
    @staticmethod
    def get_profile(profile: ImageProfile) -> 'ProfileConfig':
        profiles = {
            ImageProfile.LINE_ART: ProfileConfig(5, 10, 1000, 2, 0.0003, True, cv2.RETR_LIST, 5),
            ImageProfile.HIGH_FIDELITY: ProfileConfig(5, 10, 500, 3, 0.0005, False, cv2.RETR_LIST, 7),
            ImageProfile.LOGO: ProfileConfig(50, 20, 50, 8, 0.001, False, cv2.RETR_EXTERNAL, 8),
            ImageProfile.PHOTO: ProfileConfig(100, 40, 150, 10, 0.002, False, cv2.RETR_EXTERNAL, 12),
            ImageProfile.DEFAULT: ProfileConfig(80, 30, 100, 5, 0.0002, False, cv2.RETR_EXTERNAL, 10),
        }
        return profiles.get(profile, profiles[ImageProfile.DEFAULT])
