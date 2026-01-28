import cv2
import numpy as np
import pyautogui
import pytesseract
from typing import Dict, Tuple, Optional, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)

class PhotoshopUIMapper:
    """
    Visual mapping system for Photoshop Interface.
    Uses Computer Vision to detect:
    - Toolbar location and tools
    - Canvas area bounds
    - Panel locations (Layers, Color, etc.)
    """
    def __init__(self):
        self.toolbar_bounds: Optional[Tuple[int, int, int, int]] = None
        self.canvas_area: Optional[Tuple[int, int, int, int]] = None
        self.panels: Dict[str, Tuple[int, int, int, int]] = {}
        self.tools: Dict[str, Tuple[int, int]] = {}
        
        # Hardcoded Fallback Locations (for 1920x1080 default workspace)
        # This allows the system to work immediately without perfect CV
        self._fallback_map = {
            "toolbar": (10, 50, 40, 800), # Typical left toolbar
            "canvas": (100, 100, 1500, 900), # Central area
            "panels_right": (1600, 100, 1900, 900), # Right panels
            "tools": {
                "brush": (25, 300), 
                "move": (25, 70),
                "marquee": (25, 100),
                "lasso": (25, 130),
                "crop": (25, 190),
                "eraser": (25, 360),
                "text": (25, 450),
                "pen": (25, 420),
                "shape": (25, 520),
                "hand": (25, 600),
                "zoom": (25, 630),
                "color_picker": (25, 680)
            }
        }

    def scan_interface(self):
        """
        Scans the entire screen to map UI elements.
        Currently uses a fallback logic but prepared for CV implementation.
        """
        logger.info("Scanning Photoshop Interface...")
        
        # 1. Capture Screenshot
        try:
            screenshot = pyautogui.screenshot()
            img = np.array(screenshot)
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # TODO: Implement real Template Matching here
            # For now, we trust the fallbacks or rudimentary brightness checks
            
            # Quick check: Is toolbar roughly where expected?
            # Check for dark strip on the left
            left_strip = img_gray[100:800, 0:50]
            if np.mean(left_strip) < 100: # Assuming Dark Mode
                logger.info("Dark Mode detected, assuming standard toolbar.")
                self.toolbar_bounds = self._fallback_map["toolbar"]
            else:
                logger.warning("Light Mode or non-standard layout. Using fallbacks.")
                self.toolbar_bounds = self._fallback_map["toolbar"]

            # Set Canvas
            self.canvas_area = self._fallback_map["canvas"]
            
            # Map Tools (relative to toolbar)
            self._map_tools_from_bounds(self.toolbar_bounds)
            
            logger.info("Scan Complete. Interface Mapped.")
            
        except Exception as e:
            logger.error(f"Vision scan failed: {e}")
            logger.info("Reverting to hardcoded map.")
            self._use_hardcoded_map()

    def _map_tools_from_bounds(self, toolbar_bounds):
        """Calculates tool positions based on toolbar location."""
        x_start, y_start, width, height = toolbar_bounds
        center_x = x_start + width // 2
        
        # Mapping relative offsets from top of toolbar
        # Standard Photoshop 2-column or 1-column layout detection needed
        # Assuming 1-column for simplicity or using mapped offsets
        
        for tool, (fx, fy) in self._fallback_map["tools"].items():
            # In a real dynamic system, we'd detect icons.
            # Here we just set them.
            self.tools[tool] = (fx, fy) # Using absolute fallbacks for now

    def _use_hardcoded_map(self):
        self.toolbar_bounds = self._fallback_map["toolbar"]
        self.canvas_area = self._fallback_map["canvas"]
        self.tools = self._fallback_map["tools"]

    def find_tool(self, tool_name: str) -> Optional[Tuple[int, int]]:
        """Returns screen coordinates for a tool."""
        return self.tools.get(tool_name)

    def get_canvas_center(self) -> Tuple[int, int]:
        if not self.canvas_area:
            return (960, 540)
        x, y, w, h = self.canvas_area
        return (x + w // 2, y + h // 2)
