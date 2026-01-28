"""
ONI Shape Executor - Service Orchestrator
"""
import asyncio
import structlog
from typing import Dict, Optional, List, Any
from .types import ShapeCommand
from .base import AppAdapter
from .adapters.photoshop import PhotoshopAdapter
from .adapters.corel import CorelDRAWAdapter
from .adapters.illustrator import IllustratorAdapter

logger = structlog.get_logger(__name__)

class ShapeExecutorService:
    """
    Serviço que executa ShapeCommands usando o adapter apropriado.
    Detecta automaticamente a aplicação ativa e usa o adapter correto.
    """
    
    # Registro de adapters
    _adapters: Dict[str, AppAdapter] = {
        "Photoshop.exe": PhotoshopAdapter(),
        "CorelDRW.exe": CorelDRAWAdapter(),
        "illustrator.exe": IllustratorAdapter(),
    }
    
    @classmethod
    def get_adapter(cls, process_name: str) -> Optional[AppAdapter]:
        """Retorna o adapter para a aplicação."""
        # Busca case-insensitive
        for key, adapter in cls._adapters.items():
            if key.lower() == process_name.lower():
                return adapter
        return None
    
    @classmethod
    async def execute_command(
        cls,
        command: ShapeCommand,
        process_name: str
    ) -> Dict[str, Any]:
        """Executa um comando de forma na aplicação especificada."""
        
        adapter = cls.get_adapter(process_name)
        
        if not adapter:
            # Fallback: usar Photoshop adapter como padrão
            logger.warning("no_adapter_found", process=process_name, using="PhotoshopAdapter")
            adapter = PhotoshopAdapter()
        
        logger.info("executing_shape", 
                   shape=command.shape_type.value,
                   adapter=adapter.app_name)
        
        return await adapter.execute(command)
    
    @classmethod
    async def execute_commands(
        cls,
        commands: List[ShapeCommand],
        process_name: str
    ) -> List[Dict[str, Any]]:
        """Executa múltiplos comandos em sequência."""
        results = []
        
        for cmd in commands:
            result = await cls.execute_command(cmd, process_name)
            results.append(result)
            await asyncio.sleep(0.3)  # Delay entre comandos
        
        return results
    
    @classmethod
    def list_supported_apps(cls) -> List[str]:
        """Lista aplicações suportadas."""
        return list(cls._adapters.keys())
