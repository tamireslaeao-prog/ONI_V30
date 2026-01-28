"""
ONI ArtMaster - GIMP Strategy
GIMP-specific automation strategy.
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional

import structlog

from .base_strategy import ApplicationStrategy, PYAUTOGUI_AVAILABLE
from .detector import ApplicationInfo
from .timing_config import TimingConfig

if PYAUTOGUI_AVAILABLE:
    import pyautogui

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    gw = None
    PYGETWINDOW_AVAILABLE = False

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
        if not PYGETWINDOW_AVAILABLE:
            return False
            
        try:
            windows = [w for w in gw.getAllWindows()
                      if "gimp" in w.title.lower()]
            
            if not windows:
                return False
            
            target = windows[0]
            if not target.isActive:
                try:
                    target.activate()
                except Exception:
                    pass
                await asyncio.sleep(TimingConfig.WINDOW_ACTIVATE)
            
            self.canvas_center = (
                target.left + target.width // 2,
                target.top + target.height // 2
            )
            
            logger.info("gimp_focused", title=target.title)
            return True
            
        except Exception as e:
            logger.error("gimp_focus_failed", error=str(e))
            return False
    
    async def select_tool(self, tool_name: str) -> bool:
        """Select GIMP tool."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        tool_lower = tool_name.lower()
        if tool_lower in self.TOOL_SHORTCUTS:
            shortcut = self.TOOL_SHORTCUTS[tool_lower]
            if '+' in shortcut:
                keys = shortcut.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(shortcut)
            await asyncio.sleep(TimingConfig.TOOL_SELECT)
            return True
        
        return False
    
    async def prepare_canvas(self) -> bool:
        """Prepare GIMP canvas."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.click(self.canvas_center[0], self.canvas_center[1], _pause=False)
        await asyncio.sleep(TimingConfig.CANVAS_CLICK)
        return True
    
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get GIMP tool shortcuts."""
        return self.TOOL_SHORTCUTS
    
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Create layer in GIMP."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.hotkey('ctrl', 'shift', 'n')
        await asyncio.sleep(TimingConfig.LAYER_CREATE)
        
        if name:
            pyautogui.write(name, interval=0.05)
            pyautogui.press('enter')
        
        await asyncio.sleep(TimingConfig.TYPE_FINISH)
        logger.info("gimp_layer_created", name=name)
        return True
    
    async def save_file(self, path: str) -> bool:
        """Save GIMP file."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        # Ctrl+Shift+E (Export As)
        pyautogui.hotkey('ctrl', 'shift', 'e')
        await asyncio.sleep(TimingConfig.FILE_SAVE)
        
        pyautogui.write(str(path), interval=0.05)
        pyautogui.press('enter')
        
        await asyncio.sleep(1.0)
        logger.info("gimp_file_saved", path=path)
        return True
