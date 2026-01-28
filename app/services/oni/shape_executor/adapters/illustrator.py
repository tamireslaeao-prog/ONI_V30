"""
ONI Shape Executor - Illustrator Adapter
"""
import asyncio
from ..base import AppAdapter
from ..types import ShapeType, ShapeCommand

class IllustratorAdapter(AppAdapter):
    """Adapter para Adobe Illustrator."""
    
    app_name = "illustrator.exe"
    
    TOOL_HOTKEYS = {
        ShapeType.CIRCLE: "l",
        ShapeType.ELLIPSE: "l",
        ShapeType.RECTANGLE: "m",
        ShapeType.SQUARE: "m",
        ShapeType.LINE: "\\",
        ShapeType.POLYGON: "p",
    }
    
    async def select_tool(self, shape_type: ShapeType) -> bool:
        if not self.actuation: return False
        try:
            if shape_type in self.TOOL_HOTKEYS:
                hotkey = self.TOOL_HOTKEYS[shape_type]
                await self.actuation.keyboard.press_key(hotkey)
                await asyncio.sleep(0.2)
                return True
            return False
        except:
            return False
    
    async def draw_shape(self, command: ShapeCommand) -> bool:
        if not self.actuation: return False
        try:
            params = command.params
            
            if command.shape_type in [ShapeType.CIRCLE, ShapeType.ELLIPSE]:
                cx = params.get("center_x", 0)
                cy = params.get("center_y", 0)
                radius = params.get("radius", 50)
                
                x1, y1 = cx - radius, cy - radius
                x2, y2 = cx + radius, cy + radius
                
                if command.shape_type == ShapeType.CIRCLE:
                    await self.actuation.keyboard.key_down('shift')
                
                await self.actuation.mouse.drag(x1, y1, x2, y2, duration=0.3)
                
                if command.shape_type == ShapeType.CIRCLE:
                    await self.actuation.keyboard.key_up('shift')
                    
            return True
        except:
            return False
    
    async def set_fill_color(self, hex_color: str) -> bool:
        return True
