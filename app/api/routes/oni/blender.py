
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.core.dependencies import container
from app.services.blender_service import BlenderService

router = APIRouter()

def get_blender_service() -> BlenderService:
    if not container.has("blender_service"):
        # Lazy initialization if not in container (or we can register it in main.py)
        service = BlenderService()
        container.register("blender_service", service)
    return container.get("blender_service")

@router.post("/render/donut")
async def render_donut():
    """Triggers the detailed Cyber Donut test render."""
    service = get_blender_service()
    result = await service.render_cyber_donut()
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
        
    return result

@router.post("/execute")
async def execute_generic_job(payload: Dict[str, Any]):
    """Executes a generic job payload defined in JSON."""
    service = get_blender_service()
    result = await service.run_script(payload)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
        
    return result
