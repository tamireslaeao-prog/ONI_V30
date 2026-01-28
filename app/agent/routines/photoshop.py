"""
ONI v5.0 - Photoshop Routines
Keyboard shortcuts and automation routines for Adobe Photoshop.
"""

from typing import Any

import structlog

from .base import RoutinesBase

logger = structlog.get_logger(__name__)


class PhotoshopRoutines(RoutinesBase):
    """Photoshop-specific routines: tools, layers, selection, transform."""
    
    # =========================================================================
    # BASIC TOOLS
    # =========================================================================
    
    async def move_tool(self) -> bool:
        """Move tool (V)."""
        return await self.press_keys("v")
    
    async def marquee(self) -> bool:
        """Rectangular Marquee (M)."""
        return await self.press_keys("m")
    
    async def lasso(self) -> bool:
        """Lasso (L)."""
        return await self.press_keys("l")
    
    async def magic_wand(self) -> bool:
        """Magic Wand (W)."""
        return await self.press_keys("w")
    
    async def quick_selection(self) -> bool:
        """Quick Selection (W)."""
        return await self.press_keys("w")
    
    async def crop(self) -> bool:
        """Crop (C)."""
        return await self.press_keys("c")
    
    async def eyedropper(self) -> bool:
        """Eyedropper (I)."""
        return await self.press_keys("i")
    
    async def brush(self) -> bool:
        """Brush (B)."""
        return await self.press_keys("b")
    
    async def pencil(self) -> bool:
        """Pencil (B, cycle)."""
        return await self.press_keys("b")
    
    async def eraser(self) -> bool:
        """Eraser (E)."""
        return await self.press_keys("e")
    
    async def gradient(self) -> bool:
        """Gradient (G)."""
        return await self.press_keys("g")
    
    async def paint_bucket(self) -> bool:
        """Paint Bucket (G, cycle)."""
        return await self.press_keys("g")
    
    async def clone_stamp(self) -> bool:
        """Clone Stamp (S)."""
        return await self.press_keys("s")
    
    async def healing_brush(self) -> bool:
        """Healing Brush (J)."""
        return await self.press_keys("j")
    
    async def spot_healing(self) -> bool:
        """Spot Healing (J)."""
        return await self.press_keys("j")
    
    async def text(self) -> bool:
        """Text (T)."""
        return await self.press_keys("t")
    
    async def pen(self) -> bool:
        """Pen (P)."""
        return await self.press_keys("p")
    
    async def shape(self) -> bool:
        """Shape (U)."""
        return await self.press_keys("u")
    
    async def hand(self) -> bool:
        """Hand (H)."""
        return await self.press_keys("h")
    
    async def zoom(self) -> bool:
        """Zoom (Z)."""
        return await self.press_keys("z")
    
    async def dodge(self) -> bool:
        """Dodge (O)."""
        return await self.press_keys("o")
    
    async def burn(self) -> bool:
        """Burn (O, cycle)."""
        return await self.press_keys("o")
    
    async def sponge(self) -> bool:
        """Sponge (O, cycle)."""
        return await self.press_keys("o")
    
    # =========================================================================
    # BRUSH ADJUSTMENTS
    # =========================================================================
    
    async def brush_bigger(self) -> bool:
        """Increase brush size (])."""
        return await self.press_keys("]")
    
    async def brush_smaller(self) -> bool:
        """Decrease brush size ([)."""
        return await self.press_keys("[")
    
    async def brush_harder(self) -> bool:
        """Increase brush hardness (Shift+])."""
        return await self.press_keys("shift", "]")
    
    async def brush_softer(self) -> bool:
        """Decrease brush hardness (Shift+[)."""
        return await self.press_keys("shift", "[")
    
    # =========================================================================
    # LAYERS
    # =========================================================================
    
    async def new_layer(self) -> bool:
        """New layer (Ctrl+Shift+N)."""
        return await self.press_keys("ctrl", "shift", "n")
    
    async def duplicate_layer(self) -> bool:
        """Duplicate layer (Ctrl+J)."""
        return await self.press_keys("ctrl", "j")
    
    async def layer_via_copy(self) -> bool:
        """Layer via copy (Ctrl+J)."""
        return await self.press_keys("ctrl", "j")
    
    async def layer_via_cut(self) -> bool:
        """Layer via cut (Ctrl+Shift+J)."""
        return await self.press_keys("ctrl", "shift", "j")
    
    async def merge_down(self) -> bool:
        """Merge down (Ctrl+E)."""
        return await self.press_keys("ctrl", "e")
    
    async def merge_visible(self) -> bool:
        """Merge visible (Ctrl+Shift+E)."""
        return await self.press_keys("ctrl", "shift", "e")
    
    async def stamp_visible(self) -> bool:
        """Stamp visible (Ctrl+Alt+Shift+E)."""
        return await self.press_keys("ctrl", "alt", "shift", "e")
    
    async def select_all_layers(self) -> bool:
        """Select all layers (Ctrl+Alt+A)."""
        return await self.press_keys("ctrl", "alt", "a")
    
    async def lock_transparency(self) -> bool:
        """Lock transparency (/)."""
        return await self.press_keys("/")
    
    # =========================================================================
    # SELECTION
    # =========================================================================
    
    async def deselect(self) -> bool:
        """Deselect (Ctrl+D)."""
        return await self.press_keys("ctrl", "d")
    
    async def reselect(self) -> bool:
        """Reselect (Ctrl+Shift+D)."""
        return await self.press_keys("ctrl", "shift", "d")
    
    async def invert_selection(self) -> bool:
        """Invert selection (Ctrl+Shift+I)."""
        return await self.press_keys("ctrl", "shift", "i")
    
    async def feather(self) -> bool:
        """Feather (Shift+F6)."""
        return await self.press_keys("shift", "F6")
    
    async def select_and_mask(self) -> bool:
        """Select and Mask (Ctrl+Alt+R)."""
        return await self.press_keys("ctrl", "alt", "r")
    
    # =========================================================================
    # TRANSFORM
    # =========================================================================
    
    async def free_transform(self) -> bool:
        """Free Transform (Ctrl+T)."""
        return await self.press_keys("ctrl", "t")
    
    async def scale(self) -> bool:
        """Scale (use Free Transform)."""
        return await self.press_keys("ctrl", "t")
    
    async def rotate(self) -> bool:
        """Rotate (use Free Transform)."""
        return await self.press_keys("ctrl", "t")
    
    async def flip_horizontal(self) -> bool:
        """Flip horizontal (menu action)."""
        # Note: No direct shortcut, use menu
        return False
    
    async def flip_vertical(self) -> bool:
        """Flip vertical (menu action)."""
        # Note: No direct shortcut, use menu
        return False
    
    # =========================================================================
    # COLOR
    # =========================================================================
    
    async def default_colors(self) -> bool:
        """Default foreground/background (D)."""
        return await self.press_keys("d")
    
    async def swap_colors(self) -> bool:
        """Swap foreground/background (X)."""
        return await self.press_keys("x")
    
    async def fill_foreground(self) -> bool:
        """Fill with foreground (Alt+Backspace)."""
        return await self.press_keys("alt", "backspace")
    
    async def fill_background(self) -> bool:
        """Fill with background (Ctrl+Backspace)."""
        return await self.press_keys("ctrl", "backspace")
    
    # =========================================================================
    # IMAGE ADJUSTMENTS
    # =========================================================================
    
    async def levels(self) -> bool:
        """Levels (Ctrl+L)."""
        return await self.press_keys("ctrl", "l")
    
    async def curves(self) -> bool:
        """Curves (Ctrl+M)."""
        return await self.press_keys("ctrl", "m")
    
    async def hue_saturation(self) -> bool:
        """Hue/Saturation (Ctrl+U)."""
        return await self.press_keys("ctrl", "u")
    
    async def color_balance(self) -> bool:
        """Color Balance (Ctrl+B)."""
        return await self.press_keys("ctrl", "b")
    
    async def desaturate(self) -> bool:
        """Desaturate (Ctrl+Shift+U)."""
        return await self.press_keys("ctrl", "shift", "u")
    
    async def invert(self) -> bool:
        """Invert (Ctrl+I)."""
        return await self.press_keys("ctrl", "i")
    
    # =========================================================================
    # VIEW
    # =========================================================================
    
    async def fit_screen(self) -> bool:
        """Fit on screen (Ctrl+0)."""
        return await self.press_keys("ctrl", "0")
    
    async def actual_pixels(self) -> bool:
        """Actual pixels/100% (Ctrl+Alt+0)."""
        return await self.press_keys("ctrl", "alt", "0")
    
    async def zoom_in(self) -> bool:
        """Zoom in (Ctrl++)."""
        return await self.press_keys("ctrl", "plus")
    
    async def zoom_out(self) -> bool:
        """Zoom out (Ctrl+-)."""
        return await self.press_keys("ctrl", "minus")
    
    async def toggle_rulers(self) -> bool:
        """Toggle rulers (Ctrl+R)."""
        return await self.press_keys("ctrl", "r")
    
    async def toggle_guides(self) -> bool:
        """Toggle guides (Ctrl+;)."""
        return await self.press_keys("ctrl", ";")
    
    async def toggle_grid(self) -> bool:
        """Toggle grid (Ctrl+')."""
        return await self.press_keys("ctrl", "'")
    
    # =========================================================================
    # FILTER
    # =========================================================================
    
    async def last_filter(self) -> bool:
        """Repeat last filter (Ctrl+F)."""
        return await self.press_keys("ctrl", "f")
    
    async def fade(self) -> bool:
        """Fade last filter (Ctrl+Shift+F)."""
        return await self.press_keys("ctrl", "shift", "f")
