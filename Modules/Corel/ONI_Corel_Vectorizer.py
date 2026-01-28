"""
ONI Corel Advanced Vectorizer - Extracted from COR2/vetorizador.py
Contains: UltimateBezierDrawer, AdvancedImageProcessor, Shape Classification
"""
import cv2
import numpy as np
import colorsys
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
from scipy.interpolate import splprep, splev

logger = logging.getLogger(__name__)


class ShapeType(Enum):
    """Tipos de formas identificadas"""
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    STAR = "star"
    CURVE = "curve"
    TEXT = "text"
    COMPLEX = "complex"


class DrawTool(Enum):
    """Ferramentas do CorelDRAW"""
    BEZIER = "bezier"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    ARTISTIC_MEDIA = "artistic_media"
    PEN = "pen"


class DrawStrategy(Enum):
    """Estratégias de desenho"""
    ULTRA_PRECISE = "ultra_precise"
    PRECISE = "precise"
    BALANCED = "balanced"
    FAST = "fast"
    ULTRA_FAST = "ultra_fast"


@dataclass
class Point:
    x: int
    y: int
    
    def distance_to(self, other: 'Point') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y}
    
    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class ColorInfo:
    """Informações de cor"""
    rgb: Tuple[int, int, int]
    hsv: Tuple[float, float, float]
    hex: str
    is_grayscale: bool
    
    @staticmethod
    def from_rgb(rgb: Tuple[int, int, int]) -> 'ColorInfo':
        r, g, b = rgb
        hsv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        is_gray = abs(r - g) < 15 and abs(g - b) < 15 and abs(r - b) < 15
        return ColorInfo(rgb=rgb, hsv=(hsv[0]*360, hsv[1]*100, hsv[2]*100), hex=hex_color, is_grayscale=is_gray)


@dataclass
class BoundingBox:
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
    
    def touches_border(self, container_width: int, container_height: int, margin: int = 5) -> bool:
        return (self.x <= margin or self.y <= margin or 
                (self.x + self.width) >= container_width - margin or 
                (self.y + self.height) >= container_height - margin)


@dataclass
class Contour:
    """Representação avançada de um contorno"""
    points: List[Point]
    area: float
    perimeter: float
    bbox: BoundingBox
    complexity: float
    shape_type: ShapeType
    color_info: Optional[ColorInfo] = None
    circularity: float = 0.0
    solidity: float = 0.0
    
    @property
    def center(self) -> Point:
        avg_x = sum(p.x for p in self.points) // len(self.points)
        avg_y = sum(p.y for p in self.points) // len(self.points)
        return Point(avg_x, avg_y)
    
    @property
    def recommended_strategy(self) -> DrawStrategy:
        if self.shape_type in [ShapeType.CIRCLE, ShapeType.ELLIPSE, ShapeType.RECTANGLE]:
            return DrawStrategy.FAST
        if self.complexity > 0.85:
            return DrawStrategy.ULTRA_PRECISE
        elif self.complexity > 0.65:
            return DrawStrategy.PRECISE
        elif self.complexity < 0.25:
            return DrawStrategy.ULTRA_FAST
        return DrawStrategy.BALANCED
    
    @property
    def recommended_tool(self) -> DrawTool:
        tool_map = {
            ShapeType.CIRCLE: DrawTool.CIRCLE,
            ShapeType.ELLIPSE: DrawTool.CIRCLE,
            ShapeType.RECTANGLE: DrawTool.RECTANGLE,
            ShapeType.POLYGON: DrawTool.POLYGON,
        }
        return tool_map.get(self.shape_type, DrawTool.BEZIER)


