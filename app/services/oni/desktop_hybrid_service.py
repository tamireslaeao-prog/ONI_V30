"""
Desktop Hybrid Vision Service V2 (Canvas Aware)
Adapts the "Accessibility Tree" concept from Browser Subagents to Windows Desktop Apps.
Uses pywinauto (UIA backend) to extract semantic structure of windows.
"""

import structlog
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pywinauto
import pywinauto
from pywinauto import Desktop
from app.services.vision_shared import get_shared_vision
import cv2
import numpy as np
from PIL import Image as PILImage

logger = structlog.get_logger(__name__)

@dataclass
class DesktopElement:
    """Represents a UI element in a desktop application."""
    id: str
    name: str
    control_type: str
    rect: Dict[str, int]
    is_enabled: bool
    is_visible: bool
    is_keyboard_focusable: bool
    # Metadata for LLM
    description: str 

@dataclass
class DesktopVisionResult:
    """Complete analysis result."""
    window_title: str
    process_name: str
    elements: List[DesktopElement]
    screenshot_path: Optional[str] = None
    annotated_path: Optional[str] = None
    canvas_limits: Optional[Dict[str, int]] = None
    
    def to_dict(self):
        return {
            'window_title': self.window_title,
            'process_name': self.process_name,
            'elements': [asdict(e) for e in self.elements],
            'screenshot_path': self.screenshot_path,
            'annotated_path': self.annotated_path,
            'canvas_limits': self.canvas_limits
        }

