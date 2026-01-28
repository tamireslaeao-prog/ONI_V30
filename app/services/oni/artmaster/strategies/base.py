"""
ONI ArtMaster - Base Strategy Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from ..types import ApplicationInfo

class ApplicationStrategy(ABC):
    """Abstract base class for application-specific strategies."""
    
    def __init__(self, app_info: ApplicationInfo):
        self.app_info = app_info
        self.canvas_center = app_info.canvas_center
    
    @abstractmethod
    async def ensure_focus(self) -> bool:
        """Ensure application window is focused."""
        pass
    
    @abstractmethod
    async def select_tool(self, tool_name: str) -> bool:
        """Select a tool by name."""
        pass
    
    @abstractmethod
    async def prepare_canvas(self) -> bool:
        """Prepare canvas for drawing."""
        pass
    
    @abstractmethod
    def get_tool_shortcuts(self) -> Dict[str, str]:
        """Get tool name to keyboard shortcut mapping."""
        pass
    
    @abstractmethod
    async def create_layer(self, name: Optional[str] = None) -> bool:
        """Create new layer (if supported)."""
        pass
    
    @abstractmethod
    async def save_file(self, path: str) -> bool:
        """Save current work."""
        pass
