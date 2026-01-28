
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import ONIError
from app.core.process_sentinel import sentinel

logger = structlog.get_logger(__name__)

def safe_log_critical(event: str, **kwargs):
    """
    Safely logs critical events, suppressing OSError (Broken Pipe) 
    which causes Zombie process state on Windows.
    """
    try:
        logger.critical(event, **kwargs)
    except OSError:
        # Failsafe: Console is dead (WinError 233). 
        # We swallow the error to let the API return the 500 response.
        pass

async def oni_error_handler(request: Request, exc: ONIError):
    """
    Global handler for ONI-specific errors.
    If the error is marked as critical, triggers the Panic System (Sentinel Purge).
    """
    error_data = {
        "status_code": 500,
        "error_type": exc.__class__.__name__,
        "message": exc.message,
        "details": exc.details,
        "is_critical": exc.is_critical
    }

    # Panic Logic
    if exc.is_critical:
        safe_log_critical("ONI_PANIC_SYSTEM_TRIGGERED", 
                        reason=exc.message, 
                        error_type=exc.__class__.__name__)
        
        # 1. Emergency Purge of automation artifacts/processes
        try:
            sentinel.emergency_purge_automation()
        except Exception as e:
            try:
                logger.error("sentinel_panic_purge_failed", error=str(e))
            except OSError:
                pass
            
        # 2. Log state dump (Mock: in a real system, we'd capture screenshots/process lists)
        try:
            logger.info("panic_state_dump", url=str(request.url), method=request.method)
        except OSError:
            pass
        
    # Standard log
    try:
        log_level = "critical" if exc.is_critical else "error"
        getattr(logger, log_level)("oni_exception_intercepted", **error_data)
    except OSError:
        pass

    return JSONResponse(
        status_code=500,
        content=error_data
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Fallback handler for unhandled generic exceptions.
    Forces a Sentinel purge to be safe (Fail-Safe strategy).
    """
    safe_log_critical("UNHANDLED_EXCEPTION_INTERCEPTED", 
                    error=str(exc), 
                    type=exc.__class__.__name__)
    
    # Safe strategy: Purge and Reset
    try:
        sentinel.emergency_purge_automation()
    except Exception:
        pass
        
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "error_type": "InternalServerError",
            "message": "An unhandled critical error occurred. ONI Sentinel has purged automation processes for safety.",
            "is_critical": True
        }
    )
