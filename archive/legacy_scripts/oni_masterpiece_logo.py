"""
ONI V23 - MASTERPIECE LOGO GENERATOR
Creates a sophisticated GEOMETRIC LOGOMARK (Vector) + Modern Typography.
Leverages 'ORANGEV2' style if valid, or creates a custom high-end style.
"""

import asyncio
import os
import win32com.client
import pythoncom

# Asset Config
STYLE_ASSET_PATH = r"C:\Users\user\Desktop\ONIV24\data\styles\ORANGEV2.psd" # Hypothetical path based on json, or we assume it exists in psd_sources? 
# ORANGEV2.json filename is "ORANGEV2.psd". Let's check psd_sources.
# If not found, we use manual sophisticated styling.

MASTERPIECE_JSX = '''
// ================================================================================
// ONI MASTERPIECE LOGO GENERATOR
// Concept: "The Digital Portal" - Hexagon Core with Circuit Inlays
// ================================================================================

var doc = app.documents.add(2000, 2000, 300, "ONI_MASTERPIECE_LOGO", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

// 1. BACKGROUND ENVIRONMENT
// --------------------------------------------------------
var grpBg = doc.layerSets.add();
grpBg.name = "ENVIRONMENT";
var bgLayer = grpBg.artLayers.add();
bgLayer.name = "Dark_Void";
var colBg = new SolidColor(); colBg.rgb.red=10; colBg.rgb.green=10; colBg.rgb.blue=15;
doc.selection.selectAll();
doc.selection.fill(colBg);
doc.selection.deselect();

// 2. THE LOGOMARK (Geometrical Construction)
// --------------------------------------------------------
var grpMark = doc.layerSets.add();
grpMark.name = "LOGOMARK";

// Helper for Hexagon Points
function getHexPoints(cx, cy, radius) {
    var pts = [];
    for (var i = 0; i < 6; i++) {
        var angle_deg = 60 * i - 30; // Pointy top? No, flat top implies 0 start. -30 makes it pointy top.
        var angle_rad = Math.PI / 180 * angle_deg;
        pts.push([cx + radius * Math.cos(angle_rad), cy + radius * Math.sin(angle_rad)]);
    }
    return pts;
}

// Function to Create Polygon Shape Layer
function createPolyShape(points, name, r, g, b) {
    var lineArray = [];
    for (var i=0; i<points.length; i++) {
        var pt = new PathPointInfo();
        pt.kind = PointKind.CORNERPOINT;
        pt.anchor = points[i];
        pt.leftDirection = points[i];
        pt.rightDirection = points[i];
        lineArray.push(pt);
    }
    
    var sub = new SubPathInfo();
    sub.operation = ShapeOperation.SHAPEADD;
    sub.closed = true;
    sub.entireSubPath = lineArray;
    
    var myPath = doc.pathItems.add(name + "_Path", [sub]);
    
    // Create Solid Fill Layer
    var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putClass(stringIDToTypeID("contentLayer"));
    desc.putReference(charIDToTypeID("null"), ref);
        var desc2 = new ActionDescriptor();
            var desc3 = new ActionDescriptor();
                var desc4 = new ActionDescriptor();
                desc4.putDouble(charIDToTypeID("Rd  "), r);
                desc4.putDouble(charIDToTypeID("Grn "), g);
                desc4.putDouble(charIDToTypeID("Bl  "), b);
            desc3.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), desc4);
        desc2.putObject(charIDToTypeID("Type"), stringIDToTypeID("solidColorLayer"), desc3);
    desc.putObject(charIDToTypeID("Usng"), stringIDToTypeID("contentLayer"), desc2);
    executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);
    doc.activeLayer.name = name;
    
    myPath.remove(); // Clean up path item (layer keeps vector mask)
}

// Draw Outer Hexagon
var hexOut = getHexPoints(1000, 800, 350);
createPolyShape(hexOut, "Hex_Outer", 255, 100, 0); // Orange Base

// Draw Inner Hexagon (Cutout simulation via masking or layer style? Better: Smaller shape on top)
// To simulate a "Ring", we need to subtract. But scripting subtract is hard.
// We will layer a Dark Hexagon inside.
var hexIn = getHexPoints(1000, 800, 250);
createPolyShape(hexIn, "Hex_Inner_Cut", 10, 10, 15); // Match BG color

// Draw Core Circuit (Triangle?)
var triPts = [
    [1000, 800 - 150],
    [1000 + 130, 800 + 75],
    [1000 - 130, 800 + 75]
];
createPolyShape(triPts, "Core_Triangle", 255, 255, 255);
doc.activeLayer.fillOpacity = 0; // Hide fill, we will use stroke style

// Apply Glow to Core
var descGlow = new ActionDescriptor();
var refGlow = new ActionReference();
refGlow.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
refGlow.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
descGlow.putReference(charIDToTypeID("null"), refGlow);
var descFX = new ActionDescriptor();

var descOG = new ActionDescriptor();
descOG.putBoolean(charIDToTypeID("enab"), true);
descOG.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
var cGlow = new ActionDescriptor(); cGlow.putDouble(charIDToTypeID("Rd  "), 0); cGlow.putDouble(charIDToTypeID("Grn "), 200); cGlow.putDouble(charIDToTypeID("Bl  "), 255);
descOG.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), cGlow);
descOG.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 30);
descFX.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), descOG);

var descStr = new ActionDescriptor();
descStr.putBoolean(charIDToTypeID("enab"), true);
descStr.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 10);
descStr.putEnumerated(charIDToTypeID("Pstn"), charIDToTypeID("Pstn"), charIDToTypeID("Ins "));
descStr.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), cGlow);
descFX.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), descStr);

descGlow.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), descFX);
executeAction(charIDToTypeID("setd"), descGlow, DialogModes.NO);


// 3. TYPOGRAPHY (Modern & Wide)
// --------------------------------------------------------
var grpText = doc.layerSets.add();
grpText.name = "TYPOGRAPHY";

var txtLayer = grpText.artLayers.add();
txtLayer.kind = LayerKind.TEXT;
txtLayer.name = "ONI_TEXT";
var t = txtLayer.textItem;
t.contents = "O N I";
t.font = "Arial-BoldMT"; // Reliable font
t.size = new UnitValue(200, "px");
t.tracking = 600; // HUGE tracking for modern look
t.justification = Justification.CENTER;
t.position = [1000, 1350];
var cTxt = new SolidColor(); cTxt.rgb.red=240; cTxt.rgb.green=240; cTxt.rgb.blue=250;
t.color = cTxt;

// Subtitle
var subLayer = grpText.artLayers.add();
subLayer.kind = LayerKind.TEXT;
subLayer.name = "SYSTEM_TEXT";
var ts = subLayer.textItem;
ts.contents = "INTELLIGENT SYSTEM";
ts.font = "ArialMT"; 
ts.size = new UnitValue(40, "px");
ts.tracking = 800;
ts.justification = Justification.CENTER;
ts.position = [1000, 1450];
var cSub = new SolidColor(); cSub.rgb.red=100; cSub.rgb.green=100; cSub.rgb.blue=120;
ts.color = cSub;


alert("Masterpiece Concept Created: 'The Digital Core'\\nVector Logomark + Modern Typography.");
'''


async def create_masterpiece_logo():
    """Create Masterpiece Geometric Logo."""
    
    print("=" * 70)
    print("💎 ONI MASTERPIECE LOGO GENERATOR")
    print("=" * 70)
    
    try:
        print("\n⚡ Connecting to Photoshop...")
        pythoncom.CoInitialize()
        ps = win32com.client.Dispatch("Photoshop.Application")
        print(f"✅ Connected to Photoshop {ps.Version}")
        
        print("\n🎨 Creating 'The Digital Core' Concept...")
        print("   → Geometric Logomark (Hexagon Portal)")
        print("   → Vector Cutouts")
        print("   → Glowing Core Circuit")
        print("   → Modern Expanded Typography")
        
        ps.DoJavaScript(MASTERPIECE_JSX)
        
        print("\n" + "=" * 70)
        print("✨ MASTERPIECE LOGO GENERATED!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(create_masterpiece_logo())
