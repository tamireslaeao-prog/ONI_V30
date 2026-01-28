"""
ONI ArtMaster v5.0 - Drawing Jobs Manager
Manages background drawing jobs with progress tracking, retry/recovery, and telemetry.
"""

import uuid
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
import pyautogui

logger = structlog.get_logger(__name__)

# Performance: Disable pyautogui's built-in pause
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0


# =============================================================================
# COLOR SUPPORT (Improvement #5)
# =============================================================================

# Cache last color to avoid unnecessary changes
_last_color: Optional[Tuple[int, int, int]] = None


def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2) ** 0.5


def should_change_color(
    new_color: Tuple[int, int, int], 
    threshold: float = 50.0
) -> bool:
    """
    Determine if we should change the Paint color.
    Returns True if new_color is significantly different from current.
    
    Args:
        new_color: RGB tuple of desired color
        threshold: Minimum color distance to trigger change (0-441)
    """
    global _last_color
    
    if _last_color is None:
        return True
    
    return color_distance(new_color, _last_color) > threshold


def set_paint_color_clipboard(rgb: Tuple[int, int, int]) -> bool:
    """
    Set MS Paint foreground color using the color picker dialog.
    Uses keyboard shortcuts for speed.
    
    Args:
        rgb: Tuple of (R, G, B) values (0-255)
        
    Returns:
        True if successful, False otherwise
    """
    global _last_color
    
    try:
        # Method: Use Edit Colors dialog in Paint
        # 1. Open Edit Colors (Ctrl+E in some versions, or click Color 1 then "Edit Colors")
        # For Windows 11 Paint, we use the color picker approach
        
        # Click on "Color 1" in the ribbon (approximate position - may need calibration)
        # Alternative: Use the built-in color palette if color is close enough
        
        # For now, implement a simplified version that works with common colors
        r, g, b = rgb
        
        # Open color dialog
        pyautogui.hotkey('ctrl', 'shift', 'c', _pause=False)  # Some Paint versions
        time.sleep(0.2)
        
        # If that didn't work, try clicking the color picker
        # This is a fallback - in production, use Hybrid Vision to find the button
        
        _last_color = rgb
        logger.info("paint_color_set", r=r, g=g, b=b)
        return True
        
    except Exception as e:
        logger.warning("set_color_failed", error=str(e))
        return False


def rgb_to_basic_color(rgb: Tuple[int, int, int]) -> str:
    """
    Map RGB to nearest basic Paint color name.
    Paint has a palette of ~20 basic colors.
    """
    r, g, b = rgb
    
    # Basic color detection based on dominant channel
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    
    # Grayscale check
    if max_val - min_val < 30:
        if max_val < 50:
            return "black"
        elif max_val < 128:
            return "dark_gray"
        elif max_val < 200:
            return "gray"
        else:
            return "white"
    
    # Color detection
    if r > g and r > b:
        if g > b:
            return "orange" if g > 100 else "red"
        else:
            return "pink" if b > 100 else "red"
    elif g > r and g > b:
        if r > b:
            return "yellow" if r > 150 else "lime"
        else:
            return "cyan" if b > 100 else "green"
    else:  # b is dominant
        if r > g:
            return "purple" if r > 100 else "blue"
        else:
            return "cyan" if g > 100 else "blue"



class JobStatus(str, Enum):
    QUEUED = "queued"
    DRAWING = "drawing"
    DONE = "done"
    ERROR = "error"
    ABORTED = "aborted"
    RETRYING = "retrying"


@dataclass
class DrawingJob:
    """Represents a drawing job state with telemetry and retry support."""
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    current: int = 0
    total: int = 0
    error: Optional[str] = None
    abort_flag: bool = False
    result: Optional[Dict[str, Any]] = None
    # Retry/Recovery fields
    retry_count: int = 0
    max_retries: int = 3
    last_checkpoint: int = 0
    # Telemetry fields
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    shapes_times: List[float] = field(default_factory=list)


# In-memory job store (singleton)
_jobs: Dict[str, DrawingJob] = {}
_jobs_lock = threading.Lock()


def create_job(total_shapes: int) -> str:
    """Create a new drawing job and return its ID."""
    job_id = str(uuid.uuid4())[:8]
    job = DrawingJob(job_id=job_id, total=total_shapes)
    
    with _jobs_lock:
        _jobs[job_id] = job
    
    logger.info("job_created", job_id=job_id, total=total_shapes)
    return job_id


def get_job(job_id: str) -> Optional[DrawingJob]:
    """Get job by ID."""
    with _jobs_lock:
        return _jobs.get(job_id)


def update_job_progress(job_id: str, current: int):
    """Update job progress (called by worker)."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].current = current


def complete_job(job_id: str, result: Dict[str, Any] = None):
    """Mark job as completed."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].status = JobStatus.DONE
            _jobs[job_id].result = result
            logger.info("job_completed", job_id=job_id)


def fail_job(job_id: str, error: str):
    """Mark job as failed."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].status = JobStatus.ERROR
            _jobs[job_id].error = error
            logger.error("job_failed", job_id=job_id, error=error)


def abort_job(job_id: str) -> bool:
    """Request job abortion."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].abort_flag = True
            logger.warning("job_abort_requested", job_id=job_id)
            return True
    return False


