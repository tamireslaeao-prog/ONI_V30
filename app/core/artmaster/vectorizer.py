
"""
ONI ArtMaster v3.1 - Neural Vectorizer (Enhanced)
Ported from Smart Vectorizer v6.0 - Optimized for ONI Architecture.
Includes "Onihand" Skeletonization Mechanism (Zhang-Suen) for complete strokes.
"""

import cv2
import numpy as np
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Set
from enum import Enum
import logging
from collections import defaultdict
import colorsys
from pathlib import Path
import hashlib
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

class ProcessingConstants:
    """Central location for all processing constants."""
    
    # Image size limits
    MIN_IMAGE_SIZE = 10
    MAX_IMAGE_SIZE = 10000
    MAX_FILE_SIZE_MB = 50
    
    # Brightness thresholds
    BRIGHTNESS_DARK = 80
    BRIGHTNESS_BRIGHT = 180
    
    # Color similarity thresholds
    COLOR_SIMILARITY_RGB = 15
    
    # Edge detection
    CANNY_LOW_DEFAULT = (20, 60)
    CANNY_MED_DEFAULT = (40, 120)
    CANNY_HIGH_DEFAULT = (60, 180)
    
    # Morphology
    MORPH_KERNEL_SIZE_SMALL = 2
    MORPH_KERNEL_SIZE_DEFAULT = 3
    
    # Cache
    CACHE_HASH_BYTES = 8192  # Read first 8KB for hash
    CACHE_DEFAULT_TTL_SECONDS = 3600


# =============================================================================
# ENUMS
# =============================================================================

class ShapeType(str, Enum):
    """Identified shape types."""
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    STAR = "star"
    CURVE = "curve"
    TEXT = "text"
    COMPLEX = "complex"


class DrawStrategy(str, Enum):
    """Drawing strategies based on complexity."""
    ULTRA_PRECISE = "ultra_precise"
    PRECISE = "precise"
    BALANCED = "balanced"
    FAST = "fast"
    ULTRA_FAST = "ultra_fast"


class ImageProfile(str, Enum):
    """Pre-configured profiles for different image types."""
    LINE_ART = "line_art"              # Manga, sketches, technical drawings (Onihand Mode)
    HIGH_FIDELITY = "high_fidelity"    # Exact reproduction needed
    LOGO = "logo"                       # Logos, icons, simple graphics
    PHOTO = "photo"                     # Photographs, complex images
    DEFAULT = "default"                 # Balanced general-purpose


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Point:
    """2D point with utility methods."""
    x: int
    y: int
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple."""
        return (self.x, self.y)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y}
    
    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class BoundingBox:
    """Rectangle bounding box with utility methods."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Point:
        """Get center point."""
        return Point(self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def aspect_ratio(self) -> float:
        """Get width/height ratio."""
        return self.width / self.height if self.height > 0 else 1.0
    
    @property
    def area(self) -> int:
        """Get area in pixels."""
        return self.width * self.height

    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this box intersects another."""
        return not (
            self.x + self.width < other.x or
            other.x + other.width < self.x or
            self.y + self.height < other.y or
            other.y + other.height < self.y
        )
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside this box."""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)


@dataclass
class ColorInfo:
    """Color information in multiple formats."""
    rgb: Tuple[int, int, int]
    hsv: Tuple[float, float, float]
    hex: str
    is_grayscale: bool
    
    @staticmethod
    def from_rgb(rgb: Tuple[int, int, int]) -> 'ColorInfo':
        """Create ColorInfo from RGB tuple."""
        r, g, b = rgb
        hsv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Check if grayscale
        is_gray = (abs(r - g) < ProcessingConstants.COLOR_SIMILARITY_RGB and 
                   abs(g - b) < ProcessingConstants.COLOR_SIMILARITY_RGB and 
                   abs(r - b) < ProcessingConstants.COLOR_SIMILARITY_RGB)
        
        return ColorInfo(
            rgb=rgb,
            hsv=(hsv[0]*360, hsv[1]*100, hsv[2]*100),
            hex=hex_color,
            is_grayscale=is_gray
        )


