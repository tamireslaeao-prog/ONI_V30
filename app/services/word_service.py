import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from Modules.Word.ONI_Word_Bridge import WordBridge
except ImportError:
    pass

logger = get_logger(__name__)

class WordService(HealingMixin):
    healing_context = "word"
    """
    ONIV24 Service Wrapper for Microsoft Word.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.Word.ONI_Word_Bridge import WordBridge
            self.bridge = WordBridge()
            if self.bridge.connect():
                self._connected = True
                logger.info("word_service_connected")
                return True
            return False
        except Exception as e:
            logger.error("word_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to Word.")

    def create_document(self):
        self.ensure_connection()
        return self.bridge.new_document()

    def write_text(self, text: str, style="Normal"):
        self.ensure_connection()
        return self.bridge.write_text(text, style)

    def export_pdf(self, path: str):
        self.ensure_connection()
        return self.bridge.save_pdf(path)
