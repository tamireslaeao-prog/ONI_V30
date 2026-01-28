"""
ONI Recovery Routes
Endpoints para sistema de recuperação de erros.
"""

import time
import hashlib

from fastapi import APIRouter, HTTPException, Query, Depends
import structlog

from .core import get_vision_service, WindowManager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.get("/check")
async def check_and_recover(
    vision=Depends(get_vision_service)
):
    """Check for anomalies and attempt recovery if needed."""
    from app.services.oni.error_recovery import ErrorRecoveryService
    
    try:
        # Get current state
        window_info = await WindowManager.get_active_window_info()
        window_title = window_info.get("title", "") if window_info else ""
        
        # Check for anomalies
        anomaly = await ErrorRecoveryService.detect_anomaly(window_title)
        
        if anomaly:
            # Attempt recovery
            recovery = await ErrorRecoveryService.attempt_recovery(anomaly)
            return {
                "anomaly_detected": True,
                "anomaly": anomaly.to_dict() if hasattr(anomaly, 'to_dict') else str(anomaly),
                "recovery_attempted": True,
                "recovery_result": recovery
            }
        
        return {
            "anomaly_detected": False,
            "status": "healthy"
        }
    except Exception as e:
        logger.error("recovery_check_failed", error=str(e))
        return {"success": False, "error": str(e)}


@router.post("/checkpoint")
async def create_checkpoint(
    action: str = Query(...)
):
    """Create a checkpoint before executing an action."""
    from app.services.oni.error_recovery import ErrorRecoveryService
    
    window_info = await WindowManager.get_active_window_info()
    window_title = window_info.get("title", "") if window_info else ""
    screen_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    checkpoint = ErrorRecoveryService.create_checkpoint(action, screen_hash, window_title)
    return {"checkpoint_id": checkpoint.id, "action": action}


@router.get("/status")
async def recovery_status():
    """Get recovery system status."""
    from app.services.oni.error_recovery import ErrorRecoveryService
    
    return {
        "success": True,
        "checkpoints_count": len(ErrorRecoveryService._checkpoints) if hasattr(ErrorRecoveryService, '_checkpoints') else 0,
        "status": "active"
    }
