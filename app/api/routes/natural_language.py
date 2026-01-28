"""
ONI v12.0 - Natural Language Instruction API
Enables external clients to trigger complex automation tasks via text.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import structlog

from app.core.dependencies import container

logger = structlog.get_logger()
router = APIRouter()

class InstructionRequest(BaseModel):
    instruction: str = Field(..., description="Natural language command", min_length=3)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context variables")
    sync: bool = Field(False, description="Wait for completion (timeout risk)")

class InstructionResponse(BaseModel):
    task_id: str
    status: str
    message: str

# In-memory task store (should be Redis/DB in prod)
_tasks: Dict[str, Dict[str, Any]] = {}

@router.post("/instruction", response_model=InstructionResponse)
async def execute_instruction(
    request: InstructionRequest, 
    background_tasks: BackgroundTasks
):
    """
    Submit a natural language instruction for execution.
    """
    task_id = str(uuid.uuid4())
    
    # Tier 3: Parse Intent (Mooshot)
    from app.core.intent_parser import IntentParser
    parser = IntentParser()
    intent = parser.parse(request.instruction)
    
    logger.info("instruction_received", 
                task_id=task_id, 
                instruction=request.instruction,
                parsed_intent=intent.action,
                confidence=intent.confidence)
                
    # Check agent availability
    if not container.has("agent"):
        raise HTTPException(status_code=503, detail="Agent system not available")
    
    agent = container.get("agent")
    
    # Register task
    _tasks[task_id] = {
        "id": task_id,
        "instruction": request.instruction,
        "status": "pending",
        "result": None
    }
    
    async def run_task(tid: str, instr: str):
        try:
            _tasks[tid]["status"] = "running"
            
            # Delegate to Agent
            # Using execute_goal as the entry point
            if hasattr(agent, "execute_goal"):
                result = await agent.execute_goal(instr)
                _tasks[tid]["status"] = "completed" if result.success else "failed"
                _tasks[tid]["result"] = result
            else:
                _tasks[tid]["status"] = "error"
                _tasks[tid]["error"] = "Agent missing execute_goal method"
                
        except Exception as e:
            logger.error("instruction_failed", task_id=tid, error=str(e))
            _tasks[tid]["status"] = "error"
            _tasks[tid]["error"] = str(e)

    if request.sync:
        await run_task(task_id, request.instruction)
        status = _tasks[task_id]["status"]
        return InstructionResponse(
            task_id=task_id,
            status=status,
            message=f"Execution finished with status: {status}"
        )
    else:
        background_tasks.add_task(run_task, task_id, request.instruction)
        return InstructionResponse(
            task_id=task_id,
            status="queued",
            message="Instruction accepted for background execution"
        )

@router.get("/instruction/{task_id}")
async def get_instruction_status(task_id: str):
    """Check status of an instruction."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _tasks[task_id]
    
    # Serialize result if present
    result_data = None
    if task.get("result"):
        # Assuming ActionResult or similar dataclass
        if hasattr(task["result"], "__dict__"):
            result_data = task["result"].__dict__
        else:
            result_data = str(task["result"])
            
    return {
        "id": task_id,
        "status": task["status"],
        "error": task.get("error"),
        "result": result_data
    }