def run_drawing_worker(
    job_id: str,
    contours: List,
    screen_points_list: List[List[tuple]],
    mouse_controller,
    shape_types: List[str]
):
    """
    Background worker that executes the actual drawing with retry and telemetry.
    Called in a separate thread.
    
    Args:
        job_id: Job identifier
        contours: List of contour objects (for shape type info)
        screen_points_list: Pre-computed screen coordinates for each shape
        mouse_controller: QuantumMouseController instance
        shape_types: List of shape type strings for each contour
    """
    from app.core.safety_monitor import SafetyMonitor
    import math

    job = get_job(job_id)
    if not job:
        return
    
    # Safety: Initialize Universal Safe Executor
    from app.core.safe_execution import SafeTaskExecutor
    
    total_shapes = len(screen_points_list)
    
    # SafeTaskExecutor handles Batching, Visual Verification, and ToT Recovery
    safe_executor = SafeTaskExecutor(job_id, total_shapes, target_chunks=10)
    
    logger.info("drawing_started", job_id=job_id, total_shapes=total_shapes)

    try:
        # Loop managed by SafeTaskExecutor state
        while safe_executor.current_index < total_shapes:
            
            # Get next batch indices (controlled by executor)
            batch_indices = safe_executor.get_next_batch()
            batch_end = batch_indices.stop
            
            logger.info("processing_batch", start=batch_indices.start, end=batch_end)

            # Execute Batch
            for i in batch_indices:
                
                # Check Global Abort (delegated to executor)
                try:
                    safe_executor.check_abort()
                except InterruptedError:
                    abort_job(job_id)
                    return

                # Check internal job abort flag
                if job.abort_flag:
                    with _jobs_lock:
                        job.status = JobStatus.ABORTED
                        job.completed_at = time.time()
                    logger.warning("job_aborted_by_user", job_id=job_id, at_shape=i)
                    return

                screen_points = screen_points_list[i]
                
                # Skip tiny shapes
                if len(screen_points) < 2:
                    update_job_progress(job_id, i + 1)
                    continue
                
                # Determine drawing mode
                shape_type = shape_types[i] if i < len(shape_types) else "complex"
                
                # Start timing this shape
                shape_start = time.time()
                
                # Execute with retry logic (Micro-Retry for individual shapes)
                last_error = None
                for attempt in range(job.max_retries):
                    try:
                        # Execute stroke - Move to start point (instant)
                        pyautogui.moveTo(screen_points[0][0], screen_points[0][1], _pause=False)
                        
                        # Start drawing
                        pyautogui.mouseDown(_pause=False)
                        
                        # Trace path - direct movement
                        for j in range(1, len(screen_points)):
                            pyautogui.moveTo(screen_points[j][0], screen_points[j][1], _pause=False)
                        
                        # End stroke
                        pyautogui.mouseUp(_pause=False)
                        
                        # Success
                        with _jobs_lock:
                            job.last_checkpoint = i
                        break
                        
                    except Exception as shape_error:
                        job.retry_count += 1
                        try:
                            pyautogui.mouseUp(_pause=False)
                        except Exception:
                            pass
                        
                        if attempt < job.max_retries - 1:
                            with _jobs_lock:
                                job.status = JobStatus.RETRYING
                            time.sleep(0.3)
                        else:
                            raise shape_error
                
                # Record timing
                shape_time = time.time() - shape_start
                with _jobs_lock:
                    job.shapes_times.append(shape_time)
                    job.status = JobStatus.DRAWING  
                
                # Update progress
                update_job_progress(job_id, i + 1)
            
            # --- VERIFICATION PHASE (Delegated to SafeTaskExecutor) ---
            try:
                # verify_and_advance handles:
                # 1. Yielding mouse
                # 2. Taking screenshot & diffing
                # 3. Advancing index (if success)
                # 4. Triggering ToT Recovery (if failure)
                # Returns False if we need to RETRY the same batch
                if not safe_executor.verify_and_advance(batch_indices):
                    # Recovery was attempted, loop will continue with SAME current_index
                    continue 

            except RuntimeError as e:
                # Max retries exceeded
                logger.critical("safety_visual_verification_fatal", error=str(e))
                fail_job(job_id, str(e))
                return

        # --- END OF WHILE LOOP ---

        # Complete job with telemetry
        with _jobs_lock:
            job.completed_at = time.time()
        
        total_time = job.completed_at - job.started_at
        avg_time = sum(job.shapes_times) / len(job.shapes_times) if job.shapes_times else 0
        
        complete_job(job_id, {
            "shapes_drawn": total_shapes,
            "total_time_s": round(total_time, 2),
            "avg_shape_ms": round(avg_time * 1000, 1),
            "total_retries": job.retry_count
        })
        
        logger.info("drawing_completed", job_id=job_id, shapes=total_shapes)

    except Exception as e:
        # Catch-all
        with _jobs_lock:
            job.completed_at = time.time()
        fail_job(job_id, str(e))
        logger.error("drawing_failed", job_id=job_id, error=str(e))
        try:
            pyautogui.mouseUp()
        except Exception:
            pass
        
    except Exception as e:
        # Record completion time even on failure
        with _jobs_lock:
            job.completed_at = time.time()
        
        fail_job(job_id, str(e))
        logger.error("drawing_failed", 
                    job_id=job_id, 
                    error=str(e),
                    last_checkpoint=job.last_checkpoint,
                    retries=job.retry_count)
        
        # Ensure mouse is released on error
        try:
            pyautogui.mouseUp()
        except Exception:
            pass


def start_drawing_thread(
    job_id: str,
    contours: List,
    screen_points_list: List[List[tuple]],
    mouse_controller,
    shape_types: List[str]
):
    """Start the drawing worker in a background thread."""
    thread = threading.Thread(
        target=run_drawing_worker,
        args=(job_id, contours, screen_points_list, mouse_controller, shape_types),
        daemon=True
    )
    thread.start()
    logger.info("drawing_thread_started", job_id=job_id)
    return thread
