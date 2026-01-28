"""
ONI Canvas Routes
Endpoints para gerenciamento de limites do canvas.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
import structlog

from .core import get_vision_service, WindowManager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/canvas", tags=["canvas"])


@router.get("/detect")
async def detect_canvas(
    vision=Depends(get_vision_service)
):
    """Auto-detect canvas bounds from active window."""
    from app.services.canvas_bounds import CanvasBoundsService
    
    try:
        window_info = await WindowManager.get_active_window_info()
        if not window_info:
            raise HTTPException(400, "No active window")
        
        bounds = await CanvasBoundsService.detect_canvas(
            process_name=window_info.get('process_name', ''),
            window_x=window_info.get('x', 0),
            window_y=window_info.get('y', 0),
            window_width=window_info.get('width', 1920),
            window_height=window_info.get('height', 1080)
        )
        
        if bounds:
            return {
                "success": True,
                "bounds": bounds.to_dict()
            }
        return {"success": False, "error": "Could not detect canvas"}
    except Exception as e:
        logger.error("canvas_detect_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/set")
async def set_canvas(
    x: int = Query(...),
    y: int = Query(...),
    width: int = Query(...),
    height: int = Query(...)
):
    """Manually set canvas bounds."""
    from app.services.canvas_bounds import CanvasBoundsService, CanvasBounds
    
    bounds = CanvasBounds(
        x=x, y=y, width=width, height=height,
        app_name="manual", confidence=1.0
    )
    CanvasBoundsService.set_bounds(bounds)
    
    return {
        "success": True,
        "bounds": {"x": x, "y": y, "width": width, "height": height}
    }


@router.get("/center")
async def get_canvas_center():
    """Get center point of current canvas."""
    from app.services.canvas_bounds import CanvasBoundsService
    
    # Check all cached bounds
    all_cached = CanvasBoundsService.get_all_cached()
    if all_cached:
        # Return first available canvas center
        for app_name, bounds in all_cached.items():
            return {
                "success": True, 
                "app": app_name,
                "center_x": bounds["center_x"], 
                "center_y": bounds["center_y"],
                "bounds": bounds
            }
    
    # No canvas set - return informative message instead of error
    return {
        "success": False, 
        "error": "No canvas bounds set. Use /api/canvas/detect or /api/hybrid-vision/desktop first.",
        "hint": "Open a graphic app (Photoshop, Paint) and call /api/canvas/detect"
    }
