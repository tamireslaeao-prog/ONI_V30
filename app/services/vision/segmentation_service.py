"""
ONI v10.0 - Segmentation Service
Advanced image analysis using scikit-image for:
- Edge Detection (Canny)
- Structural Similarity (SSIM)
- Region Labeling (Connected Components)
- Contour Extraction for Vectorization
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from PIL import Image

from skimage import io, color, measure, segmentation
from skimage.feature import canny
from skimage.metrics import structural_similarity as ssim
from skimage.transform import resize


from app.infrastructure.monitoring.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SegmentationResult:
    """Result from segmentation analysis."""
    edges: np.ndarray  # Binary edge map
    contours: List[np.ndarray]  # List of contour coordinates
    regions: int  # Number of distinct regions
    labels: np.ndarray  # Labeled image
    

@dataclass
class SSIMResult:
    """Result from SSIM comparison."""
    score: float  # 0-1, 1 = identical
    diff_map: np.ndarray  # Difference visualization
    changed_regions: List[Tuple[int, int, int, int]]  # Bounding boxes of changes


class SegmentationService:
    """
    Service for advanced image analysis using scikit-image.
    
    Capabilities:
    - Edge detection for contour extraction
    - SSIM for before/after comparison
    - Region labeling for UI element detection
    """
    
    @classmethod
    def load_image(cls, path: str, grayscale: bool = True) -> np.ndarray:
        """Load image from path."""
        try:
            img = io.imread(path)
            if grayscale and len(img.shape) == 3:
                img = color.rgb2gray(img)
            return img
        except Exception as e:
            logger.error("image_load_failed", path=path, error=str(e))
            raise
    
    @classmethod
    def detect_edges(
        cls, 
        image_path: str, 
        sigma: float = 1.0,
        low_threshold: float = 0.1,
        high_threshold: float = 0.3
    ) -> SegmentationResult:
        """
        Detect edges using Canny algorithm.
        
        Args:
            image_path: Path to image
            sigma: Gaussian blur sigma (higher = smoother)
            low_threshold: Lower bound for edge detection
            high_threshold: Upper bound for edge detection
            
        Returns:
            SegmentationResult with edges and contours
        """
        img = cls.load_image(image_path, grayscale=True)
        
        # Apply Canny edge detection
        edges = canny(img, sigma=sigma, 
                     low_threshold=low_threshold, 
                     high_threshold=high_threshold)
        
        # Find contours
        contours = measure.find_contours(edges, 0.5)
        
        # Label connected regions
        labels = measure.label(edges)
        regions = int(labels.max())  # Convert numpy.int32 to int

        
        logger.info("edge_detection_complete", 
                   contours_found=len(contours), 
                   regions=regions)
        
        return SegmentationResult(
            edges=edges,
            contours=contours,
            regions=regions,
            labels=labels
        )
    
    @classmethod
    def compare_images(
        cls,
        before_path: str,
        after_path: str,
        min_change_threshold: float = 0.01
    ) -> SSIMResult:
        """
        Compare two images using Structural Similarity Index.
        
        Args:
            before_path: Path to "before" image
            after_path: Path to "after" image
            min_change_threshold: Minimum difference to consider as change
            
        Returns:
            SSIMResult with similarity score and diff map
        """
        img1 = cls.load_image(before_path, grayscale=True)
        img2 = cls.load_image(after_path, grayscale=True)
        
        # Resize if dimensions don't match
        if img1.shape != img2.shape:
            img2 = resize(img2, img1.shape, anti_aliasing=True)
        
        # Compute SSIM
        score, diff = ssim(img1, img2, full=True, data_range=1.0)
        
        # Find changed regions
        changed_regions = []
        binary_diff = (1 - diff) > min_change_threshold
        
        # Label connected changed regions
        labels = measure.label(binary_diff)
        for region in measure.regionprops(labels):
            if region.area > 100:  # Ignore tiny noise
                bbox = region.bbox  # (min_row, min_col, max_row, max_col)
                changed_regions.append(bbox)
        
        logger.info("ssim_comparison_complete",
                   score=round(score, 4),
                   changed_regions=len(changed_regions))
        
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
        tolerance: float = 2.0
    ) -> List[List[Tuple[int, int]]]:
        """
        Convert contours to list of point sequences for drawing.
        
        Args:
            contours: List of contour arrays from detect_edges
            simplify: Whether to reduce point count
            tolerance: Simplification tolerance (higher = fewer points)
            
        Returns:
            List of point sequences [[x,y], [x,y], ...]
        """
        from skimage.measure import approximate_polygon
        
        result = []
        for contour in contours:
            if len(contour) < 3:
                continue
                
            if simplify:
                # Reduce points using Douglas-Peucker
                simplified = approximate_polygon(contour, tolerance=tolerance)
            else:
                simplified = contour
            
            # Convert to [x, y] format (contours are [row, col])
            points = [[int(p[1]), int(p[0])] for p in simplified]
            
            if len(points) >= 2:
                result.append(points)
        
        return result
    
    @classmethod
    def segment_ui_elements(
        cls,
        image_path: str,
        min_area: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Segment image into distinct UI-like regions.
        
        Args:
            image_path: Path to screenshot
            min_area: Minimum region area to consider
            
        Returns:
            List of regions with bounding boxes and properties
        """
        img = cls.load_image(image_path, grayscale=True)
        
        # Edge detection + morphological closing
        edges = canny(img, sigma=2)
        
        # Fill holes to create solid regions
        from scipy import ndimage
        closed = ndimage.binary_fill_holes(edges)
        
        # Label regions
        labels = measure.label(closed)
        
        regions = []
        for prop in measure.regionprops(labels):
            if prop.area < min_area:
                continue
            
            regions.append({
                "label": prop.label,
                "area": prop.area,
                "bbox": prop.bbox,  # (min_row, min_col, max_row, max_col)
                "centroid": (int(prop.centroid[1]), int(prop.centroid[0])),
                "perimeter": prop.perimeter
            })
        
        logger.info("ui_segmentation_complete", regions_found=len(regions))
        return regions


# Convenience functions for API endpoints
def detect_edges_from_path(path: str) -> Dict[str, Any]:
    """API-friendly wrapper for edge detection."""
    result = SegmentationService.detect_edges(path)
    points = SegmentationService.contours_to_points(result.contours)
    return {
        "success": True,
        "contours_count": len(result.contours),
        "regions_count": result.regions,
        "points": points[:10]  # Limit for API response size
    }


def compare_images_from_paths(before: str, after: str) -> Dict[str, Any]:
    """API-friendly wrapper for SSIM comparison."""
    result = SegmentationService.compare_images(before, after)
    return {
        "success": True,
        "similarity_score": round(result.score, 4),
        "is_identical": result.score > 0.99,
        "changed_regions": result.changed_regions[:5]  # Limit
    }
