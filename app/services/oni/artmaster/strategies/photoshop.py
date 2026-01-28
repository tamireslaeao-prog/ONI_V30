"""
ONI ArtMaster - Photoshop Strategy
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


class PhotoshopStrategy(ApplicationStrategy):
    """Strategy for Adobe Photoshop."""
    
    TOOL_SHORTCUTS = {
        # Selection tools
        "move": "v",
        "artboard": "v",
        "rectangular_marquee": "m",
        "elliptical_marquee": "m",
        "lasso": "l",
        "polygonal_lasso": "l",
        "magnetic_lasso": "l",
        "quick_selection": "w",
        "magic_wand": "w",
        
        # Crop & Slice
        "crop": "c",
        "slice": "c",
        "slice_select": "c",
        
        # Eyedropper & Measure
        "eyedropper": "i",
        "3d_material_eyedropper": "i",
        "color_sampler": "i",
        "ruler": "i",
        "note": "i",
        
        # Retouching
        "spot_healing_brush": "j",
        "healing_brush": "j",
        "patch": "j",
        "content_aware_move": "j",
        "red_eye": "j",
        
        # Painting
        "brush": "b",
        "pencil": "b",
        "color_replacement": "b",
        "mixer_brush": "b",
        "clone_stamp": "s",
        "pattern_stamp": "s",
        "history_brush": "y",
        "art_history": "y",
        
        # Eraser
        "eraser": "e",
        "background_eraser": "e",
        "magic_eraser": "e",
        
        # Paint & Fill
        "gradient": "g",
        "paint_bucket": "g",
        "3d_material_drop": "g",
        
        # Drawing & Type
        "blur": "r",
        "sharpen": "r",
        "smudge": "r",
        "dodge": "o",
        "burn": "o",
        "sponge": "o",
        "pen": "p",
        "freeform_pen": "p",
        "add_anchor": "p",
        "delete_anchor": "p",
        "convert_point": "p",
        "text": "t",
        "vertical_text": "t",
        
        # Shape tools
        "rectangle": "u",
        "rounded_rectangle": "u",
        "ellipse": "u",
        "polygon": "u",
        "line": "u",
        "custom_shape": "u",
        
        # Path Selection
        "path_selection": "a",
        "direct_selection": "a",
        
        # 3D & Navigation
        "rotate_view": "r",
        "hand": "h",
        "rotate": "r",
        "zoom": "z",
        
        # Colors
        "default_colors": "d",
        "swap_colors": "x",
        "deselect": "ctrl+d",
        "reselect": "ctrl+shift+d",
        "merge_layers": "ctrl+e",
        "transform": "ctrl+t",
    }
    
    async def ensure_focus(self) -> bool:
        """Focus Photoshop window."""
        if not gw:
            return False
            
        try:
            windows = gw.getWindowsWithTitle("Photoshop")
            if not windows:
                # Try alternative patterns
                windows = [w for w in gw.getAllWindows() 
                          if any(kw in w.title.lower() 
                                for kw in ["photoshop", "ps cc", "adobe ps", " @ ", "(rgb/", "(cmyk/"])]
            
            if not windows:
                return False
            
            target = windows[0]
            if not target.isActive:
                try:
                    target.activate()
                except Exception:
                    pass
                await asyncio.sleep(0.5)
            
            # Update canvas center
            self.canvas_center = (
                target.left + target.width // 2,
                target.top + target.height // 2
            )
            
            logger.info("photoshop_focused", title=target.title)
            return True
            
        except Exception as e:
            logger.error("photoshop_focus_failed", error=str(e))
            return False
    
    @mandatory_vision_check
    async def select_tool(self, tool_name: str) -> bool:
        """Select Photoshop tool."""
        if not pyautogui: return False
        
        tool_lower = tool_name.lower()
        if tool_lower in self.TOOL_SHORTCUTS:
            shortcut = self.TOOL_SHORTCUTS[tool_lower]
            
            # Handle combinations like 'ctrl+d' or 'shift+b'
            if '+' in shortcut:
                keys = shortcut.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(shortcut)
                
            await asyncio.sleep(0.1)
            logger.info("photoshop_tool_selected", tool=tool_name, key=shortcut)
            return True
        
        logger.warning("photoshop_tool_unknown", tool=tool_name)
        return False
    
    async def prepare_canvas(self) -> bool:
        """Prepare Photoshop canvas."""
        if not pyautogui: return False
        
        # Click canvas center to ensure focus
        pyautogui.click(self.canvas_center[0], self.canvas_center[1], _pause=False)
        await asyncio.sleep(0.2)
        
        # Select brush tool by default
        await self.select_tool("brush")
        
        return True
    
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get Photoshop tool shortcuts."""
        return self.TOOL_SHORTCUTS
    
    @mandatory_vision_check
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Create new layer in Photoshop."""
        if not pyautogui: return False
        
        # Ctrl+Shift+N (New Layer)
        pyautogui.hotkey('ctrl', 'shift', 'n')
        await asyncio.sleep(0.3)
        
        if name:
            # Type layer name
            pyautogui.write(name, interval=0.05)
            await asyncio.sleep(0.1)
        
        # Press Enter to confirm
        pyautogui.press('enter')
        await asyncio.sleep(0.2)
        
        logger.info("photoshop_layer_created", name=name)
        return True
    
    @mandatory_vision_check
    async def save_file(self, path: str) -> bool:
        """Save Photoshop file."""
        if not pyautogui: return False
        
        # Ctrl+S (Save) or Ctrl+Shift+S (Save As)
        if Path(path).exists():
            pyautogui.hotkey('ctrl', 's')
        else:
            pyautogui.hotkey('ctrl', 'shift', 's')
            await asyncio.sleep(0.5)
            
            # Type path
            pyautogui.write(str(path), interval=0.05)
            await asyncio.sleep(0.2)
            pyautogui.press('enter')
        
        await asyncio.sleep(0.5)
        logger.info("photoshop_file_saved", path=path)
        return True

    async def set_opacity(self, opacity: int) -> bool:
        """Set brush opacity (10-100%). Maps to keys '1'-'0'."""
        if not pyautogui: return False
        
        # Normalize opacity to 10-100 range
        opacity = max(10, min(100, opacity))
        
        # Convert to key: 10->'1', ... 100->'0'
        val = int(round(opacity / 10.0))
        if val == 0: val = 1
        key = str(val) if val < 10 else '0'
        
        pyautogui.press(key)
        await asyncio.sleep(0.1)
        return True

    async def set_flow(self, flow: int) -> bool:
        """Set brush flow (10-100%). Maps to Shift + '1'-'0'."""
        if not pyautogui: return False

        flow = max(10, min(100, flow))
        val = int(round(flow / 10.0))
        if val == 0: val = 1
        key = str(val) if val < 10 else '0'
        
        pyautogui.hotkey('shift', key)
        await asyncio.sleep(0.1)
        return True
