"""
ONI Illustrator Bridge
Direct communication with Adobe Illustrator via COM/JSX.

Usage:
    from ONI_Illustrator_Bridge import IllustratorBridge
    
    bridge = IllustratorBridge()
    bridge.new_document()
    bridge.draw_rectangle(100, 100, 200, 200)
    bridge.export_png("output.png")

Version: 1.0.0
"""

import os
import subprocess
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

try:
    import win32com.client
    HAS_COM = True
except ImportError:
    HAS_COM = False


class IllustratorBridge:
    """
    Bridge for controlling Adobe Illustrator via COM/JSX.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize Illustrator Bridge."""
        if not HAS_COM:
            raise RuntimeError("win32com not installed. Run: pip install pywin32")
        
        self.app = None
        self.temp_dir = tempfile.mkdtemp(prefix="oni_illustrator_")
        self._connect()
    
    def _connect(self):
        """Connect to Illustrator."""
        try:
            self.app = win32com.client.Dispatch("Illustrator.Application")
            print(f"Connected to Illustrator {self.app.Version}")
        except Exception as e:
            raise RuntimeError(f"Could not connect to Illustrator: {e}")
    
    @property
    def doc(self):
        """Get active document."""
        if self.app.Documents.Count == 0:
            raise RuntimeError("No document open. Use new_document() first.")
        return self.app.ActiveDocument
    
    # =========================================================================
    # JSX EXECUTION
    # =========================================================================
    
    def execute_jsx(self, code: str) -> Dict[str, Any]:
        """Execute ExtendScript (JSX) code."""
        try:
            # Create temp JSX file
            jsx_path = os.path.join(self.temp_dir, "oni_script.jsx")
            with open(jsx_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute via DoJavaScriptFile
            result = self.app.DoJavaScriptFile(jsx_path)
            
            return {"success": True, "output": str(result) if result else "OK"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================
    
    def new_document(self, width: float = 1920, height: float = 1080,
                     color_mode: str = "RGB") -> Dict[str, Any]:
        """
        Create new document.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            color_mode: "RGB" or "CMYK"
        """
        try:
            preset = self.app.StartupPresetsList.Item("Web")  # or "Print"
            doc = self.app.Documents.Add(
                preset,  # Document preset
                width,   # Width
                height   # Height
            )
            return {"success": True, "output": f"Created document {width}x{height}"}
        except Exception as e:
            # Fallback: use JSX
            jsx = f'''
var doc = app.documents.add(
    DocumentColorSpace.{"RGB" if color_mode == "RGB" else "CMYK"},
    {width},
    {height}
);
doc.name;
'''
            return self.execute_jsx(jsx)
    
    def open_document(self, filepath: str) -> Dict[str, Any]:
        """Open existing document."""
        try:
            self.app.Open(filepath)
            return {"success": True, "output": f"Opened: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_document(self, filepath: str = None) -> Dict[str, Any]:
        """Save document."""
        try:
            if filepath:
                self.doc.SaveAs(filepath)
            else:
                self.doc.Save()
            return {"success": True, "output": "Document saved"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_document(self, save: bool = True) -> Dict[str, Any]:
        """Close active document."""
        try:
            if save:
                self.doc.Close(1)  # aiSaveChanges
            else:
                self.doc.Close(2)  # aiDoNotSaveChanges
            return {"success": True, "output": "Document closed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # DRAWING OPERATIONS
    # =========================================================================
    
    def draw_rectangle(self, x: float, y: float, width: float, height: float,
                       fill_color: Tuple[int, int, int] = None) -> Dict[str, Any]:
        """Draw a rectangle."""
        jsx = f'''
var doc = app.activeDocument;
var rect = doc.pathItems.rectangle({-y}, {x}, {width}, {height});
{"rect.fillColor = new RGBColor(); rect.fillColor.red = " + str(fill_color[0]) + "; rect.fillColor.green = " + str(fill_color[1]) + "; rect.fillColor.blue = " + str(fill_color[2]) + ";" if fill_color else ""}
rect.name;
'''
        return self.execute_jsx(jsx)
    
    def draw_ellipse(self, x: float, y: float, width: float, height: float) -> Dict[str, Any]:
        """Draw an ellipse."""
        jsx = f'''
var doc = app.activeDocument;
var ellipse = doc.pathItems.ellipse({-y}, {x}, {width}, {height});
ellipse.name;
'''
        return self.execute_jsx(jsx)
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float,
                  stroke_width: float = 1) -> Dict[str, Any]:
        """Draw a line."""
        jsx = f'''
var doc = app.activeDocument;
var line = doc.pathItems.add();
line.setEntirePath([[{x1}, {-y1}], [{x2}, {-y2}]]);
line.stroked = true;
line.strokeWidth = {stroke_width};
line.filled = false;
line.name;
'''
        return self.execute_jsx(jsx)
    
    def draw_polygon(self, points: List[Tuple[float, float]], closed: bool = True) -> Dict[str, Any]:
        """Draw a polygon from points."""
        points_js = ", ".join([f"[{p[0]}, {-p[1]}]" for p in points])
        jsx = f'''
var doc = app.activeDocument;
var poly = doc.pathItems.add();
poly.setEntirePath([{points_js}]);
poly.closed = {str(closed).lower()};
poly.name;
'''
        return self.execute_jsx(jsx)
    
    def draw_text(self, text: str, x: float, y: float,
                  font: str = "Arial", size: float = 12) -> Dict[str, Any]:
        """Add point text."""
        jsx = f'''
var doc = app.activeDocument;
var textFrame = doc.textFrames.add();
textFrame.contents = "{text}";
textFrame.position = [{x}, {-y}];
textFrame.textRange.characterAttributes.size = {size};
try {{
    textFrame.textRange.characterAttributes.textFont = app.textFonts.getByName("{font}");
}} catch(e) {{}}
textFrame.name;
'''
        return self.execute_jsx(jsx)
    
    def draw_area_text(self, text: str, x: float, y: float,
                       width: float, height: float,
                       font: str = "Arial", size: float = 12) -> Dict[str, Any]:
        """Add area text."""
        jsx = f'''
var doc = app.activeDocument;
var rect = doc.pathItems.rectangle({-y}, {x}, {width}, {height});
var textFrame = doc.textFrames.areaText(rect);
textFrame.contents = "{text}";
textFrame.textRange.characterAttributes.size = {size};
textFrame.name;
'''
        return self.execute_jsx(jsx)
    
    # =========================================================================
    # COLORS & STYLES
    # =========================================================================
    
    def set_fill_color(self, r: int, g: int, b: int) -> Dict[str, Any]:
        """Set fill color for selection."""
        jsx = f'''
var sel = app.activeDocument.selection;
if (sel.length > 0) {{
    var color = new RGBColor();
    color.red = {r};
    color.green = {g};
    color.blue = {b};
    for (var i = 0; i < sel.length; i++) {{
        sel[i].fillColor = color;
    }}
    "Fill color set";
}} else {{
    "No selection";
}}
'''
        return self.execute_jsx(jsx)
    
    def set_stroke_color(self, r: int, g: int, b: int, width: float = 1) -> Dict[str, Any]:
        """Set stroke color for selection."""
        jsx = f'''
var sel = app.activeDocument.selection;
if (sel.length > 0) {{
    var color = new RGBColor();
    color.red = {r};
    color.green = {g};
    color.blue = {b};
    for (var i = 0; i < sel.length; i++) {{
        sel[i].stroked = true;
        sel[i].strokeColor = color;
        sel[i].strokeWidth = {width};
    }}
    "Stroke set";
}} else {{
    "No selection";
}}
'''
        return self.execute_jsx(jsx)
    
    def remove_fill(self) -> Dict[str, Any]:
        """Remove fill from selection."""
        jsx = '''
var sel = app.activeDocument.selection;
for (var i = 0; i < sel.length; i++) {
    sel[i].filled = false;
}
"Fill removed";
'''
        return self.execute_jsx(jsx)
    
    def remove_stroke(self) -> Dict[str, Any]:
        """Remove stroke from selection."""
        jsx = '''
var sel = app.activeDocument.selection;
for (var i = 0; i < sel.length; i++) {
    sel[i].stroked = false;
}
"Stroke removed";
'''
        return self.execute_jsx(jsx)
    
    # =========================================================================
    # TRANSFORMATIONS
    # =========================================================================
    
    def move(self, dx: float, dy: float) -> Dict[str, Any]:
        """Move selection."""
        jsx = f'''
var sel = app.activeDocument.selection;
for (var i = 0; i < sel.length; i++) {{
    sel[i].translate({dx}, {-dy});
}}
"Moved";
'''
        return self.execute_jsx(jsx)
    
    def rotate(self, angle: float) -> Dict[str, Any]:
        """Rotate selection in degrees."""
        jsx = f'''
var sel = app.activeDocument.selection;
for (var i = 0; i < sel.length; i++) {{
    sel[i].rotate({angle});
}}
"Rotated";
'''
        return self.execute_jsx(jsx)
    
    def scale(self, scale_x: float, scale_y: float = None) -> Dict[str, Any]:
        """Scale selection (percentage)."""
        if scale_y is None:
            scale_y = scale_x
        jsx = f'''
var sel = app.activeDocument.selection;
for (var i = 0; i < sel.length; i++) {{
    sel[i].resize({scale_x}, {scale_y});
}}
"Scaled";
'''
        return self.execute_jsx(jsx)
    
    # =========================================================================
    # SELECTION
    # =========================================================================
    
    def select_all(self) -> Dict[str, Any]:
        """Select all objects."""
        jsx = '''
app.activeDocument.selection = app.activeDocument.pathItems;
"All selected";
'''
        return self.execute_jsx(jsx)
    
    def deselect_all(self) -> Dict[str, Any]:
        """Deselect all."""
        jsx = '''
app.activeDocument.selection = null;
"Deselected";
'''
        return self.execute_jsx(jsx)
    
    def select_by_name(self, name: str) -> Dict[str, Any]:
        """Select item by name."""
        jsx = f'''
var doc = app.activeDocument;
var item = doc.pathItems.getByName("{name}");
doc.selection = [item];
"Selected: {name}";
'''
        return self.execute_jsx(jsx)
    
    # =========================================================================
    # LAYERS
    # =========================================================================
    
    def create_layer(self, name: str) -> Dict[str, Any]:
        """Create new layer."""
        jsx = f'''
var doc = app.activeDocument;
var layer = doc.layers.add();
layer.name = "{name}";
layer.name;
'''
        return self.execute_jsx(jsx)
    
    def set_active_layer(self, name: str) -> Dict[str, Any]:
        """Set active layer by name."""
        jsx = f'''
var doc = app.activeDocument;
var layer = doc.layers.getByName("{name}");
doc.activeLayer = layer;
"Active: {name}";
'''
        return self.execute_jsx(jsx)
    
    def list_layers(self) -> Dict[str, Any]:
        """List all layers."""
        jsx = '''
var doc = app.activeDocument;
var names = [];
for (var i = 0; i < doc.layers.length; i++) {
    names.push(doc.layers[i].name);
}
names.join(", ");
'''
        return self.execute_jsx(jsx)
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export_png(self, filepath: str, width: int = 1920) -> Dict[str, Any]:
        """Export to PNG."""
        jsx = f'''
var doc = app.activeDocument;
var file = new File("{filepath.replace(os.sep, '/')}");
var opts = new ExportOptionsPNG24();
opts.horizontalScale = {width / 1920 * 100};
opts.verticalScale = {width / 1920 * 100};
opts.antiAliasing = true;
opts.transparency = true;
doc.exportFile(file, ExportType.PNG24, opts);
"Exported to {filepath}";
'''
        return self.execute_jsx(jsx)
    
    def export_svg(self, filepath: str) -> Dict[str, Any]:
        """Export to SVG."""
        jsx = f'''
var doc = app.activeDocument;
var file = new File("{filepath.replace(os.sep, '/')}");
var opts = new ExportOptionsSVG();
opts.embedRasterImages = true;
doc.exportFile(file, ExportType.SVG, opts);
"Exported to {filepath}";
'''
        return self.execute_jsx(jsx)
    
    def export_pdf(self, filepath: str) -> Dict[str, Any]:
        """Export to PDF."""
        jsx = f'''
var doc = app.activeDocument;
var file = new File("{filepath.replace(os.sep, '/')}");
var opts = new PDFSaveOptions();
opts.compatibility = PDFCompatibility.ACROBAT7;
doc.saveAs(file, opts);
"Exported to {filepath}";
'''
        return self.execute_jsx(jsx)


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    try:
        bridge = IllustratorBridge()
        print("Illustrator connected!")
        
    except Exception as e:
        print(f"Error: {e}")
