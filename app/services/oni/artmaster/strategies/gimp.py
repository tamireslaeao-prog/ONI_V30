"""
ONI ArtMaster - GIMP Strategy
"""
import asyncio
import structlog
from typing import Dict, Optional, Tuple
from pathlib import Path

# Safe imports
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from .base import ApplicationStrategy
from ..utils import mandatory_vision_check

logger = structlog.get_logger(__name__)


class GimpStrategy(ApplicationStrategy):
    """Strategy for GIMP."""
    
    TOOL_SHORTCUTS = {
        "rectangle_select": "r",
        "ellipse_select": "e",
        "free_select": "f",
        "fuzzy_select": "u",
        "select_by_color": "shift+o",
        "scissors": "i",
        "foreground_select": "ctrl+h",
        "path": "b",
        "color_picker": "o",
        "zoom": "z",
        "measure": "shift+m",
        "move": "m",
        "align": "q",
        "crop": "shift+c",
        "rotate": "shift+r",
        "scale": "shift+t",
        "shear": "shift+s",
        "perspective": "shift+p",
        "flip": "shift+f",
        "text": "t",
        "fill": "shift+b",
        "gradient": "g",
        "pencil": "n",
        "paintbrush": "p",
        "eraser": "shift+e",
        "airbrush": "a",
        "ink": "k",
        "clone": "c",
        "heal": "h",
        "perspective_clone": "ctrl+shift+c",
        "blur": "shift+u",
        "smudge": "s",
        "dodge": "shift+d",
    }
    
    async def ensure_focus(self) -> bool:
        """Focus GIMP window."""
        if not gw: return False
        
        try:
            windows = [w for w in gw.getAllWindows()
                      if "gimp" in w.title.lower()]
            
            if not windows:
                return False
            
            target = windows[0]
            if not target.isActive:
                target.activate()
                await asyncio.sleep(0.5)
            
            self.canvas_center = (
                target.left + target.width // 2,
                target.top + target.height // 2
            )
            
            return True
            
        except Exception as e:
            logger.error("gimp_focus_failed", error=str(e))
            return False
    
    @mandatory_vision_check
    async def select_tool(self, tool_name: str) -> bool:
        """Select GIMP tool."""
        if not pyautogui: return False
        
        tool_lower = tool_name.lower()
        if tool_lower in self.TOOL_SHORTCUTS:
            key = self.TOOL_SHORTCUTS[tool_lower]
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            await asyncio.sleep(0.1)
            return True
        
        return False
    
    async def prepare_canvas(self) -> bool:
        """Prepare GIMP canvas."""
        if not pyautogui: return False
        
        pyautogui.click(self.canvas_center[0], self.canvas_center[1], _pause=False)
        await asyncio.sleep(0.2)
        
        return True
    
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get GIMP tool shortcuts."""
        return self.TOOL_SHORTCUTS
    
    @mandatory_vision_check
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Create layer in GIMP."""
        if not pyautogui: return False
        
        # Ctrl+Shift+N
        pyautogui.hotkey('ctrl', 'shift', 'n')
        await asyncio.sleep(0.3)
        
        if name:
            pyautogui.write(name, interval=0.05)
        
        pyautogui.press('enter')
        await asyncio.sleep(0.2)
        
        return True
    
    @mandatory_vision_check
    async def save_file(self, path: str) -> bool:
        """Save GIMP file."""
        if not pyautogui: return False
        
        # Ctrl+Shift+E (Export As)
        pyautogui.hotkey('ctrl', 'shift', 'e')
        await asyncio.sleep(0.5)
        
        pyautogui.write(str(path), interval=0.05)
        pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        return True
