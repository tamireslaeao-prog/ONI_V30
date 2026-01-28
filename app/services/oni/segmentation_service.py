"""
ONI v10.0 - Segmentation Service
Advanced image analysis using scikit-image for:
- Edge Detection (Canny)
- Structural Similarity (SSIM)
- Region Labeling (Connected Components)
- Contour Extraction for Vectorization
"""

import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from PIL import Image
from scipy import ndimage
from skimage import io, color, measure, segmentation
from skimage.feature import canny
from skimage.measure import approximate_polygon
from skimage.metrics import structural_similarity as ssim
from skimage.transform import resize

from app.infrastructure.monitoring.logger import get_logger

logger = get_logger(__name__)

# Constants
DEFAULT_SIGMA = 1.0
DEFAULT_LOW_THRESHOLD = 0.1
DEFAULT_HIGH_THRESHOLD = 0.3
DEFAULT_MIN_CHANGE = 0.01
DEFAULT_MIN_AREA = 500
DEFAULT_SIMPLIFY_TOLERANCE = 2.0
MIN_REGION_AREA = 100
MIN_CONTOUR_POINTS = 3
MIN_POINT_SEQUENCE = 2


@dataclass
class SegmentationResult:
    """Result from segmentation analysis."""
    edges: np.ndarray
    contours: List[np.ndarray]
    regions: int
    labels: np.ndarray
    
    @property
    def has_contours(self) -> bool:
        """Check if any contours were found."""
        return len(self.contours) > 0


@dataclass
class SSIMResult:
    """Result from SSIM comparison."""
    score: float
    diff_map: np.ndarray
    changed_regions: List[Tuple[int, int, int, int]]
    
    @property
    def is_identical(self) -> bool:
        """Check if images are nearly identical."""
        return self.score > 0.99
    
    @property
    def has_changes(self) -> bool:
        """Check if significant changes were detected."""
        return len(self.changed_regions) > 0


