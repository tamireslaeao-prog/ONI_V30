"""
ONI Adapter Routes
Endpoints para sistema de adaptador universal.
"""

from fastapi import APIRouter, Query
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/adapter", tags=["adapter"])


@router.get("/resolve")
async def resolve_action(
    app: str = Query(..., description="Application name/process"),
    action: str = Query(..., description="Action name (e.g., 'new_file', 'save')")
):
    """Resolve an action to its keyboard shortcut for the given app."""
    from app.services.oni.universal_adapter import UniversalAdapterService
    
    try:
        result = await UniversalAdapterService.resolve_action(app, action)
        return result
    except Exception as e:
        logger.error("adapter_resolve_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/execute")
async def execute_action(
    app: str = Query(...),
    action: str = Query(...)
):
    """Resolve and execute an action for the given app."""
    from app.services.oni.universal_adapter import UniversalAdapterService
    
    try:
        result = await UniversalAdapterService.execute_action(app, action)
        return result
    except Exception as e:
        logger.error("adapter_execute_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.get("/apps")
async def list_known_apps():
    """List all apps with known shortcuts."""
    from app.services.oni.universal_adapter import UniversalAdapterService
    
    apps = UniversalAdapterService.list_apps()
    return {"success": True, "apps": apps}


@router.get("/actions")
async def list_app_actions(
    app: str = Query(...)
):
    """List all known actions for an app."""
    from app.services.oni.universal_adapter import UniversalAdapterService
    
    actions = UniversalAdapterService.list_actions(app)
    return {"success": True, "app": app, "actions": actions}


@router.post("/learn")
async def learn_shortcut(
    app: str = Query(...),
    action: str = Query(...),
    shortcut: str = Query(..., description="Shortcut keys (e.g., 'ctrl+n')")
):
    """Teach a new shortcut for an app."""
    from app.services.oni.universal_adapter import UniversalAdapterService
    
    success = UniversalAdapterService.learn_shortcut(app, action, shortcut)
    return {"success": success, "app": app, "action": action, "shortcut": shortcut}
