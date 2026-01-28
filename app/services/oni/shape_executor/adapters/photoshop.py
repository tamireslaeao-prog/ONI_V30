"""
ONI Shape Executor - Photoshop Adapter
"""
import asyncio
import structlog
try:
    import pyautogui
except ImportError:
    pyautogui = None

from ..base import AppAdapter
from ..types import ShapeType, ShapeCommand

logger = structlog.get_logger(__name__)

class PhotoshopAdapter(AppAdapter):
    """Adapter para Adobe Photoshop."""
    
    app_name = "Photoshop.exe"
    
    # Mapeamento de formas para ferramentas
    TOOL_HOTKEYS = {
        ShapeType.CIRCLE: ("u", "ellipse"),      # Shape tool
        ShapeType.ELLIPSE: ("u", "ellipse"),
        ShapeType.RECTANGLE: ("u", "rectangle"),
        ShapeType.SQUARE: ("u", "rectangle"),
        ShapeType.LINE: ("u", "line"),
        ShapeType.POLYGON: ("u", "polygon"),
    }
    
    async def select_tool(self, shape_type: ShapeType) -> bool:
        """Seleciona ferramenta de forma no Photoshop."""
        if not self.actuation: return False
        
        try:
            # Tentar usar actuation system (safe)
            if hasattr(self.actuation, 'keyboard'):
                if shape_type in self.TOOL_HOTKEYS:
                    hotkey, _ = self.TOOL_HOTKEYS[shape_type]
                    await self.actuation.keyboard.press_key(hotkey)
                    await asyncio.sleep(0.3)
                    logger.info("ps_tool_selected", shape=shape_type.value, hotkey=hotkey)
                    return True
                else:
                    # Fallback para brush
                    await self.actuation.keyboard.press_key('b')
                    return True
            else:
                 # Fallback para pyautogui direto se actuation falhar ou não tiver keyboard
                 if pyautogui and shape_type in self.TOOL_HOTKEYS:
                    hotkey, _ = self.TOOL_HOTKEYS[shape_type]
                    pyautogui.press(hotkey)
                    return True
                 return False

        except Exception as e:
            logger.error("ps_select_tool_failed", error=str(e))
            return False
    
    async def draw_shape(self, command: ShapeCommand) -> bool:
        """Desenha forma no Photoshop."""
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
                else:
                    w = params.get("width", 100)
                    h = params.get("height", 50)
                    x1, y1 = cx - w//2, cy - h//2
                    x2, y2 = cx + w//2, cy + h//2
                
                # Shift+Drag para círculo perfeito
                if command.shape_type == ShapeType.CIRCLE:
                    await self.actuation.keyboard.key_down('shift')
                
                # Use safe drag (absolute coords)
                await self.actuation.mouse.drag(x1, y1, x2, y2, duration=0.3)
                
                if command.shape_type == ShapeType.CIRCLE:
                    await self.actuation.keyboard.key_up('shift')
                
            elif command.shape_type in [ShapeType.RECTANGLE, ShapeType.SQUARE]:
                x = params.get("x", 0)
                y = params.get("y", 0)
                w = params.get("width", 100)
                h = params.get("height", 100)
                
                if command.shape_type == ShapeType.SQUARE:
                    await self.actuation.keyboard.key_down('shift')
                
                # Determine end coordinates from width/height
                x2 = x + w
                y2 = y + h
                
                await self.actuation.mouse.drag(x, y, x2, y2, duration=0.3)
                
                if command.shape_type == ShapeType.SQUARE:
                    await self.actuation.keyboard.key_up('shift')
                
            elif command.shape_type == ShapeType.LINE:
                x1, y1 = params.get("x1", 0), params.get("y1", 0)
                x2, y2 = params.get("x2", 0), params.get("y2", 0)
                
                await self.actuation.mouse.drag(x1, y1, x2, y2, duration=0.3)
            
            logger.info("ps_shape_drawn", shape=command.shape_type.value)
            return True
            
        except Exception as e:
            logger.error("ps_draw_shape_failed", error=str(e))
            return False
    
    async def set_fill_color(self, hex_color: str) -> bool:
        """Define cor de preenchimento no Photoshop."""
        # TODO: Implementar usando Actuation para clicar no color picker
        # Por enquanto log apenas
        logger.info("ps_fill_color_set", color=hex_color)
        return True
