import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from Modules.Corel.ONI_Corel_Bridge import CorelBridge
except ImportError:
    # Log warning but don't crash, allowing service to be imported even if module missing
    pass

logger = get_logger(__name__)

class CorelService(HealingMixin):
    healing_context = "corel"
    """
    ONIV24 Service Wrapper for CorelDRAW.
    Delegates commands to the ONI_Corel_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.Corel.ONI_Corel_Bridge import CorelBridge
            self.bridge = CorelBridge()
            # Check if actually connected (CorelBridge usually connects in __init__)
            if self.bridge.app: 
                self._connected = True
                logger.info("corel_service_connected")
                return True
            else:
                return False
        except Exception as e:
            logger.error("corel_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to CorelDRAW.")

    # WRAPPERS
    def create_document(self, width: float, height: float, name="ONI_Doc"):
        self.ensure_connection()
        return self.bridge.new_document(name, width, height)

    def draw_rectangle(self, x1, y1, x2, y2):
        self.ensure_connection()
        return self.bridge.draw_rectangle(x1, y1, x2, y2)
    
    def draw_text(self, text, x, y, size=24):
        self.ensure_connection()
        return self.bridge.draw_text(text, x, y, size)
    
    def export_jpg(self, filepath):
        self.ensure_connection()
        return self.bridge.export_jpg(filepath)

    def trace_bitmap(self, image_path, output_path, trace_type="HighQualityImage"):
        """
        Trace a bitmap image to vector.
        """
        self.ensure_connection()
        return self.bridge.trace_bitmap(image_path, output_path, trace_type)

    # ============================================================
    # PHASE 7: COREL ARCHITECT (2026-01-23)
    # ============================================================

    def create_page(self, name: str):
        """Creates a new page after the current one."""
        self.ensure_connection()
        # Direct COM method if available in Bridge, or via VB Script injection
        # Assuming Bridge supports generic command or we extend it
        # For now, we simulate via macro or extended bridge call
        return self.bridge.create_page(name) # Requires Bridge update or generic call

    def import_vector(self, file_path: str, x: float = 0, y: float = 0):
        """Imports SVG/EPS/PDF."""
        self.ensure_connection()
        return self.bridge.import_file(file_path)

    def set_outline(self, width: float, color_hex: str = "#000000"):
        """Sets outline properties for selection."""
        self.ensure_connection()
        # Convert hex to rgb
        h = color_hex.lstrip('#')
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return self.bridge.set_outline(width=width, r=r, g=g, b=b)
        
    def group_objects(self):
        """Groups selected objects."""
        self.ensure_connection()
        return self.bridge.group_selection()
