"""
ONI Errors Routes
Endpoints para sistema de aprendizado de erros.
"""

from fastapi import APIRouter, Query
import structlog

from app.services.oni.error_learning import ErrorLearningService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/errors", tags=["errors"])


@router.get("/check")
async def check_known_errors(
    action: str = Query(..., description="Action description to check")
):
    """
    Check if action has known errors. Call BEFORE executing action.
    """
    result = ErrorLearningService.check_action(action)
    return result


@router.get("/list")
async def list_known_errors():
    """List all known errors in the system."""
    return {"errors": ErrorLearningService.list_errors()}


@router.post("/register")
async def register_new_error(
    category: str = Query(...),
    name: str = Query(...),
    pattern: str = Query(...),
    symptom: str = Query(...),
    cause: str = Query(...),
    solution: str = Query(...),
    context: str = Query("")
):
    """Register a new error in the system."""
    error_id = ErrorLearningService.register_error(
        category, name, pattern, symptom, cause, solution, context
    )
    return {"success": True, "error_id": error_id}


@router.get("/solution")
async def get_error_solution(
    error_id: str = Query(...)
):
    """Get solution for a specific error."""
    solution = ErrorLearningService.get_solution(error_id)
    if solution:
        return {"success": True, "error_id": error_id, "solution": solution}
    return {"success": False, "error": "Error ID not found"}
