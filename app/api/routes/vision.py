"""
ONI Vision Routes
Endpoints para screenshots, análise visual e mapeamento de tela.
"""

import os
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import pyautogui
import structlog

from app.core.dependencies import container
from app.infrastructure.vision.capture import ScreenCapture
from .core import (
    ImageFormat, 
    ScreenshotResponse, 
    WindowManager, 
    OCRService,
    rate_limit,
    get_vision_service
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["vision"])

# =============================================================================
# CONFIGURAÇÕES DE PASTA
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "temp" / "ANALIZER"
SCREENSHOT_LEGACY_NAME = "screenshot.png"
SCREENSHOT_PREFIX = "screen"
DEFAULT_QUALITY = 95

def ensure_screenshot_dir() -> Path:
    """Ensure screenshot directory exists and return path."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR

def generate_screenshot_path(step_description: str = "") -> tuple[Path, Path]:
    """Generate unique and fixed screenshot paths with timestamp and step description."""
    save_dir = ensure_screenshot_dir()
    
    timestamp = datetime.now().strftime("%H-%M-%S")
    
    safe_desc = ""
    if step_description:
        safe_desc = "_" + "".join(c if c.isalnum() or c in "-_" else "-" for c in step_description)[:30]
    
    unique_name = f"{SCREENSHOT_PREFIX}_{timestamp}{safe_desc}.png"
    unique_path = save_dir / unique_name
    fixed_path = save_dir / SCREENSHOT_LEGACY_NAME
    
    return unique_path, fixed_path


# =============================================================================
# RESPONSE MODELS
# =============================================================================

from pydantic import BaseModel

class EnhancedScreenshotResponse(BaseModel):
    """Enhanced screenshot with window info."""
    image: str
    resolution: str
    format: str
    saved_path: Optional[str] = None
    file_size_kb: Optional[float] = None
    active_window_title: str
    active_window_process: str
    mouse_x: int
    mouse_y: int
    mouse_in_primary_monitor: bool
    capture_time_ms: float


class UIAnalysisResponse(BaseModel):
    """Response from UI analysis with optimized element detection."""
    monitor: int
    image_dimensions: dict
    total_elements: int
    key_buttons: list
    text_labels: list
    interactive_areas: list
    annotated_image_path: Optional[str] = None
    annotated_image_path: Optional[str] = None
    analysis_time_ms: float


class OmniParserResponse(BaseModel):
    """Response from OmniParser analysis."""
    annotated_base64: str
    elements: list[dict]
    latency_ms: float


# =============================================================================
# SCREENSHOT ENDPOINTS
# =============================================================================

@router.get("/screenshot", response_model=ScreenshotResponse)
@rate_limit(limit=10, window=1)
async def get_screenshot(
    format: ImageFormat = Query(ImageFormat.JPEG),
    quality: int = Query(DEFAULT_QUALITY, ge=1, le=100),
    draw_cursor: bool = Query(True, description="Draw cursor position on screenshot"),
    step_name: str = Query("", description="Step name for unique filename"),
    monitor: int = Query(2, description="Monitor to capture: 1=left, 2=right"),
    vision=Depends(get_vision_service)
):
    """Capture screen from specific monitor with cursor overlay."""
    start_time = perf_counter()
    
    try:
        # Capture screen
        capture_result = await vision.capture()
        if capture_result is None:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        
        # Convert to PIL Image
        image_array = capture_result.image
        rgb_array = image_array[:, :, ::-1]
        img = Image.fromarray(rgb_array)
        
        # Crop to specific monitor if dual setup detected
        global_offset_x = 0
        if img.width > 2000:  # Dual monitor detected
            split_point = img.width // 2
            
            if monitor == 2:
                # Monitor 2 = Left (Primary/Main)
                img = img.crop((0, 0, split_point, img.height))
                global_offset_x = 0
            else:
                # Monitor 1 = Right
                img = img.crop((split_point, 0, img.width, img.height))
                global_offset_x = split_point
            
            logger.info("monitor_cropped", monitor=monitor, offset_x=global_offset_x)
        
        # Draw cursor if requested
        if draw_cursor:
            from PIL import ImageDraw
            mouse_x, mouse_y = pyautogui.position()
            
            # Adjust coordinates for cropped monitor
            mouse_x -= global_offset_x
            
            # Only draw if cursor is in visible area
            if 0 <= mouse_x < img.width and 0 <= mouse_y < img.height:
                draw = ImageDraw.Draw(img)
                
                cursor_radius = 15
                # Red circle
                draw.ellipse(
                    [mouse_x - cursor_radius, mouse_y - cursor_radius,
                     mouse_x + cursor_radius, mouse_y + cursor_radius],
                    outline=(255, 0, 0), width=3
                )
                # Crosshair
                crosshair_size = 10
                draw.line([(mouse_x - crosshair_size, mouse_y), 
                          (mouse_x + crosshair_size, mouse_y)], 
                         fill=(255, 0, 0), width=2)
                draw.line([(mouse_x, mouse_y - crosshair_size), 
                          (mouse_x, mouse_y + crosshair_size)], 
                         fill=(255, 0, 0), width=2)
                # Center dot
                draw.ellipse([mouse_x - 3, mouse_y - 3, mouse_x + 3, mouse_y + 3], 
                           fill=(255, 0, 0))
                
                # Coordinates text
                coord_text = f"({mouse_x + global_offset_x}, {mouse_y})"
                text_x = mouse_x + cursor_radius + 5
                text_y = mouse_y - 10
                draw.rectangle([text_x - 2, text_y - 2, text_x + 80, text_y + 16], 
                             fill=(0, 0, 0))
                draw.text((text_x, text_y), coord_text, fill=(255, 255, 0))
                
                logger.info("cursor_drawn", x=mouse_x + global_offset_x, y=mouse_y)
        
        # Generate paths
        unique_path, fixed_path = generate_screenshot_path(step_name)
        
        # Save both files
        img.save(str(unique_path))
        img.save(str(fixed_path))
        
        file_size_kb = unique_path.stat().st_size / 1024
        capture_time_ms = (perf_counter() - start_time) * 1000
        resolution = f"{img.width}x{img.height}"
        
        file_url = f"file:///{str(unique_path).replace(os.sep, '/')}"
        
        logger.info("screenshot_captured", 
                   resolution=resolution, 
                   format=format.value,
                   size_kb=file_size_kb,
                   time_ms=capture_time_ms,
                   monitor=monitor)
        
        # Import ActionGuardService
        from app.services.oni.guards import ActionGuardService, UndoGuardService
        ActionGuardService.record_screenshot()
        UndoGuardService.record_verification()
        
        return ScreenshotResponse(
            image="",
            resolution=resolution,
            format=format.value,
            saved_path=str(unique_path),
            file_size_kb=round(file_size_kb, 2),
            capture_time_ms=round(capture_time_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("screenshot_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screenshot-enhanced", response_model=EnhancedScreenshotResponse)
@rate_limit(limit=10, window=1)
async def get_enhanced_screenshot(
    format: ImageFormat = Query(ImageFormat.JPEG),
    quality: int = Query(85, ge=1, le=100),
    vision=Depends(get_vision_service)
):
    """Enhanced screenshot with active window info."""
    start_time = perf_counter()
    
    try:
        window_info = await WindowManager.get_active_window_info()
        active_title = window_info['title'] if window_info else "Unknown"
        active_process = window_info['process_name'] if window_info else "unknown"
        
        mouse_x, mouse_y = pyautogui.position()
        mouse_in_primary = (0 <= mouse_x < 1920 and 0 <= mouse_y < 1080)
        
        capture_result = await vision.capture()
        if capture_result is None:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        
        image_array = capture_result.image
        rgb_array = image_array[:, :, ::-1]
        img = Image.fromarray(rgb_array)
        
        save_dir = ensure_screenshot_dir()
        fixed_path = save_dir / SCREENSHOT_LEGACY_NAME
        img.save(str(fixed_path))
        file_size_kb = fixed_path.stat().st_size / 1024
        
        capture_time_ms = (perf_counter() - start_time) * 1000
        resolution = f"{img.width}x{img.height}"
        
        logger.info("enhanced_screenshot", 
                   resolution=resolution,
                   active_window=active_title,
                   time_ms=capture_time_ms)
        
        return EnhancedScreenshotResponse(
            image="",
            resolution=resolution,
            format=format.value,
            saved_path=str(fixed_path),
            file_size_kb=round(file_size_kb, 2),
            active_window_title=active_title,
            active_window_process=active_process,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            mouse_in_primary_monitor=mouse_in_primary,
            capture_time_ms=round(capture_time_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("enhanced_screenshot_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/serve-image")
async def serve_image(
    path: str = Query(..., description="Path to the screenshot file to serve"),
):
    """Serve local screenshot via HTTP."""
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Image not found: {path}")
        
        allowed_dirs = ["C:\\temp\\oni_screenshots", "C:/temp/oni_screenshots"]
        is_allowed = any(
            os.path.normpath(path).startswith(os.path.normpath(d)) 
            for d in allowed_dirs
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=403, 
                detail="Access denied. Only files from C:/temp/oni_screenshots/ allowed."
            )
        
        ext = os.path.splitext(path)[1].lower()
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp"
        }
        content_type = content_types.get(ext, "image/png")
        
        return FileResponse(
            path=path,
            media_type=content_type,
            filename=os.path.basename(path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("serve_image_failed", error=str(e), path=path)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# UI ANALYZER ENDPOINT - OPTIMIZED
# =============================================================================

@router.get("/ui-analyze")
@rate_limit(limit=5, window=1)
async def analyze_ui_elements(
    screenshot_path: str = Query(None, description="Path to screenshot"),
    annotate: bool = Query(True, description="Generate annotated image"),
    monitor: int = Query(2, description="Monitor to analyze: 1=right, 2=left (primary)"),
    step_name: str = Query("", description="Step description for unique filenames"),
    max_buttons: int = Query(30, description="Max buttons to detect"),
    max_texts: int = Query(80, description="Max text labels to detect"),
    min_confidence: float = Query(0.4, description="Minimum detection confidence"),
    nocache: int = Query(0, description="Cache buster timestamp - use different value each call"),
    vision=Depends(get_vision_service)
):
    """
    Analyze UI elements with optimized detection.
    
    Features:
    - Captures specific monitor (default=2, left/primary)
    - Saves with timestamp: screen_HH-MM-SS_step.png, annotated_HH-MM-SS_step.png
    - Limits detection to key interactive elements
    - Clean annotations with precise coordinates
    """
    start_time = perf_counter()
    
    try:
        from app.services.oni.ui_analyzer_optimized import OptimizedUIAnalyzer
        
        save_dir = ensure_screenshot_dir()
        
        # 1. Capture or use existing screenshot
        if not screenshot_path:
            screenshot_path = str(save_dir / SCREENSHOT_LEGACY_NAME)
            capture_result = await vision.capture()
            if capture_result is None:
                raise HTTPException(status_code=500, detail="Failed to capture screenshot")
            
            image_array = capture_result.image
            rgb_array = image_array[:, :, ::-1]
            img = Image.fromarray(rgb_array)
            
            # Crop to selected monitor
            global_offset_x = 0
            if img.width > 2000:
                split_point = img.width // 2
                
                if monitor == 2:
                    # Monitor 2 = Left (Primary/Main)
                    img = img.crop((0, 0, split_point, img.height))
                    global_offset_x = 0
                else:
                    # Monitor 1 = Right
                    img = img.crop((split_point, 0, img.width, img.height))
                    global_offset_x = split_point
                
                logger.info("monitor_selected", monitor=monitor, offset_x=global_offset_x)
            
                logger.info("monitor_selected", monitor=monitor, offset_x=global_offset_x)
            
            # Generate timestamp with milliseconds for unique filenames
            timestamp = datetime.now().strftime("%H-%M-%S-") + f"{datetime.now().microsecond // 1000:03d}"
            safe_step = ""
            if step_name:
                safe_step = "_" + "".join(c if c.isalnum() or c in "-_" else "-" for c in step_name)[:30]
            
            # Save screenshot with timestamp
            screenshot_unique = str(save_dir / f"screen_{timestamp}{safe_step}.png")
            img.save(screenshot_unique)
            logger.info("screenshot_saved", unique=screenshot_unique)
            
            # Use unique path for analysis
            target_path = screenshot_unique
        else:
            # Use provided path
            target_path = screenshot_path
            if not os.path.exists(target_path):
                raise HTTPException(status_code=404, detail=f"Screenshot not found: {target_path}")

        # 2. Analyze with optimized detector
        analyzer = OptimizedUIAnalyzer(
            target_path,
            max_buttons=max_buttons,
            max_texts=max_texts,
            min_confidence=min_confidence
        )
        ui_data = analyzer.analyze()
        
        # 3. Adjust coordinates to global space if monitor 2
        global_offset_x = ui_data.get('monitor_offset_x', 0)
        
        if global_offset_x > 0:
            def offset_element(item):
                if 'coordinates' in item:
                    c = item['coordinates']
                    c['x'] += global_offset_x
                    c['center_x'] += global_offset_x
                    if 'bbox' in c:
                        c['bbox'][0] += global_offset_x
                        c['bbox'][2] += global_offset_x
                return item
            
            ui_data['key_buttons'] = [offset_element(b) for b in ui_data['key_buttons']]
            ui_data['text_labels'] = [offset_element(t) for t in ui_data['text_labels']]
            ui_data['interactive_areas'] = [offset_element(a) for a in ui_data['interactive_areas']]
        
        # 4. Generate unique filenames with timestamp (if not already set above)
        if 'timestamp' not in dir() or not timestamp:
            timestamp = datetime.now().strftime("%H-%M-%S")
            safe_step = ""
            if step_name:
                safe_step = "_" + "".join(c if c.isalnum() or c in "-_" else "-" for c in step_name)[:30]
        
        # 5. Generate clean annotated image
        annotated_path = None
        annotated_unique = None
        if annotate:
            # Get current mouse position to draw on annotation
            import pyautogui
            mouse_x, mouse_y = pyautogui.position()
            
            # Adjust mouse position relative to the cropped image
            # If we cropped, the image coords are local (0..width), so we need to subtract global_offset_x from mouse_x
            # to get the position ON THE IMAGE
            local_mouse_x = mouse_x - global_offset_x
            local_mouse_y = mouse_y
            
            # Pass tuple or None if out of bounds (though mouse_x/y are global, function expects global or local? 
            # The analyzer works on the loaded image (which is cropped). annotations are drawn on that image.
            # So we should pass LOCAL coordinates relative to the cropped image.
            
            # Check if mouse is within this monitor's crop
            mouse_pos = None
            # If monitor 2 (left, offset 0), mouse should be < split_point (approx 1920)
            # If monitor 1 (right, offset 1920), mouse should be >= split_point
            
            annotated_unique = str(save_dir / f"annotated_{timestamp}{safe_step}.png")
            
            # Pass local coordinates to draw correctly on the cropped image
            analyzer.create_clean_annotation(annotated_unique, mouse_pos=(local_mouse_x, local_mouse_y))
            annotated_path = annotated_unique
        
        # 6. Save structured JSON (with timestamp)
        json_unique = str(save_dir / f"ui_data_{timestamp}{safe_step}.json")
        import json
        with open(json_unique, 'w', encoding='utf-8') as f:
            json.dump(ui_data, f, indent=2, ensure_ascii=False, default=str)
        
        analysis_time_ms = (perf_counter() - start_time) * 1000
        
        logger.info(
            "ui_analysis_complete",
            monitor=monitor,
            buttons=len(ui_data['key_buttons']),
            texts=len(ui_data['text_labels']),
            areas=len(ui_data['interactive_areas']),
            time_ms=analysis_time_ms
        )
        
        # Return with anti-cache headers
        response_data = UIAnalysisResponse(
            monitor=monitor,
            image_dimensions=ui_data['image_dimensions'],
            total_elements=ui_data['total_elements'],
            key_buttons=ui_data['key_buttons'],
            text_labels=ui_data['text_labels'],
            interactive_areas=ui_data['interactive_areas'],
            annotated_image_path=annotated_path,
            analysis_time_ms=round(analysis_time_ms, 2)
        )
        
        return JSONResponse(
            content=response_data.model_dump(),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except ImportError as e:
        logger.error("ui_analyzer_import_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"UIAnalyzer not available: {e}")
    except Exception as e:
        logger.error("ui_analysis_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/omniparser", response_model=OmniParserResponse)
@rate_limit(limit=5, window=1)
async def omniparser_analyze(
    screenshot_path: str = Query(None, description="Path to screenshot"),
    confidence: float = Query(0.15, description="Confidence threshold"),
    vision=Depends(get_vision_service)
):
    """
    Analyze screen using OmniParser (YOLO + Strings) with caching support.
    Returns base64 annotated image and element list with IDs.
    """
    start_time = perf_counter()
    
    try:
        if not container.has("omniparser"):
             raise HTTPException(status_code=503, detail="OmniParser service not initialized")
             
        omniparser = container.get("omniparser")
        
        # 1. Get Image and Hash
        image = None
        frame_hash = None
        
        if screenshot_path and os.path.exists(screenshot_path):
            image = Image.open(screenshot_path)
            # Optional: compute hash for files too? 
            # For now, we prioritize current screen caching
        else:
            # Try to get from Shared Vision for cache efficiency
            from app.services.vision_shared import get_shared_vision
            shared_vision = get_shared_vision()
            
            if shared_vision:
                cached_frame = shared_vision.get_current_frame()
                if cached_frame:
                    # Use RGB version directly
                    image = Image.fromarray(cached_frame.image_rgb)
                    frame_hash = cached_frame.hash
            
            # Fallback if shared vision not ready/available
            if image is None:
                capture = await vision.capture()
                if not capture:
                    raise HTTPException(status_code=500, detail="Capture failed")
                image = Image.fromarray(capture.image[:, :, ::-1])
                # Note: vision.capture() result might not have hash yet in standard interface
            
        # 2. Parse with Caching
        # omniparser.parse_screen now accepts frame_hash
        result = await omniparser.parse_screen(
            image, 
            confidence_threshold=confidence,
            frame_hash=frame_hash
        )
        
        # 3. Convert annotated to base64
        import io
        import base64
        buffered = io.BytesIO()
        result["annotated_image"].save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        latency = (perf_counter() - start_time) * 1000
        
        # Log if it was a cache hit (implied by latency < threshold, but result has no meta)
        # We could add "cached": True to OmniParserResponse if needed
        
        return OmniParserResponse(
            annotated_base64=img_str,
            elements=result["elements"],
            latency_ms=round(latency, 2)
        )
        
    except Exception as e:
        logger.error("omniparser_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
