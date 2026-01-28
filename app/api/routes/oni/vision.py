import structlog
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Import both services
from app.services.oni.hybrid_vision_service import HybridVisionService
from app.services.oni.desktop_hybrid_service import desktop_vision_v2, DesktopVisionResult

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["vision"])

# =============================================================================
# HYBRID VISION RESPONSES
# =============================================================================

class HybridWebResponse(BaseModel):
    url: str
    title: str
    viewport_size: Dict[str, int]
    element_count: int
    clickable_count: int
    editable_count: int
    scene_description: str
    elements: List[Dict[str, Any]]
    screenshot_base64: str

# Re-exporting this model for documentation clarity
# DesktopVisionResult is defined in desktop_hybrid_service, but we can't use it directly in response_model 
# without Pydantic conversion unless it's a Pydantic model. 
# It's a dataclass, so we define a Pydantic mirror for the API.

class DesktopElementModel(BaseModel):
    id: str
    name: str
    control_type: str
    rect: Dict[str, int]
    is_enabled: bool
    is_visible: bool
    is_keyboard_focusable: bool
    description: str

class HybridDesktopResponse(BaseModel):
    window_title: str
    process_name: str
    elements: List[DesktopElementModel]
    screenshot_path: Optional[str]
    annotated_path: Optional[str]
    canvas_limits: Optional[Dict[str, int]]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/hybrid-vision/web", response_model=HybridWebResponse)
async def hybrid_vision_web(
    url: Optional[str] = Query(None, description="URL to analyze (optional if browser already open)"),
    headless: bool = Query(True, description="Run browser in headless mode"),
    nocache: Optional[str] = Query(None, description="Cache buster")
):
    """
    WEB HYBRID VISION (Selenium).
    Combines Selenium DOM extraction + Accessibility Tree.
    Best for: Chrome, Firefox, Web scraping.
    """
    service = HybridVisionService(headless=headless)
    
    try:
        target_url = url if url else "https://www.google.com"
        logger.info("starting_web_hybrid_vision", url=target_url)
        result = service.analyze(target_url)
        
        return HybridWebResponse(
            url=result.url,
            title=result.title,
            viewport_size=result.viewport_size,
            element_count=len(result.elements),
            clickable_count=len(result.clickable_elements),
            editable_count=len(result.editable_elements),
            scene_description=result.scene_description,
            elements=[asdict(e) for e in result.elements],
            screenshot_base64=result.screenshot_base64
        )
        
    except Exception as e:
        logger.error("web_hybrid_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/hybrid-vision/desktop", response_model=HybridDesktopResponse)
async def hybrid_vision_desktop(
    nocache: Optional[str] = Query(None, description="Cache buster")
):
    """
    DESKTOP HYBRID VISION (PyWinAuto + UIA).
    Scans the ACTIVE WINDOW using Windows Accessibility API.
    Best for: Photoshop, Paint, Notepad, Native Apps.
    Generates: annotated_hybrid_TIMESTAMP.png
    """
    try:
        logger.info("starting_desktop_hybrid_vision")
        result = await desktop_vision_v2.scan_active_window()
        
        # Convert dataclass list to Pydantic list
        elements_pydantic = [
            DesktopElementModel(**asdict(e)) for e in result.elements
        ]
        
        return HybridDesktopResponse(
            window_title=result.window_title,
            process_name=result.process_name,
            elements=elements_pydantic,
            screenshot_path=result.screenshot_path,
            annotated_path=result.annotated_path,
            canvas_limits=result.canvas_limits
        )
        
    except Exception as e:
        logger.error("desktop_hybrid_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hybrid-vision/semantic-find")
async def semantic_find_element(
    query: str = Query(..., description="Natural language query (e.g., 'login button', 'close icon')"),
    nocache: Optional[str] = Query(None, description="Cache buster")
):
    """
    VISUAL CORTEX 3.0 - Semantic UI Element Finder.
    Find UI elements using natural language queries.
    
    Examples:
    - "red button"
    - "close icon"
    - "login"
    - "the primary action"
    - "save button"
    
    Returns coordinates for clicking.
    """
    try:
        logger.info("semantic_find_starting", query=query)
        result = await desktop_vision_v2.semantic_find(query)
        return result
        
    except Exception as e:
        logger.error("semantic_find_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/configure")
async def configure_vision(
    fps: float = Query(..., description="Target FPS for Shared Vision (1-60)")
):
    """
    CONFIGURE VISION BURST MODE.
    Sets the capture rate of the background Vision Service.
    - 1.0 = Idle Mode (Save CPU)
    - 30.0 = Normal Mode
    - 60.0 = Burst Mode (High Velocity)
    """
    from app.services.vision_shared import get_shared_vision
    try:
        service = get_shared_vision()
        service.set_capture_fps(fps)
        return {"status": "ok", "fps": fps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
