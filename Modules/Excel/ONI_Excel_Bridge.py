import win32com.client
import pythoncom
import os
from typing import Union, List

class ExcelBridge:
    def __init__(self):
        self.app = None
        self.wb = None
        self.ws = None
        self._connected = False

    def connect(self):
        try:
            pythoncom.CoInitialize()
            try:
                self.app = win32com.client.GetActiveObject("Excel.Application")
            except Exception:
                self.app = win32com.client.Dispatch("Excel.Application")
            
            self.app.Visible = True
            self.app.DisplayAlerts = False
            self._connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Excel: {e}")
            self._connected = False
            return False

    def new_workbook(self):
        if not self._connected: self.connect()
        self.wb = self.app.Workbooks.Add()
        self.ws = self.wb.ActiveSheet
        return self.wb.Name

    def set_cell(self, row: int, col: int, value: Union[str, int, float]):
        if not self._connected or not self.ws: self.new_workbook()
        self.ws.Cells(row, col).Value = value

    def get_cell(self, row: int, col: int):
        if not self._connected or not self.ws: return None
        return self.ws.Cells(row, col).Value

    def set_range_data(self, start_cell: str, data: List[List[Union[str, int]]]):
        """Write 2D list to range, e.g. A1"""
        if not self._connected or not self.ws: self.new_workbook()
        
        rows = len(data)
        cols = len(data[0]) if rows > 0 else 0
        if cols == 0: return

        # Identify range object
        # Simple implementation: assumes start_cell is top-left
        range_obj = self.ws.Range(start_cell, self.ws.Cells(
            self.ws.Range(start_cell).Row + rows - 1,
            self.ws.Range(start_cell).Column + cols - 1
        ))
        range_obj.Value = data

    def run_macro(self, macro_name: str):
        if not self._connected: return
        self.app.Run(macro_name)

    def save_as(self, filepath: str):
        if not self._connected or not self.wb: return False
        try:
            # 51 = xlOpenXMLWorkbook (.xlsx)
            self.wb.SaveAs(filepath, FileFormat=51)
            return True
        except Exception as e:
            print(f"Error saving Excel: {e}")
            return False

    def close(self):
        if self.app:
            self.app.Quit()
            self._connected = False
