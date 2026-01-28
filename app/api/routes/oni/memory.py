"""
ONI Memory Routes
Endpoints para gerenciamento de memória cognitiva.
"""

from typing import Optional

from fastapi import APIRouter, Query
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/heatmap")
async def get_failure_heatmap(
    app_name: Optional[str] = Query(None, description="Filter by app"),
    limit: int = Query(20, ge=1, le=100)
):
    """Get failure hotspot heatmap data."""
    from app.services.oni import CognitiveMemoryService
    
    hotspots = CognitiveMemoryService.get_failure_hotspots(app_name, limit)
    return {
        "success": True,
        "hotspots": hotspots,
        "count": len(hotspots)
    }


@router.post("/cleanup")
async def cleanup_memory(
    days: int = Query(30, ge=1, le=365)
):
    """Remove old action history."""
    from app.services.oni import CognitiveMemoryService
    
    deleted = CognitiveMemoryService.cleanup_old_data(days)
    return {
        "success": True,
        "deleted_rows": deleted,
        "retention_days": days
    }


@router.get("/status")
async def memory_status():
    """Get memory system status."""
    from app.services.oni import CognitiveMemoryService
    import sqlite3
    
    try:
        conn = sqlite3.connect(CognitiveMemoryService.DB_FILE)
        cursor = conn.execute("SELECT COUNT(*) FROM action_history")
        total = cursor.fetchone()[0]
        conn.close()
        
        return {
            "success": True,
            "total_actions": total,
            "db_file": CognitiveMemoryService.DB_FILE
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
