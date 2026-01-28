import win32com.client
import pythoncom
import os
import time

class WordBridge:
    def __init__(self):
        self.app = None
        self.doc = None
        self._connected = False

    def connect(self):
        try:
            pythoncom.CoInitialize()
            try:
                self.app = win32com.client.GetActiveObject("Word.Application")
            except:
                self.app = win32com.client.Dispatch("Word.Application")
            
            self.app.Visible = True
            self._connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Word: {e}")
            self._connected = False
            return False

    def new_document(self):
        if not self._connected: self.connect()
        self.doc = self.app.Documents.Add()
        return self.doc.Name

    def write_text(self, text, style="Normal"):
        if not self._connected: self.connect()
        if not self.app.ActiveDocument: self.new_document()
        
        selection = self.app.Selection
        if style:
            try:
                selection.Style = style
            except:
                pass # Fallback if style doesn't exist
        
        selection.TypeText(text)
        selection.TypeParagraph()

    def save_pdf(self, filepath):
        if not self._connected or not self.app.ActiveDocument: return False
        try:
            # 17 = PDF format
            self.app.ActiveDocument.SaveAs2(filepath, FileFormat=17)
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False

    def close(self):
        if self.app:
            self.app.Quit()
            self._connected = False