@dataclass
class Region:
    """
    Represents a filled region/area in an image (for ArtMaster V2.0).
    Used for Paint Bucket fills and shape detection.
    """
    contour: List[Tuple[int, int]]  # Boundary points
    fill_color: Tuple[int, int, int]  # RGB color to fill (sampled from image)
    area: int  # Pixel area
    centroid: Tuple[int, int]  # Center point for paint bucket click
    bounding_box: Tuple[int, int, int, int]  # x, y, w, h
    is_background: bool = False  # True if this is the largest region (background)
    hierarchy_level: int = 0  # 0 = outermost, higher = nested deeper
    
    @property
    def is_large(self) -> bool:
        """Check if region is large enough for fill."""
        return self.area > 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "centroid": self.centroid,
            "fill_color": self.fill_color,
            "area": self.area,
            "bounding_box": self.bounding_box,
            "is_background": self.is_background,
            "point_count": len(self.contour)
        }


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
        """Get centroid of contour."""
        if not self.points: 
            return Point(0, 0)
        avg_x = sum(p.x for p in self.points) // len(self.points)
        avg_y = sum(p.y for p in self.points) // len(self.points)
        return Point(avg_x, avg_y)

    @property
    def recommended_strategy(self) -> DrawStrategy:
        """Get recommended drawing strategy based on shape."""
        if self.shape_type in [ShapeType.CIRCLE, ShapeType.ELLIPSE, ShapeType.RECTANGLE]:
            return DrawStrategy.FAST
        
        if self.complexity > 0.85: 
            return DrawStrategy.ULTRA_PRECISE
        elif self.complexity > 0.65: 
            return DrawStrategy.PRECISE
        elif self.complexity < 0.25: 
            return DrawStrategy.ULTRA_FAST
        elif self.complexity < 0.45: 
            return DrawStrategy.FAST
        return DrawStrategy.BALANCED


@dataclass
class Stroke:
    """Represents a continuous line stroke for line art drawing."""
    points: List[Tuple[int, int]]
    thickness: int = 2
    color: Tuple[int, int, int] = (0, 0, 0)
    
    @property
    def length(self) -> int:
        """Number of points in stroke."""
        return len(self.points)
    
    @property
    def is_valid(self) -> bool:
        """Check if stroke has enough points."""
        return len(self.points) >= 2
    
    @property
    def pixel_length(self) -> float:
        """Calculate actual pixel length of stroke."""
        if len(self.points) < 2:
            return 0
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
        """Get pre-configured profile."""
        profiles = {
            ImageProfile.LINE_ART: ProfileConfig(
                min_area=5,
                min_perimeter=10,
                max_shapes=1000, # Increased for skeleton details
                duplicate_threshold=2,
                approx_epsilon=0.0003,
                use_line_art_mode=True,
                retrieval_mode=cv2.RETR_LIST,
                denoise_strength=5
            ),
            ImageProfile.HIGH_FIDELITY: ProfileConfig(
                min_area=5,
                min_perimeter=10,
                max_shapes=500,
                duplicate_threshold=3,
                approx_epsilon=0.0005,
                retrieval_mode=cv2.RETR_LIST,
                denoise_strength=7
            ),
            ImageProfile.LOGO: ProfileConfig(
                min_area=50,
                min_perimeter=20,
                max_shapes=50,
                duplicate_threshold=8,
                approx_epsilon=0.001,
                retrieval_mode=cv2.RETR_EXTERNAL,
                denoise_strength=8
            ),
            ImageProfile.PHOTO: ProfileConfig(
                min_area=100,
                min_perimeter=40,
                max_shapes=150,
                duplicate_threshold=10,
                approx_epsilon=0.002,
                retrieval_mode=cv2.RETR_EXTERNAL,
                denoise_strength=12
            ),
            ImageProfile.DEFAULT: ProfileConfig(
                min_area=80,
                min_perimeter=30,
                max_shapes=100,
                duplicate_threshold=5,
                approx_epsilon=0.0002,
                retrieval_mode=cv2.RETR_EXTERNAL,
                denoise_strength=10
            )
        }
        return profiles.get(profile, profiles[ImageProfile.DEFAULT])


# =============================================================================
# LINE ART EXTRACTOR (ONIHAND MECHANISM)
# =============================================================================


# =============================================================================
# CURVE SMOOTHING & POST-PROCESSING
# =============================================================================