class BezierMath:
    """Matemática de curvas Bezier cúbicas"""
    
    @staticmethod
    def cubic_point(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Tuple[float, float]:
        """Calcula ponto na curva Bezier cúbica"""
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        
        x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x
        y = mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y
        return x, y
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Função de easing suave"""
        if t < 0.5:
            return 4 * t * t * t
        p = 2 * t - 2
        return 1 + p * p * p / 2
    
    @staticmethod
    def smooth_contour(contour: np.ndarray, smoothness: float = 0.001) -> np.ndarray:
        """Suaviza contorno usando splines"""
        if len(contour) < 4:
            return contour
        
        epsilon = smoothness * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) < 4:
            return approx
        
        points = approx.reshape(-1, 2).T
        try:
            tck, u = splprep(points, s=len(points)*0.5, per=True, k=min(3, len(points)-1))
            u_new = np.linspace(0, 1, len(approx) * 2)
            smooth_points = splev(u_new, tck)
            return np.array(list(zip(smooth_points[0], smooth_points[1]))).astype(np.int32)
        except:
            return approx.reshape(-1, 2)


class AdvancedImageProcessor:
    """Processador de imagens com análise profunda"""
    
    def __init__(self):
        self.min_area = 80
        self.max_shapes = 100
    
    def analyze_complexity(self, image: np.ndarray) -> Dict:
        """Análise de complexidade da imagem"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        edge_density = np.sum(edges > 0) / edges.size
        corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
        num_corners = len(corners) if corners is not None else 0
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_variance = laplacian.var()
        
        return {
            'edge_density': edge_density,
            'num_corners': num_corners,
            'texture_variance': texture_variance,
            'complexity': min(1.0, edge_density * 8 + num_corners / 100 + texture_variance / 1000),
            'is_high_contrast': np.std(gray) > 60,
        }
    
    def extract_color_palette(self, image: np.ndarray, n_colors: int = 8) -> List[ColorInfo]:
        """Extrai paleta de cores dominantes via K-Means"""
        pixels = image.reshape(-1, 3)[::20].astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        
        unique, counts = np.unique(labels, return_counts=True)
        sorted_colors = sorted([(centers[i], counts[list(unique).index(i)] if i in unique else 0) 
                                for i in range(len(centers))], key=lambda x: x[1], reverse=True)
        
        return [ColorInfo.from_rgb(tuple(map(int, color))) for color, _ in sorted_colors]
    
    def classify_shape(self, contour: np.ndarray, area: float, perimeter: float) -> ShapeType:
        """Classifica tipo de forma"""
        if len(contour) < 5:
            return ShapeType.CURVE
        
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 1
        
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_vertices = len(approx)
        
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        if circularity > 0.85:
            return ShapeType.CIRCLE if 0.9 < aspect_ratio < 1.1 else ShapeType.ELLIPSE
        if num_vertices == 4 and 0.9 < aspect_ratio < 1.1:
            return ShapeType.RECTANGLE
        if 5 <= num_vertices <= 8:
            return ShapeType.STAR if solidity < 0.8 else ShapeType.POLYGON
        if num_vertices > 15:
            return ShapeType.COMPLEX
        return ShapeType.CURVE
    
    def find_contours(self, image: np.ndarray) -> List[Contour]:
        """Encontra e classifica contornos"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        contours_cv, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
        
        result = []
        for cnt in contours_cv:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
            
            perimeter = cv2.arcLength(cnt, True)
            x, y, w, h = cv2.boundingRect(cnt)
            bbox = BoundingBox(x, y, w, h)
            
            shape_type = self.classify_shape(cnt, area, perimeter)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
            
            points = [Point(int(p[0][0]), int(p[0][1])) for p in cnt]
            
            contour = Contour(
                points=points, area=area, perimeter=perimeter,
                bbox=bbox, complexity=min(1.0, len(cnt) / 100),
                shape_type=shape_type, circularity=circularity
            )
            result.append(contour)
        
        return sorted(result, key=lambda c: c.area, reverse=True)[:self.max_shapes]


# Export main classes
__all__ = [
    'ShapeType', 'DrawTool', 'DrawStrategy',
    'Point', 'ColorInfo', 'BoundingBox', 'Contour',
    'BezierMath', 'AdvancedImageProcessor'
]
