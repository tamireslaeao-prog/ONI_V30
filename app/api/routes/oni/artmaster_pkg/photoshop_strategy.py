"""
ONI ArtMaster - Photoshop Strategy
Adobe Photoshop-specific automation strategy.
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
        "eyedropper": "i",
        "color_sampler": "i",
        
        # Retouching
        "spot_healing": "j",
        "healing_brush": "j",
        "patch": "j",
        "red_eye": "j",
        "brush": "b",
        "pencil": "b",
        "color_replacement": "b",
        "mixer_brush": "b",
        
        # Clone & History
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
        if not PYGETWINDOW_AVAILABLE:
            return False
            
        try:
            windows = gw.getWindowsWithTitle("Photoshop")
            if not windows:
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
                await asyncio.sleep(TimingConfig.WINDOW_ACTIVATE)
            
            self.canvas_center = (
                target.left + target.width // 2,
                target.top + target.height // 2
            )
            
            logger.info("photoshop_focused", title=target.title)
            return True
            
        except Exception as e:
            logger.error("photoshop_focus_failed", error=str(e))
            return False
    
    async def select_tool(self, tool_name: str) -> bool:
        """Select Photoshop tool."""
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
            logger.info("photoshop_tool_selected", tool=tool_name, key=shortcut)
            return True
        
        logger.warning("photoshop_tool_unknown", tool=tool_name)
        return False
    
    async def prepare_canvas(self) -> bool:
        """Prepare Photoshop canvas."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.click(self.canvas_center[0], self.canvas_center[1], _pause=False)
        await asyncio.sleep(TimingConfig.CANVAS_CLICK)
        await self.select_tool("brush")
        return True
    
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get Photoshop tool shortcuts."""
        return self.TOOL_SHORTCUTS
    
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Create new layer in Photoshop."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.hotkey('ctrl', 'shift', 'n')
        await asyncio.sleep(TimingConfig.LAYER_CREATE)
        
        if name:
            pyautogui.write(name, interval=0.05)
            await asyncio.sleep(TimingConfig.TYPE_CHAR)
        
        pyautogui.press('enter')
        await asyncio.sleep(TimingConfig.TYPE_FINISH)
        
        logger.info("photoshop_layer_created", name=name)
        return True
    
    async def save_file(self, path: str) -> bool:
        """Save Photoshop file."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        if Path(path).exists():
            pyautogui.hotkey('ctrl', 's')
        else:
            pyautogui.hotkey('ctrl', 'shift', 's')
            await asyncio.sleep(TimingConfig.UI_SETTLE)
            pyautogui.write(str(path), interval=0.05)
            await asyncio.sleep(0.2)
            pyautogui.press('enter')
        
        await asyncio.sleep(TimingConfig.FILE_SAVE)
        logger.info("photoshop_file_saved", path=path)
        return True
    
    async def set_opacity(self, opacity: int) -> bool:
        """Set brush opacity (10-100%)."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        opacity = max(10, min(100, opacity))
        val = int(round(opacity / 10.0))
        if val == 0: val = 1
        key = str(val) if val < 10 else '0'
        
        pyautogui.press(key)
        await asyncio.sleep(TimingConfig.UI_INSTANT)
        logger.info("photoshop_opacity_set", value=opacity, key=key)
        return True
    
    async def set_flow(self, flow: int) -> bool:
        """Set brush flow (10-100%)."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        flow = max(10, min(100, flow))
        val = int(round(flow / 10.0))
        if val == 0: val = 1
        key = str(val) if val < 10 else '0'
        
        pyautogui.hotkey('shift', key)
        await asyncio.sleep(TimingConfig.UI_INSTANT)
        logger.info("photoshop_flow_set", value=flow, key=f"shift+{key}")
        return True
    
    async def deselect(self) -> bool:
        """Deselect active selection (Ctrl+D)."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.hotkey('ctrl', 'd')
        await asyncio.sleep(TimingConfig.UI_INSTANT)
        logger.info("photoshop_deselect_executed")
        return True
    
    async def merge_layers(self) -> bool:
        """Merge selected layers (Ctrl+E)."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.hotkey('ctrl', 'e')
        await asyncio.sleep(TimingConfig.LAYER_MERGE)
        logger.info("photoshop_layers_merged")
        return True
    
    async def transform_layer(self) -> bool:
        """Free Transform (Ctrl+T)."""
        if not PYAUTOGUI_AVAILABLE:
            return False
            
        pyautogui.hotkey('ctrl', 't')
        await asyncio.sleep(TimingConfig.UI_QUICK)
        logger.info("photoshop_transform_activated")
        return True
