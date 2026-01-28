"""
ONI v2.0 - Agent Control Endpoints
"""
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import structlog

router = APIRouter()
logger = structlog.get_logger()


# =============================================================================
# Request/Response Models
# =============================================================================

class AgentMode(str, Enum):
    """Agent operation modes."""
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    MANUAL = "manual"


class AgentStatus(str, Enum):
    """Agent status."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    ERROR = "error"


class SetGoalRequest(BaseModel):
    """Request to set agent goal."""
    goal: str = Field(..., min_length=1, max_length=2000)
    mode: AgentMode = AgentMode.SUPERVISED
    constraints: list[str] = Field(default_factory=list)


class SetGoalResponse(BaseModel):
    """Response after setting goal."""
    success: bool
    goal: str
    plan_steps: int


class AgentStateResponse(BaseModel):
    """Current agent state."""
    status: AgentStatus
    goal: str | None
    current_step: int
    total_steps: int
    mode: AgentMode
    actions_executed: int
    last_action: str | None
    uptime_seconds: float


class ActionResponse(BaseModel):
    """Response for action execution."""
    success: bool
    action_type: str
    duration_ms: float
    details: dict[str, Any]


# =============================================================================
# In-memory state (will be replaced with proper state management)
# =============================================================================

_agent_state = {
    "status": AgentStatus.IDLE,
    "goal": None,
    "current_step": 0,
    "total_steps": 0,
    "mode": AgentMode.SUPERVISED,
    "actions_executed": 0,
    "last_action": None,
    "start_time": datetime.now(),
}


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/goal", response_model=SetGoalResponse)
async def set_goal(request: SetGoalRequest) -> SetGoalResponse:
    """
    Set a new goal for the agent.
    
    The agent will plan and execute actions to achieve this goal.
    """
    logger.info("setting_goal", goal=request.goal, mode=request.mode.value)
    
    # Update state
    _agent_state["goal"] = request.goal
    _agent_state["mode"] = request.mode
    _agent_state["status"] = AgentStatus.PLANNING
    _agent_state["total_steps"] = 5  # Placeholder
    _agent_state["current_step"] = 0
    
    return SetGoalResponse(
        success=True,
        goal=request.goal,
        plan_steps=5
    )


@router.get("/state", response_model=AgentStateResponse)
async def get_agent_state() -> AgentStateResponse:
    """Get current agent state."""
    uptime = (datetime.now() - _agent_state["start_time"]).total_seconds()
    
    return AgentStateResponse(
        status=_agent_state["status"],
        goal=_agent_state["goal"],
        current_step=_agent_state["current_step"],
        total_steps=_agent_state["total_steps"],
        mode=_agent_state["mode"],
        actions_executed=_agent_state["actions_executed"],
        last_action=_agent_state["last_action"],
        uptime_seconds=uptime
    )


@router.post("/start")
async def start_agent() -> dict[str, Any]:
    """Start agent execution."""
    if _agent_state["goal"] is None:
        raise HTTPException(status_code=400, detail="No goal set")
    
    _agent_state["status"] = AgentStatus.EXECUTING
    logger.info("agent_started")
    
    # Check if we have the real agent and trigger it
    from app.core.dependencies import container
    import asyncio
    
    if container.has("agent"):
        agent = container.get("agent")
        goal = _agent_state["goal"]
        
        # Define background task wrapper
        async def run_agent_task():
            try:
                # Update status
                _agent_state["status"] = AgentStatus.EXECUTING
                logger.info("agent_task_running", goal=goal)
                
                if hasattr(agent, "execute_goal"):
                    result = await agent.execute_goal(goal)
                    
                    # Update status based on result
                    _agent_state["status"] = AgentStatus.IDLE
                    _agent_state["last_action"] = "completed" if result.success else "failed"
                    logger.info("agent_task_completed", success=result.success)
                else:
                    logger.warning("agent_missing_execute_goal")
            except Exception as e:
                logger.error("agent_task_failed", error=str(e))
                _agent_state["status"] = AgentStatus.ERROR
        
        # Fire and forget background task
        asyncio.create_task(run_agent_task())
    
    return {"success": True, "message": "Agent started"}


@router.post("/pause")
async def pause_agent() -> dict[str, Any]:
    """Pause agent execution."""
    _agent_state["status"] = AgentStatus.PAUSED
    logger.info("agent_paused")
    
    return {"success": True, "message": "Agent paused"}


@router.post("/resume")
async def resume_agent() -> dict[str, Any]:
    """Resume agent execution."""
    if _agent_state["status"] != AgentStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Agent not paused")
    
    _agent_state["status"] = AgentStatus.EXECUTING
    logger.info("agent_resumed")
    
    return {"success": True, "message": "Agent resumed"}


@router.post("/stop")
async def stop_agent() -> dict[str, Any]:
    """Stop agent execution and clear goal."""
    _agent_state["status"] = AgentStatus.IDLE
    _agent_state["goal"] = None
    _agent_state["current_step"] = 0
    _agent_state["total_steps"] = 0
    logger.info("agent_stopped")
    
    return {"success": True, "message": "Agent stopped"}


@router.post("/emergency-stop")
async def emergency_stop() -> dict[str, Any]:
    """
    Emergency stop - immediately halt all actions.
    
    This will:
    1. Stop all pending actions
    2. Release mouse/keyboard control
    3. Clear action queue
    """
    from app.core.dependencies import container
    
    logger.warning("emergency_stop_triggered")
    
    # Call emergency stop on actual agent if available
    if container.has("agent"):
        agent = container.get("agent")
        if hasattr(agent, 'emergency_stop'):
            await agent.emergency_stop()
    
    _agent_state["status"] = AgentStatus.IDLE
    _agent_state["goal"] = None
    _agent_state["current_step"] = 0
    _agent_state["total_steps"] = 0
    
    return {"success": True, "message": "Emergency stop executed"}


# =============================================================================
# v3.0 HybridAgent Endpoints
# =============================================================================

@router.get("/stats")
async def get_agent_stats() -> dict[str, Any]:
    """
    Get detailed agent statistics (v3.0).
    
    Returns:
        Comprehensive stats including grounding, reflection, and execution metrics.
    """
    from app.core.dependencies import container
    
    if not container.has("agent"):
        return {"error": "Agent not available"}
    
    agent = container.get("agent")
    
    if hasattr(agent, 'get_stats'):
        return agent.get_stats()
    else:
        # Legacy agent fallback
        return {
            "status": _agent_state["status"].value,
            "actions_executed": _agent_state["actions_executed"],
        }


@router.get("/grounding-stats")
async def get_grounding_stats() -> dict[str, Any]:
    """
    Get grounding system statistics (v3.0).
    
    Shows UI-TARS vs OCR usage breakdown.
    """
    from app.core.dependencies import container
    
    if not container.has("grounding"):
        return {"error": "Grounding not available", "ui_tars": False, "ocr": True}
    
    grounding = container.get("grounding")
    stats = grounding.get_stats() if hasattr(grounding, 'get_stats') else {}
    
    return {
        "ui_tars_available": grounding.ui_tars_available if hasattr(grounding, 'ui_tars_available') else False,
        **stats
    }


class ExecuteCodeRequest(BaseModel):
    """Request to execute code task."""
    task: str = Field(..., min_length=1, max_length=5000)
    timeout: float = Field(default=60.0, ge=1.0, le=300.0)


@router.post("/execute-code")
async def execute_code_task(request: ExecuteCodeRequest) -> dict[str, Any]:
    """
    Execute a task using Code Agent (v3.0).
    
    The Code Agent can run Python/Bash to accomplish data manipulation tasks.
    
    WARNING: This executes code on your machine. Use with caution.
    """
    from app.core.dependencies import container
    
    if not container.has("agent"):
        raise HTTPException(status_code=400, detail="Agent not available")
    
    agent = container.get("agent")
    
    if not hasattr(agent, 'execute_code_task'):
        raise HTTPException(status_code=400, detail="Code Agent not available (legacy agent)")
    
    logger.info("code_task_requested", task=request.task[:100])
    
    try:
        result = await agent.execute_code_task(request.task)
        
        return {
            "success": result.completion_reason == "DONE",
            "completion_reason": result.completion_reason,
            "steps_executed": result.steps_executed,
            "summary": result.summary,
            "history": result.execution_history[-5:] if result.execution_history else [],
        }
    except Exception as e:
        logger.error("code_task_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version")
async def get_version() -> dict[str, Any]:
    """Get agent version info."""
    from app.core.config import settings
    from app.core.dependencies import container
    
    agent_type = "unknown"
    if container.has("agent"):
        agent = container.get("agent")
        if hasattr(agent, 'execute_goal'):
            agent_type = "HybridAgent v3.0"
        else:
            agent_type = "CognitiveAgent v2.0"
    
    return {
        "version": settings.app_version,
        "agent_type": agent_type,
        "features": {
            "ui_tars": container.has("grounding") and getattr(container.get("grounding"), 'ui_tars_available', False),
            "reflection": settings.agent.enable_reflection,
            "code_agent": settings.agent.enable_code_agent,
        }
    }
