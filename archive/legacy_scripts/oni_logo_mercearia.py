"""
ONI V23 - MERCEARIA LOGO GENERATOR
Adaptation of Ultra Premium Generator.
"""

import asyncio
import os
import win32com.client
import pythoncom

MERCEARIA_JSX = '''
// ================================================================================
// MERCEARIA LOGO GENERATOR
// Warm, Organic, Market Style
// ================================================================================

var doc = app.documents.add(1920, 1080, 300, "ONI_MERCEARIA_LOGO", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

// BACKGROUND - Warm Paper / Kraft
var bgLayer = doc.artLayers.add();
bgLayer.name = "Background_Paper";
var paperColor = new SolidColor(); 
paperColor.rgb.red = 245; paperColor.rgb.green = 240; paperColor.rgb.blue = 230;
doc.selection.selectAll();
doc.selection.fill(paperColor);
doc.selection.deselect();

// TEXT - "MERCEARIA"
var titleLayer = doc.artLayers.add();
titleLayer.kind = LayerKind.TEXT;
titleLayer.name = "Title_MERCEARIA";
var t = titleLayer.textItem;
t.contents = "MERCEARIA";
t.font = "Impact"; // Fallback to safe font, prefer Cooper Black or similar if available
t.size = new UnitValue(180, "px");
t.tracking = 50;
t.color.rgb.red = 60; t.color.rgb.green = 40; t.color.rgb.blue = 20; // Dark Brown
t.justification = Justification.CENTER;
t.position = [960, 500];

// TEXT - "DO BAIRRO"
var subLayer = doc.artLayers.add();
subLayer.kind = LayerKind.TEXT;
subLayer.name = "Subtitle";
var s = subLayer.textItem;
s.contents = "SAO PAULO";
s.font = "Arial-BoldMT";
s.size = new UnitValue(60, "px");
s.tracking = 200;
s.color.rgb.red = 160; s.color.rgb.green = 80; s.color.rgb.blue = 40; // Orange/Rust
s.justification = Justification.CENTER;
s.position = [960, 600];

// ICON / CIRCLE
var shapeLayer = doc.artLayers.add();
shapeLayer.name = "Circle_Frame";

// Draw Circle
function drawCircle(x, y, r) {
    var selRegion = Array(4); // Approximation... 
    // Easier: Create circular selection
    doc.selection.select([
        [x-r, y-r], [x+r, y-r], [x+r, y+r], [x-r, y+r] // This is square, ellipse needed.
    ], SelectionType.REPLACE, 0, false);
    // Actually using Elliptical Marquee in script is different.
}
// Simple Square Frame instead for robust script
doc.selection.select([[400, 200], [1520, 200], [1520, 880], [400, 880]]);
doc.selection.stroke(t.color, 10, StrokeLocation.INSIDE);
doc.selection.deselect();


// Save PNG
var pngPath = "C:/Users/user/Desktop/ONIV24/temp/mercearia_logo.png";
var pngFile = new File(pngPath);
var pngOpts = new PNGSaveOptions();
doc.saveAs(pngFile, pngOpts, true);
'''

async def create_mercearia_logo():
    print("Creating Mercearia Logo...")
    try:
        pythoncom.CoInitialize()
        ps = win32com.client.Dispatch("Photoshop.Application")
        ps.DoJavaScript(MERCEARIA_JSX)
        print("Logo Created: c:\\Users\\user\\Desktop\\ONIV24\\temp\\mercearia_logo.png")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_mercearia_logo())
