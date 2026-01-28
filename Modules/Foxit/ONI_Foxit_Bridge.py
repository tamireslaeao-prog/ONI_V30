"""
ONI Foxit PDF Bridge
Direct communication with Foxit PDF Editor via COM/CLI.

Usage:
    from ONI_Foxit_Bridge import FoxitBridge
    
    bridge = FoxitBridge()
    bridge.open_document("document.pdf")
    bridge.add_text_annotation(100, 700, "Comment here")
    bridge.export_png("page_1.png", page=1)

Version: 1.0.0
"""

import os
import subprocess
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import win32com.client
    HAS_COM = True
except ImportError:
    HAS_COM = False


class FoxitBridge:
    """
    Bridge for controlling Foxit PDF Editor.
    Uses COM automation when available, CLI otherwise.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, foxit_path: Optional[str] = None):
        """
        Initialize Foxit Bridge.
        
        Args:
            foxit_path: Path to FoxitPDFEditor.exe. Auto-detects if not provided.
        """
        self.foxit_path = foxit_path or self._find_foxit()
        self.app = None
        self.temp_dir = tempfile.mkdtemp(prefix="oni_foxit_")
        
        if HAS_COM:
            self._try_connect_com()
    
    def _find_foxit(self) -> Optional[str]:
        """Auto-detect Foxit installation."""
        paths = [
            r"C:\Program Files\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe",
            r"C:\Program Files (x86)\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe",
            r"C:\Program Files\Foxit Software\Foxit PhantomPDF\FoxitPhantomPDF.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _try_connect_com(self):
        """Try to connect via COM."""
        try:
            # Foxit COM automation (if available)
            self.app = win32com.client.Dispatch("FoxitReader.Application")
            print("Connected to Foxit via COM")
        except:
            self.app = None
    
    # =========================================================================
    # CLI METHODS
    # =========================================================================
    
    def _run_cli(self, args: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Run Foxit via command line."""
        if not self.foxit_path:
            return {"success": False, "error": "Foxit not found"}
        
        try:
            cmd = [self.foxit_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================
    
    def open_document(self, filepath: str) -> Dict[str, Any]:
        """Open a PDF document."""
        filepath = os.path.abspath(filepath)
        
        if self.app:
            try:
                self.app.OpenDocument(filepath)
                return {"success": True, "output": f"Opened: {filepath}"}
            except:
                pass
        
        # Fallback: CLI
        return self._run_cli([filepath])
    
    def close_document(self) -> Dict[str, Any]:
        """Close current document."""
        if self.app:
            try:
                self.app.ActiveDocument.Close()
                return {"success": True, "output": "Document closed"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def save_document(self, filepath: str = None) -> Dict[str, Any]:
        """Save document."""
        if self.app:
            try:
                if filepath:
                    self.app.ActiveDocument.SaveAs(filepath)
                else:
                    self.app.ActiveDocument.Save()
                return {"success": True, "output": "Document saved"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection. Open Foxit manually."}
    
    # =========================================================================
    # PDF OPERATIONS
    # =========================================================================
    
    def get_page_count(self) -> Dict[str, Any]:
        """Get number of pages."""
        if self.app:
            try:
                count = self.app.ActiveDocument.Pages.Count
                return {"success": True, "output": count, "data": count}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def go_to_page(self, page: int) -> Dict[str, Any]:
        """Navigate to specific page."""
        if self.app:
            try:
                self.app.ActiveDocument.GoTo(page)
                return {"success": True, "output": f"Went to page {page}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # ANNOTATIONS
    # =========================================================================
    
    def add_text_annotation(self, x: float, y: float, text: str,
                            page: int = 1) -> Dict[str, Any]:
        """Add text annotation (sticky note)."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                annotation = doc.Pages.Item(page).Annotations.Add(
                    1,  # Text annotation type
                    x, y, x + 100, y + 50
                )
                annotation.Contents = text
                return {"success": True, "output": f"Added annotation: {text[:20]}..."}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def add_highlight(self, x1: float, y1: float, x2: float, y2: float,
                      page: int = 1, color: str = "yellow") -> Dict[str, Any]:
        """Add highlight annotation."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                # Highlight markup type
                annotation = doc.Pages.Item(page).Annotations.Add(
                    8,  # Highlight type
                    x1, y1, x2, y2
                )
                return {"success": True, "output": "Highlight added"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # TEXT OPERATIONS
    # =========================================================================
    
    def extract_text(self, page: int = None) -> Dict[str, Any]:
        """Extract text from PDF."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                if page:
                    text = doc.Pages.Item(page).GetText()
                else:
                    text = ""
                    for i in range(1, doc.Pages.Count + 1):
                        text += doc.Pages.Item(i).GetText() + "\n"
                return {"success": True, "output": text, "data": text}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def find_text(self, search_text: str) -> Dict[str, Any]:
        """Find text in document."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                result = doc.Find(search_text)
                return {"success": True, "output": f"Found: {result}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def replace_text(self, find_text: str, replace_text: str) -> Dict[str, Any]:
        """Find and replace text."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.Replace(find_text, replace_text)
                return {"success": True, "output": f"Replaced '{find_text}' with '{replace_text}'"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export_png(self, filepath: str, page: int = 1, dpi: int = 150) -> Dict[str, Any]:
        """Export page to PNG."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.Pages.Item(page).Export(filepath, "PNG", dpi)
                return {"success": True, "output": f"Exported page {page} to {filepath}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Fallback: no easy CLI for this
        return {"success": False, "error": "No COM connection. Use GUI export."}
    
    def export_all_pages_png(self, output_dir: str, prefix: str = "page",
                             dpi: int = 150) -> Dict[str, Any]:
        """Export all pages to PNG."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                os.makedirs(output_dir, exist_ok=True)
                
                for i in range(1, doc.Pages.Count + 1):
                    filepath = os.path.join(output_dir, f"{prefix}_{i:03d}.png")
                    doc.Pages.Item(i).Export(filepath, "PNG", dpi)
                
                return {"success": True, "output": f"Exported {doc.Pages.Count} pages"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def export_word(self, filepath: str) -> Dict[str, Any]:
        """Export PDF to Word document."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.ExportAsWord(filepath)
                return {"success": True, "output": f"Exported to Word: {filepath}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def export_excel(self, filepath: str) -> Dict[str, Any]:
        """Export PDF to Excel."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.ExportAsExcel(filepath)
                return {"success": True, "output": f"Exported to Excel: {filepath}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # PAGE OPERATIONS
    # =========================================================================
    
    def insert_page(self, position: int = None) -> Dict[str, Any]:
        """Insert blank page."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                if position:
                    doc.Pages.Insert(position)
                else:
                    doc.Pages.Insert(doc.Pages.Count + 1)
                return {"success": True, "output": "Page inserted"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def delete_page(self, page: int) -> Dict[str, Any]:
        """Delete a page."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.Pages.Delete(page)
                return {"success": True, "output": f"Deleted page {page}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def rotate_page(self, page: int, angle: int = 90) -> Dict[str, Any]:
        """Rotate a page (90, 180, 270)."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                doc.Pages.Item(page).Rotate(angle)
                return {"success": True, "output": f"Rotated page {page} by {angle}°"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # MERGE/SPLIT
    # =========================================================================
    
    def merge_pdfs(self, input_files: List[str], output_file: str) -> Dict[str, Any]:
        """Merge multiple PDFs."""
        if self.app:
            try:
                # Open first file
                self.app.OpenDocument(input_files[0])
                doc = self.app.ActiveDocument
                
                # Append others
                for pdf in input_files[1:]:
                    doc.InsertPages(doc.Pages.Count, pdf)
                
                doc.SaveAs(output_file)
                return {"success": True, "output": f"Merged {len(input_files)} files to {output_file}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    def split_pdf(self, output_dir: str, prefix: str = "split") -> Dict[str, Any]:
        """Split PDF into individual pages."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                os.makedirs(output_dir, exist_ok=True)
                
                for i in range(1, doc.Pages.Count + 1):
                    output_file = os.path.join(output_dir, f"{prefix}_{i:03d}.pdf")
                    doc.ExtractPages(i, i, output_file)
                
                return {"success": True, "output": f"Split into {doc.Pages.Count} files"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No COM connection"}
    
    # =========================================================================
    # PRINT
    # =========================================================================
    
    def print_document(self, printer: str = None, pages: str = "all") -> Dict[str, Any]:
        """Print document."""
        if self.app:
            try:
                doc = self.app.ActiveDocument
                if printer:
                    doc.Print(printer)
                else:
                    doc.Print()
                return {"success": True, "output": "Document sent to printer"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Fallback: CLI
        if self.foxit_path:
            args = ["/p"]
            if printer:
                args.append(f"/t:{printer}")
            return self._run_cli(args)
        
        return {"success": False, "error": "No Foxit connection"}


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    try:
        bridge = FoxitBridge()
        if bridge.foxit_path:
            print(f"Foxit found at: {bridge.foxit_path}")
        if bridge.app:
            print("COM connection established")
        else:
            print("No COM connection (will use CLI fallback)")
    except Exception as e:
        print(f"Error: {e}")
