/**
 * ONI PROCEDURAL ENGINE: VILE PROJETOS "FLAT-TECH" GENERATOR
 * Generates a complex, multi-layered geometric logo purely via code.
 */

// --- CONFIGURATION ---
var docSize = 1024;
var mainColor = { r: 0, g: 255, b: 255 }; // Cyan
var secondaryColor = { r: 30, g: 30, b: 35 }; // Dark Tech
var layerCountFilter = 80; // Target Minimum Layers

// --- UTILS ---
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }

function createDoc() {
    var doc = app.documents.add(docSize, docSize, 72, "VILE_PROCEDURAL_V3", NewDocumentMode.RGB, DocumentFill.WHITE);
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
    var pathName = "TempPath_" + Math.random().toString().substring(2,7);
    var pathItem = doc.pathItems.add(pathName, [spi]);
    pathItem.makeSelection(0, true, SelectionType.REPLACE);
    pathItem.remove(); // Cleanup path after selecting
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

// --- GENERATORS ---

/**
 * Generates the "V" Core Monogram
 */
function buildVCore(centerX, centerY, scale) {
    var width = 200 * scale;
    var height = 300 * scale;
    
    // Main V Shape - Left Leg
    var legWidth = 60 * scale;
    
    // Procedural "Plating" - generate multiple stacked plates for the V
    for(var i=0; i<5; i++) {
        var offset = i * 10;
        var color = (i%2 == 0) ? "222222" : "00FFFF";
        
        var p1 = [centerX - width/2 + offset, centerY - height/2 + offset];
        var p2 = [centerX + offset, centerY + height/2 + offset]; // Tip
        var p3 = [centerX + width/2 + offset, centerY - height/2 + offset];
        var p4 = [centerX + width/2 - legWidth + offset, centerY - height/2 + offset];
        var p5 = [centerX + offset, centerY + height/2 - legWidth*1.5 + offset]; // Inner Tip
        var p6 = [centerX - width/2 + legWidth + offset, centerY - height/2 + offset];
        
        createShapeLayer("V_Plate_" + i, [p1, p2, p3, p4, p5, p6], color);
    }
}

/**
 * Generates "Circuit Lines" around the center
 */
function buildCircuits(centerX, centerY) {
    var numCircuits = 40; // High layer count generator
    var radius = 400;
    
    for(var i=0; i<numCircuits; i++) {
        var angle = (i / numCircuits) * Math.PI * 2;
        var startR = radius * (0.8 + Math.random() * 0.2);
        var endR = radius * (1.1 + Math.random() * 0.1);
        var thickness = 2 + Math.random() * 4;
        
        var x1 = centerX + Math.cos(angle) * startR;
        var y1 = centerY + Math.sin(angle) * startR;
        var x2 = centerX + Math.cos(angle) * endR;
        var y2 = centerY + Math.sin(angle) * endR;
        
        // Rectangular "Line" segments
        var dx = x2 - x1;
        var dy = y2 - y1;
        var len = Math.sqrt(dx*dx + dy*dy);
        var perpX = -dy / len * thickness;
        var perpY = dx / len * thickness;
        
        var poly = [
            [x1 + perpX, y1 + perpY],
            [x2 + perpX, y2 + perpY],
            [x2 - perpX, y2 - perpY],
            [x1 - perpX, y1 - perpY]
        ];
        
        createShapeLayer("Circuit_Node_" + i, poly, "CCCCCC");
    }
}

/**
 * Generates a Grid background
 */
function buildGrid() {
    var gridSize = 50;
    var steps = docSize / gridSize;
    
    for(var i=0; i<=steps; i++) {
        var pos = i * gridSize;
        // Vert
        createShapeLayer("Grid_V_" + i, [[pos, 0], [pos+1, 0], [pos+1, docSize], [pos, docSize]], "E0E0E0");
        // Horiz
        createShapeLayer("Grid_H_" + i, [[0, pos], [0, pos+1], [docSize, pos+1], [docSize, pos]], "E0E0E0");
    }
}

/**
 * Main Text "VILEPROJETOS" constructed procedurally
 * (Simulating vector font construction for extra "complexity")
 */
function buildText() {
    // Ideally use textItem, but for procedural "layers" we can add decorative underlines
    var doc = app.activeDocument;
    var textLayer = doc.artLayers.add();
    textLayer.kind = LayerKind.TEXT;
    textLayer.textItem.contents = "VILEPROJETOS";
    textLayer.textItem.position = [150, 850];
    textLayer.textItem.size = 100;
    textLayer.textItem.font = "Arial-BoldMT";
    textLayer.textItem.color = hexToRgb("333333");
    
    // Add underline shards
    for(var i=0; i<10; i++) {
        var x = 150 + i * 80;
        var width = 60;
        createShapeLayer("Underline_Shard_" + i, [[x, 870], [x+width, 870], [x+width, 880], [x, 880]], "00FFFF");
    }
}

// --- MAIN EXECUTION ---
try {
    var doc = createDoc();
    
    // 1. Background Grid (20+ layers)
    buildGrid();
    
    // 2. Center V-Monogram (5 layers)
    buildVCore(docSize/2, docSize/2, 1.5);
    
    // 3. Tech Circuits (40 layers)
    buildCircuits(docSize/2, docSize/2);
    
    // 4. Branding
    buildText();
    
    // 5. Final "Noise/Glitch" overlays (20 layers)
    for(var j=0; j<20; j++) {
        var rx = Math.random() * docSize;
        var ry = Math.random() * docSize;
        var rw = Math.random() * 50;
        var rh = Math.random() * 5;
        createShapeLayer("Glitch_" + j, [[rx, ry], [rx+rw, ry], [rx+rw, ry+rh], [rx, ry+rh]], "FF00FF");
    }

} catch(e) {
    alert("Error: " + e);
}
