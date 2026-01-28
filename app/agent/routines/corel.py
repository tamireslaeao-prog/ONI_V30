"""
ONI v5.0 - CorelDRAW Routines
Keyboard shortcuts and automation routines for CorelDRAW.
"""

from typing import Any

import structlog

from .base import RoutinesBase

logger = structlog.get_logger(__name__)


class CorelRoutines(RoutinesBase):
    """CorelDRAW-specific routines: tools, objects, fills, alignment, nodes."""
    
    # =========================================================================
    # BASIC TOOLS
    # =========================================================================
    
    async def pick_tool(self) -> bool:
        """Pick/Selection tool (V)."""
        return await self.press_keys("v")
    
    async def rectangle(self) -> bool:
        """Rectangle tool (F6)."""
        return await self.press_keys("F6")
    
    async def ellipse(self) -> bool:
        """Ellipse/Circle tool (F7)."""
        return await self.press_keys("F7")
    
    async def polygon(self) -> bool:
        """Polygon tool (Y)."""
        return await self.press_keys("y")
    
    async def star(self) -> bool:
        """Star tool (A)."""
        return await self.press_keys("a")
    
    async def text(self) -> bool:
        """Text tool (F8)."""
        return await self.press_keys("F8")
    
    async def shape_tool(self) -> bool:
        """Shape/Node editing tool (F10)."""
        return await self.press_keys("F10")
    
    async def bezier(self) -> bool:
        """Bézier tool (F5)."""
        return await self.press_keys("F5")
    
    async def freehand(self) -> bool:
        """Freehand tool (F5)."""
        return await self.press_keys("F5")
    
    # =========================================================================
    # OBJECT OPERATIONS
    # =========================================================================
    
    async def convert_curves(self) -> bool:
        """Convert to curves (Ctrl+Q)."""
        return await self.press_keys("ctrl", "q")
    
    async def group(self) -> bool:
        """Group objects (Ctrl+G)."""
        return await self.press_keys("ctrl", "g")
    
    async def ungroup(self) -> bool:
        """Ungroup objects (Ctrl+U)."""
        return await self.press_keys("ctrl", "u")
    
    async def duplicate(self) -> bool:
        """Duplicate (Ctrl+D)."""
        return await self.press_keys("ctrl", "d")
    
    async def clone(self) -> bool:
        """Clone (Ctrl+Shift+D)."""
        return await self.press_keys("ctrl", "shift", "d")
    
    async def combine(self) -> bool:
        """Combine/Weld (Ctrl+L)."""
        return await self.press_keys("ctrl", "l")
    
    async def break_apart(self) -> bool:
        """Break apart (Ctrl+K)."""
        return await self.press_keys("ctrl", "k")
    
    async def lock(self) -> bool:
        """Lock object."""
        return await self.press_keys("ctrl", "l")
    
    async def unlock(self) -> bool:
        """Unlock object."""
        return await self.press_keys("ctrl", "u")
    
    async def outline_to_object(self) -> bool:
        """Convert outline to object (Ctrl+Shift+Q)."""
        return await self.press_keys("ctrl", "shift", "q")
    
    # =========================================================================
    # FILL & OUTLINE
    # =========================================================================
    
    async def fill_uniform(self) -> bool:
        """Uniform fill dialog (Shift+F11)."""
        return await self.press_keys("shift", "F11")
    
    async def fill_gradient(self) -> bool:
        """Gradient fill dialog (F11)."""
        return await self.press_keys("F11")
    
    async def fill_interactive(self) -> bool:
        """Interactive fill tool (G)."""
        return await self.press_keys("g")
    
    async def outline(self) -> bool:
        """Outline dialog (F12)."""
        return await self.press_keys("F12")
    
    async def copy_properties(self) -> bool:
        """Copy properties (Ctrl+Shift+A)."""
        return await self.press_keys("ctrl", "shift", "a")
    
    # =========================================================================
    # ORDER & ALIGNMENT
    # =========================================================================
    
    async def bring_front(self) -> bool:
        """Bring forward (Ctrl+PageUp)."""
        return await self.press_keys("ctrl", "pageup")
    
    async def send_back(self) -> bool:
        """Send backward (Ctrl+PageDown)."""
        return await self.press_keys("ctrl", "pagedown")
    
    async def bring_front_all(self) -> bool:
        """Bring to front (Shift+PageUp)."""
        return await self.press_keys("shift", "pageup")
    
    async def send_back_all(self) -> bool:
        """Send to back (Shift+PageDown)."""
        return await self.press_keys("shift", "pagedown")
    
    async def align_left(self) -> bool:
        """Align left (L)."""
        return await self.press_keys("l")
    
    async def align_right(self) -> bool:
        """Align right (R)."""
        return await self.press_keys("r")
    
    async def align_top(self) -> bool:
        """Align top (T)."""
        return await self.press_keys("t")
    
    async def align_bottom(self) -> bool:
        """Align bottom (B)."""
        return await self.press_keys("b")
    
    async def align_center_h(self) -> bool:
        """Align center horizontal (E)."""
        return await self.press_keys("e")
    
    async def align_center_v(self) -> bool:
        """Align center vertical (C)."""
        return await self.press_keys("c")
    
    async def distribute_h(self) -> bool:
        """Distribute horizontally (Shift+P)."""
        return await self.press_keys("shift", "p")
    
    async def distribute_v(self) -> bool:
        """Distribute vertically (Shift+A)."""
        return await self.press_keys("shift", "a")
    
    # =========================================================================
    # NODE EDITING
    # =========================================================================
    
    async def node_cusp(self) -> bool:
        """Cusp node (C)."""
        return await self.press_keys("c")
    
    async def node_smooth(self) -> bool:
        """Smooth node (S)."""
        return await self.press_keys("s")
    
    async def node_symmetric(self) -> bool:
        """Symmetric node (Y)."""
        return await self.press_keys("y")
    
    async def node_join(self) -> bool:
        """Join nodes (J)."""
        return await self.press_keys("j")
    
    async def node_break(self) -> bool:
        """Break curve at node (B)."""
        return await self.press_keys("b")
    
    # =========================================================================
    # ZOOM & VIEW
    # =========================================================================
    
    async def fit_page(self) -> bool:
        """Fit page in window (Shift+F4)."""
        return await self.press_keys("shift", "F4")
    
    async def zoom_100(self) -> bool:
        """Zoom 100% (F2)."""
        return await self.press_keys("F2")
    
    async def zoom_selected(self) -> bool:
        """Zoom to selection (Shift+F2)."""
        return await self.press_keys("shift", "F2")
    
    async def zoom_all(self) -> bool:
        """Zoom to all objects (F4)."""
        return await self.press_keys("F4")
    
    # =========================================================================
    # EFFECTS
    # =========================================================================
    
    async def envelope(self) -> bool:
        """Envelope (Ctrl+F7)."""
        return await self.press_keys("ctrl", "F7")
    
    async def blend(self) -> bool:
        """Blend tool (B)."""
        return await self.press_keys("b")
    
    async def export(self) -> bool:
        """Export (Ctrl+E)."""
        return await self.press_keys("ctrl", "e")
    
    async def import_file(self) -> bool:
        """Import (Ctrl+I)."""
        return await self.press_keys("ctrl", "i")
