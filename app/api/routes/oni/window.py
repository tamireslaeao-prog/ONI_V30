"""
ONI Window Routes
Endpoints para gerenciamento de janelas.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import structlog
import mss

from .core import WindowManager
from app.core.dependencies import container
from app.infrastructure.actuation.window_manager import WindowInfo
from app.services.oni.guards import ActionGuardService

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["window"])


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class WindowDetailResponse(BaseModel):
    """Detailed info for a window."""
    hwnd: int
    title: str
    class_name: str
    process_id: int
    x: int
    y: int
    width: int
    height: int
    is_visible: bool
    is_minimized: bool
    is_maximized: bool
    is_active: bool


class ActiveWindowResponse(BaseModel):
    """Response for active window info."""
    success: bool
    title: str
    process_name: str
    process_id: int
    x: int
    y: int
    width: int
    height: int
    is_maximized: bool = False
    is_minimized: bool = False
    is_active: bool = True
    screen_coverage_percent: Optional[float] = None


class ScreenInfoResponse(BaseModel):
    """Response for screen info."""
    resolution: str
    active_window: Optional[str] = None
    screen_count: int = 1
    primary_screen_index: int = 1


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/active-window", response_model=ActiveWindowResponse)
async def get_active_window():
    """Get detailed information about the currently active window."""
    try:
        window_info = await WindowManager.get_active_window_info()
        
        if not window_info:
            return ActiveWindowResponse(
                success=False,
                title="ERROR: Could not get active window",
                process_name="unknown",
                process_id=0,
                x=0, y=0, width=0, height=0
            )
        
        if window_info:
            ActionGuardService.record_active_window_check()
            
        logger.info("active_window_retrieved", 
                   title=window_info['title'],
                   process=window_info['process_name'])
        
        return ActiveWindowResponse(
            success=True,
            title=window_info['title'],
            process_name=window_info['process_name'],
            process_id=window_info['process_id'],
            x=window_info['x'],
            y=window_info['y'],
            width=window_info['width'],
            height=window_info['height'],
            is_maximized=window_info.get('is_maximized', False),
            is_minimized=window_info.get('is_minimized', False),
            is_active=window_info.get('is_active', True),
            screen_coverage_percent=window_info.get('screen_coverage_percent')
        )
        
    except Exception as e:
        logger.error("active_window_failed", error=str(e), exc_info=True)
        return ActiveWindowResponse(
            success=False,
            title=f"ERROR: {str(e)}",
            process_name="unknown",
            process_id=0,
            x=0, y=0, width=0, height=0
        )


@router.get("/screen-info", response_model=ScreenInfoResponse)
async def get_screen_info():
    """Get current screen information including resolution and active window."""
    try:
        window_info = await WindowManager.get_active_window_info()
        active_window = window_info['title'] if window_info else None
        
        with mss.mss() as sct:
            monitor_count = len(sct.monitors) - 1
            primary = sct.monitors[1]
            resolution = f"{primary['width']}x{primary['height']}"
        
        return ScreenInfoResponse(
            resolution=resolution,
            active_window=active_window,
            screen_count=monitor_count,
            primary_screen_index=1
        )
        
    except Exception as e:
        logger.error("screen_info_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/list", response_model=List[WindowDetailResponse])
async def list_windows(visible_only: bool = True):
    """List all available windows using smart filtering."""
    try:
        wm = container.get("window_manager")
        if not wm:
            raise HTTPException(503, "WindowManager not available")
            
        windows = wm.get_all_windows(visible_only=visible_only)
        active_info = await WindowManager.get_active_window_info()
        active_hwnd = active_info.get('hwnd') if active_info else 0
        
        response = []
        for w in windows:
            # Skip empty titles if they somehow got through
            if not w.title:
                continue
                
            response.append(WindowDetailResponse(
                hwnd=w.hwnd,
                title=w.title,
                class_name=w.class_name,
                process_id=w.process_id,
                x=w.x,
                y=w.y,
                width=w.width,
                height=w.height,
                is_visible=w.is_visible,
                is_minimized=w.is_minimized,
                is_maximized=w.is_maximized,
                is_active=(w.hwnd == active_hwnd)
            ))
            
        return response
        
    except Exception as e:
        logger.error("list_windows_failed", error=str(e))
        raise HTTPException(500, str(e))


@router.get("/focus")
async def focus_window(
    hwnd: Optional[int] = Query(None, description="Window Handle ID"),
    title: Optional[str] = Query(None, description="Window Title (fuzzy match)")
):
    """Focus a window by HWND (preferred) or Title using Power Focus."""
    try:
        wm = container.get("window_manager")
        if not wm:
            raise HTTPException(503, "WindowManager not available")
            
        target = hwnd if hwnd else title
        if not target:
            raise HTTPException(400, "Must provide hwnd or title")
            
        success = wm.focus_window(target)
        
        if not success:
            return {"success": False, "message": "Failed to focus window"}
            
        # Verify focus
        final_active = await WindowManager.get_active_window_info()
        is_focused = False
        if final_active:
            if hwnd:
                is_focused = (final_active['hwnd'] == hwnd)
            else:
                # Fuzzy verify
                from rapidfuzz import fuzz
                is_focused = fuzz.partial_ratio(title.lower(), final_active['title'].lower()) > 80
        
        return {
            "success": success, 
            "message": "Window focused successfully" if is_focused else "Focus command sent but verification failed",
            "active_window": final_active['title'] if final_active else None
        }
        
    except Exception as e:
        logger.error("focus_window_failed", error=str(e))
        raise HTTPException(500, str(e))
