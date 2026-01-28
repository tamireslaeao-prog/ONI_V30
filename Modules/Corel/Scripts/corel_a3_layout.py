
import win32com.client
import os

def cm_to_doc(val_cm):
    # Corel Default is usually inches or current doc unit.
    # Safe bet: use Millimeters if we set unit.
    return val_cm * 10.0 # to mm

def main():
    try:
        corel = win32com.client.Dispatch("CorelDRAW.Application")
        corel.Visible = True
        
        # New Document
        doc = corel.CreateDocument()
        
        # Setup Page: A3 (297 x 420 mm)
        # 415 height fits better in 420 (Portrait)
        # Set Unit to Millimeters (CDR Unit 4 = Millimeters)
        doc.Unit = 4 
        
        doc.ActivePage.SetSize(297, 420)
        doc.ActivePage.Orientation = 1 # 1 = Portrait, 2 = Landscape
        
        print("DEBUG: Creating Grid Layer")
        # --- 1. DRAW BACKGROUND GRID (1x1cm) ---
        layer_grid = doc.ActivePage.CreateLayer("GRID_BACKGROUND")
        layer_grid.Editable = True
        
        # Draw Vertical Lines (every 10mm)
        # Canvas: 0 to 297 width, 0 to 420 height
        
        lines = []
        
        # Verticals
        print("DEBUG: Drawing Lines")
        for x in range(0, 300, 10):
            layer_grid.CreateLineSegment(x, 0, x, 420)
            
        # Horizontals
        for y in range(0, 430, 10):
            layer_grid.CreateLineSegment(0, y, 297, y)
            
        # Group Grid and Lock
        # (Grouping logical objects in loop might be slow if standard list, Corel handles shapes)
        # For simplicity, just lock the layer
        layer_grid.Editable = False
        layer_grid.Visible = True
        
        
        # --- 2. IMPORT DXF ---
        print("DEBUG: Creating Mold Layer")
        layer_mold = doc.ActivePage.CreateLayer("MOLD_DXF")
        layer_mold.Activate()
        
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        # AutoCAD added .dwg extension to our .dxf filename
        dxf_path = os.path.join(desktop, "box_mold_export.dxf.dwg")
        
        if not os.path.exists(dxf_path):
             # Try without .dwg just in case
             dxf_path = os.path.join(desktop, "box_mold_export.dxf")
             if not os.path.exists(dxf_path):
                 print(f"DXF file NOT found at {dxf_path}!")
                 return

        print(f"DEBUG: Importing {dxf_path}")
        # 1805 = DXF in some versions, 0 = Auto.
        # Try passing just the path again but verify path string encoding?
        # Let's try explicit AutoSense (0)
        try:
            imp_filter = layer_mold.Import(dxf_path, 0)
        except Exception:
            # Fallback for some versions
            imp_filter = layer_mold.Import(dxf_path)
            
        print("DEBUG: Import Called")
        imp_filter.Finish()  # Complete import
        print("DEBUG: Import Finished")
        
        # The imported objects are selected usually.
        # Let's Group and Center.
        sel = doc.ActiveSelection
        if sel.Shapes.Count == 0:
            # Maybe need to select all on layer
            sel = layer_mold.Shapes.All()
            
        print("DEBUG: Grouping")
        grp = sel.Group()
        
        # Center on Page
        # Center X = 297/2 = 148.5
        # Center Y = 420/2 = 210
        print("DEBUG: Centering")
        grp.CenterX = 148.5
        grp.CenterY = 210.0
        
        print("Imported and centered in CorelDRAW A3.")
        
    except Exception as e:
        print(f"Corel Automation Failed: {e}")

if __name__ == "__main__":
    main()
