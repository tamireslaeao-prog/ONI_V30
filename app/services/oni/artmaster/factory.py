"""
ONI ArtMaster - Strategy Factory
"""
import structlog
from .types import ApplicationType, ApplicationInfo
from .strategies.base import ApplicationStrategy
from .strategies.photoshop import PhotoshopStrategy
from .strategies.paint import PaintStrategy
from .strategies.gimp import GimpStrategy

logger = structlog.get_logger(__name__)

class ApplicationStrategyFactory:
    """Factory to create appropriate application strategy."""
    
    @staticmethod
    def create_strategy(app_info: ApplicationInfo) -> ApplicationStrategy:
        """Create strategy based on application type."""
        strategies = {
            ApplicationType.PHOTOSHOP: PhotoshopStrategy,
            ApplicationType.PAINT: PaintStrategy,
            ApplicationType.GIMP: GimpStrategy,
        }
        
        strategy_class = strategies.get(app_info.app_type)
        
        if not strategy_class:
            logger.warning("unsupported_application", app_type=app_info.app_type)
            # Fallback to Paint strategy
            strategy_class = PaintStrategy
        
        return strategy_class(app_info)