class CurveSmoothing:
    """
    Advanced curve smoothing and stroke connecting logic.
    Transforms raw pixel chains into organic, human-like strokes.
    """
    
    @staticmethod
    def remove_close_points(points: List[Point], min_dist: float = 2.0) -> List[Point]:
        """Remove points that are too close to each other."""
        if len(points) < 3: return points
        
        result = [points[0]]
        for i in range(1, len(points)):
            if points[i].distance_to(result[-1]) >= min_dist:
                result.append(points[i])
        
        # Always keep last point
        if result[-1] != points[-1]:
            result.append(points[-1])
            
        return result

    @staticmethod
    def douglas_peucker(points: List[Point], epsilon: float) -> List[Point]:
        """Simplify curve using partial Ramer-Douglas-Peucker algorithm."""
        if len(points) < 3: return points
        
        # Convert to numpy for cv2
        pts = np.array([(p.x, p.y) for p in points], dtype=np.int32)
        
        # Calculate arc length for epsilon scaling
        arc_len = cv2.arcLength(pts, False)
        real_epsilon = epsilon * arc_len
        
        approx = cv2.approxPolyDP(pts, real_epsilon, False)
        
        return [Point(int(p[0][0]), int(p[0][1])) for p in approx]

    @staticmethod
    def catmull_rom_spline(points: List[Point], num_points: int = 4) -> List[Point]:
        """
        Generate smooth Catmull-Rom spline through points.
        Adds 'num_points' interpolated points between each pair.
        """
        if len(points) < 4: return points
        
        # Helper to unpack
        def get_pt(idx):
            idx = max(0, min(len(points) - 1, idx))
            return points[idx].x, points[idx].y

        new_points = []
        
        for i in range(len(points) - 1):
            p0x, p0y = get_pt(i - 1)
            p1x, p1y = get_pt(i)
            p2x, p2y = get_pt(i + 1)
            p3x, p3y = get_pt(i + 2)
            
            for t in np.linspace(0, 1, num_points, endpoint=False):
                # Catmull-Rom formula
                t2 = t * t
                t3 = t2 * t
                
                # Coefficients
                b0 = 0.5 * (-t3 + 2*t2 - t)
                b1 = 0.5 * (3*t3 - 5*t2 + 2)
                b2 = 0.5 * (-3*t3 + 4*t2 + t)
                b3 = 0.5 * (t3 - t2)
                
                x = p0x * b0 + p1x * b1 + p2x * b2 + p3x * b3
                y = p0y * b0 + p1y * b1 + p2y * b2 + p3y * b3
                new_points.append(Point(int(x), int(y)))
        
        new_points.append(points[-1])
        return new_points

    @staticmethod
    def connect_nearby_strokes(strokes: List[Stroke], max_dist: float = 15.0) -> List[Stroke]:
        """
        Connect endpoints of strokes that are close to each other.
        Reduces fragmentation common in skeletonization.
        """
        if not strokes: return []
        
        # Convert to list of point lists for easier manipulation
        chains = [list(s.points) for s in strokes]
        merged = True
        
        while merged:
            merged = False
            i = 0
            while i < len(chains):
                # Get endpoints of current chain
                c1_start = Point(*chains[i][0])
                c1_end = Point(*chains[i][-1])
                
                best_match = -1
                best_dist = max_dist
                merge_type = None # 0: end-start, 1: end-end, 2: start-start, 3: start-end
                
                for j in range(len(chains)):
                    if i == j: continue
                    
                    c2_start = Point(*chains[j][0])
                    c2_end = Point(*chains[j][-1])
                    
                    # Check connection possibilities
                    # End -> Start
                    d1 = c1_end.distance_to(c2_start)
                    if d1 < best_dist:
                        best_dist = d1
                        best_match = j
                        merge_type = 0
                    
                    # End -> End (reverse c2)
                    d2 = c1_end.distance_to(c2_end)
                    if d2 < best_dist:
                        best_dist = d2
                        best_match = j
                        merge_type = 1
                        
                    # Start -> Start (reverse c1)
                    d3 = c1_start.distance_to(c2_start)
                    if d3 < best_dist:
                        best_dist = d3
                        best_match = j
                        merge_type = 2
                        
                    # Start -> End (reverse both? no, just c1 reversed and c2 normal, acts like end->start)
                    d4 = c1_start.distance_to(c2_end)
                    if d4 < best_dist:
                        best_dist = d4
                        best_match = j
                        merge_type = 3
                
                if best_match != -1:
                    # Merge chains
                    target = chains[best_match]
                    
                    if merge_type == 0: # End -> Start
                        chains[i].extend(target)
                    elif merge_type == 1: # End -> End
                        chains[i].extend(target[::-1])
                    elif merge_type == 2: # Start -> Start
                        chains[i] = target[::-1] + chains[i]
                    elif merge_type == 3: # Start -> End
                        chains[i] = target + chains[i]
                        
                    chains.pop(best_match)
                    merged = True
                    # Don't increment i, check this merged chain again
                else:
                    i += 1
        
        # Convert back to Strokes
        new_strokes = []
        for chain in chains:
            if len(chain) >= 2:
                new_strokes.append(Stroke(points=chain, color=(0,0,0)))
                
        return new_strokes

