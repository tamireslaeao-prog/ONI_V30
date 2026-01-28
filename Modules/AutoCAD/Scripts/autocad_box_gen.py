
import win32com.client
import pythoncom
import math
import array

def connect_to_autocad():
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
    except:
        # Create a new instance if not running (though we tried starting it via PS)
        acad = win32com.client.Dispatch("AutoCAD.Application")
    
    acad.Visible = True
    return acad

def draw_polyline(ms, points, layer="0"):
    # Flatten list
    flat_points = []
    for x, y in points:
        flat_points.extend([float(x), float(y)])
    
    # Convert to Variant/Array (Double)
    # pywin32 usually handles list of floats automatically for methods requiring arrays
    # But for LightweightPolyline we pass a flat list of doubles.
    
    try:
        # Create Lightweight Polyline
        # Coordinates are 2D (x, y)
        import array
        # COM expects a variant array of doubles. 
        # In win32com, passing a python list of floats usually works.
        pline = ms.AddLightweightPolyline(flat_points)
        pline.Layer = layer
        pline.Closed = True
        return pline
    except Exception as e:
        print(f"Error drawing polyline: {e}")
        return None


def to_point(x, y, z=0.0):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])

def main():
    try:
        acad = connect_to_autocad()
        
        try:
            doc = acad.ActiveDocument
        except:
            doc = None
            
        # If no active document (Start Sreen), add one
        if doc is None or doc.ModelSpace is None:
            print("No active document found. Creating new...")
            doc = acad.Documents.Add()
            
        ms = doc.ModelSpace
        
        # Units: MM (User said CM, we convert to MM for precision)
        # 1 cm = 10 mm
        
        # --- LAYERS ---
        try:
            l_cut = doc.Layers.Add("CORTE")
            l_cut.color = 7 # White/Black
            l_fold = doc.Layers.Add("DOBRA")
            l_fold.color = 1 # Red
        except:
            pass # Layer exists
            
        # --- GEOMETRY POINTS (MM) ---
        # Origin (0,0) is bottom-left of the main body (excluding bottom flap)
        # Actually let's use global coords.
        
        # Dimensions
        W_BODY = 95.0  # 9.5 cm
        H_BOT_FLAP = 120.0 # 12 cm
        H_SEC_1 = 90.0   # 9 cm (attached to left flap)
        H_SEC_2 = 120.0  # 12 cm
        H_TOP_LID = 85.0 # 8.5 cm (actually 41.5 total check: 12+9+12+8.5 = 41.5)
        
        # Y Levels
        Y0 = 0 # Bottom of Bottom Flap
        Y1 = Y0 + H_BOT_FLAP # Joint 1 (120)
        Y2 = Y1 + H_SEC_1    # Joint 2 (210)
        Y3 = Y2 + H_SEC_2    # Joint 3 (330)
        Y4 = Y3 + H_TOP_LID  # Top (415)
        
        # X Levels
        X0 = 0             # Left Edge of Body
        X1 = W_BODY        # Right Edge of Body
        

        # --- 1. MAIN OUTLINE (Corte) ---
        # Revised for Rounded Corner and Holes
        
        # Corner Parameters
        R_CORNER = 50.0
        
        # Points for Rounded Top-Right Corner
        # Previous Top-Right was (X1, Y4).
        # New geometry:
        # Line up to (X1, Y4 - R_CORNER)
        # Arc centered at (X1 - R_CORNER, Y4 - R_CORNER)
        # Line from (X1 - R_CORNER, Y4) to Left
        
        # --- 1. MAIN OUTLINE (Corte) ---
        # Revised for Rounded Corner (NOW ON LEFT)
        
        # Corner Parameters
        R_CORNER = 50.0
        
        # New Geometry Logic (Curve on Left):
        # 1. Right side goes straight up to (X1, Y4).
        # 2. Top side goes left from (X1, Y4) to (X0 + R, Y4).
        # 3. Arc at Top-Left.
        # 4. Left side goes down from (X0, Y4 - R) to (X0, Y2).
        
        lines_list = [
            ((X0, Y0), (X1, Y0)),               # Bottom
            ((X1, Y0), (X1, Y3)),               # Right Wall (Body)
            ((X1, Y3), (X1, Y4)),               # Lid Right (Straight up to Top-Right)
            ((X1, Y4), (X0 + R_CORNER, Y4)),    # Lid Top (Right to start of Left Arc)
            # ((X0 + R, Y4) ... Arc ... (X0, Y4 - R))
            ((X0, Y4 - R_CORNER), (X0, Y2)),    # Lid Left (from arc end down)
            
            ((X0, Y2), (X0-80, Y2-5)),          # Flap Top Edge
            ((X0-80, Y2-5), (X0-80, Y1+5)),     # Flap Left Edge
            ((X0-80, Y1+5), (X0, Y1)),          # Flap Bottom Edge
            ((X0, Y1), (X0, Y0))                # Bottom Wall
        ]
        
        # Draw Straight Lines
        for start, end in lines_list:
            try:
                p1 = to_point(start[0], start[1], 0.0)
                p2 = to_point(end[0], end[1], 0.0)
                line = ms.AddLine(p1, p2)
                line.Layer = "CORTE"
            except Exception as ex:
                print(f"Failed to draw line {start}->{end}: {ex}")
        
        # Draw Corner Arc (Top Left)
        try:
            center = to_point(X0 + R_CORNER, Y4 - R_CORNER, 0.0)
            # Arc from Top (90 deg / pi/2) to Left (180 deg / pi)
            arc = ms.AddArc(center, R_CORNER, math.pi/2, math.pi)
            arc.Layer = "CORTE"
        except Exception as ex:
            print(f"Failed to draw arc: {ex}")

        # --- 2. HOLES (Furos) ---
        # 2 Holes, 5mm diameter (R=2.5).
        # Locations approximated from image logic.
        R_HOLE = 2.5
        holes_coords = [
            (X1 - 15, Y4 - 42.5),  # Top Lid (centered vertically in 85mm? No, looks higher)
                                   # Let's put it near the arc.
            (X1 - 15, Y0 + 15)     # Bottom Corner?
        ]
        
        for hx, hy in holes_coords:
            try:
                cen = to_point(hx, hy, 0.0)
                circ = ms.AddCircle(cen, R_HOLE)
                circ.Layer = "CORTE"
            except Exception as ex:
                print(f"Failed to draw hole at ({hx},{hy}): {ex}")


        # --- 3. FOLD LINES (Dobra) ---
        folds = [
            [(X0, Y1), (X1, Y1)],
            [(X0, Y2), (X1, Y2)],
            [(X0, Y3), (X1, Y3)],
        ]
        
        for p1, p2 in folds:
            try:
                pt1 = to_point(p1[0], p1[1], 0.0)
                pt2 = to_point(p2[0], p2[1], 0.0)
                line = ms.AddLine(pt1, pt2)
                line.Layer = "DOBRA"
            except Exception as ex:
                print(f"Failed to draw fold {p1}->{p2}: {ex}")
                
        # --- 4. DIMENSIONS (Cotas) ---
        # Add layer COTAS
        try:
            l_dim = doc.Layers.Add("COTAS")
            l_dim.color = 3 # Green
        except:
            pass
            
        dims_data = [
            # Vertical Left Chain
            ((X0-10, Y0), (X0-10, Y1), (X0-20, (Y0+Y1)/2), "12cm"),
            ((X0-10, Y1), (X0-10, Y2), (X0-20, (Y1+Y2)/2), "9cm"),
            ((X0-10, Y2), (X0-10, Y3), (X0-20, (Y2+Y3)/2), "12cm"),
            ((X0-10, Y3), (X0-10, Y4), (X0-20, (Y3+Y4)/2), "8.5cm"), # Lid Height
            
            # Horizontal Bottom
            ((X0, Y0-10), (X1, Y0-10), ((X0+X1)/2, Y0-20), "9.5cm"),
            
            # Flap Width
            ((X0, Y2+10), (X0-80, Y2+10), (X0-40, Y2+20), "8cm"),
            
            # Radius Label?
            # Creating a text for radius "R5cm" at the corner
            # Using simple MText for now
        ]
        
        for p1, p2, loc, txt in dims_data:
            try:
                pt1 = to_point(p1[0], p1[1])
                pt2 = to_point(p2[0], p2[1])
                pt_loc = to_point(loc[0], loc[1])
                
                # AddDimAligned(ExtLine1Point, ExtLine2Point, TextPosition)
                dim = ms.AddDimAligned(pt1, pt2, pt_loc)
                dim.Layer = "COTAS"
                # dim.TextOverride = txt # Let AutoCAD measure it? Or force text?
                # User asked for "cotas" (dimensions), usually real measurements.
                # But to match image labels exactly, we can override.
                # Let's override to match the user's mental model "12cm" (even though drawing is 120mm)
                # dim.TextOverride = txt 
            except Exception as ex:
                print(f"Failed to draw dim: {ex}")

        # Add Radius Text manually
        try:
             pt_txt = to_point(X1-30, Y4-30)
             txt_obj = ms.AddText("R5cm", pt_txt, 5.0) # Height 5.0mm
             txt_obj.Layer = "COTAS"
        except:
             pass
            
        
        print("Box mold generated successfully.")
        
        acad.ZoomExtents()
        
        # EXPORT FOR COREL (DXF 2013)
        # 60 = ac2013_dxf
        import os
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        dxf_path = os.path.join(desktop, "box_mold_export.dxf")
        
        try:
            doc.SaveAs(dxf_path, 60)
            print(f"Exported to DXF: {dxf_path}")
        except Exception as save_err:
            print(f"Failed to auto-save DXF: {save_err}")
            # If open, user might need to close or save manually
        
    except Exception as e:
        print(f"Failed to generate mold: {e}")

if __name__ == "__main__":
    main()
