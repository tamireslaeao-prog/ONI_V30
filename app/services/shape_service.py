"""
ONI v5.0 - Shape Service (The Specialist)
Advanced computer vision for shape detection and complexity analysis.
"""
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np
import structlog

logger = structlog.get_logger()

class ShapeType(Enum):
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    STAR = "star"
    CURVE = "curve"
    TEXT = "text"
    COMPLEX = "complex"

@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

@dataclass
class Shape:
    """Represents a detected shape."""
    type: ShapeType
    points: List[Tuple[int, int]]
    center: Tuple[int, int]
    bbox: BoundingBox
    area: float
    perimeter: float
    complexity: float
    circularity: float
    solidity: float
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "center": self.center,
            "bbox": {"x": self.bbox.x, "y": self.bbox.y, "w": self.bbox.width, "h": self.bbox.height},
            "area": self.area,
            "complexity": self.complexity
        }

class ShapeService:
    """
    Advanced Image Processor service for identifying shapes and UI elements.
    """
    
    def __init__(self):
        self.min_area = 50
        
    def analyze_image(self, image_bgr: np.ndarray, max_shapes: int = 50) -> Dict:
        """
        Analyze image to find shapes.
        
        Returns:
            Dict containing detected shapes and global metrics.
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Basic Metrics
        mean_brightness = np.mean(gray)
        
        # Detect Shapes
        shapes = self._find_shapes(image_bgr, gray)
        
        # Sort by importance (Area * Complexity)
        shapes.sort(key=lambda s: s.area * s.complexity, reverse=True)
        shapes = shapes[:max_shapes]
        
        return {
            "brightness": float(mean_brightness),
            "total_shapes": len(shapes),
            "shapes": [s.to_dict() for s in shapes]
        }
        
    def _find_shapes(self, image: np.ndarray, gray: np.ndarray) -> List[Shape]:
        """Find contours and classify shapes."""
        # Preprocessing
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Multi-threshold detection (canny + adaptive)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_shapes = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
                
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
                
            # Approx Poly
            epsilon = 0.02 * perimeter
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            # Bounding Box
            x, y, w, h = cv2.boundingRect(cnt)
            bbox = BoundingBox(x, y, w, h)
            
            # Metrics
            circularity = (4 * np.pi * area) / (perimeter ** 2)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # Classification
            shape_type = self._classify_shape(len(approx), circularity, solidity, w/h if h>0 else 1)
            
            # Complexity (0.0 to 1.0)
            complexity = 1.0 - solidity # More holes/concavity = more complex
            if shape_type == ShapeType.COMPLEX:
                complexity += 0.2
            
            # Convert points (only store approx for lightness)
            points = [(int(p[0][0]), int(p[0][1])) for p in approx]
            cx = x + w//2
            cy = y + h//2
            
            detected_shapes.append(Shape(
                type=shape_type,
                points=points,
                center=(cx, cy),
                bbox=bbox,
                area=area,
                perimeter=perimeter,
                complexity=complexity,
                circularity=circularity,
                solidity=solidity
            ))
            
        return detected_shapes

    def _classify_shape(self, vertices: int, circularity: float, solidity: float, aspect_ratio: float) -> ShapeType:
        """Classify shape based on geometry."""
        if circularity > 0.8:
            return ShapeType.CIRCLE if 0.8 < aspect_ratio < 1.2 else ShapeType.ELLIPSE
            
        if vertices == 3:
            return ShapeType.POLYGON # Triangle
            
        if vertices == 4:
            return ShapeType.RECTANGLE if 0.8 < aspect_ratio < 1.2 else ShapeType.RECTANGLE # Square is rect
            
        if vertices > 8:
            return ShapeType.CURVE if circularity < 0.5 else ShapeType.COMPLEX
            
        return ShapeType.POLYGON
