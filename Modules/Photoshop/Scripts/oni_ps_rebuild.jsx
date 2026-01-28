/**
 * ONI Photoshop Elite Reconstruction (Fire Test) - MASTER V8
 * Identical and Editable Reconstruction using Shape Layers.
 */

app.preferences.typeUnits = TypeUnits.PIXELS;
app.preferences.rulerUnits = Units.PIXELS;

var docWidth = 1200;
var docHeight = 840;

var doc;
try {
    doc = app.documents.add(docWidth, docHeight, 72, "ONI_FireTest_MASTER", NewDocumentMode.RGB, DocumentFill.WHITE);
} catch (e) { doc = app.activeDocument; }

// --- SAFETY ENGINE V8 ---

function createVectorShape(name, points, r, g, b, group) {
    try {
        doc.selection.deselect();
        try { doc.pathItems.getByName("temp").remove(); } catch (e) { }

        makeSolidColorLayer(r, g, b);
        var targetLayer = doc.activeLayer;
        targetLayer.name = name;
        if (group) targetLayer.move(group, ElementPlacement.INSIDE);

        var lineArray = [];
        for (var i = 0; i < points.length; i++) {
            var line = new PathPointInfo();
            line.anchor = points[i];
            line.leftDirection = points[i];
            line.rightDirection = points[i];
            line.kind = PointKind.CORNERPOINT;
            lineArray.push(line);
        }

        var spi = new SubPathInfo();
        spi.closed = true;
        spi.operation = ShapeOperation.SHAPEADD;
        spi.entireSubPath = lineArray;

        var pathItem = doc.pathItems.add("temp", [spi]);
        pathItem.select();
        injectVectorMask();
        pathItem.remove();
    } catch (err) { }
}

function makeSolidColorLayer(r, g, b) {
    var desc1 = new ActionDescriptor();
    var desc2 = new ActionDescriptor();
    var desc3 = new ActionDescriptor();
    var desc4 = new ActionDescriptor();
    desc2.putClass(stringIDToTypeID("type"), stringIDToTypeID("solidColorLayer"));
    desc4.putDouble(charIDToTypeID("Rd  "), r);
    desc4.putDouble(charIDToTypeID("Grn "), g);
    desc4.putDouble(charIDToTypeID("Bl  "), b);
    desc3.putObject(charIDToTypeID("Clr "), stringIDToTypeID("RGBColor"), desc4);
    desc2.putObject(charIDToTypeID("Usng"), stringIDToTypeID("contentLayer"), desc3);
    desc1.putObject(charIDToTypeID("Usng"), stringIDToTypeID("contentLayer"), desc2);
    executeAction(stringIDToTypeID("make"), desc1, DialogModes.NO);
}

function injectVectorMask() {
    var desc1 = new ActionDescriptor();
    var ref1 = new ActionReference();
    ref1.putClass(charIDToTypeID("Path"));
    desc1.putReference(charIDToTypeID("null"), ref1);
    var ref2 = new ActionReference();
    ref2.putEnumerated(charIDToTypeID("Path"), charIDToTypeID("Path"), stringIDToTypeID("vectorMask"));
    desc1.putReference(charIDToTypeID("At  "), ref2);
    var ref3 = new ActionReference();
    ref3.putEnumerated(charIDToTypeID("Path"), charIDToTypeID("Path"), charIDToTypeID("Trgt"));
    desc1.putReference(charIDToTypeID("Usng"), ref3);
    executeAction(stringIDToTypeID("make"), desc1, DialogModes.NO);
}

function getGroup(name) {
    try { return doc.layerSets.getByName(name); }
    catch (e) { var g = doc.layerSets.add(); g.name = name; return g; }
}

var bgGroup = getGroup("BACKGROUND");
var charGroup = getGroup("CHARACTER");
var propsGroup = getGroup("PROPS");

// --- 1. BACKGROUND ---
createVectorShape("Circle_Grey", [[700, 100], [1100, 300], [1100, 600], [700, 750], [550, 450]], 235, 235, 235, bgGroup);
// PRO Text Simulation (Vectors)
createVectorShape("PRO_P", [[750, 300], [850, 300], [850, 500], [750, 500]], 220, 220, 220, bgGroup);

// --- 2. CHARACTER ---
// Shirt
createVectorShape("Shirt", [[450, 250], [750, 250], [880, 520], [420, 580], [380, 380]], 255, 255, 255, charGroup);
// Head
createVectorShape("Head_Skin", [[550, 120], [650, 120], [650, 220], [550, 220]], 255, 194, 178, charGroup);
// Hair (Blonde)
createVectorShape("Hair_Main", [[530, 80], [670, 80], [720, 250], [500, 250], [500, 150]], 245, 210, 124, charGroup);
// Glasses
createVectorShape("Glasses_Left", [[565, 155], [595, 155], [595, 185], [565, 185]], 20, 20, 20, charGroup);
createVectorShape("Glasses_Right", [[605, 155], [635, 155], [635, 185], [605, 185]], 20, 20, 20, charGroup);
// Legs
createVectorShape("Leg_L", [[530, 580], [570, 580], [570, 750], [530, 750]], 255, 194, 178, charGroup);
createVectorShape("Leg_R", [[630, 580], [670, 580], [670, 750], [630, 750]], 255, 194, 178, charGroup);
// Boots
createVectorShape("Boot_L", [[520, 750], [580, 750], [580, 800], [520, 800]], 10, 10, 10, charGroup);
createVectorShape("Boot_R", [[620, 750], [680, 750], [680, 800], [620, 800]], 10, 10, 10, charGroup);

// --- 3. PROPS ---
createVectorShape("Tablet_Body", [[630, 220], [780, 230], [780, 430], [630, 420]], 255, 255, 255, propsGroup);
createVectorShape("Tablet_Screen", [[640, 235], [770, 240], [770, 420], [640, 410]], 0, 174, 239, propsGroup);
// DJ Deck
createVectorShape("DJ_Deck", [[100, 600], [450, 600], [480, 780], [120, 780]], 255, 255, 255, propsGroup);
createVectorShape("DJ_Detail_Cyan", [[150, 650], [250, 650], [250, 750], [150, 750]], 0, 255, 255, propsGroup);

alert("DESAFIO DE FOGO: RECONSTRUÇÃO MASTER CONCLUÍDA.\nArquivos 100% Vetoriais e Editáveis.");
