
import win32com.client
import pythoncom
import subprocess
import os
import time

class FoxitAdapter:
    def __init__(self):
        self.app = None
        self.mode = "UNKNOWN"
        self.binary_path = self._find_binary()
        
    def _find_binary(self):
        paths = [
            r"C:\Program Files (x86)\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe",
            r"C:\Program Files\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe"
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def connect(self):
        # Try COM first
        try:
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("FoxitPhantomPDF.Application")
            self.mode = "COM"
            return True
        except Exception as e:
            # Fallback to Binary
            if self.binary_path:
                self.mode = "BINARY"
                return True
            else:
                self.mode = "MISSING"
                return False

    def open_document(self, path):
        if self.mode == "COM":
            try:
                self.app.OpenDocument(path)
                return True
            except:
                return False
        elif self.mode == "BINARY":
            try:
                subprocess.Popen([self.binary_path, path])
                return True
            except:
                return False
        return False
        
    def get_status(self):
        return f"Foxit Adapter: {self.mode} Mode"

if __name__ == "__main__":
    adapter = FoxitAdapter()
    if adapter.connect():
        print(f"SUCCESS: {adapter.get_status()}")
        if adapter.mode == "BINARY":
            print(f"Binary Path: {adapter.binary_path}")
    else:
        print("FAIL: Foxit not found (COM or Binary)")
