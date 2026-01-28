"""
ONI Shape Executor - Base Adapter
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any
import structlog
from app.core.dependencies import container
from .types import ShapeType, ShapeCommand

logger = structlog.get_logger(__name__)

class AppAdapter(ABC):
    """Adapter base para aplicações gráficas."""
    
    app_name: str = "unknown"
    
    @property
    def actuation(self):
        """Lazy load actuation system from container."""
        if container.has("actuation"):
            return container.get("actuation")
        # Fallback se não inicializado (não deveria acontecer em prod)
        logger.warning("actuation_not_found_in_container")
        return None

    @abstractmethod
    async def select_tool(self, shape_type: ShapeType) -> bool:
        """Seleciona a ferramenta apropriada."""
        pass
    
    @abstractmethod
    async def draw_shape(self, command: ShapeCommand) -> bool:
        """Desenha a forma."""
        pass
    
    @abstractmethod
    async def set_fill_color(self, hex_color: str) -> bool:
        """Define cor de preenchimento."""
        pass
    
    async def execute(self, command: ShapeCommand) -> Dict[str, Any]:
        """Executa um comando completo."""
        result = {
            "shape": command.shape_type.value,
            "success": False,
            "steps": []
        }
        
        # 1. Selecionar ferramenta
        if await self.select_tool(command.shape_type):
            result["steps"].append("tool_selected")
        else:
            result["error"] = "Failed to select tool"
            return result
        
        await asyncio.sleep(0.2)
        
        # 2. Definir cor se especificada
        if command.fill_color:
            if await self.set_fill_color(command.fill_color):
                result["steps"].append("color_set")
        
        await asyncio.sleep(0.1)
        
        # 3. Desenhar forma
        if await self.draw_shape(command):
            result["steps"].append("shape_drawn")
            result["success"] = True
        else:
            result["error"] = "Failed to draw shape"
        
        return result
