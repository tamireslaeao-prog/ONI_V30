import maya.cmds as cmds
import os
import re
import xml.etree.ElementTree as ET

def parse_svg_path(path_data):
    """
    Parses SVG path data (M, L, Q, Z) into Maya curve commands.
    Returns a list of point tuples and knot vectors suitable for cmds.curve.
    """
    # Simple tokenizer for the specific format output by vision_factory_ultra (space separated)
    tokens = path_data.split()
    
    CurveData = []
    
    current_points = []
    
    # Iterate tokens
    i = 0
    start_point = (0,0)
    current_pos = (0,0)
    
    while i < len(tokens):
        cmd = tokens[i]
        
        if cmd == 'M':
            # Move To - Start of new sub-path (or curve)
            if current_points:
                CurveData.append(current_points)
                current_points = []
            
            x = float(tokens[i+1])
            y = float(tokens[i+2])
            # SVG represents Y downwards usually, Maya is Y up. Flip Y.
            # Center it roughly: 1024/2 = 512
            start_point = (x, -y)
            current_pos = start_point
            current_points.append(start_point)
            i += 3
            
        elif cmd == 'L':
            # Line To
            x = float(tokens[i+1])
            y = float(tokens[i+2])
            pt = (x, -y)
            current_points.append(pt)
            current_pos = pt
            i += 3
            
        elif cmd == 'Q':
            # Quadratic Bezier (Control, End)
            # Maya requires degree 2 (or 3) curves. 
            # For Q, we have start(implied), control, end.
            # cmds.curve(d=2, p=[start, control, end])
            
            cx = float(tokens[i+1])
            cy = float(tokens[i+2])
            x = float(tokens[i+3])
            y = float(tokens[i+4])
            
            control = (cx, -cy)
            end = (x, -y)
            
            current_points.append(control)
            current_points.append(end)
            
            current_pos = end
            i += 5
            
        elif cmd == 'Z':
            # Close path (connect to start)
            # Maya auto-close via curve setting is easiest, or just add start point
            if current_points:
                current_points.append(start_point)
            i += 1
        else:
            i += 1
            
    if current_points:
        CurveData.append(current_points)
        
    return CurveData

def create_curve_from_points(points):
    """Creates a degree 1 (linear) or degree 2 curve in Maya."""
    # For robustness, we'll linearize it (degree 1) effectively 
    # since we have high-density points from the vector factory anyway.
    # OR we try degree 2 if we have bezier points.
    # Given the mix, degree 1 is safest for arbitrary data unless we strictly separate spans.
    
    # Vision Factory Ultra creates dense points for smoothness? 
    # Actually it uses Q, so it's sparse.
    # If we treat Q control points as linear points, it looks jagged.
    # We must treat them as degree 2 controls.
    
    try:
        # Degree 1 (Linear) trace is safest fallback
        # Let's try degree 1 first for guaranteed geometry
        pts_3d = [(p[0], p[1], 0) for p in points]
        
        # If huge number of points, it might be heavy.
        curve = cmds.curve(d=1, p=pts_3d)
        return curve
    except Exception as e:
        print(f"Failed to create curve: {e}")
        return None

def model_jequiti_logo(svg_path):
    print("--------------------------------------------------")
    print(f"Modeling Jequiti Logo (Custom Importer) from: {svg_path}")
    
    cmds.file(new=True, force=True)
    
    if not os.path.exists(svg_path):
        print("Error: SVG file not found.")
        return

    # Parse SVG manually
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Namespace map in case it's stripped or present
        # SVG usually has xmlns="http://www.w3.org/2000/svg"
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Find paths (namespace aware or not)
        paths = root.findall(".//svg:path", ns)
        if not paths:
            paths = root.findall(".//path") # Try without namespace
            
        print(f"Found {len(paths)} paths in SVG.")
        
        curves = []
        for p in paths:
            d = p.get('d')
            if d:
                # Parse data
                sub_paths = parse_svg_path(d)
                for points in sub_paths:
                    if len(points) > 1:
                        c = create_curve_from_points(points)
                        if c:
                            curves.append(c)
                            
        if not curves:
            print("No curves created from parsed data.")
            return
            
        print(f"Created {len(curves)} Maya curves.")
        
        # Group
        curve_grp = cmds.group(curves, n="Curves_Grp")
        
        # Center & Scale
        cmds.xform(curve_grp, cp=True)
        # Flip Y was done during parse (y = -y), but check orientation
        
        # Extrusion Logic
        # Planar Surface + Extrude is better than BevelPlus for arbitrary shapes
        surfaces = []
        for c in curves:
            try:
                # 1. Planar Surface
                planar = cmds.planarSrf(c, tol=0.01, polygon=1) # 1=Poly
                if planar:
                    surfaces.append(planar[0])
            except:
                pass
                
        if surfaces:
            mesh_grp = cmds.group(surfaces, n="Jequiti_Meshes")
            
            # Poly Extrude Face
            cmd_result = cmds.polyExtrudeFacet(mesh_grp, constructionHistory=1, keepFacesTogether=1, thickness=20.0)
            
            # Material
            shader = cmds.shadingNode("blinn", asShader=True, n="Jequiti_Mat")
            cmds.setAttr(shader + ".color", 0.05, 0.2, 0.6, type="double3") 
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n="Jequiti_SG")
            cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader")
            cmds.sets(surfaces, forceElement=sg)
            
            # Cleanup curves
            cmds.hide(curve_grp)
            
            print("Extrusion Complete.")
        else:
            print("Planar Surface failed. Saving curves only.")

        # Save
        output_file = os.path.join(os.path.dirname(svg_path), "jequiti_logo_v2.mb")
        cmds.file(rename=output_file)
        cmds.file(save=True, type="mayaBinary")
        print(f"Saved scene to: {output_file}")
        
    except Exception as e:
        print(f"Manual Import Failed: {e}")
        import traceback
        traceback.print_exc()

# EXECUTE
if __name__ == "__main__":
    svg_input = r"c:/Users/user/Desktop/ONI_V27/output/jequiti_logo.png.svg"
    model_jequiti_logo(svg_input)
