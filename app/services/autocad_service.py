import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from Modules.AutoCAD.ONI_AutoCAD_Bridge import AutoCADBridge
except ImportError:
    from Modules.AutoCAD.ONI_AutoCAD_Bridge import AutoCADBridge

logger = get_logger(__name__)

class AutoCADService(HealingMixin):
    healing_context = "autocad"
    """
    ONIV24 Service Wrapper for AutoCAD.
    Delegates commands to the ONI_AutoCAD_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            self.bridge = AutoCADBridge()
            if self.bridge.connect():
                self._connected = True
                logger.info("autocad_service_connected")
                return True
            else:
                raise Exception("Bridge connect() returned False")
        except Exception as e:
            logger.error("autocad_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge or not self.bridge.is_connected():
            if not self.connect():
                raise ConnectionError("Could not connect to AutoCAD.")

    # WRAPPERS
    def draw_line(self, x1, y1, x2, y2) -> object:
        self.ensure_connection()
        return self.bridge.draw_line(x1, y1, x2, y2)

    def draw_circle(self, x, y, radius) -> object:
        self.ensure_connection()
        return self.bridge.draw_circle(x, y, radius)
    
    def save_dwg(self, path: str) -> bool:
        self.ensure_connection()
        return self.bridge.save(path)
    
    def send_command(self, cmd: str):
        self.ensure_connection()
        self.bridge.send_command(cmd)

    # ============================================================
    # PHASE 7: CAD ARCHITECT (2026-01-23)
    # ============================================================

    def create_layer(self, layer_name: str, color_index: int = 7) -> str:
        """
        Creates a new layer with specified color.
        Color 7 = White/Black (Standard).
        """
        self.ensure_connection()
        cmd = f"-LAYER N {layer_name} C {color_index} {layer_name} "
        self.bridge.send_command(cmd)
        return layer_name

    def insert_block(self, block_name: str, x: float, y: float, scale: float = 1.0, rotation: float = 0.0):
        """
        Inserts a block at specific coordinates.
        Note: Block definition must exist or be in search path.
        """
        self.ensure_connection()
        cmd = f"-INSERT {block_name} {x},{y} {scale} {scale} {rotation} "
        self.bridge.send_command(cmd)

    def create_hatch(self, pattern: str, scale: float = 1.0, rotation: float = 0.0):
        """
        Applies hatch to the last created object or current selection.
        """
        self.ensure_connection()
        # -HATCH command logic
        cmd = f"-HATCH P {pattern} {scale} {rotation}  " # ending with spaces to enter
        self.bridge.send_command(cmd)
