
import cv2
import numpy as np
import os

# Configuration
INPUT_IMAGE = r"C:\Users\user\.gemini\antigravity\brain\8ec0e989-69b8-47f3-b226-333a3bdccf39\oni_logo_concept_cyber_1768003376511.png"
FX_LIB = r"C:\Users\user\Desktop\ONIV24\app\scripts\fx_library.jsx"
OUTPUT_JSX = r"C:\Users\user\Desktop\ONIV24\app\scripts\oni_logo_master_v3.jsx"
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 1024

def generate_jsx(groups):
    # Read FX Library
    with open(FX_LIB, 'r') as lib_file:
        fx_code = lib_file.read()

    jsx = f"""/**
 * ONI ULTIMATE LOGO V3 - ARTIST MODE
 * Neural Fabrication: Smart Points + FX Injection.
 */
app.preferences.typeUnits = TypeUnits.PIXELS;
app.preferences.rulerUnits = Units.PIXELS;

// --- EMBEDDED FX LIBRARY ---
{fx_code}
// ---------------------------

try {{
    var doc = app.documents.add({CANVAS_WIDTH}, {CANVAS_HEIGHT}, 72, "ONI_LOGO_V3_ARTIST", NewDocumentMode.RGB, DocumentFill.WHITE);
}} catch(e) {{ var doc = app.activeDocument; }}

function createGroup(name) {{
    var group = doc.layerSets.add();
    group.name = name;
    return group;
}}

function createNeuralShape(name, points, r, g, b, groupName) {{
    // Select Group (by creating inside it if active, but simplified: assume linear creation)
    // Actually, simpler to Create Layer -> Move to Group.
    // Or just create paths and then fill.
    
    var lineArray = [];
    for (var i = 0; i < points.length; i++) {{
        var line = new PathPointInfo();
        line.kind = PointKind.CORNERPOINT;
        line.anchor = points[i];
        line.leftDirection = points[i];
        line.rightDirection = points[i];
        lineArray.push(line);
    }}
    var spi = new SubPathInfo();
    spi.operation = ShapeOperation.SHAPEADD;
    spi.closed = true;
    spi.entireSubPath = lineArray;
    
    // Path
    var pathItem = doc.pathItems.add("Path_" + name, [spi]);
    
    // Raster Layer
    var layer = doc.artLayers.add();
    layer.name = name;
    
    // Move to designated group (if we implement robust grouping)
    // For V3 Speed: We will apply styles to specific LAYERS immediately upon creation.
    
    pathItem.makeSelection(0, true, SelectionType.REPLACE);
    var color = new SolidColor();
    color.rgb.red = r; color.rgb.green = g; color.rgb.blue = b;
    doc.selection.fill(color);
    doc.selection.deselect();
    
    return layer;
}}

// GROUPS & FX LOGIC
"""
    jsx += "createCosmicBG();\n"
    
    # EXPLICIT RENDER ORDER (Bottom to Top)
    render_order = ["BASE_OTHER", "ARMOR_DARK", "PLATING_LIGHT", "NEON_CORE"]
    
    for group_name in render_order:
        if group_name not in groups: continue
        layers = groups[group_name]
        if not layers: continue
        
        jsx += f"\n// --- GROUP: {group_name} ---\n"
        jsx += f"var group_{group_name} = doc.layerSets.add();\n"
        jsx += f"group_{group_name}.name = '{group_name}';\n"
        
        # Sort layers by area
        layers.sort(key=lambda x: x[3], reverse=True) 
        
        for name, color, paths, area in layers:
            r, g, b = color
            for idx, points in enumerate(paths):
                pts_str = ", ".join(points)
                jsx += f"var l = createNeuralShape('{name}_{idx}', [{pts_str}], {r}, {g}, {b}, '{group_name}');\n"
                jsx += f"l.move(group_{group_name}, ElementPlacement.INSIDE);\n"
        
        # APPLY GROUP FX (V5: CHROME & COSMOS)
        if group_name == "NEON_CORE":
            jsx += "doc.activeLayer = group_NEON_CORE;\n"
            # Super Bloom: High Size, Add Mode
            jsx += "applyNeonGlow(0, 255, 255, 45, 90);\n" 
        elif group_name == "ARMOR_DARK":
            jsx += "doc.activeLayer = group_ARMOR_DARK;\n"
            # Deep Blue Tech Armor
            jsx += "applyTechBevel(200, 3);\n"
            jsx += "applyDropShadow(8, 20, 50);\n"
        elif group_name == "PLATING_LIGHT":
             jsx += "doc.activeLayer = group_PLATING_LIGHT;\n"
             # THE CHROME MATERIAL
             jsx += "applyChromeFX();\n"

    jsx += 'alert("ONI LOGO V5 (CHROME & COSMOS) COMPLETE");'
    return jsx

# Main Processing
img = cv2.imread(INPUT_IMAGE)
if img is None: raise Exception("Image not found: " + INPUT_IMAGE)

# V3: ULTRA FIDELITY (K=24) + SMART POLY
data = np.float32(img).reshape((-1, 3))
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
K = 24 
_, label, center = cv2.kmeans(data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
center = np.uint8(center)

# Grouping Buckets
groups = {
    "NEON_CORE": [],     # Light Teals/Cyans
    "ARMOR_DARK": [],    # Blacks/Dark Blues
    "PLATING_LIGHT": [], # Whites/Greys
    "BASE_OTHER": []
}

for i, color in enumerate(center):
    b, g, r = int(color[0]), int(color[1]), int(color[2])
    
    # Analyze Color for Grouping
    luminance = (0.299*r + 0.587*g + 0.114*b)
    # Saturation approx
    max_c = max(r,g,b)
    min_c = min(r,g,b)
    delta = max_c - min_c
    
    target_group = "BASE_OTHER"
    
    if luminance > 200 and delta < 30:
        target_group = "PLATING_LIGHT" # White/Grey
    elif luminance < 60:
        target_group = "ARMOR_DARK"    # Dark
    elif g > r and g > b and luminance > 100:
         target_group = "NEON_CORE"     # Greenish/Teal pop?
    elif b > r and b > 150:
         target_group = "NEON_CORE"     # Blue pop
    else:
         target_group = "ARMOR_DARK"   # Fallback to armor
         
    # Remove bg
    label_mask = label.reshape(img.shape[:2])
    binary_mask = np.uint8(label_mask == i) * 255
    coverage = np.sum(label_mask == i)
    if coverage > (img.shape[0] * img.shape[1] * 0.90): continue 

    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_paths = []
    total_area = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 15: continue # Keep decent detail (V1 was 10)
        
        # V3 SMART POLY: Less smoothing for straight precision
        epsilon = 0.0005 * cv2.arcLength(cnt, True) # Ultra High Res (V1 was 0.001)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        pts = []
        for p in approx:
            x, y = p[0]
            pts.append(f"[{x}, {y}]")
            
        valid_paths.append(pts)
        total_area += area
        
    if valid_paths:
        groups[target_group].append((f"Color_{i}_{r}_{g}_{b}", (r, g, b), valid_paths, total_area))

# Write
with open(OUTPUT_JSX, "w", encoding='utf-8') as f:
    f.write(generate_jsx(groups))
print("JSX Logo Generator V3-Artist Ready")
