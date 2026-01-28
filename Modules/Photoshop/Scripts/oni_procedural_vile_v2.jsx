/**
 * ONI PROCEDURAL ENGINE: VILE PROJETOS "NEURAL-DEPTH" GENERATOR (V2)
 * Advanced procedural generation with 3D Layer Styles (FX)
 */

// --- CONFIGURATION ---
var docSize = 1024;
var mainColorHex = "FFFFFF"; // Pure White
var darkMetalHex = "1A1A1A";

// --- UTILS ---
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }

function createDoc() {
    var doc = app.documents.add(docSize, docSize, 72, "VILE_PROCEDURAL_V6_WHITE", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

    // Create Background Layer
    var bgLayer = doc.artLayers.add();
    bgLayer.name = "Background_Dark";
    doc.activeLayer = bgLayer;
    doc.selection.selectAll();
    var bgColor = hexToRgb(darkMetalHex);
    doc.selection.fill(bgColor);
    doc.selection.deselect();

    return doc;
}

function hexToRgb(hex) {
    var r = parseInt(hex.substring(0, 2), 16);
    var g = parseInt(hex.substring(2, 4), 16);
    var b = parseInt(hex.substring(4, 6), 16);
    var c = new SolidColor();
    c.rgb.red = r; c.rgb.green = g; c.rgb.blue = b;
    return c;
}

function makeSelectionFromPoints(points) {
    var lineArray = [];
    for (var i = 0; i < points.length; i++) {
        var line = new PathPointInfo();
        line.kind = PointKind.CORNERPOINT;
        line.anchor = points[i];
        line.leftDirection = points[i];
        line.rightDirection = points[i];
        lineArray.push(line);
    }
    var spi = new SubPathInfo();
    spi.operation = ShapeOperation.SHAPEADD;
    spi.closed = true;
    spi.entireSubPath = lineArray;

    var doc = app.activeDocument;
    var pathName = "TempPath_" + Math.random().toString().substring(2, 7);
    var pathItem = doc.pathItems.add(pathName, [spi]);
    pathItem.makeSelection(0, true, SelectionType.REPLACE);
    pathItem.remove();
}

function createShapeLayer(name, points, colorHex) {
    var doc = app.activeDocument;
    var layer = doc.artLayers.add();
    layer.name = name;

    makeSelectionFromPoints(points);

    var c = hexToRgb(colorHex);
    doc.selection.fill(c);
    doc.selection.deselect();
    return layer;
}

// --- FX ENGINE (Styles) ---

function applyNeonGlow(layer) {
    doc.activeLayer = layer;
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var fxDesc = new ActionDescriptor();

    // Outer Glow
    var glowDesc = new ActionDescriptor();
    glowDesc.putBoolean(cTID('enab'), true);
    glowDesc.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Lght')); // Linear Dodge
    glowDesc.putUnitDouble(cTID('Opct'), cTID('#Prc'), 100.0);

    var colorDesc = new ActionDescriptor();
    colorDesc.putDouble(cTID('Rd  '), 255.0);
    colorDesc.putDouble(cTID('Grn '), 255.0);
    colorDesc.putDouble(cTID('Bl  '), 255.0); // White
    glowDesc.putObject(cTID('Clr '), cTID('RGBC'), colorDesc);
    glowDesc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 15.0);
    glowDesc.putUnitDouble(cTID('Sprd'), cTID('#Prc'), 0.0);

    fxDesc.putObject(cTID('OrGl'), cTID('OrGl'), glowDesc);
    desc.putObject(cTID('T   '), cTID('Lefx'), fxDesc);
    executeAction(cTID('setd'), desc, DialogModes.NO);
}

