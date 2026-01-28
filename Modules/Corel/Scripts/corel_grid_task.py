import win32com.client
import os

def cm_to_doc(val_cm):
    return val_cm * 10.0 # to mm

def main():
    try:
        print("Connecting to CorelDRAW 2026...")
        corel = win32com.client.Dispatch("CorelDRAW.Application.26")
        corel.Visible = True
        
        # New Document
        doc = corel.CreateDocument()
        
        # Setup Page: A4 (210 x 297 mm)
        # Set Unit to Millimeters (CDR Unit 4 = Millimeters)
        doc.Unit = 4 
        
        # Landscape A4: 297 width, 210 height
        doc.ActivePage.SetSize(297, 210)
        doc.ActivePage.Orientation = 2 # 2 = Landscape
        
        print("Creating Grid Layer...")
        # --- 1. DRAW BACKGROUND GRID ---
        layer_grid = doc.ActivePage.CreateLayer("GRID_BACKGROUND")
        layer_grid.Editable = True
        
        # 5mm Grid
        # Major lines every 10mm (Gray 50%)
        # Minor lines every 5mm (Gray 20%)
        
        # Draw Minor Lines first (Background)
        
        # We need to set Outline properties for lines
        # Corel lines take current outline properties? Or we set 'em after?
        # CreateLineSegment returns a Shape.
        
        # NOTE: Drawing many lines individually via COM is slow.
        # But for A4 it's manageable (approx 60 + 40 lines).
        
        lines_minor = []
        lines_major = []
        
        print("Drawing Vertical Grid...")
        # Verticals (Width 297)
        lines_minor = []
        lines_major = []
        
        # Create Colors
        col_major = corel.CreateColor()
        col_major.CMYKAssign(0, 0, 0, 50)
        
        col_minor = corel.CreateColor()
        col_minor.CMYKAssign(0, 0, 0, 20)
        
        print("Drawing Vertical Grid...")
        # Verticals (Width 297)
        for x in range(0, 300, 5):
            shape = layer_grid.CreateLineSegment(x, 0, x, 210)
            if x % 10 == 0:
                shape.Outline.Width = 0.2
                shape.Outline.Color = col_major
            else:
                shape.Outline.Width = 0.1
                shape.Outline.Color = col_minor
                
        print("Drawing Horizontal Grid...")
        # Horizontals (Height 210)
        for y in range(0, 215, 5):
            shape = layer_grid.CreateLineSegment(0, y, 297, y)
            if y % 10 == 0:
                shape.Outline.Width = 0.2
                shape.Outline.Color = col_major
            else:
                shape.Outline.Width = 0.1
                shape.Outline.Color = col_minor
        
        # Lock Grid
        layer_grid.Editable = False
        
        # --- 2. IMPORT DXF ---
        print("Creating Mold Layer...")
        layer_mold = doc.ActivePage.CreateLayer("MOLD_DXF")
        layer_mold.Activate()
        
        dxf_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "ONIV24", "temp", "mold_final.dxf")
        
        if not os.path.exists(dxf_path):
             print(f"DXF file NOT found at {dxf_path}!")
             return

        print(f"Importing {dxf_path}...")
        try:
            # 1805 = DXF filter ID. 0 = Auto.
            imp_filter = layer_mold.Import(dxf_path, 1805)
            imp_filter.Finish() 
        except Exception as e:
            print(f"Import Error: {e}")
            # Fallback: SendKeys? No, let's just trace.
            import traceback
            traceback.print_exc()
            
        print("Import Finished. Grouping and Centering...")
        
        # Center on Page
        # Center X = 297/2 = 148.5
        # Center Y = 210/2 = 105.0
        
        # Select imported shapes
        # If import keeps selection, good. If not, select all on layer.
        sel = doc.ActiveSelection
        if sel.Shapes.Count == 0:
            sel = layer_mold.Shapes.All()
            
        if sel.Shapes.Count > 0:
            grp = sel.Group()
            grp.CenterX = 148.5
            grp.CenterY = 105.0
            print("Centered MOLD.")
        else:
            print("Warning: No shapes found after import.")
        
        print("SUCCESS: A4 Grid setup complete.")
        
    except Exception as e:
        print(f"Corel Automation Failed: {e}")

if __name__ == "__main__":
    main()
