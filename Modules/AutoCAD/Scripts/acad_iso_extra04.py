
import win32com.client
import math
import os

def to_point(x, y, z=0):
    return win32com.client.VARIANT(win32com.client.pythoncom.VT_ARRAY | win32com.client.pythoncom.VT_R8, [x, y, z])

def iso_proj(x, y, z):
    # Iso Projection to 2D Plane (AutoCAD Model Space)
    # Mapping 3D coords to 2D Iso representation
    # X axis: 30 deg
    # Y axis: 150 deg (or -210)
    # Z axis: 90 deg
    
    # Radians
    rad30 = math.radians(30)
    
    # AutoCad X is Right, Y is Up.
    # Iso X (Right-Down? or Right-Up?)
    # Standard Iso: Right-Up (30deg), Left-Up (150deg). Vertical (90).
    # Coords:
    # u = (x - y) * cos(30)
    # v = z + (x + y) * sin(30) 
    
    # Wait, if Z is Up.
    # Let's use standard Formula:
    # x_screen = (x - y) * cos(30)
    # y_screen = z + (x + y) * sin(30)
    
    cos30 = math.cos(rad30) # 0.866
    sin30 = math.sin(rad30) # 0.5
    
    # Center Offset
    CX, CY = 100, 100
    
    u = (x - y) * cos30
    v = z + (x + y) * sin30
    
    return [CX + u, CY + v, 0.0]

def draw_line(ms, p1, p2):
    ms.AddLine(to_point(*p1), to_point(*p2))

def run():
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        doc = acad.ActiveDocument
        if not doc:
            doc = acad.Documents.Add()
        ms = doc.ModelSpace
        
        # Geometry Definitions (Same as Corel)
        # Base L-Shape
        # Width 60 (x), Depth 40 (y), Height 10 (z_base) + 30 (tower)
        
        # Vertices Calculation
        # Tower (Left)
        p_t_fl = iso_proj(0, 40, 0);   p_t_fr = iso_proj(20, 40, 0)
        p_t_bl = iso_proj(0, 0, 0);    p_t_br = iso_proj(20, 0, 0)
        p_t_tfl = iso_proj(0, 40, 40); p_t_tfr = iso_proj(20, 40, 40)
        p_t_tbl = iso_proj(0, 0, 40);  p_t_tbr = iso_proj(20, 0, 40)
        
        # Base Plate
        # Starts X=20
        p_b_fr = iso_proj(60, 40, 0)
        p_b_br = iso_proj(60, 0, 0)
        p_b_tfr = iso_proj(60, 40, 10)
        p_b_tbr = iso_proj(60, 0, 10)
        
        # Junctions
        p_j_f = iso_proj(20, 40, 10)
        p_j_b = iso_proj(20, 0, 10)
        
        # Draw Tower
        draw_line(ms, p_t_tfl, p_t_tfr)
        draw_line(ms, p_t_tfr, p_t_tbr)
        draw_line(ms, p_t_tbr, p_t_tbl)
        draw_line(ms, p_t_tbl, p_t_tfl)
        draw_line(ms, p_t_tfl, p_t_fl)
        draw_line(ms, p_t_tfr, p_j_f)
        draw_line(ms, p_t_tbr, p_j_b)
        
        # Draw Base
        draw_line(ms, p_j_b, p_b_tbr)
        draw_line(ms, p_b_tbr, p_b_tfr)
        draw_line(ms, p_b_tfr, p_j_f)
        draw_line(ms, p_j_f, p_j_b)
        
        draw_line(ms, p_b_tfr, p_b_fr)
        draw_line(ms, p_b_tbr, p_b_br)
        draw_line(ms, p_t_fl, p_b_fr) # Front Bottom Edge
        draw_line(ms, p_b_fr, p_b_br) # Right Bottom Edge
        
        # Slot (U-Shape)
        # Top Arc (Z=10), Bottom Arc (Z=0)
        # Center (40, 20). R=10.
        # Approximating Arc with segments or using AddArc if 2D plane aligned?
        # Iso circles are Ellipses. AddEllipse?
        # Let's use segments for compatibility.
        
        center_top = (40, 20, 10)
        center_bot = (40, 20, 0)
        
        def draw_iso_arc(cx, cy, cz, r, ang_start, ang_end):
            segments = 10
            step = (ang_end - ang_start) / segments
            pts = []
            for i in range(segments + 1):
                ang = math.radians(ang_start + i * step)
                lx = cx + r * math.cos(ang)
                ly = cy + r * math.sin(ang)
                pts.append(iso_proj(lx, ly, cz))
            
            for k in range(len(pts)-1):
                draw_line(ms, pts[k], pts[k+1])
        
        # Slot Top
        draw_iso_arc(40, 20, 10, 10, 90, 270)
        draw_line(ms, iso_proj(40, 10, 10), iso_proj(60, 10, 10))
        draw_line(ms, iso_proj(40, 30, 10), iso_proj(60, 30, 10))
        
        # Slot Bottom
        draw_iso_arc(40, 20, 0, 10, 90, 270)
        draw_line(ms, iso_proj(40, 10, 10), iso_proj(40, 10, 0))
        draw_line(ms, iso_proj(30, 20, 10), iso_proj(30, 20, 0)) # Tangent
        
        # Floating Wedge
        # Top 20x20 at Z=80. Bottom 10x10 at Z=60.
        p_wt1 = iso_proj(30, 10, 80); p_wt2 = iso_proj(50, 10, 80)
        p_wt3 = iso_proj(50, 30, 80); p_wt4 = iso_proj(30, 30, 80)
        
        p_wb1 = iso_proj(35, 15, 60); p_wb2 = iso_proj(45, 15, 60)
        p_wb3 = iso_proj(45, 25, 60); p_wb4 = iso_proj(35, 25, 60) # Back ones
        
        draw_line(ms, p_wt1, p_wt2)
        draw_line(ms, p_wt2, p_wt3)
        draw_line(ms, p_wt3, p_wt4)
        draw_line(ms, p_wt4, p_wt1)
        
        draw_line(ms, p_wb1, p_wb2)
        draw_line(ms, p_wt1, p_wb1)
        draw_line(ms, p_wt2, p_wb2)
        draw_line(ms, p_wt3, p_wb3) # to back
        
        doc.Regen(1)
        print("AutoCAD Iso Drawn.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
