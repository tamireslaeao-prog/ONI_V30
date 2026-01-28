"""
ONI ArtMaster - Utilities
"""
import asyncio
import structlog
from functools import wraps
from app.services.oni.desktop_hybrid_service import desktop_vision_v2

logger = structlog.get_logger(__name__)

def mandatory_vision_check(func):
    """Decorator to enforce Pre/Post Hybrid Vision scans."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 1. PRE-ACTION SCAN
        try:
            await desktop_vision_v2.scan_active_window()
        except Exception as e:
            logger.warning("pre_action_scan_failed", error=str(e))

        # Execute
        result = await func(*args, **kwargs)

        # 2. POST-ACTION SCAN
        try:
            await asyncio.sleep(0.5) # Allow UI update
            await desktop_vision_v2.scan_active_window()
        except Exception as e:
            logger.warning("post_action_scan_failed", error=str(e))
            
        return result
    return wrapper

def track_execution_time(func):
    """Track execution time decorator."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        # Services container will be imported inside wrapper to avoid circular import if needed
        # Or we assume a global container. 
        # For now, let's just log time, metrics can be handled by middleware or global stats
        
        try:
            result = await func(*args, **kwargs)
            
            elapsed = (time.time() - start) * 1000
            if isinstance(result, dict) and 'execution_time_ms' in result:
                result['execution_time_ms'] = elapsed
            elif hasattr(result, 'execution_time_ms'):
                 # Check if it's a Pydantic model
                 try:
                    result.execution_time_ms = elapsed
                 except:
                    pass
            
            return result
            
        except Exception:
            raise
    
    return wrapper
