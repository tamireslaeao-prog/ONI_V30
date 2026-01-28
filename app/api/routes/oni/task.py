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
    """Execute a task by decomposing and running each step."""
    from app.services.deep_reasoning import DeepReasoningService
    import pyautogui
    import asyncio
    
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
        
        # Execute each action in plan
        results = []
        actions = analysis.get("actions", [])
        
        for i, action in enumerate(actions):
            action_type = action.get("type", "")
            params = action.get("params", {})
            
            try:
                if action_type == "click":
                    pyautogui.click(params.get("x", 0), params.get("y", 0))
                elif action_type == "drag":
                    pyautogui.drag(
                        params.get("x1", 0), params.get("y1", 0),
                        params.get("x2", 0), params.get("y2", 0),
                        duration=0.5
                    )
                elif action_type == "hotkey":
                    keys = params.get("keys", [])
                    if keys:
                        pyautogui.hotkey(*keys)
                elif action_type == "type":
                    pyautogui.write(params.get("text", ""), interval=0.02)
                elif action_type == "wait":
                    await asyncio.sleep(params.get("seconds", 0.5))
                
                results.append({"step": i+1, "action": action_type, "success": True})
                await asyncio.sleep(0.2)  # Delay between actions
                
            except Exception as step_err:
                results.append({"step": i+1, "action": action_type, "success": False, "error": str(step_err)})
        
        return {
            "success": True,
            "task": description,
            "steps_executed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error("task_execute_failed", error=str(e))
        return {"success": False, "error": str(e)}