class DesktopHybridVision:
    """
    Scans desktop windows using UI Automation to build a semantic tree.
    """
    
    def __init__(self):
        self.desktop = Desktop(backend="uia")
    
    # Alias for backwards compatibility
    async def scan_active_window_v2(self) -> DesktopVisionResult:
        """Alias for scan_active_window"""
        return await self.scan_active_window()
    
    async def scan_active_window(self) -> DesktopVisionResult:
        """
        Scans the currently active window and extracts all interactive elements.
        """
        try:
            # 1. Get Active Window
            import pygetwindow as gw
            active_win = gw.getActiveWindow()
            if not active_win:
                raise Exception("No active window found")
            
            title = active_win.title
            logger.info("scanning_window", title=title)
            
            # Connect using pywinauto
            # Using 'connect' instead of getting from Desktop to be safer
            try:
                # Try to find window by handle
                app_wrapper = self.desktop.window(handle=active_win._hWnd)
            except Exception:
                # Fallback to title
                app_wrapper = self.desktop.window(title=title)
            
            if not app_wrapper.exists():
                logger.warning("window_not_found_in_uia", title=title)
                # Fallback to loose matching
                app_wrapper = self.desktop.window(title_re=f".*{title}.*")

            # 1.1 Capture Screenshot (Visual Grounding)
            # UPGRADE: Use SharedVision for <10ms latency if available
            import os
            from datetime import datetime
            
            # Ensure directory exists
            output_dir = os.path.join(os.getcwd(), "temp", "ANALIZER")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%H-%M-%S-%f")[:-3]
            screenshot_filename = f"hybrid_{timestamp}.png"
            screenshot_path = os.path.join(output_dir, screenshot_filename)

            try:
                # Try getting fresh frame from shared service
                shared_vision = get_shared_vision()
                # Use a tight 200ms age limit for real-time accuracy
                frame = await shared_vision.get_fresh_frame(max_age=0.2)
                
                if frame:
                    # Save for record/annotation (async I/O optimization could happen here, keeping it simple)
                    cv2.imwrite(screenshot_path, frame.image_bgr)
                    logger.info("screenshot_captured_via_shared_vision", path=screenshot_path)
                else:
                    raise Exception("Shared Vision returned None")
                    
            except Exception as e:
                logger.warning("shared_vision_capture_failed_fallback_to_pyautogui", error=str(e))
                # Fallback to PyAutoGUI
                import pyautogui
                pyautogui.screenshot(screenshot_path)
                logger.info("screenshot_captured_fallback", path=screenshot_path)

            # 2. Walk the Tree
            elements = []
            
            # Optimized: Find all descendants that are "Control" type
            # We filter for common interactive types to avoid noise
            # or we just dump everything and filter later.
            # UIA Walk can be slow. Using find_all is better.
            
            try:
                uia_elements = app_wrapper.descendants()
            except Exception as e:
                logger.error("uia_descendants_failed", error=str(e))
                uia_elements = []
            
            logger.info("elements_found", count=len(uia_elements))
            
            for elem in uia_elements:
                try:
                    # Basic properties
                    rect = elem.rectangle()
                    if rect.width() == 0 or rect.height() == 0:
                        continue # Skip invisible/zero-size
                        
                    visible = elem.is_visible()
                    if not visible:
                        continue

                    name = elem.window_text()
                    control_type = elem.element_info.control_type
                    
                    # Generate ID
                    elem_id = f"uid_{uuid.uuid4().hex[:8]}"
                    
                    # Build struct
                    element = DesktopElement(
                        id=elem_id,
                        name=name,
                        control_type=control_type,
                        rect={
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height(),
                            'center_x': rect.mid_point().x,
                            'center_y': rect.mid_point().y
                        },
                        is_enabled=elem.is_enabled(),
                        is_visible=visible,
                        is_keyboard_focusable=elem.is_keyboard_focusable(),
                        description=f"{control_type} '{name}'"
                    )
                    
                    elements.append(element)
                    
                except Exception as e:
                    # Element might have disappeared or is invalid
                    continue
            
            # 1.2 Draw Annotations (Proof of Vision)
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                image = Image.open(screenshot_path)
                draw = ImageDraw.Draw(image)
                
                # Load font (optional, default to simple)
                # font = ImageFont.truetype("arial.ttf", 15)
                
                for elem in elements:
                    r = elem.rect
                    # Draw Box (Green for enabled, Red for disabled)
                    color = "green" if elem.is_enabled else "red"
                    draw.rectangle([r['left'], r['top'], r['right'], r['bottom']], outline=color, width=2)
                    
                    # Draw Label (if space permits)
                    if r['height'] > 10:
                        text = f"{elem.id}: {elem.name}"
                        # draw.text((r['left'], r['top'] - 12), text, fill="yellow") # Simple text
                        
                annotated_filename = f"annotated_hybrid_{timestamp}.png"
                annotated_path = os.path.join(output_dir, annotated_filename)
                image.save(annotated_path)
                logger.info("annotation_saved", path=annotated_path)
                
            except Exception as e:
                logger.error("annotation_failed", error=str(e))
                annotated_path = None

            # 2.5: Detect Canvas Limits (Universal)
            canvas_bounds = None
            try:
                # Load image for CV processing
                import cv2
                import numpy as np
                img_whole = cv2.imread(screenshot_path)
                
                # Determine active window rect
                win_rect = active_win.box # (left, top, width, height)
                
                # Crop to window to avoid noise from other apps/taskbar
                # Ensure bounds are within image
                h_img, w_img = img_whole.shape[:2]
                x1 = max(0, win_rect.left)
                y1 = max(0, win_rect.top)
                x2 = min(w_img, win_rect.left + win_rect.width)
                y2 = min(h_img, win_rect.top + win_rect.height)
                
                img_cv = img_whole[y1:y2, x1:x2]
                
                # Use CanvasBoundsService for Visual Detection
                from app.services.canvas_bounds import CanvasBoundsService
                
                # Detect (now relative to window)
                detected = await CanvasBoundsService.detect_canvas_visual(
                    image_bgr=img_cv,
                    window_x=x1, # Pass window_x as base
                    window_y=y1
                )
                
                if detected:
                    canvas_bounds = {
                        "x": detected.x,
                        "y": detected.y,
                        "width": detected.width,
                        "height": detected.height,
                        "center_x": detected.center_x,
                        "center_y": detected.center_y
                    }
                    logger.info("hybrid_canvas_detected", bounds=canvas_bounds)
                    
            except Exception as e:
                logger.warning("hybrid_canvas_detection_failed", error=str(e))

            # 3. Create Result
            return DesktopVisionResult(
                window_title=title,
                process_name="ActiveCanvas_v2", # Debug marker
                elements=elements,
                screenshot_path=screenshot_path,
                annotated_path=annotated_path,
                canvas_limits=canvas_bounds
            )
            
        except Exception as e:
            logger.error("scan_failed", error=str(e))
            raise
    
    async def semantic_find(self, query: str) -> Dict[str, Any]:
        """
        Find UI element using natural language query.
        Visual Cortex 3.0 Integration.
        
        Args:
            query: Natural language (e.g., "red button", "login", "close icon")
        
        Returns:
            Dict with element info and coordinates
        """
        from PIL import Image
        from app.core.vision.semantic_cortex import semantic_cortex
        
        try:
            # 1. Scan current window to get screenshot and OCR
            scan_result = await self.scan_active_window()
            
            if not scan_result.screenshot_path:
                return {"success": False, "error": "No screenshot available"}
            
            # 2. Load screenshot
            image = Image.open(scan_result.screenshot_path)
            
            # 3. Convert UIA elements to OCR-like format for cortex
            ocr_results = []
            for elem in scan_result.elements:
                if elem.name:
                    ocr_results.append({
                        "text": elem.name,
                        "bbox": [
                            elem.rect['left'],
                            elem.rect['top'],
                            elem.rect['right'],
                            elem.rect['bottom']
                        ],
                        "confidence": 0.9
                    })
            
            # 4. Run semantic search
            result = await semantic_cortex.find_element(image, query, ocr_results)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.explanation,
                    "query": query
                }
            
            return {
                "success": True,
                "query": query,
                "element": {
                    "type": result.element.element_type,
                    "label": result.element.label,
                    "confidence": result.element.confidence,
                    "bbox": result.element.bbox,
                    "center_x": result.element.center[0],
                    "center_y": result.element.center[1]
                },
                "alternatives": [
                    {
                        "type": e.element_type,
                        "label": e.label,
                        "center": e.center
                    } for e in result.elements[1:4]  # Top 3 alternatives
                ],
                "screenshot_path": scan_result.screenshot_path
            }
            
        except Exception as e:
            logger.error("semantic_find_failed", error=str(e))
            return {"success": False, "error": str(e)}

# Singleton instance
desktop_vision_v2 = DesktopHybridVision()

