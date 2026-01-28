"""
ONI ArtMaster API v6.1 - Multi-Application Edition
Advanced GUI Automation for Creative Tasks.

Architecture: Modular Service-Based (Refactored Phase 2)
"""

import structlog
from fastapi import APIRouter, Depends
from app.services.oni.artmaster.types import ApplicationType
from app.services.oni.artmaster.models import (
    ApplicationInfoResponse, DrawRequest, WorkflowResponse, CalibrateRequest, BaseResponse
)
from app.services.oni.artmaster.services import (
    ApplicationService, DrawingService, VectorizationService, get_services, ServiceContainer
)
from app.services.oni.artmaster.utils import track_execution_time
from app.services.oni.artmaster.config import ArtMasterConfig

logger = structlog.get_logger(__name__)

# Router definition
router = APIRouter(
    prefix="/artmaster",
    tags=["artmaster"]
    # Rate limit dependency can be re-added here if moved to common middlewares
)

@router.get("/application/detect", response_model=ApplicationInfoResponse)
@track_execution_time
async def detect_application():
    """Detect which creative application is currently active."""
    try:
        app_info, _ = await ApplicationService.get_active_application(preferred=None)
        return ApplicationInfoResponse(
            success=True,
            application=app_info,
            message=f"Detected {app_info.app_type.value}"
        )
    except Exception as e:
        return ApplicationInfoResponse(
            success=False,
            message=f"Detection failed: {str(e)}"
        )

@router.get("/application/tools")
@track_execution_time
async def get_application_tools(app_type: ApplicationType = None):
    """Get available tool shortcuts."""
    try:
        if not app_type:
            _, strategy = await ApplicationService.get_active_application()
        else:
            # For tools info we might not need active app if we had a pure static method,
            # but current architecture requires instance. 
            # We revert to detecting active for safety or creating dummy info if we want purely static.
            # Simplified: Use active detection.
             _, strategy = await ApplicationService.get_active_application(preferred=app_type)
             
        return {
            "success": True, 
            "tools": strategy.get_tool_shortcuts()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/draw", response_model=WorkflowResponse)
@track_execution_time
async def draw_shapes(
    request: DrawRequest,
    services: ServiceContainer = Depends(get_services)
):
    """Execute drawing workflow."""
    try:
        # 1. Setup Application
        app_info, strategy = await ApplicationService.get_active_application(preferred=request.application)
        
        # 2. Vectorize
        contours = await VectorizationService.vectorize_image(
            request.image_path, 
            request.max_shapes,
            request.high_fidelity,
            request.line_art
        )
        
        if not contours:
            return WorkflowResponse(success=False, shapes_drawn=0, total_shapes=0)
            
        # 3. Compute Coords
        screen_points, shape_types = VectorizationService.compute_screen_coordinates(
            contours,
            center_x=request.center_x or app_info.canvas_center[0],
            center_y=request.center_y or app_info.canvas_center[1],
            scale=request.scale,
            image_shape=(1080, 1920) # Mock, should get from image
        )
        
        # 4. Prepare Canvas
        await strategy.ensure_focus()
        await strategy.prepare_canvas()
        
        if request.create_layer:
            await strategy.create_layer(request.layer_name)
            
        # 5. Draw
        mouse = services.get_mouse()
        drawing_service = DrawingService(mouse, strategy)
        
        count = await drawing_service.draw_shape_batch(screen_points, shape_types)
        
        return WorkflowResponse(
            success=True,
            application_used=app_info.app_type,
            shapes_drawn=count,
            total_shapes=len(contours)
        )
        
    except Exception as e:
        logger.error("draw_workflow_failed", error=str(e))
        return WorkflowResponse(success=False, shapes_drawn=0, total_shapes=0)

@router.post("/calibrate")
@track_execution_time
async def calibrate_canvas(request: CalibrateRequest):
    """Calibrate canvas coordinates."""
    # Simplified calibration logic
    return {"success": True, "message": "Calibration simulated"}

