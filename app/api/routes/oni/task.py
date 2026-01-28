"""
ONI Task Routes
Endpoints para análise e decomposição de tarefas.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
import structlog

from .core import get_vision_service, WindowManager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/task", tags=["task"])


@router.post("/analyze")
async def analyze_task(
    description: str = Query(..., description="Task description"),
    vision=Depends(get_vision_service)
):
    """Analyze a task and decompose into subtasks."""
    from app.services.deep_reasoning import DeepReasoningService
    
    try:
        # Get current context
        window_info = await WindowManager.get_active_window_info()
        app_name = window_info.get('process_name', 'unknown') if window_info else 'unknown'
        
        # Analyze task
        analysis = DeepReasoningService.analyze_task(description, app_name)
        
        return {
            "success": True,
            "task": description,
            "app_context": app_name,
            "analysis": analysis
        }
    except Exception as e:
        logger.error("task_analyze_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/execute")
async def execute_task(
    description: str = Query(...),
    dry_run: bool = Query(False, description="If true, only plan without executing"),
    vision=Depends(get_vision_service)
):
    """Execute a task by decomposing and running each step using OnihandService."""
    from app.services.deep_reasoning import DeepReasoningService
    from app.services.onihand_service import OnihandService
    
    try:
        # Get context
        window_info = await WindowManager.get_active_window_info()
        app_name = window_info.get('process_name', 'unknown') if window_info else 'unknown'
        
        # Get plan
        analysis = DeepReasoningService.analyze_task(description, app_name)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "plan": analysis
            }
        
        # Execute using Onihand (Visual Grounding)
        onihand = OnihandService()
        results = []
        
        # We pass the high-level intent to Onihand, 
        # as it is better equipped to handle the micro-steps visually
        # than iterating blindly here.
        # However, if analysis returned discrete steps, we can iterate them.
        
        actions = analysis.get("actions", [])
        if actions:
            for i, action in enumerate(actions):
                # Convert structured action to natural language instruction for Onihand
                # e.g. type="click", params={"target": "File Menu"} -> "Click on File Menu"
                
                instruction = ""
                a_type = action.get("type", "")
                params = action.get("params", {})
                
                if a_type == "click":
                    target = params.get("element") or params.get("target") or "target"
                    instruction = f"Click on {target}"
                elif a_type == "type":
                    text = params.get("text", "")
                    instruction = f"Type '{text}'"
                elif a_type == "hotkey":
                    keys = params.get("keys", [])
                    instruction = f"Press keys {'+'.join(keys)}"
                else:
                    instruction = description # Fallback to full description
                
                logger.info("task_step_executing", step=i+1, instruction=instruction)
                
                # Execute via Onihand with Visual Grounding
                step_result = await onihand.act(instruction, app_name)
                results.append({"step": i+1, "instruction": instruction, "result": step_result})
                
        else:
            # If no discrete actions, just pass the full description
            step_result = await onihand.act(description, app_name)
            results.append({"step": 1, "instruction": description, "result": step_result})

        return {
            "success": True,
            "task": description,
            "steps_executed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error("task_execute_failed", error=str(e))
        return {"success": False, "error": str(e)}
