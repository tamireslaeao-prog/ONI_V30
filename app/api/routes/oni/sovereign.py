"""
ONI v5.0 - Sovereign API Routes
Exposes the Adaptive Sovereign Agent via REST API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

from app.agent.adaptive_sovereign import AdaptiveSovereign, create_sovereign, SovereignResult

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/sovereign", tags=["sovereign"])


class SovereignRequest(BaseModel):
    """Request body for Sovereign execution."""
    goal: str
    with_llm: bool = True
    with_executor: bool = True


class SovereignResponse(BaseModel):
    """Response from Sovereign execution."""
    success: bool
    goal: str
    steps_completed: int
    total_steps: int
    errors: list[str]
    tools_forged: list[str]
    duration_seconds: float
    final_message: str


@router.post("/execute", response_model=SovereignResponse)
async def execute_sovereign(request: SovereignRequest):
    """
    Execute a goal using the Adaptive Sovereign Agent.
    
    The Sovereign combines:
    - UBIE: Planning and validation
    - ONI: Visual execution
    - ANT: Tool creation on failure
    
    Args:
        request: Goal and configuration
        
    Returns:
        Execution result with status and details
    """
    logger.info("sovereign_api_called", goal=request.goal)
    
    try:
        # Create configured sovereign
        sovereign = create_sovereign(
            with_llm=request.with_llm,
            with_executor=request.with_executor
        )
        
        # Run the goal
        result: SovereignResult = await sovereign.run(request.goal)
        
        return SovereignResponse(
            success=result.success,
            goal=result.goal,
            steps_completed=result.steps_completed,
            total_steps=result.total_steps,
            errors=result.errors,
            tools_forged=result.tools_forged,
            duration_seconds=result.duration_seconds,
            final_message=result.final_message
        )
        
    except Exception as e:
        logger.exception("sovereign_api_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def sovereign_status():
    """Get status of the Sovereign system."""
    return {
        "status": "ready",
        "version": "5.0",
        "modes": ["planning", "executing", "forging", "reflecting"],
        "description": "The Adaptive Sovereign Agent - UBIE + ONI + ANT fusion"
    }