class LineArtExtractor:
    """
    Extracts continuous strokes from line art images using skeletonization (Zhang-Suen).
    This provides 'complete strokes' (centerlines) rather than outlines.
    """
    
    def __init__(self, min_stroke_length: int = 15, dark_threshold: int = -1): # -1 for Adaptive (Otsu)
        """
        Initialize extractor.
        
        Args:
            min_stroke_length: Minimum points in a stroke to be kept
            dark_threshold: Pixels darker than this are considered lines (0-255). -1 uses Otsu.
        """
        self.min_stroke_length = min_stroke_length
        self.dark_threshold = dark_threshold
    
    def extract_strokes(self, image: np.ndarray) -> List[Stroke]:
        """
        Extract all strokes from a line art image.
        
        Args:
            image: BGR or grayscale image
            
        Returns:
            List of Stroke objects representing continuous lines
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Threshold to get binary image (invert so lines are white)
        if self.dark_threshold == -1:
             # Adaptive thresholding (Otsu) - Robust for sketches
            thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 1. Sensitivity Boost +40 (Capture Faint Lines)
            boosted_thresh = min(thresh_val + 40, 250)
            _, binary = cv2.threshold(gray, boosted_thresh, 255, cv2.THRESH_BINARY_INV)
            
            # 2. AGGRESSIVE Morphological Closing (5x5 kernel to connect gaps BEFORE skeletonization)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            logger.info(f"lineart_threshold: mode=otsu value={thresh_val} boosted={boosted_thresh} morphology=close_5x5")
        else:
            _, binary = cv2.threshold(gray, self.dark_threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Apply morphological skeleton (The "Onihand" Core)
        # USE CANNY EDGE DETECTION instead of skeletonization
        # This preserves the original line shape better for thick line art
        raw_strokes = self._extract_contours_canny(gray)
        logger.info(f"lineart_raw: strokes_found={len(raw_strokes)}")
        
        # --- HUMANIZED STROKES PIPELINE ---
        
        # 1. Merge nearby fragments (FINE: Connect only very close fragments, preserve details)
        merged_strokes = CurveSmoothing.connect_nearby_strokes(raw_strokes, max_dist=5.0)
        logger.info(f"lineart_merged: from={len(raw_strokes)} to={len(merged_strokes)}")
        
        final_strokes = []
        for stroke in merged_strokes:
            points = [Point(p[0], p[1]) for p in stroke.points]
            
            # 2. Simplify (remove pixel noise, keep corners)
            simplified = CurveSmoothing.remove_close_points(points, min_dist=1.5)
            simplified = CurveSmoothing.douglas_peucker(simplified, epsilon=0.001)
            
            # 3. Smooth (add organic curvature)
            # Only smooth if enough points to avoid distorting tiny details
            smoothed = CurveSmoothing.catmull_rom_spline(simplified, num_points=4)
            
            if len(smoothed) >= 2:
                final_strokes.append(Stroke(
                    points=[s.to_tuple() for s in smoothed],
                    color=stroke.color
                ))
        
        logger.info(f"lineart_final: smoothed_strokes={len(final_strokes)}")
        
        return final_strokes
    
    def _skeletonize_optimized(self, binary: np.ndarray) -> np.ndarray:
        """
        Optimized skeletonization using Zhang-Suen algorithm.
        Faster than iterative morphological approach.
        """
        skeleton = np.zeros(binary.shape, dtype=np.uint8)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        
        temp = binary.copy()
        iterations = 0
        max_iterations = 100  # Safety limit
        
        while iterations < max_iterations:
            eroded = cv2.erode(temp, element)
            opened = cv2.dilate(eroded, element)
            subset = cv2.subtract(temp, opened)
            skeleton = cv2.bitwise_or(skeleton, subset)
            temp = eroded.copy()
            
            if cv2.countNonZero(temp) == 0:
                break
            
            iterations += 1
        
        logger.debug(f"skeletonization_complete: iterations={iterations}")
        return skeleton
    
    def _extract_contours_canny(self, gray: np.ndarray) -> List[Stroke]:
        """
        Alternative to skeletonization: Use Canny Edge Detection to find
        the OUTER CONTOURS of thick black lines, then trace them directly.
        This preserves the original shape better than skeletonization.
        """
        # 1. Apply Canny Edge Detection (Higher thresholds = cleaner edges, less noise)
        edges = cv2.Canny(gray, 100, 200)
        
        # 2. Dilate edges slightly to connect nearby fragments
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # 3. Find ALL contours on the edge image (RETR_LIST captures inner details too)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        strokes = []
        for contour in contours:
            if len(contour) < self.min_stroke_length:
                continue
            
            # Convert contour to list of points
            points = [(int(p[0][0]), int(p[0][1])) for p in contour]
            
            stroke = Stroke(
                points=points,
                thickness=2,
                color=(0, 0, 0)
            )
            
            if stroke.is_valid:
                strokes.append(stroke)
        
        # Sort strokes by size (largest first - these are the main shapes)
        strokes.sort(key=lambda s: len(s.points), reverse=True)
        
        logger.info(f"canny_contours_found: count={len(strokes)}")
        return strokes
    
    def _trace_strokes(self, skeleton: np.ndarray) -> List[Stroke]:
        """
        Trace continuous strokes from skeleton image.
        Uses connected component analysis and contour tracing.
        """
        strokes = []
        
        # Find all contours in the skeleton
        contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        for contour in contours:
            if len(contour) < self.min_stroke_length:
                continue
            
            # Extract all points (CHAIN_APPROX_NONE gives us every pixel)
            points = [(int(p[0][0]), int(p[0][1])) for p in contour]
            
            stroke = Stroke(
                points=points,
                thickness=2,
                color=(0, 0, 0)
            )
            
            if stroke.is_valid:
                strokes.append(stroke)
        
        # Sort strokes by position (top-left to bottom-right)
        strokes.sort(key=lambda s: (s.points[0][1], s.points[0][0]))
        
        return strokes
    
    def _extract_regions(self, image: np.ndarray) -> List[Region]:
        """
        Extract filled regions from image for Paint Bucket fills.
        
        Uses RETR_TREE to detect region hierarchy (outer vs inner regions).
        Samples fill color from the centroid of each region.
        
        Returns list of Region objects sorted by area (largest first).
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            color_image = image
        else:
            gray = image.copy()
            color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Threshold to find filled areas (inverted: white areas become fillable regions)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours with hierarchy (RETR_TREE gives parent-child relationships)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if hierarchy is None or len(contours) == 0:
            return []
        
        regions = []
        hierarchy = hierarchy[0]  # Flatten hierarchy array
        
        # Find the largest area to identify background
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Skip tiny regions (noise)
            if area < 100:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate centroid using moments
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2
            
            # Sample fill color from centroid (ensure within image bounds)
            cx = max(0, min(cx, color_image.shape[1] - 1))
            cy = max(0, min(cy, color_image.shape[0] - 1))
            
            # Get color at centroid (BGR -> RGB)
            bgr = color_image[cy, cx]
            fill_color = (int(bgr[2]), int(bgr[1]), int(bgr[0]))
            
            # Determine hierarchy level from parent info
            parent_idx = hierarchy[i][3]
            level = 0
            while parent_idx >= 0:
                level += 1
                parent_idx = hierarchy[parent_idx][3]
            
            # Check if this is the background (largest region at level 0)
            is_background = (area == max_area and level == 0)
            
            # Convert contour points to list of tuples
            points = [(int(p[0][0]), int(p[0][1])) for p in contour]
            
            region = Region(
                contour=points,
                fill_color=fill_color,
                area=int(area),
                centroid=(cx, cy),
                bounding_box=(x, y, w, h),
                is_background=is_background,
                hierarchy_level=level
            )
            regions.append(region)
        
        # Sort by area (largest first, but background should be handled separately)
        regions.sort(key=lambda r: r.area, reverse=True)
        
        logger.info(f"regions_extracted: count={len(regions)} max_area={max_area}")
        return regions
    
    def strokes_to_contours(self, strokes: List[Stroke]) -> List[Contour]:
        """Convert strokes to Contour objects for compatibility."""
        contours = []
        
        for stroke in strokes:
            if not stroke.is_valid:
                continue
            
            # Calculate bounding box
            xs = [p[0] for p in stroke.points]
            ys = [p[1] for p in stroke.points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            bbox = BoundingBox(
                x=min_x,
                y=min_y,
                width=max(1, max_x - min_x),
                height=max(1, max_y - min_y)
            )
            
            # Create contour with all stroke points
            points = [Point(p[0], p[1]) for p in stroke.points]
            
            contour = Contour(
                points=points,
                area=stroke.pixel_length,
                perimeter=stroke.pixel_length,
                bbox=bbox,
                complexity=0.7,
                shape_type=ShapeType.CURVE,
                color_info=ColorInfo.from_rgb(stroke.color),
                circularity=0.0,
                solidity=1.0,
                aspect_ratio=bbox.aspect_ratio
            )
            contours.append(contour)
        
        return contours


# =============================================================================
# IMAGE PROCESSOR
# =============================================================================

class AdvancedImageProcessor:
    """
    Deep Image Analysis Logic with profile-based configuration.
    """
    
    def __init__(self, profile: ImageProfile = ImageProfile.DEFAULT, config: Optional[ProfileConfig] = None):
        """
        Initialize processor with profile.
        
        Args:
            profile: Pre-configured profile type
            config: Custom configuration (overrides profile)
        """
        self.profile = profile
        self.config = config if config else ProfileConfig.get_profile(profile)
        self.roi_margin = 0.15
        self.metrics = ProcessingMetrics()
        
        logger.info(f"processor_initialized: profile={profile.value} max_shapes={self.config.max_shapes}")
    
    def validate_image(self, image: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Validate image array.
        
        Returns:
            (is_valid, error_message)
        """
        if image is None:
            return False, "Image is None"
        
        if not isinstance(image, np.ndarray):
            return False, f"Image must be numpy array, got {type(image)}"
        
        if image.size == 0:
            return False, "Image is empty"
        
        h, w = image.shape[:2]
        
        if h < ProcessingConstants.MIN_IMAGE_SIZE or w < ProcessingConstants.MIN_IMAGE_SIZE:
            return False, f"Image too small: {w}x{h}"
        
        if h > ProcessingConstants.MAX_IMAGE_SIZE or w > ProcessingConstants.MAX_IMAGE_SIZE:
            return False, f"Image too large: {w}x{h}"
        
        return True, None
    
    def analyze_complexity(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze image metrics and characteristics.
        
        Returns:
            Dictionary with analysis results
        """
        start = datetime.now()
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        # Edge detection
        edges = cv2.Canny(gray, 30, 100)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Texture analysis
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_variance = laplacian.var()
        
        # Overall complexity score
        complexity = min(1.0, (edge_density * 8 + texture_variance / 1000))
        
        result = {
            'brightness': float(mean_brightness),
            'contrast': float(std_brightness),
            'edge_density': float(edge_density),
            'texture_variance': float(texture_variance),
            'complexity': float(complexity),
            'is_dark': mean_brightness < ProcessingConstants.BRIGHTNESS_DARK,
            'is_bright': mean_brightness > ProcessingConstants.BRIGHTNESS_BRIGHT,
            'is_line_art': edge_density > 0.05 and texture_variance < 200
        }
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        self.metrics.preprocessing_time_ms += elapsed
        
        return result

    def ultra_preprocessing(self, image: np.ndarray, analysis: Dict) -> List[np.ndarray]:
        """Generate multiple preprocessed image candidates."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        processed = []
        
        # Adaptive denoising
        if analysis['texture_variance'] > 500:
            denoised = cv2.fastNlMeansDenoising(gray, None, 
                                                self.config.denoise_strength, 7, 21)
        else:
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        limit = 4.0 if analysis['is_dark'] else (2.0 if analysis['is_bright'] else 3.0)
        clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        processed.append(enhanced)
        return processed

    def multi_scale_detection(self, image: np.ndarray, analysis: Dict) -> List[np.ndarray]:
        """Detect contours using multiple thresholding techniques."""
        preprocessed = self.ultra_preprocessing(image, analysis)
        all_masks = []
        
        for proc_img in preprocessed:
            # Otsu thresholding
            _, otsu = cv2.threshold(proc_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            all_masks.append(otsu)
            all_masks.append(cv2.bitwise_not(otsu))
            
            # Multi-level Canny edge detection
            for low, high in [ProcessingConstants.CANNY_LOW_DEFAULT,
                            ProcessingConstants.CANNY_MED_DEFAULT,
                            ProcessingConstants.CANNY_HIGH_DEFAULT]:
                canny = cv2.Canny(proc_img, low, high)
                kernel = np.ones((2, 2), np.uint8)
                dilated = cv2.dilate(canny, kernel, iterations=1)
                all_masks.append(dilated)
                
        return all_masks

    def classify_shape(self, contour_cv: np.ndarray, area: float, perimeter: float) -> ShapeType:
        """Classify contour shape type."""
        if len(contour_cv) < 5: 
            return ShapeType.CURVE
        
        # Calculate metrics
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        x, y, w, h = cv2.boundingRect(contour_cv)
        aspect = w / h if h > 0 else 1
        
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour_cv, epsilon, True)
        num_vertices = len(approx)
        
        hull = cv2.convexHull(contour_cv)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Classification logic
        if circularity > 0.85:
            return ShapeType.CIRCLE if 0.9 < aspect < 1.1 else ShapeType.ELLIPSE
            
        if num_vertices == 4 and 0.9 < aspect < 1.1:
            return ShapeType.RECTANGLE
            
        if num_vertices > 15:
            return ShapeType.COMPLEX
            
        return ShapeType.CURVE

    def calculate_complexity(self, cnt, area, perimeter, circularity, solidity, shape_type) -> float:
        """Calculate shape complexity score (0-1)."""
        compactness = (perimeter ** 2) / (4 * np.pi * area) if area > 0 else 1
        
        epsilon = 0.01 * perimeter
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        vertex_score = min(1.0, len(approx) / 50)
        
        type_weights = {
            ShapeType.CIRCLE: 0.2, ShapeType.ELLIPSE: 0.3, ShapeType.RECTANGLE: 0.3,
            ShapeType.POLYGON: 0.5, ShapeType.STAR: 0.7, ShapeType.CURVE: 0.6,
            ShapeType.COMPLEX: 0.9, ShapeType.TEXT: 0.8
        }
        
        complexity = (compactness * 0.2 + vertex_score * 0.3 + 
                     (1-circularity) * 0.2 + (1-solidity) * 0.2 + 
                     type_weights.get(shape_type, 0.5) * 0.1)
        
        return min(1.0, complexity)

    def find_contours(self, image: np.ndarray) -> List[Contour]:
        """
        Find and extract all contours from image.
        
        Returns:
            List of Contour objects
        """
        start = datetime.now()
        
        # Validate
        valid, error = self.validate_image(image)
        if not valid:
            logger.error(f"image_validation_failed: error={error}")
            return []
        
        h, w = image.shape[:2]
        analysis = self.analyze_complexity(image)
        masks = self.multi_scale_detection(image, analysis)
        
        all_contours = []
        seen_signatures = set()
        
        detection_start = datetime.now()
        
        for mask in masks:
            # Clean mask
            kernel_size = self.config.duplicate_threshold if self.config.use_line_art_mode else 3
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours_cv, _ = cv2.findContours(mask, self.config.retrieval_mode, 
                                             cv2.CHAIN_APPROX_TC89_L1)
            
            for cnt in contours_cv:
                area = cv2.contourArea(cnt)
                if area < self.config.min_area: 
                    continue
                
                perimeter = cv2.arcLength(cnt, True)
                if perimeter < self.config.min_perimeter: 
                    continue
                
                x, y, bw, bh = cv2.boundingRect(cnt)
                bbox = BoundingBox(x, y, bw, bh)
                
                # Deduplication signature
                div = self.config.duplicate_threshold
                sig = (x // div, y // div, bw // (div*2), bh // (div*2), int(area / (div*10)))
                if sig in seen_signatures: 
                    continue
                
                # Classify shape
                shape_type = self.classify_shape(cnt, area, perimeter)
                
                # Calculate metrics
                circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = area / hull_area if hull_area > 0 else 0
                
                complexity = self.calculate_complexity(cnt, area, perimeter, 
                                                      circularity, solidity, shape_type)
                
                # Approximate contour
                epsilon = self.config.approx_epsilon * perimeter
                if complexity > 0.8:
                    epsilon *= 0.1  # More precise for complex shapes
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                
                points = [Point(int(p[0][0]), int(p[0][1])) for p in approx]
                
                # In high fidelity mode, keep more points
                if self.config.use_line_art_mode and len(points) < len(cnt):
                    points = [Point(int(p[0][0]), int(p[0][1])) for p in cnt[::2]]
                
                # Extract average color
                mask_region = np.zeros(image.shape[:2], dtype=np.uint8)
                cv2.drawContours(mask_region, [cnt], -1, 255, -1)
                mean_color = cv2.mean(image, mask=mask_region)[:3]
                color_info = ColorInfo.from_rgb(tuple(map(int, mean_color)))
                
                contour_obj = Contour(
                    points=points, area=area, perimeter=perimeter,
                    bbox=bbox, complexity=complexity, shape_type=shape_type,
                    color_info=color_info, circularity=circularity,
                    solidity=solidity, aspect_ratio=bbox.aspect_ratio
                )
                
                all_contours.append(contour_obj)
                seen_signatures.add(sig)
        
        self.metrics.detection_time_ms = (datetime.now() - detection_start).total_seconds() * 1000
        self.metrics.shapes_found = len(all_contours)
        
        # Sort contours
        if self.config.use_line_art_mode:
            # Position-based sorting for consistent drawing
            all_contours.sort(key=lambda c: (c.bbox.y, c.bbox.x))
        else:
            # Importance-based sorting
            all_contours.sort(key=lambda c: c.area * (1 + c.complexity), reverse=True)
        
        # Limit to max shapes
        result = all_contours[:self.config.max_shapes]
        self.metrics.shapes_filtered = len(all_contours) - len(result)
        self.metrics.total_time_ms = (datetime.now() - start).total_seconds() * 1000
        
        logger.info(f"contours_found: total={len(result)} filtered={self.metrics.shapes_filtered} time_ms={round(self.metrics.total_time_ms, 1)}")
        
        return result


# =============================================================================
# NEURAL VECTORIZER (Main Service)
# =============================================================================

class NeuralVectorizer:
    """
    Main vectorization service with caching, profiles, and batch processing.
    """
    
    # Class-level cache
    _cache: Dict[str, Tuple[List[Contour], datetime]] = {}
    _cache_hits: int = 0
    _cache_misses: int = 0
    
    def __init__(
        self, 
        profile: ImageProfile = ImageProfile.DEFAULT,
        config: Optional[ProfileConfig] = None,
        enable_cache: bool = True
    ):
        """
        Initialize vectorizer.
        
        Args:
            profile: Pre-configured processing profile
            config: Custom configuration (overrides profile)
            enable_cache: Whether to use caching
        """
        self.profile = profile
        self.config = config if config else ProfileConfig.get_profile(profile)
        self.enable_cache = enable_cache
        
        # Initialize processor and line art extractor
        self.processor = AdvancedImageProcessor(profile=profile, config=self.config)
        self.line_art_extractor = LineArtExtractor(min_stroke_length=5)
        
        logger.info(f"vectorizer_initialized: profile={profile.value} line_art_mode={self.config.use_line_art_mode} cache={enable_cache}")
    
    def _compute_file_hash(self, image_path: str) -> str:
        """
        Compute fast hash of image file (first few KB only).
        
        Args:
            image_path: Path to image file
            
        Returns:
            MD5 hash string
        """
        try:
            with open(image_path, 'rb') as f:
                # Read only first portion for speed
                data = f.read(ProcessingConstants.CACHE_HASH_BYTES)
                file_size = Path(image_path).stat().st_size
                # Include file size in hash to differentiate files
                hash_input = data + str(file_size).encode()
                return hashlib.md5(hash_input).hexdigest()
        except Exception as e:
            logger.warning(f"hash_computation_failed: path={image_path} error={e}")
            return ""
    
    def _get_cache_key(self, image_path: str) -> Optional[str]:
        """Generate cache key for image."""
        if not self.enable_cache:
            return None
        
        file_hash = self._compute_file_hash(image_path)
        if not file_hash:
            return None
        
        # Include configuration in key
        mode_suffix = f"_{self.profile.value}_{self.config.max_shapes}"
        return f"{file_hash}{mode_suffix}"
    
    def _cache_get(self, key: str) -> Optional[List[Contour]]:
        """Get from cache if valid."""
        if not self.enable_cache or not key:
            return None
        
        if key in self._cache:
            contours, timestamp = self._cache[key]
            # Check if expired (1 hour default)
            if (datetime.now() - timestamp).total_seconds() < ProcessingConstants.CACHE_DEFAULT_TTL_SECONDS:
                NeuralVectorizer._cache_hits += 1
                logger.debug(f"cache_hit: key={key[:16]}")
                return contours
            else:
                # Expired
                del self._cache[key]
        
        return None
    
    def _cache_set(self, key: str, contours: List[Contour]):
        """Store in cache."""
        if not self.enable_cache or not key:
            return
        
        self._cache[key] = (contours, datetime.now())
        logger.debug(f"cache_set: key={key[:16]} shapes={len(contours)}")
    
    def vector_from_image(
        self, 
        image_path: Optional[str] = None, 
        image_array: Optional[np.ndarray] = None,
        profile: Optional[ImageProfile] = None
    ) -> List[Contour]:
        """
        Convert image to vector contours.
        
        Args:
            image_path: Path to image file
            image_array: numpy array of image (alternative to path)
            profile: Override profile for this call
            
        Returns:
            List of Contour objects
        """
        # Handle profile override
        if profile and profile != self.profile:
            self.profile = profile
            self.config = ProfileConfig.get_profile(profile)
            self.processor = AdvancedImageProcessor(profile=profile, config=self.config)
        
        # Try cache first (file-based only)
        if image_path:
            cache_key = self._get_cache_key(image_path)
            if cache_key:
                cached = self._cache_get(cache_key)
                if cached is not None:
                    return cached
        
        # Cache miss
        NeuralVectorizer._cache_misses += 1
        
        # Load image if needed
        if image_array is None and image_path:
            if not Path(image_path).exists():
                logger.error(f"image_not_found: path={image_path}")
                return []
            
            # Check file size
            try:
                file_size_mb = Path(image_path).stat().st_size / (1024 * 1024)
                if file_size_mb > ProcessingConstants.MAX_FILE_SIZE_MB:
                    logger.error(f"image_too_large: path={image_path} size_mb={round(file_size_mb, 1)}")
                    return []
            except Exception as e:
                logger.error(f"file_check_error: {e}")
                return []
            
            image_array = cv2.imread(image_path)
        
        if image_array is None:
            logger.error("no_image_provided")
            return []
        
        # Process based on mode
        if self.config.use_line_art_mode:
            logger.info(f"processing_lineart: path={image_path or 'array'}")
            strokes = self.line_art_extractor.extract_strokes(image_array)
            result = self.line_art_extractor.strokes_to_contours(strokes)
        else:
            logger.info(f"processing_standard: path={image_path or 'array'} profile={self.profile.value}")
            result = self.processor.find_contours(image_array)
        
        # Cache result
        if image_path:
            cache_key = self._get_cache_key(image_path)
            if cache_key:
                self._cache_set(cache_key, result)
        
        return result
    
    def batch_process(
        self, 
        image_paths: List[str],
        profile: Optional[ImageProfile] = None
    ) -> Dict[str, List[Contour]]:
        """
        Process multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            profile: Profile to use for all images
            
        Returns:
            Dictionary mapping paths to contour lists
        """
        logger.info(f"batch_processing_started: count={len(image_paths)}")
        start = datetime.now()
        
        results = {}
        for path in image_paths:
            try:
                contours = self.vector_from_image(image_path=path, profile=profile)
                results[path] = contours
            except Exception as e:
                logger.error(f"batch_item_failed: path={path} error={e}")
                results[path] = []
        
        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"batch_processing_complete: count={len(image_paths)} succeeded={sum(1 for v in results.values() if v)} time_s={round(elapsed, 2)}")
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics."""
        return {
            "processor_metrics": {
                "total_time_ms": round(self.processor.metrics.total_time_ms, 1),
                "shapes_found": self.processor.metrics.shapes_found,
                "shapes_filtered": self.processor.metrics.shapes_filtered
            },
            "cache_metrics": self.cache_stats()
        }
    
    @classmethod
    def cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        total = cls._cache_hits + cls._cache_misses
        hit_rate = cls._cache_hits / total if total > 0 else 0
        return {
            "size": len(cls._cache),
            "hits": cls._cache_hits,
            "misses": cls._cache_misses,
            "hit_rate_percent": round(hit_rate * 100, 1)
        }
    
    @classmethod
    def clear_cache(cls):
        """Clear vectorization cache."""
        cache_size = len(cls._cache)
        cls._cache.clear()
        cls._cache_hits = 0
        cls._cache_misses = 0
        logger.info(f"cache_cleared: items_removed={cache_size}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    vectorizer = NeuralVectorizer(profile=ImageProfile.LINE_ART)
    # contours = vectorizer.vector_from_image("path/to/image.png")
    pass