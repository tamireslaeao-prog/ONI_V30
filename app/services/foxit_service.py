import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logger = get_logger(__name__)

class FoxitService(HealingMixin):
    healing_context = "foxit"
    """
    ONIV24 Service Wrapper for Foxit PDF Editor.
    Delegates commands to the ONI_Foxit_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.Foxit.ONI_Foxit_Bridge import FoxitBridge
            self.bridge = FoxitBridge()
            if self.bridge.connect():
                self._connected = True
                logger.info("foxit_service_connected")
                return True
            return False
        except Exception as e:
            logger.error("foxit_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to Foxit.")

    def open_document(self, path: str):
        self.ensure_connection()
        return self.bridge.open_pdf(path)
    
    def extract_text(self, page_num=0):
        self.ensure_connection()
        return self.bridge.get_text(page_num)
