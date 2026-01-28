from fastapi import APIRouter, HTTPException, Query, Body
import structlog
from typing import Dict, Any, Optional
from app.services.molt_service import molt_service

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/molt", tags=["molt"])

@router.get("/status")
async def get_status():
    """Check if Moltbot service is accessible."""
    is_alive = await molt_service.check_health()
    return {"status": "online" if is_alive else "offline"}

@router.post("/navigate")
async def navigate(url: str = Query(...), profile: Optional[str] = None):
    """Navigate to a URL using Moltbot."""
    result = await molt_service.navigate(url, profile)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Navigation failed"))
    return result

@router.get("/snapshot")
async def snapshot(mode: str = "aria", profile: Optional[str] = None):
    """Get page snapshot for AI analysis."""
    result = await molt_service.get_snapshot(mode, profile)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Snapshot failed"))
    return result

@router.post("/action")
async def perform_action(
    kind: str = Body(...), 
    params: Dict[str, Any] = Body(...),
    profile: Optional[str] = None
):
    """Perform a browser action (click, type, etc.)."""
    result = await molt_service.act(kind, params, profile)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", "Action failed"))
    return result

@router.post("/skill/{skill_name}")
async def invoke_skill(
    skill_name: str,
    action: str = Body(...),
    params: Dict[str, Any] = Body(...)
):
    """Invoke a Moltbot Skill (e.g., spotify, notion, github)."""
    result = await molt_service.run_skill(skill_name, action, params)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", f"Skill {skill_name} failed"))
    return result

@router.post("/extension/{extension_name}")
async def invoke_extension(
    extension_name: str,
    command: str = Body(...),
    data: Dict[str, Any] = Body(...)
):
    """Invoke a Moltbot Extension (e.g., whatsapp, slack, telegram)."""
    result = await molt_service.run_extension(extension_name, command, data)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=result.get("error", f"Extension {extension_name} failed"))
    return result
