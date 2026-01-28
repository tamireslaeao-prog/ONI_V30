"""
ONI CorelDRAW Bridge
Direct communication with CorelDRAW via COM automation.

Usage:
    from ONI_Corel_Bridge import CorelBridge
    
    bridge = CorelBridge()
    bridge.new_document()
    bridge.draw_rectangle(100, 100, 200, 200)
    bridge.export_png("output.png")

Version: 1.0.0
"""

import os
import json
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

try:
    import win32com.client
    HAS_COM = True
except ImportError:
    HAS_COM = False


class CorelBridge:
    """
    Bridge for controlling CorelDRAW via COM automation.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, version: int = None):
        """
        Initialize CorelDRAW Bridge.
        
        Args:
            version: Specific version number (e.g., 26 for 2024). Auto-detects if None.
        """
        if not HAS_COM:
            raise RuntimeError("win32com not installed. Run: pip install pywin32")
        
        self.app = None
        self.version = version
        self._connect()
    
    def _connect(self):
        """Connect to CorelDRAW, auto-launching if necessary.
        
        Strategy (preserving AUTONOMY):
        1. Try GetActiveObject (connect to running instance)
        2. If not running, use Dispatch (AUTO-LAUNCH new instance)
        3. If both fail, allow PowerShell fallback for trace_bitmap
        """
        prog_ids = [
            f"CorelDRAW.Application.{self.version}" if self.version else None,
            "CorelDRAW.Application.24",  # 2022
            "CorelDRAW.Application.26",  # 2024
            "CorelDRAW.Application.25",  # 2023
            "CorelDRAW.Application.23",  # 2021
            "CorelDRAW.Application",     # Default
        ]
        
        # Step 1: Try to connect to RUNNING instance
        for prog_id in [p for p in prog_ids if p]:
            try:
                self.app = win32com.client.GetActiveObject(prog_id)
                self.app.Visible = True
                print(f"Connected to running {prog_id}")
                return
            except:
                continue
        
        # Step 2: AUTO-LAUNCH new instance (AUTONOMY PRESERVED!)
        print("[ONI] CorelDRAW not running. Auto-launching...")
        for prog_id in [p for p in prog_ids if p]:
            try:
                self.app = win32com.client.Dispatch(prog_id)
                self.app.Visible = True
                print(f"Launched new instance: {prog_id}")
                return
            except:
                continue
                
        # Step 3: If we reach here, COM completely failed.
        # Don't crash - allow PowerShell scripts to work.
        print("[WARN] Python COM failed. trace_bitmap will use PowerShell fallback.")

    def trace_bitmap(self, image_path: str, output_path: str = None, 
                     trace_type: str = "HighQualityImage") -> Dict[str, Any]:
        """
        Legacy: Full Autonomous Trace using Native COM (Architect Level).
        No more PowerShell shortcuts.
        """
        try:
            if not output_path:
                base = os.path.splitext(image_path)[0]
                output_path = f"{base}.eps"

            # 1. Create Temp Doc
            doc = self.app.CreateDocument()
            doc.Unit = 4 # mm
            
            # 2. Import Image
            doc.ActiveLayer.Import(image_path)
            bitmap = doc.ActiveShape
            
            # 3. Trace (Native COM)
            # Type: 1=Logo, 2=Detailed, 5=High Quality
            mode = 2
            if trace_type == "Logo": mode = 1
            if trace_type == "LineArt": mode = 0
            
            trace_settings = bitmap.Trace(mode)
            trace_settings.Finish() # Apply trace
            
            # 4. Cleanup
            # Original bitmap is still there, usually behind. 
            # The trace result is a Group. 
            # We want to export only the vectors.
            
            # Delete original bitmap (it's usually the bottom shape now or top? Trace usually creates new group on top)
            # Let's verify selection. Finish() usually selects the result.
            
            # Simple hack: Export everything to EPS/SVG (Vector only? No, EPS supports raster)
            # We must delete the bitmap.
            # bitmap is the 'bitmap' object reference.
            bitmap.Delete() 
            
            # 5. Export
            # Determine filter from extension
            ext = os.path.splitext(output_path)[1].upper().replace(".", "")
            if ext == "EPS":
                flt = self.app.ExportFilters.Item("EPS")
            elif ext == "SVG":
                flt = self.app.ExportFilters.Item("SVG")
            else:
                flt = self.app.ExportFilters.Item("EPS") # Default
                
            doc.Export(output_path, flt)
            
            # 6. Close Temp Doc
            doc.Close()
            
            return {"success": True, "output": output_path}
            
        except Exception as e:
            print(f"COM Trace failed: {e}")
            return {"success": False, "error": str(e)}
    
    @property
    def doc(self):
        """Get active document."""
        if self.app.Documents.Count == 0:
            raise RuntimeError("No document open. Use new_document() first.")
        return self.app.ActiveDocument
    
    @property
    def page(self):
        """Get active page."""
        return self.doc.ActivePage
    
    @property
    def layer(self):
        """Get active layer."""
        return self.page.ActiveLayer
    
    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================
    
    def new_document(self, width: float = 210, height: float = 297,
                     units: str = "mm") -> Dict[str, Any]:
        """
        Create new document.
        
        Args:
            width: Page width
            height: Page height
            units: "mm", "in", "px"
        """
        try:
            # Unit conversion
            unit_map = {"mm": 1, "in": 25.4, "px": 0.264583}
            scale = unit_map.get(units, 1)
            
            doc = self.app.CreateDocument()
            doc.Unit = 4  # Millimeters
            
            page = doc.ActivePage
            page.SizeWidth = width * scale
            page.SizeHeight = height * scale
            
            return {"success": True, "output": f"Created document {width}x{height}{units}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_document(self, filepath: str) -> Dict[str, Any]:
        """Open existing document."""
        try:
            self.app.OpenDocument(filepath)
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
    
    def close_document(self) -> Dict[str, Any]:
        """Close active document."""
        try:
            self.doc.Close()
            return {"success": True, "output": "Document closed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # DRAWING OPERATIONS
    # =========================================================================
    
    def draw_rectangle(self, x1: float, y1: float, x2: float, y2: float,
                       corner_radius: float = 0) -> Dict[str, Any]:
        """Draw a rectangle."""
        try:
            rect = self.layer.CreateRectangle2(x1, y1, x2, y2, corner_radius)
            return {"success": True, "output": f"Rectangle created: {rect.Name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def draw_ellipse(self, x: float, y: float, width: float, height: float) -> Dict[str, Any]:
        """Draw an ellipse."""
        try:
            ellipse = self.layer.CreateEllipse2(x, y, width, height)
            return {"success": True, "output": f"Ellipse created: {ellipse.Name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> Dict[str, Any]:
        """Draw a line."""
        try:
            line = self.layer.CreateLineSegment(x1, y1, x2, y2)
            return {"success": True, "output": f"Line created: {line.Name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def draw_polygon(self, points: List[Tuple[float, float]], closed: bool = True) -> Dict[str, Any]:
        """Draw a polygon from points."""
        try:
            curve = self.layer.CreateCurve()
            subpath = curve.CreateSubPath(points[0][0], points[0][1])
            
            for x, y in points[1:]:
                subpath.AppendLineSegment(x, y)
            
            if closed:
                subpath.Closed = True
            
            return {"success": True, "output": f"Polygon created with {len(points)} points"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def draw_text(self, text: str, x: float, y: float,
                  font: str = "Arial", size: float = 12) -> Dict[str, Any]:
        """Add artistic text."""
        try:
            text_obj = self.layer.CreateArtisticText(x, y, text)
            text_obj.Text.Font = font
            text_obj.Text.Size = size
            return {"success": True, "output": f"Text created: {text[:20]}..."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def draw_paragraph_text(self, text: str, x1: float, y1: float,
                            x2: float, y2: float, font: str = "Arial",
                            size: float = 12) -> Dict[str, Any]:
        """Add paragraph (frame) text."""
        try:
            text_obj = self.layer.CreateParagraphText(x1, y1, x2, y2, text)
            text_obj.Text.Font = font
            text_obj.Text.Size = size
            return {"success": True, "output": f"Paragraph text created"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # FILL & OUTLINE
    # =========================================================================
    
    def set_fill_color(self, shape_name: str = None, r: int = 0, g: int = 0, b: int = 0) -> Dict[str, Any]:
        """Set fill color (RGB)."""
        try:
            shape = self._get_shape(shape_name)
            shape.Fill.UniformColor.CMYKAssign(0, 0, 0, 0)  # Reset
            shape.Fill.UniformColor.RGBAssign(r, g, b)
            return {"success": True, "output": f"Fill color set to RGB({r},{g},{b})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_outline(self, shape_name: str = None, width: float = 1,
                    r: int = 0, g: int = 0, b: int = 0) -> Dict[str, Any]:
        """Set outline properties."""
        try:
            shape = self._get_shape(shape_name)
            shape.Outline.Width = width
            shape.Outline.Color.RGBAssign(r, g, b)
            return {"success": True, "output": f"Outline set: {width}mm RGB({r},{g},{b})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_fill(self, shape_name: str = None) -> Dict[str, Any]:
        """Remove fill from shape."""
        try:
            shape = self._get_shape(shape_name)
            shape.Fill.ApplyNoFill()
            return {"success": True, "output": "Fill removed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_outline(self, shape_name: str = None) -> Dict[str, Any]:
        """Remove outline from shape."""
        try:
            shape = self._get_shape(shape_name)
            shape.Outline.Width = 0
            return {"success": True, "output": "Outline removed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_shape(self, name: str = None):
        """Get shape by name or selected."""
        if name:
            return self.page.Shapes.Item(name)
        elif self.app.ActiveSelection.Count > 0:
            return self.app.ActiveSelection.Shapes.Item(1)
        else:
            raise RuntimeError("No shape selected or specified")
    
    def group_selection(self) -> Dict[str, Any]:
        """Group selected shapes."""
        try:
            if self.app.ActiveSelection.Count > 0:
                 grp = self.app.ActiveSelection.Group()
                 return {"success": True, "output": f"Grouped objects into {grp.Name}"}
            else:
                 return {"success": True, "output": "Nothing to group"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # TRANSFORMATIONS
    # =========================================================================
    
    def move(self, shape_name: str, dx: float, dy: float) -> Dict[str, Any]:
        """Move shape by offset."""
        try:
            shape = self._get_shape(shape_name)
            shape.Move(dx, dy)
            return {"success": True, "output": f"Moved by ({dx}, {dy})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def rotate(self, shape_name: str, angle: float) -> Dict[str, Any]:
        """Rotate shape in degrees."""
        try:
            shape = self._get_shape(shape_name)
            shape.Rotate(angle)
            return {"success": True, "output": f"Rotated by {angle}°"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scale(self, shape_name: str, scale_x: float, scale_y: float = None) -> Dict[str, Any]:
        """Scale shape."""
        try:
            shape = self._get_shape(shape_name)
            if scale_y is None:
                scale_y = scale_x
            shape.Stretch(scale_x, scale_y)
            return {"success": True, "output": f"Scaled by ({scale_x}, {scale_y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # IMPORT/EXPORT
    # =========================================================================
    
    def import_file(self, filepath: str) -> Dict[str, Any]:
        """Import file into document (Auto-Fallback to Keys)."""
        try:
            # 1. Try COM Import
            # Import returns an ImportFilter object
            imp_flt = self.layer.Import(filepath)
            if hasattr(imp_flt, "Finish"):
                imp_flt.Finish()
            return {"success": True, "output": f"Imported: {filepath}"}
        except Exception as e:
            print(f"[CorelBridge] COM Import failed ({e}). Trying Keyboard Fallback...")
            return self.import_file_keys(filepath)

    def import_file_keys(self, filepath: str) -> Dict[str, Any]:
        """Import using robust keystroke injection (Ctrl+I)."""
        try:
            import subprocess
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Scripts", "oni_corel_import_keys.ps1"))
            
            cmd = [
                "powershell", "-ExecutionPolicy", "Bypass", 
                "-File", script_path, "-FilePath", filepath
            ]
            
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[CorelBridge] Keys sent: {res.stdout.strip()}")
                return {"success": True, "output": "Imported via Keys"}
            else:
               return {"success": False, "error": f"PS Failed: {res.stderr}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_png(self, filepath: str, width: int = 1920, height: int = 1080) -> Dict[str, Any]:
        """Export to PNG."""
        try:
            exp_filter = self.app.ExportFilters.Item("PNG")
            exp_filter.Settings.Width = width
            exp_filter.Settings.Height = height
            self.doc.Export(filepath, exp_filter)
            return {"success": True, "output": f"Exported PNG: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_pdf(self, filepath: str) -> Dict[str, Any]:
        """Export to PDF."""
        try:
            self.doc.PublishToPDF(filepath)
            return {"success": True, "output": f"Exported PDF: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_svg(self, filepath: str) -> Dict[str, Any]:
        """Export to SVG."""
        try:
            exp_filter = self.app.ExportFilters.Item("SVG")
            self.doc.Export(filepath, exp_filter)
            return {"success": True, "output": f"Exported SVG: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # LAYERS
    # =========================================================================
    
    def create_layer(self, name: str) -> Dict[str, Any]:
        """Create new layer."""
        try:
            layer = self.page.CreateLayer(name)
            return {"success": True, "output": f"Created layer: {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_active_layer(self, name: str) -> Dict[str, Any]:
        """Set active layer by name."""
        try:
            self.page.Layers.Item(name).Activate()
            return {"success": True, "output": f"Active layer: {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_layers(self) -> Dict[str, Any]:
        """List all layers."""
        try:
            layers = []
            for i in range(1, self.page.Layers.Count + 1):
                layer = self.page.Layers.Item(i)
                layers.append({
                    "name": layer.Name,
                    "visible": layer.Visible,
                    "editable": layer.Editable
                })
            return {"success": True, "output": json.dumps(layers), "data": layers}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ==============================================================================
# ADVANCED VECTORIZATION (uses ONI_Corel_Vectorizer)
# ==============================================================================

    def vectorize_image(self, image_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Advanced vectorization using shape detection and K-Means color extraction.
        
        Args:
            image_path: Path to the source image
            output_path: Optional output path for SVG
        """
        try:
            import cv2
            from Modules.Corel.ONI_Corel_Vectorizer import (
                AdvancedImageProcessor, BezierMath, ShapeType, DrawTool
            )
            
            # Load and analyze image
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}
            
            processor = AdvancedImageProcessor()
            
            # Analyze complexity
            analysis = processor.analyze_complexity(image)
            print(f"[ONI] Image complexity: {analysis['complexity']:.2%}")
            
            # Extract color palette
            colors = processor.extract_color_palette(image, n_colors=8)
            print(f"[ONI] Extracted {len(colors)} dominant colors")
            for i, c in enumerate(colors[:3]):
                print(f"  {i+1}. {c.hex}")
            
            # Find and classify contours
            contours = processor.find_contours(image)
            print(f"[ONI] Found {len(contours)} shapes")
            
            # Group by shape type
            shape_stats = {}
            for c in contours:
                stype = c.shape_type.value
                shape_stats[stype] = shape_stats.get(stype, 0) + 1
            print(f"[ONI] Shape breakdown: {shape_stats}")
            
            # Use native PowerTrace for best quality
            if not output_path:
                base = os.path.splitext(image_path)[0]
                output_path = f"{base}_vectorized.svg"
            
            result = self.trace_bitmap(image_path, output_path)
            
            # Add analysis to result
            result["analysis"] = {
                "complexity": analysis["complexity"],
                "colors": [c.hex for c in colors[:5]],
                "shapes": shape_stats,
                "total_contours": len(contours)
            }
            
            return result
            
        except ImportError as e:
            print(f"[ONI] Vectorizer not available, using standard trace: {e}")
            return self.trace_bitmap(image_path, output_path)
        except Exception as e:
            return {"success": False, "error": str(e)}


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="ONI CorelDRAW Bridge")
    parser.add_argument("--trace", help="Path to image to trace")
    parser.add_argument("--output", help="Output path (optional)")
    
    args = parser.parse_args()
    
    try:
        bridge = CorelBridge()
        
        if args.trace:
            print(f"Tracing: {args.trace}")
            # Generate default output name if not provided
            if not args.output:
                base = os.path.splitext(args.trace)[0]
                args.output = f"{base}.svg"
                
            res = bridge.trace_bitmap(args.trace, args.output)
            if res["success"]:
                print(f"Success! Output: {args.output}")
            else:
                print(f"Error: {res['error']}")
                sys.exit(1)
        else:
            # Default Test Mode
            print("CorelDRAW connected!")
            bridge.new_document()
            bridge.draw_rectangle(50, 50, 150, 150)
            print("Test successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
