"""
Self-Healing API Routes
/api/healing/...
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.self_healing_executor import get_healing_engine

router = APIRouter(prefix="/api/healing", tags=["Self-Healing"])

class LearnFixRequest(BaseModel):
    error_pattern: str  # Regex pattern
    fix_type: str       # 'import', 'replace', 'wrap', 'suggestion'
    fix_data: Dict[str, Any]
    app_context: str = "universal"

@router.get("/stats")
async def get_stats():
    """Get self-healing statistics."""
    engine = get_healing_engine()
    return engine.get_stats()

@router.post("/learn")
async def learn_fix(req: LearnFixRequest):
    """
    Teach the system a new fix.
    
    Example payload:
    {
        "error_pattern": "cannot find 'foo'",
        "fix_type": "import",
        "fix_data": {"foo": "from bar import foo"},
        "app_context": "blender"
    }
    """
    engine = get_healing_engine()
    success = engine.learn_fix(
        req.error_pattern, 
        req.fix_type, 
        req.fix_data, 
        req.app_context
    )
    
    if success:
        return {"status": "learned", "pattern": req.error_pattern}
    else:
        raise HTTPException(500, "Failed to learn fix")

@router.get("/fixes")
async def list_fixes():
    """List all known fixes."""
    engine = get_healing_engine()
    return {
        "count": len(engine.fixes),
        "fixes": [
            {"pattern": p, "type": f.get("type"), "context": f.get("context")}
            for p, f in engine.fixes.items()
        ]
    }
