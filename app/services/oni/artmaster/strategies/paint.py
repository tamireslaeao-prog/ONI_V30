"""
ONI ArtMaster - Paint Strategy
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


class PaintStrategy(ApplicationStrategy):
    """Strategy for MS Paint."""
    
    TOOL_SHORTCUTS = {
        "pencil": "ctrl+p",
        "brush": "ctrl+b",
        "fill": "ctrl+f",
        "text": "ctrl+t",
        "eraser": "ctrl+e",
        "color_picker": "ctrl+k",
        "magnifier": "ctrl+m",
    }
    
    async def ensure_focus(self) -> bool:
        """Focus Paint window."""
        if not gw: return False
        
        try:
            windows = gw.getWindowsWithTitle("Paint")
            if not windows:
                windows = [w for w in gw.getAllWindows()
                          if any(kw in w.title.lower() 
                                for kw in ["paint", "pintura", "untitled"])]
            
            if not windows:
                return False
            
            target = windows[0]
            if not target.isActive:
                try:
                    target.activate()
                except Exception:
                    pass
                await asyncio.sleep(0.5)
            
            self.canvas_center = (
                target.left + target.width // 2,
                target.top + target.height // 2
            )
            
            logger.info("paint_focused", title=target.title)
            return True
            
        except Exception as e:
            logger.error("paint_focus_failed", error=str(e))
            return False
    
    @mandatory_vision_check
    async def select_tool(self, tool_name: str) -> bool:
        """Select Paint tool."""
        if not pyautogui: return False
        
        tool_lower = tool_name.lower()
        if tool_lower in self.TOOL_SHORTCUTS:
            shortcut = self.TOOL_SHORTCUTS[tool_lower]
            keys = shortcut.split('+')
            pyautogui.hotkey(*keys)
            await asyncio.sleep(0.1)
            return True
        
        return False
    
    async def prepare_canvas(self) -> bool:
        """Prepare Paint canvas."""
        if not pyautogui: return False
        
        pyautogui.click(self.canvas_center[0], self.canvas_center[1], _pause=False)
        await asyncio.sleep(0.2)
        
        return True
    
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get Paint tool shortcuts."""
        return self.TOOL_SHORTCUTS
    
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Paint doesn't support layers."""
        logger.warning("paint_no_layers")
        return False
    
    @mandatory_vision_check
    async def save_file(self, path: str) -> bool:
        """Save Paint file."""
        if not pyautogui: return False
        
        pyautogui.hotkey('ctrl', 's')
        await asyncio.sleep(0.3)
        
        if not Path(path).exists():
            pyautogui.write(str(path), interval=0.05)
            pyautogui.press('enter')
        
        await asyncio.sleep(0.5)
        return True
