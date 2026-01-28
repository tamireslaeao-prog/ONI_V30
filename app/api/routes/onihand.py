from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.dependencies import container
from app.services.onihand_service import OnihandService

router = APIRouter()

class ActRequest(BaseModel):
    instruction: str
    parameters: Optional[Dict[str, Any]] = None

@router.post("/act")
async def onihand_act(request: ActRequest):
    """
    Execute a high-level action using Onihand-like visual grounding.
    
    Args:
        instruction: "Click the login button", "Select the red car"
    
    Returns:
        JSON with execution result and coordinates found.
    """
    # Get or Create Service
    service = None
    if container.has("onihand_service"):
        service = container.get("onihand_service")
    else:
        # Fallback: create ad-hoc
        service = OnihandService()
        await service.initialize()
        # Ideally register it, but for ad-hoc request:
        pass
        
    result = await service.act(request.instruction)
    
    if not result["success"]:
        return {
            "success": False,
            "error": result.get("error"),
            "instruction": request.instruction
        }
        
    return {
        "success": True,
        "data": result
    }