class SegmentationService:
    """
    Service for advanced image analysis using scikit-image.
    
    Capabilities:
    - Edge detection for contour extraction
    - SSIM for before/after comparison
    - Region labeling for UI element detection
    """
    
    @classmethod
    def load_image(
        cls, 
        path: str | Path, 
        grayscale: bool = True
    ) -> np.ndarray:
        """
        Load image from path.
        
        Args:
            path: Path to image file
            grayscale: Convert to grayscale
            
        Returns:
            Image as numpy array
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be loaded
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        
        try:
            img = io.imread(str(path))
            
            if img is None or img.size == 0:
                raise ValueError("Loaded image is empty")
            
            if grayscale and len(img.shape) == 3:
                img = color.rgb2gray(img)
            
            return img
            
        except Exception as e:
            logger.error("image_load_failed", path=str(path), error=str(e))
            raise ValueError(f"Failed to load image: {e}")
    
    @classmethod
    def detect_edges(
        cls, 
        image_path: str | Path, 
        sigma: float = DEFAULT_SIGMA,
        low_threshold: float = DEFAULT_LOW_THRESHOLD,
        high_threshold: float = DEFAULT_HIGH_THRESHOLD
    ) -> SegmentationResult:
        """
        Detect edges using Canny algorithm.
        
        Args:
            image_path: Path to image
            sigma: Gaussian blur sigma (higher = smoother, must be > 0)
            low_threshold: Lower bound for edge detection (0-1)
            high_threshold: Upper bound for edge detection (0-1)
            
        Returns:
            SegmentationResult with edges and contours
        """
        if sigma <= 0:
            raise ValueError(f"Sigma must be > 0, got {sigma}")
        
        if not 0 <= low_threshold <= 1 or not 0 <= high_threshold <= 1:
            raise ValueError("Thresholds must be between 0 and 1")
        
        if low_threshold >= high_threshold:
            raise ValueError("Low threshold must be < high threshold")
        
        img = cls.load_image(image_path, grayscale=True)
        
        # Apply Canny edge detection
        edges = canny(
            img, 
            sigma=sigma, 
            low_threshold=low_threshold, 
            high_threshold=high_threshold
        )
        
        # Find contours
        contours = measure.find_contours(edges, 0.5)
        
        # Label connected regions
        labels = measure.label(edges)
        regions = int(labels.max())
        
        logger.info(
            "edge_detection_complete", 
            contours_found=len(contours), 
            regions=regions
        )
        
        return SegmentationResult(
            edges=edges,
            contours=contours,
            regions=regions,
            labels=labels
        )
    
    @classmethod
    def compare_images(
        cls,
        before_path: str | Path,
        after_path: str | Path,
        min_change_threshold: float = DEFAULT_MIN_CHANGE
    ) -> SSIMResult:
        """
        Compare two images using Structural Similarity Index.
        
        Args:
            before_path: Path to "before" image
            after_path: Path to "after" image
            min_change_threshold: Minimum difference to consider as change (0-1)
            
        Returns:
            SSIMResult with similarity score and diff map
        """
        if not 0 <= min_change_threshold <= 1:
            raise ValueError(f"min_change_threshold must be 0-1, got {min_change_threshold}")
        
        img1 = cls.load_image(before_path, grayscale=True)
        img2 = cls.load_image(after_path, grayscale=True)
        
        # Resize if dimensions don't match
        if img1.shape != img2.shape:
            logger.info(
                "resizing_images_for_comparison",
                before_shape=img1.shape,
                after_shape=img2.shape
            )
            img2 = resize(img2, img1.shape, anti_aliasing=True)
        
        # Compute SSIM
        score, diff = ssim(img1, img2, full=True, data_range=1.0)
        
        # Find changed regions
        changed_regions = []
        binary_diff = (1 - diff) > min_change_threshold
        
        # Label connected changed regions
        labels = measure.label(binary_diff)
        
        for region in measure.regionprops(labels):
            if region.area > MIN_REGION_AREA:
                changed_regions.append(region.bbox)
        
        logger.info(
            "ssim_comparison_complete",
            score=round(score, 4),
            changed_regions=len(changed_regions)
        )
        
        return SSIMResult(
            score=score,
            diff_map=diff,
            changed_regions=changed_regions
        )
    
    @classmethod
    def contours_to_points(
        cls,
        contours: List[np.ndarray],
        simplify: bool = True,
        tolerance: float = DEFAULT_SIMPLIFY_TOLERANCE
    ) -> List[List[Tuple[int, int]]]:
        """
        Convert contours to list of point sequences for drawing.
        
        Args:
            contours: List of contour arrays from detect_edges
            simplify: Whether to reduce point count
            tolerance: Simplification tolerance (higher = fewer points)
            
        Returns:
            List of point sequences [(x, y), (x, y), ...]
        """
        if tolerance <= 0:
            raise ValueError(f"Tolerance must be > 0, got {tolerance}")
        
        result = []
        
        for contour in contours:
            if len(contour) < MIN_CONTOUR_POINTS:
                continue
            
            if simplify:
                simplified = approximate_polygon(contour, tolerance=tolerance)
            else:
                simplified = contour
            
            # Convert to (x, y) format (contours are (row, col))
            points = [(int(p[1]), int(p[0])) for p in simplified]
            
            if len(points) >= MIN_POINT_SEQUENCE:
                result.append(points)
        
        return result
    
    @classmethod
    def segment_ui_elements(
        cls,
        image_path: str | Path,
        min_area: int = DEFAULT_MIN_AREA
    ) -> List[Dict[str, Any]]:
        """
        Segment image into distinct UI-like regions.
        
        Args:
            image_path: Path to screenshot
            min_area: Minimum region area to consider (pixels)
            
        Returns:
            List of regions with bounding boxes and properties
        """
        if min_area <= 0:
            raise ValueError(f"min_area must be > 0, got {min_area}")
        
        img = cls.load_image(image_path, grayscale=True)
        
        # Edge detection + morphological closing
        edges = canny(img, sigma=2)
        
        # Fill holes to create solid regions
        closed = ndimage.binary_fill_holes(edges)
        
        # Label regions
        labels = measure.label(closed)
        
        regions = []
        for prop in measure.regionprops(labels):
            if prop.area < min_area:
                continue
            
            regions.append({
                "label": int(prop.label),
                "area": int(prop.area),
                "bbox": prop.bbox,
                "centroid": (int(prop.centroid[1]), int(prop.centroid[0])),
                "perimeter": float(prop.perimeter)
            })
        
        logger.info("ui_segmentation_complete", regions_found=len(regions))
        return regions


# Convenience functions for API endpoints
def detect_edges_from_path(
    path: str | Path,
    max_contours: int = 10
) -> Dict[str, Any]:
    """
    API-friendly wrapper for edge detection.
    
    Args:
        path: Path to image
        max_contours: Maximum contours to return in response
    """
    try:
        result = SegmentationService.detect_edges(path)
        points = SegmentationService.contours_to_points(result.contours)
        
        return {
            "success": True,
            "contours_count": len(result.contours),
            "regions_count": result.regions,
            "points": points[:max_contours]
        }
    except Exception as e:
        logger.error("detect_edges_api_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }


def compare_images_from_paths(
    before: str | Path, 
    after: str | Path,
    max_regions: int = 5
) -> Dict[str, Any]:
    """
    API-friendly wrapper for SSIM comparison.
    
    Args:
        before: Path to before image
        after: Path to after image
        max_regions: Maximum changed regions to return
    """
    try:
        result = SegmentationService.compare_images(before, after)
        
        return {
            "success": True,
            "similarity_score": round(result.score, 4),
            "is_identical": result.is_identical,
            "changed_regions": result.changed_regions[:max_regions]
        }
    except Exception as e:
        logger.error("compare_images_api_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }
