"""
ONI v10.0 - Segmentation API Routes
Endpoints for advanced image analysis using scikit-image.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Tuple
import structlog

from app.services.vision.segmentation_service import (
    SegmentationService,
    detect_edges_from_path,
    compare_images_from_paths
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/segmentation", tags=["Segmentation v10.0"])


# ==================== MODELS ====================

class EdgeDetectionRequest(BaseModel):
    """Request for edge detection."""
    image_path: str
    sigma: float = 1.0
    simplify: bool = True
    tolerance: float = 2.0


class SSIMCompareRequest(BaseModel):
    """Request for SSIM comparison."""
    before_path: str
    after_path: str
    min_change_threshold: float = 0.01


# ==================== ENDPOINTS ====================

@router.get("/edges")
async def detect_edges(
    image_path: str = Query(..., description="Path to image"),
    sigma: float = Query(1.0, description="Gaussian blur sigma"),
    simplify: bool = Query(True, description="Simplify contours"),
    tolerance: float = Query(2.0, description="Simplification tolerance")
):
    """
    Detect edges in an image using Canny algorithm.
    
    Returns contours as point sequences that can be used for:
    - Drawing in Photoshop via stroke_path
    - Vectorization workflows
    - UI element boundary detection
    """
    try:
        result = SegmentationService.detect_edges(image_path, sigma=sigma)
        points = SegmentationService.contours_to_points(
            result.contours, 
            simplify=simplify, 
            tolerance=tolerance
        )
        
        return {
            "success": True,
            "contours_count": len(result.contours),
            "regions_count": result.regions,
            "simplified_paths": len(points),
            "points": points[:20]  # Limit response size
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")
    except Exception as e:
        logger.error("edge_detection_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/edges")
async def detect_edges_post(request: EdgeDetectionRequest):
    """POST version of edge detection."""
    return await detect_edges(
        request.image_path, 
        request.sigma, 
        request.simplify, 
        request.tolerance
    )


@router.get("/compare")
async def compare_ssim(
    before_path: str = Query(..., description="Path to 'before' image"),
    after_path: str = Query(..., description="Path to 'after' image"),
    min_change: float = Query(0.01, description="Minimum change threshold")
):
    """
    Compare two images using Structural Similarity Index (SSIM).
    
    Returns:
    - similarity_score: 0-1 (1 = identical)
    - is_identical: True if score > 0.99
    - changed_regions: Bounding boxes of areas that changed
    
    Use cases:
    - Verify if an action changed the screen
    - Detect which regions were affected by drawing
    - Quality check for automation steps
    """
    try:
        result = SegmentationService.compare_images(
            before_path, after_path, min_change
        )
        
        return {
            "success": True,
            "similarity_score": round(result.score, 4),
            "is_identical": result.score > 0.99,
            "changed_significantly": result.score < 0.95,
            "changed_regions": [
                {"min_row": r[0], "min_col": r[1], "max_row": r[2], "max_col": r[3]}
                for r in result.changed_regions[:10]
            ],
            "regions_changed": len(result.changed_regions)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("ssim_comparison_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/compare")
async def compare_ssim_post(request: SSIMCompareRequest):
    """POST version of SSIM comparison."""
    return await compare_ssim(
        request.before_path,
        request.after_path,
        request.min_change_threshold
    )


@router.get("/ui-regions")
async def detect_ui_regions(
    image_path: str = Query(..., description="Path to screenshot"),
    min_area: int = Query(500, description="Minimum region area")
):
    """
    Segment screenshot into distinct UI-like regions.
    
    Returns list of regions with:
    - Bounding boxes
    - Centroids (click targets)
    - Area/perimeter metrics
    """
    try:
        regions = SegmentationService.segment_ui_elements(image_path, min_area)
        
        return {
            "success": True,
            "regions_count": len(regions),
            "regions": regions[:30]  # Limit response
        }
    except Exception as e:
        logger.error("ui_segmentation_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.get("/status")
async def segmentation_status():
    """Check if segmentation service is available."""
    try:
        import skimage
        return {
            "success": True,
            "scikit_image_version": skimage.__version__,
            "endpoints": [
                "/api/segmentation/edges",
                "/api/segmentation/compare",
                "/api/segmentation/ui-regions"
            ]
        }
    except ImportError:
        return {
            "success": False,
            "error": "scikit-image not installed"
        }
