"""
ONI Shape Executor - CorelDRAW Adapter
"""
import asyncio
import structlog
from ..base import AppAdapter
from ..types import ShapeType, ShapeCommand

logger = structlog.get_logger(__name__)

class CorelDRAWAdapter(AppAdapter):
    """Adapter para CorelDRAW."""
    
    app_name = "CorelDRW.exe"
    
    TOOL_HOTKEYS = {
        ShapeType.CIRCLE: "F7",
        ShapeType.ELLIPSE: "F7",
        ShapeType.RECTANGLE: "F6",
        ShapeType.SQUARE: "F6",
        ShapeType.LINE: "F5",
        ShapeType.POLYGON: "Y",
        ShapeType.BEZIER: "F5",
    }
    
    async def select_tool(self, shape_type: ShapeType) -> bool:
        """Seleciona ferramenta no CorelDRAW."""
        if not self.actuation: return False
        try:
            if shape_type in self.TOOL_HOTKEYS:
                hotkey = self.TOOL_HOTKEYS[shape_type]
                await self.actuation.keyboard.press_key(hotkey)
                await asyncio.sleep(0.2)
                logger.info("corel_tool_selected", shape=shape_type.value, hotkey=hotkey)
                return True
            return False
        except Exception as e:
            logger.error("corel_select_tool_failed", error=str(e))
            return False
    
    async def draw_shape(self, command: ShapeCommand) -> bool:
        """Desenha forma no CorelDRAW."""
        if not self.actuation: return False
        try:
            params = command.params
            
            if command.shape_type in [ShapeType.CIRCLE, ShapeType.ELLIPSE]:
                cx = params.get("center_x", 0)
                cy = params.get("center_y", 0)
                
                if command.shape_type == ShapeType.CIRCLE:
                    radius = params.get("radius", 50)
                    x1, y1 = cx - radius, cy - radius
                    x2, y2 = cx + radius, cy + radius
                    # Ctrl+Drag para círculo perfeito no Corel
                    await self.actuation.keyboard.key_down('ctrl')
                else:
                    w = params.get("width", 100)
                    h = params.get("height", 50)
                    x1, y1 = cx - w//2, cy - h//2
                    x2, y2 = cx + w//2, cy + h//2
                
                await self.actuation.mouse.drag(x1, y1, x2, y2, duration=0.3)
                
                if command.shape_type == ShapeType.CIRCLE:
                    await self.actuation.keyboard.key_up('ctrl')
                    
            elif command.shape_type in [ShapeType.RECTANGLE, ShapeType.SQUARE]:
                x = params.get("x", 0)
                y = params.get("y", 0)
                w = params.get("width", 100)
                h = params.get("height", 100)
                x2 = x + w
                y2 = y + h
                
                if command.shape_type == ShapeType.SQUARE:
                    await self.actuation.keyboard.key_down('ctrl')
                
                await self.actuation.mouse.drag(x, y, x2, y2, duration=0.3)
                
                if command.shape_type == ShapeType.SQUARE:
                    await self.actuation.keyboard.key_up('ctrl')
                    
            elif command.shape_type == ShapeType.LINE:
                x1, y1 = params.get("x1", 0), params.get("y1", 0)
                x2, y2 = params.get("x2", 0), params.get("y2", 0)
                
                await self.actuation.mouse.click(x1, y1)
                await asyncio.sleep(0.1)
                await self.actuation.mouse.click(x2, y2)
                await asyncio.sleep(0.1)
                await self.actuation.keyboard.press_key('space')  # Finalizar linha
            
            logger.info("corel_shape_drawn", shape=command.shape_type.value)
            return True
            
        except Exception as e:
            logger.error("corel_draw_shape_failed", error=str(e))
            return False
    
    async def set_fill_color(self, hex_color: str) -> bool:
        """Define cor no CorelDRAW."""
        return True
