import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

# Add project root to sys.path to ensure Modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from Modules.Illustrator.ONI_Illustrator_Bridge import IllustratorBridge
except ImportError:
    # Fallback if path appending failed or structure is different
    from Modules.Illustrator.ONI_Illustrator_Bridge import IllustratorBridge

logger = get_logger(__name__)

class IllustratorService(HealingMixin):
    healing_context = "illustrator"
    """
    ONIV24 Service Wrapper for Adobe Illustrator.
    Delegates commands to the ONI_Illustrator_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        """Establishes connection to Illustrator."""
        try:
            self.bridge = IllustratorBridge()
            self._connected = True
            logger.info("illustrator_service_connected")
            return True
        except Exception as e:
            logger.error("illustrator_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to Illustrator.")

    # WRAPPERS
    def create_document(self, width: float = 1920, height: float = 1080, mode: str = "RGB") -> dict:
        self.ensure_connection()
        return self.bridge.new_document(width, height, mode)

    def draw_rectangle(self, x: float, y: float, width: float, height: float, fill_color: tuple = None) -> dict:
        self.ensure_connection()
        return self.bridge.draw_rectangle(x, y, width, height, fill_color)
    
    def draw_text(self, text: str, x: float, y: float, font: str = "Arial", size: float = 12) -> dict:
        self.ensure_connection()
        return self.bridge.draw_text(text, x, y, font, size)

    def export_png(self, filepath: str) -> dict:
        self.ensure_connection()
        return self.bridge.export_png(filepath)
    
    def run_jsx(self, code: str) -> dict:
        self.ensure_connection()
        return self.bridge.execute_jsx(code)

    # ============================================================
    # PHASE 6: VECTOR ARCHITECT (2026-01-23)
    # ============================================================

    def create_layer(self, layer_name: str) -> dict:
        """
        Creates a new layer with the specified name.
        """
        jsx = f"""
        var doc = app.activeDocument;
        var newLayer = doc.layers.add();
        newLayer.name = "{layer_name}";
        """
        return self.run_jsx(jsx)

    def place_item(self, file_path: str, x: float = 0, y: float = 0) -> dict:
        """
        Places a file (raster or vector) into the document.
        """
        safe_path = file_path.replace("\\", "\\\\")
        jsx = f"""
        var doc = app.activeDocument;
        var placedItem = doc.placedItems.add();
        placedItem.file = new File("{safe_path}");
        placedItem.position = [{x}, {y}];
        """
        return self.run_jsx(jsx)
