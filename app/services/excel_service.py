import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from Modules.Excel.ONI_Excel_Bridge import ExcelBridge
except ImportError:
    pass

logger = get_logger(__name__)

class ExcelService(HealingMixin):
    healing_context = "excel"
    """
    ONIV24 Service Wrapper for Microsoft Excel.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.Excel.ONI_Excel_Bridge import ExcelBridge
            self.bridge = ExcelBridge()
            if self.bridge.connect():
                self._connected = True
                logger.info("excel_service_connected")
                return True
            return False
        except Exception as e:
            logger.error("excel_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to Excel.")

    def create_workbook(self):
        self.ensure_connection()
        return self.bridge.new_workbook()

    def set_cell(self, row: int, col: int, value):
        self.ensure_connection()
        return self.bridge.set_cell(row, col, value)

    def write_data(self, start_cell: str, data: list):
        self.ensure_connection()
        return self.bridge.set_range_data(start_cell, data)
    
    def save_file(self, path: str):
        self.ensure_connection()
        return self.bridge.save_as(path)
