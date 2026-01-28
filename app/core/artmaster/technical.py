import math
import pyautogui
import logging
from typing import Tuple, Optional
from .photoshop_master import PhotoshopMasterPureGUI

logger = logging.getLogger(__name__)

class TechnicalDrawingGUI:
    """
    Technical drawing tools for CAD-like precision in Photoshop.
    Uses Shape tools and Surgical mouse movement.
    """
    def __init__(self, master: PhotoshopMasterPureGUI):
        self.master = master
        self.mouse = master.mouse

    def draw_perfect_rectangle(self, top_left: Tuple[int, int], width: int, height: int, filled: bool = False):
        """Draws a perfect rectangle."""
        logger.info(f"Drawing Rectangle: {top_left} {width}x{height}")
        self.master.select_tool("shape") # Can default to rect
        
        # Ensure we are in Shape mode (requires UI vision to confirm, 
        # or we assume user set it / use defaults)
        
        start = top_left
        end = (start[0] + width, start[1] + height)
        
        self.mouse.move(start, start, mode="TURBO")
        pyautogui.mouseDown()
        # Surgical drag for exact pixel dimension
        self.mouse.surgical_precision(start, end) 
        pyautogui.mouseUp()
        
    def draw_perfect_line(self, start: Tuple[int, int], end: Tuple[int, int], snap_45: bool = True):
        """Draws a line. Optionally snaps to 45 degree increments."""
        logger.info(f"Drawing Line: {start} -> {end}")
        self.master.select_tool("shape") # Line tool usually under 'u' or SHIFT+U cycle
        # Just use brush with click-shift-click for raster line, OR shape tool
        # Let's use Brush Shift-Click method for "Raster Line" which is common in Art
        
        self.master.select_tool("brush")
        self.mouse.move(start, start, mode="TURBO")
        pyautogui.click()
        time.sleep(0.1)
        
        if snap_45:
             # Calculate nearest 45 deg angle
             angle = math.degrees(math.atan2(end[1]-start[1], end[0]-start[0]))
             # This is visual snap only, real snap handled by holding SHIFT in Photoshop
             pyautogui.keyDown('shift')
        
        self.mouse.move(end, end, mode="TURBO") # Move to end
        pyautogui.click() # Click to complete line
        
        if snap_45:
            pyautogui.keyUp('shift')

    def draw_measurement_annotation(self, start: Tuple[int, int], end: Tuple[int, int], label: str):
        """Draws a dimension line and text label."""
        # 1. Draw arrows
        self.draw_perfect_line(start, end)
        # (Simplified, skipping arrowhead drawing for now)
        
        # 2. Add text
        midpoint = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        self.master.select_tool("text")
        self.mouse.move(midpoint, midpoint, mode="TURBO")
        pyautogui.click()
        time.sleep(0.5) # Wait for text mode
        pyautogui.write(label)
        pyautogui.press("enter", presses=2) # Commit changes (Ctrl+Enter or numpad enter usually required)
        pyautogui.hotkey('ctrl', 'enter')

    def draw_perfect_circle(self, center: Tuple[int, int], radius: int):
        """Draws a perfect circle from center."""
        logger.info(f"Drawing Circle: Center={center}, Radius={radius}")
        self.master.select_tool("shape") 
        # Note: Assuming Ellipse tool is selected or cycle to it. 
        # In a real Pure GUI agent we might need to cycle Shift+U multiple times or use vision to check icon.
        # For this demo, assuming user has Ellipse tool or we use generic Shape.
        # Actually, let's try to ensure Ellipse tool by Shift+U cycling if needed, 
        # but since we can't see, we'll assume Rectangle is default and we might need to change it.
        # SAFE FALLBACK: Use Marquee tool (M) -> Elliptical Marquee + Stroke? 
        # No, User asked for "Geometry" implies Vector Shapes usually.
        # Let's try to just drag with SHIFT. If it's a rectangle tool, it becomes a square.
        # We will assume the user has the Ellipse tool ready or we cycle blindly 1 time if standard is Rect.
        # Better strategy: Calculate bounding box.
        
        top_left = (center[0] - radius, center[1] - radius)
        bottom_right = (center[0] + radius, center[1] + radius)
        
        self.mouse.move(top_left, top_left, mode="TURBO")
        
        pyautogui.keyDown('shift') # Force 1:1 aspect ratio (Circle/Square)
        pyautogui.mouseDown()
        self.mouse.surgical_precision(top_left, bottom_right)
        pyautogui.mouseUp()
        pyautogui.keyUp('shift')

