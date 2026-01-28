"""
ONI AutoCAD Bridge - Python COM Automation
Version: 1.0.0
Date: 2026-01-14

Complete Python interface for AutoCAD automation via ActiveX COM.
Supports drawing primitives, text, dimensions, layers, and file operations.

Usage:
    from ONI_AutoCAD_Bridge import AutoCADBridge
    
    cad = AutoCADBridge()
    cad.connect()
    cad.draw_line(0, 0, 100, 100)
    cad.save("output.dwg")
"""

import win32com.client
import pythoncom
import os
import time
from typing import Optional, Tuple, List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ONI_AutoCAD")


class AutoCADBridge:
    """
    ONI AutoCAD Bridge - Complete COM Automation Interface
    
    Provides methods for:
    - Connection management
    - Drawing primitives (lines, circles, rectangles, polylines)
    - Text and dimensions
    - Layer management
    - File operations (new, open, save, export)
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.acad = None
        self.doc = None
        self.model_space = None
        self._connected = False
        
    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================
    
    def connect(self, create_new_doc: bool = True) -> bool:
        """
        Connect to AutoCAD via COM.
        
        Args:
            create_new_doc: If True, creates a new document if none is open
            
        Returns:
            True if connection successful
        """
        try:
            # Try to get running instance
            try:
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                logger.info("Connected to existing AutoCAD instance")
            except:
                # Start new instance
                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                logger.info("Started new AutoCAD instance")
            
            # Make visible
            self.acad.Visible = True
            
            # Get or create document
            if self.acad.Documents.Count == 0:
                if create_new_doc:
                    self.doc = self.acad.Documents.Add()
                    logger.info("Created new document")
                else:
                    raise Exception("No document open and create_new_doc=False")
            else:
                self.doc = self.acad.ActiveDocument
                logger.info(f"Using active document: {self.doc.Name}")
            
            # Get model space
            self.model_space = self.doc.ModelSpace
            self._connected = True
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Safely disconnect from AutoCAD."""
        self.model_space = None
        self.doc = None
        self.acad = None
        self._connected = False
        logger.info("Disconnected from AutoCAD")
    
    def is_connected(self) -> bool:
        """Check if connected to AutoCAD."""
        return self._connected and self.acad is not None
    
    def get_info(self) -> dict:
        """Get AutoCAD and document info."""
        if not self.is_connected():
            return {"error": "Not connected"}
        
        return {
            "version": self.acad.Version,
            "document": self.doc.Name if self.doc else None,
            "path": self.doc.Path if self.doc else None,
            "saved": self.doc.Saved if self.doc else None,
            "units": self._get_units()
        }
    
    def _get_units(self) -> str:
        """Get current drawing units."""
        try:
            units = self.doc.GetVariable("INSUNITS")
            units_map = {
                0: "Unitless", 1: "Inches", 2: "Feet", 3: "Miles",
                4: "Millimeters", 5: "Centimeters", 6: "Meters"
            }
            return units_map.get(units, f"Unknown({units})")
        except:
            return "Unknown"
    
    # =========================================================================
    # DRAWING PRIMITIVES
    # =========================================================================
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float, z1: float = 0, z2: float = 0):
        """
        Draw a line from (x1, y1, z1) to (x2, y2, z2).
        
        Args:
            x1, y1: Start point
            x2, y2: End point
            z1, z2: Z coordinates (default 0 for 2D)
            
        Returns:
            Line object
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        start_point = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x1, y1, z1])
        end_point = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x2, y2, z2])
        
        line = self.model_space.AddLine(start_point, end_point)
        logger.debug(f"Drew line: ({x1},{y1}) to ({x2},{y2})")
        return line
    
    def draw_circle(self, center_x: float, center_y: float, radius: float, center_z: float = 0):
        """
        Draw a circle.
        
        Args:
            center_x, center_y: Center point
            radius: Circle radius
            center_z: Z coordinate (default 0)
            
        Returns:
            Circle object
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        center = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [center_x, center_y, center_z])
        circle = self.model_space.AddCircle(center, radius)
        logger.debug(f"Drew circle: center ({center_x},{center_y}), radius {radius}")
        return circle
    
    def draw_arc(self, center_x: float, center_y: float, radius: float, 
                 start_angle: float, end_angle: float, center_z: float = 0):
        """
        Draw an arc.
        
        Args:
            center_x, center_y: Center point
            radius: Arc radius
            start_angle, end_angle: Angles in radians
            
        Returns:
            Arc object
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        import math
        center = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [center_x, center_y, center_z])
        arc = self.model_space.AddArc(center, radius, start_angle, end_angle)
        return arc
    
    def draw_rectangle(self, x: float, y: float, width: float, height: float):
        """
        Draw a rectangle using polyline.
        
        Args:
            x, y: Bottom-left corner
            width, height: Dimensions
            
        Returns:
            Polyline object
        """
        points = [
            x, y,
            x + width, y,
            x + width, y + height,
            x, y + height,
            x, y  # Close rectangle
        ]
        return self.draw_polyline(points, closed=True)
    
    def draw_polyline(self, points: List[float], closed: bool = False):
        """
        Draw a 2D polyline.
        
        Args:
            points: List of [x1, y1, x2, y2, ...] coordinates
            closed: If True, closes the polyline
            
        Returns:
            Polyline object
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        pts_variant = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, points)
        pline = self.model_space.AddLightWeightPolyline(pts_variant)
        
        if closed:
            pline.Closed = True
        
        logger.debug(f"Drew polyline with {len(points)//2} vertices")
        return pline
    
    def draw_3d_polyline(self, points: List[float]):
        """
        Draw a 3D polyline.
        
        Args:
            points: List of [x1, y1, z1, x2, y2, z2, ...] coordinates
            
        Returns:
            3D Polyline object
        """
        pts_variant = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, points)
        pline3d = self.model_space.Add3DPoly(pts_variant)
        return pline3d
    
    def draw_ellipse(self, center_x: float, center_y: float, 
                     major_axis_x: float, major_axis_y: float, 
                     radius_ratio: float):
        """
        Draw an ellipse.
        
        Args:
            center_x, center_y: Center point
            major_axis_x, major_axis_y: Major axis endpoint (relative to center)
            radius_ratio: Minor/Major axis ratio (0-1)
            
        Returns:
            Ellipse object
        """
        center = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [center_x, center_y, 0])
        major_axis = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [major_axis_x, major_axis_y, 0])
        
        ellipse = self.model_space.AddEllipse(center, major_axis, radius_ratio)
        return ellipse
    
    # =========================================================================
    # TEXT AND ANNOTATIONS
    # =========================================================================
    
    def add_text(self, text: str, x: float, y: float, height: float = 2.5, 
                 rotation: float = 0, z: float = 0):
        """
        Add single-line text.
        
        Args:
            text: Text content
            x, y: Insertion point
            height: Text height
            rotation: Rotation angle in degrees
            
        Returns:
            Text object
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        import math
        insertion = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])
        text_obj = self.model_space.AddText(text, insertion, height)
        
        if rotation != 0:
            text_obj.Rotation = math.radians(rotation)
        
        logger.debug(f"Added text: '{text}' at ({x},{y})")
        return text_obj
    
    def add_mtext(self, text: str, x: float, y: float, width: float, height: float = 2.5):
        """
        Add multi-line text (MText).
        
        Args:
            text: Text content (supports formatting)
            x, y: Insertion point
            width: Text box width
            height: Text height
            
        Returns:
            MText object
        """
        insertion = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, 0])
        mtext = self.model_space.AddMText(insertion, width, text)
        mtext.Height = height
        return mtext
    
    def add_dimension_linear(self, x1: float, y1: float, x2: float, y2: float, 
                              dim_line_location: float):
        """
        Add a linear dimension.
        
        Args:
            x1, y1: First extension line origin
            x2, y2: Second extension line origin
            dim_line_location: Y position of dimension line
            
        Returns:
            Dimension object
        """
        ext1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x1, y1, 0])
        ext2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x2, y2, 0])
        dim_loc = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [
            (x1 + x2) / 2, dim_line_location, 0
        ])
        
        dim = self.model_space.AddDimAligned(ext1, ext2, dim_loc)
        return dim
    
    # =========================================================================
    # LAYER MANAGEMENT
    # =========================================================================
    
    def create_layer(self, name: str, color: int = 7) -> bool:
        """
        Create a new layer.
        
        Args:
            name: Layer name
            color: ACI color index (1-255)
            
        Returns:
            True if created successfully
        """
        if not self.is_connected():
            return False
        
        try:
            layer = self.doc.Layers.Add(name)
            layer.Color = color
            logger.info(f"Created layer: {name} (color: {color})")
            return True
        except Exception as e:
            logger.warning(f"Layer creation failed: {e}")
            return False
    
    def set_layer(self, name: str) -> bool:
        """
        Set current layer.
        
        Args:
            name: Layer name
            
        Returns:
            True if set successfully
        """
        if not self.is_connected():
            return False
        
        try:
            self.doc.ActiveLayer = self.doc.Layers.Item(name)
            return True
        except:
            return False
    
    def get_layers(self) -> List[str]:
        """Get list of all layer names."""
        if not self.is_connected():
            return []
        
        return [layer.Name for layer in self.doc.Layers]
    
    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================
    
    def new_document(self, template: Optional[str] = None) -> bool:
        """
        Create a new document.
        
        Args:
            template: Optional .dwt template path
            
        Returns:
            True if created successfully
        """
        try:
            if template:
                self.doc = self.acad.Documents.Add(template)
            else:
                self.doc = self.acad.Documents.Add()
            
            self.model_space = self.doc.ModelSpace
            logger.info("Created new document")
            return True
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return False
    
    def open_document(self, path: str) -> bool:
        """
        Open an existing document.
        
        Args:
            path: Full path to .dwg file
            
        Returns:
            True if opened successfully
        """
        try:
            self.doc = self.acad.Documents.Open(path)
            self.model_space = self.doc.ModelSpace
            logger.info(f"Opened: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to open: {e}")
            return False
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save document.
        
        Args:
            path: If provided, SaveAs to this path
            
        Returns:
            True if saved successfully
        """
        if not self.is_connected():
            return False
        
        try:
            if path:
                self.doc.SaveAs(path)
                logger.info(f"Saved as: {path}")
            else:
                self.doc.Save()
                logger.info("Document saved")
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False
    
    def close(self, save: bool = True) -> bool:
        """
        Close current document.
        
        Args:
            save: If True, save before closing
            
        Returns:
            True if closed successfully
        """
        if not self.is_connected():
            return False
        
        try:
            if save:
                self.doc.Close(True)
            else:
                self.doc.Close(False)
            
            self.doc = None
            self.model_space = None
            return True
        except Exception as e:
            logger.error(f"Close failed: {e}")
            return False
    
    def export_pdf(self, output_path: str) -> bool:
        """
        Export current drawing to PDF.
        
        Args:
            output_path: Output PDF path
            
        Returns:
            True if exported successfully
        """
        if not self.is_connected():
            return False
        
        try:
            # Use PLOT command or DWG to PDF.pc3
            self.send_command(f'-PLOT Y  DWG To PDF.pc3 ISO A3 (420.00 x 297.00 MM) M P N "{output_path}" N Y')
            logger.info(f"Exported PDF: {output_path}")
            return True
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return False
    
    def export_dxf(self, output_path: str) -> bool:
        """
        Export current drawing to DXF.
        
        Args:
            output_path: Output DXF path
            
        Returns:
            True if exported successfully
        """
        if not self.is_connected():
            return False
        
        try:
            self.doc.SaveAs(output_path, 1)  # acR12_dxf = 1
            logger.info(f"Exported DXF: {output_path}")
            return True
        except Exception as e:
            logger.error(f"DXF export failed: {e}")
            return False
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def send_command(self, command: str) -> None:
        """
        Send command to AutoCAD command line.
        
        Args:
            command: Command string (include spaces for Enter)
        """
        if not self.is_connected():
            raise Exception("Not connected to AutoCAD")
        
        self.doc.SendCommand(command + "\n")
    
    def zoom_extents(self) -> None:
        """Zoom to show all objects."""
        self.send_command("ZOOM E ")
    
    def zoom_all(self) -> None:
        """Zoom to drawing limits."""
        self.send_command("ZOOM A ")
    
    def regen(self) -> None:
        """Regenerate drawing."""
        self.send_command("REGEN ")
    
    def set_units(self, units: int = 4) -> None:
        """
        Set drawing units.
        
        Args:
            units: 0=Unitless, 1=Inches, 2=Feet, 4=Millimeters, 5=Centimeters, 6=Meters
        """
        if self.is_connected():
            self.doc.SetVariable("INSUNITS", units)
    
    def get_selection(self) -> list:
        """Get currently selected objects."""
        if not self.is_connected():
            return []
        
        selection = self.doc.SelectionSets.Add(f"ONI_Sel_{time.time()}")
        selection.SelectOnScreen()
        objects = list(selection)
        selection.Delete()
        return objects
    
    def delete_all(self) -> None:
        """Delete all objects in model space."""
        if not self.is_connected():
            return
        
        for i in range(self.model_space.Count - 1, -1, -1):
            try:
                self.model_space.Item(i).Delete()
            except:
                pass
        
        logger.info("Deleted all objects")


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    print("ONI AutoCAD Bridge - Test")
    print("=" * 50)
    
    cad = AutoCADBridge()
    
    if cad.connect():
        print("[OK] Connected to AutoCAD")
        print(f"Version: {cad.get_info()}")
        
        # Test drawing
        cad.draw_rectangle(0, 0, 100, 50)
        cad.draw_circle(50, 25, 20)
        cad.add_text("ONI Test", 10, 60, 5)
        cad.zoom_extents()
        
        print("[OK] Test drawing complete")
        print("Check AutoCAD window for results")
    else:
        print("[ERROR] Failed to connect to AutoCAD")