function applyMetalBevel(layer) {
    doc.activeLayer = layer;
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);
    var fxDesc = new ActionDescriptor();

    // Bevel & Emboss
    var bevelDesc = new ActionDescriptor();
    bevelDesc.putBoolean(cTID('enab'), true);
    bevelDesc.putEnumerated(cTID('hglM'), cTID('BlnM'), cTID('Scrn'));
    bevelDesc.putEnumerated(cTID('sdwM'), cTID('BlnM'), cTID('Mltp'));
    bevelDesc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 8.0);
    bevelDesc.putUnitDouble(cTID('Sftn'), cTID('#Pxl'), 0.0);
    bevelDesc.putUnitDouble(cTID('Dpth'), cTID('#Prc'), 200.0);
    bevelDesc.putEnumerated(cTID('bvlS'), cTID('bvlS'), cTID('InrB')); // Inner Bevel
    bevelDesc.putEnumerated(cTID('bvlT'), cTID('bvlT'), cTID('Chsl')); // Chisel Hard

    fxDesc.putObject(cTID('ebbl'), cTID('ebbl'), bevelDesc);

    // Drop Shadow
    var shadowDesc = new ActionDescriptor();
    shadowDesc.putBoolean(cTID('enab'), true);
    shadowDesc.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), 10.0);
    shadowDesc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 20.0);
    shadowDesc.putUnitDouble(cTID('Opct'), cTID('#Prc'), 75.0);

    fxDesc.putObject(cTID('DrSh'), cTID('DrSh'), shadowDesc);

    desc.putObject(cTID('T   '), cTID('Lefx'), fxDesc);
    executeAction(cTID('setd'), desc, DialogModes.NO);
}

// --- GENERATORS ---

function buildHexFrame(cx, cy, radius, thickness) {
    // Hexagon points
    var points = [];
    var innerPoints = [];

    for (var i = 0; i < 6; i++) {
        var angle_deg = 60 * i - 30;
        var angle_rad = Math.PI / 180 * angle_deg;

        points.push([
            cx + radius * Math.cos(angle_rad),
            cy + radius * Math.sin(angle_rad)
        ]);

        innerPoints.push([
            cx + (radius - thickness) * Math.cos(angle_rad),
            cy + (radius - thickness) * Math.sin(angle_rad)
        ]);
    }

    // Create hollow hex (simplified as solid for now, usually would subtract paths)
    // For this demo, just outer solid
    var lay = createShapeLayer("Hex_Frame", points, "333333");
    applyMetalBevel(lay);
}

function buildCyberCrystal(cx, cy) {
    // Central "Core"
    var lay = createShapeLayer("Core_Crystal", [
        [cx, cy - 100], [cx + 80, cy], [cx, cy + 100], [cx - 80, cy]
    ], mainColorHex);
    applyNeonGlow(lay);

    // Floating segments
    for (var i = 0; i < 3; i++) {
        var yOff = (i - 1) * 150;
        var pts = [
            [cx - 20, cy + yOff - 20], [cx + 20, cy + yOff - 20],
            [cx + 20, cy + yOff + 20], [cx - 20, cy + yOff + 20]
        ];
        var l = createShapeLayer("Node_" + i, pts, "FFFFFF");
        applyNeonGlow(l);
    }
}

function buildCircuitWeb(cx, cy) {
    for (var i = 0; i < 15; i++) {
        var angle = i * (360 / 15) * (Math.PI / 180);
        var rStart = 150;
        var rEnd = 400;
        var x1 = cx + Math.cos(angle) * rStart;
        var y1 = cy + Math.sin(angle) * rStart;
        var x2 = cx + Math.cos(angle) * rEnd;
        var y2 = cy + Math.sin(angle) * rEnd;

        var thick = 4;
        var pts = [
            [x1, y1], [x2, y2], [x2 + thick, y2 + thick], [x1 + thick, y1 + thick]
        ];

        var l = createShapeLayer("Circuit_Line_" + i, pts, "222222");
        l.opacity = 60;
    }
}

// --- EXECUTION ---
try {
    var doc = createDoc();

    // 1. Structure
    buildHexFrame(docSize / 2, docSize / 2, 450, 50);
    buildHexFrame(docSize / 2, docSize / 2, 350, 30);

    // 2. Tech
    buildCircuitWeb(docSize / 2, docSize / 2);

    // 3. Core Energy
    buildCyberCrystal(docSize / 2, docSize / 2);

    // 4. Text
    var textLayer = doc.artLayers.add();
    textLayer.kind = LayerKind.TEXT;
    textLayer.textItem.contents = "VILEPROJETOS";
    textLayer.textItem.position = [docSize / 2, 900];
    textLayer.textItem.size = 80;
    textLayer.textItem.font = "Arial-BoldMT";
    textLayer.textItem.color = hexToRgb("FFFFFF");
    textLayer.textItem.justification = Justification.CENTER;
    applyNeonGlow(textLayer);

} catch (e) {
    alert("Error: " + e);
}
