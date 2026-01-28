
// ONI SHOWTIME: GLASSMORPHIC NEUMORPHIC EMBLEM
// Bold typography, shield with glassmorphic overlay and neumorphic depth

#target photoshop
app.bringToFront();

// --- CONFIGURATION ---
var brandingText = "ONIV24";
var cNeonBlue = rgb(0, 150, 255);
var cDarkBlue = rgb(10, 50, 100);
var cLightGray = rgb(230, 235, 245);
var cWhite = rgb(255, 255, 255);
var cShieldBlue = rgb(30, 70, 130);
var cGlass = rgb(200, 220, 240); // Frosted glass color

function rgb(r, g, b) {
    var c = new SolidColor();
    c.rgb.red = r; c.rgb.green = g; c.rgb.blue = b;
    return c;
}

var docWidth = 1920;
var docHeight = 1080;
var doc = app.documents.add(docWidth, docHeight, 72, "ONI_GLASS_NEURO", NewDocumentMode.RGB, DocumentFill.WHITE);

var cx = docWidth / 2;
var cy = docHeight / 2;

// --- NEUMORPHIC BACKGROUND ---
var bg = doc.artLayers.add();
bg.name = "NEURO_BG";
doc.activeLayer = bg;
doc.selection.select([[0, 0], [docWidth, 0], [docWidth, docHeight], [0, docHeight]]);
doc.selection.fill(cLightGray);
doc.selection.deselect();

// --- SHIELD EMBLEM ---
var shieldGroup = doc.layerSets.add();
shieldGroup.name = "SHIELD_EMBLEM";

var shield = doc.artLayers.add();
shield.name = "SHIELD_BASE";
shield.move(shieldGroup, ElementPlacement.INSIDE);
doc.activeLayer = shield;

var shieldW = 500;
var shieldH = 600;
var shieldPts = [
    [cx, cy - shieldH / 2],
    [cx + shieldW / 2, cy - shieldH / 2 + 100],
    [cx + shieldW / 2, cy + shieldH / 4],
    [cx + shieldW / 3, cy + shieldH / 2 - 50],
    [cx, cy + shieldH / 2],
    [cx - shieldW / 3, cy + shieldH / 2 - 50],
    [cx - shieldW / 2, cy + shieldH / 4],
    [cx - shieldW / 2, cy - shieldH / 2 + 100]
];

doc.selection.select(shieldPts);
doc.selection.fill(cShieldBlue);
doc.selection.deselect();

// Shield effects (3D + Neumorphic)
doc.activeLayer = shield;
var sDesc = new ActionDescriptor();
var sRef = new ActionReference();
sRef.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
sRef.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
sDesc.putReference(charIDToTypeID("null"), sRef);

var sFx = new ActionDescriptor();

// Neumorphic Inner Shadow (pressed depth)
var sIS = new ActionDescriptor();
sIS.putBoolean(charIDToTypeID("enab"), true);
sIS.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
sIS.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 35);
sIS.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 120);
sIS.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 10);
sIS.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 20);
sFx.putObject(charIDToTypeID("IrSh"), charIDToTypeID("IrSh"), sIS);

// Blue glow
var sGlow = new ActionDescriptor();
sGlow.putBoolean(charIDToTypeID("enab"), true);
sGlow.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Scrn"));
sGlow.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 70);
var gCol = new ActionDescriptor();
gCol.putDouble(charIDToTypeID("Rd  "), cNeonBlue.rgb.red);
gCol.putDouble(charIDToTypeID("Grn "), cNeonBlue.rgb.green);
gCol.putDouble(charIDToTypeID("Bl  "), cNeonBlue.rgb.blue);
sGlow.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), gCol);
sGlow.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 25);
sFx.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), sGlow);

// Neumorphic Drop Shadow (soft raised)
var sDS = new ActionDescriptor();
sDS.putBoolean(charIDToTypeID("enab"), true);
sDS.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
sDS.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 50);
sDS.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 120);
sDS.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 25);
sDS.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 35);
sFx.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), sDS);

sDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), sFx);
executeAction(charIDToTypeID("setd"), sDesc, DialogModes.NO);

// --- GLASSMORPHIC OVERLAY (frosted glass effect) ---
var glass = doc.artLayers.add();
glass.name = "GLASS_OVERLAY";
glass.move(shieldGroup, ElementPlacement.PLACEATBEGINNING);
doc.activeLayer = glass;

// Create glass shape (slightly smaller than shield)
var glassW = shieldW - 60;
var glassH = shieldH - 80;
var glassPts = [
    [cx, cy - glassH / 2],
    [cx + glassW / 2, cy - glassH / 2 + 90],
    [cx + glassW / 2, cy + glassH / 4],
    [cx + glassW / 3, cy + glassH / 2 - 50],
    [cx, cy + glassH / 2],
    [cx - glassW / 3, cy + glassH / 2 - 50],
    [cx - glassW / 2, cy + glassH / 4],
    [cx - glassW / 2, cy - glassH / 2 + 90]
];

doc.selection.select(glassPts);
doc.selection.fill(cGlass);
doc.selection.deselect();

// Glassmorphic effects
glass.opacity = 50; // Semi-transparent

doc.activeLayer = glass;
var gDesc = new ActionDescriptor();
var gRef = new ActionReference();
gRef.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
gRef.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
gDesc.putReference(charIDToTypeID("null"), gRef);

var gFx = new ActionDescriptor();

// Inner Glow (light reflection on glass)
var gIG = new ActionDescriptor();
gIG.putBoolean(charIDToTypeID("enab"), true);
gIG.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Scrn"));
gIG.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 80);
var giCol = new ActionDescriptor();
giCol.putDouble(charIDToTypeID("Rd  "), 255); giCol.putDouble(charIDToTypeID("Grn "), 255); giCol.putDouble(charIDToTypeID("Bl  "), 255);
gIG.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), giCol);
gIG.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 20);
gFx.putObject(charIDToTypeID("IrGl"), charIDToTypeID("IrGl"), gIG);

// Stroke (frosted edge)
var gStroke = new ActionDescriptor();
gStroke.putBoolean(charIDToTypeID("enab"), true);
gStroke.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 2);
var gsCol = new ActionDescriptor();
gsCol.putDouble(charIDToTypeID("Rd  "), 255); gsCol.putDouble(charIDToTypeID("Grn "), 255); gsCol.putDouble(charIDToTypeID("Bl  "), 255);
gStroke.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), gsCol);
gFx.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), gStroke);

gDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), gFx);
executeAction(charIDToTypeID("setd"), gDesc, DialogModes.NO);

glass.blendMode = BlendMode.NORMAL;

// --- BOLD TEXT ---
var mainText = doc.artLayers.add();
mainText.kind = LayerKind.TEXT;
mainText.name = "TEXT_BOLD_3D";
var ti = mainText.textItem;
ti.contents = brandingText;
ti.size = UnitValue(180, "px");
ti.color = cWhite;
ti.justification = Justification.CENTER;
ti.position = [cx, cy - 30];
ti.font = "Impact";

// Text effects (3D + Neon)
doc.activeLayer = mainText;
var tDesc = new ActionDescriptor();
var tRef = new ActionReference();
tRef.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
tRef.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
tDesc.putReference(charIDToTypeID("null"), tRef);

var tFx = new ActionDescriptor();

// 3D Bevel
var tBevel = new ActionDescriptor();
tBevel.putBoolean(charIDToTypeID("enab"), true);
tBevel.putEnumerated(charIDToTypeID("Styl"), charIDToTypeID("BESl"), charIDToTypeID("Embs"));
tBevel.putUnitDouble(charIDToTypeID("sze "), charIDToTypeID("#Pxl"), 30);
tBevel.putUnitDouble(charIDToTypeID("Sftn"), charIDToTypeID("#Pxl"), 6);
tBevel.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 120);
tBevel.putUnitDouble(charIDToTypeID("Lald"), charIDToTypeID("#Ang"), 35);
tFx.putObject(charIDToTypeID("ebsl"), charIDToTypeID("ebsl"), tBevel);

// Neon glow
var tGlow = new ActionDescriptor();
tGlow.putBoolean(charIDToTypeID("enab"), true);
tGlow.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Scrn"));
tGlow.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
var tgCol = new ActionDescriptor();
tgCol.putDouble(charIDToTypeID("Rd  "), cNeonBlue.rgb.red);
tgCol.putDouble(charIDToTypeID("Grn "), cNeonBlue.rgb.green);
tgCol.putDouble(charIDToTypeID("Bl  "), cNeonBlue.rgb.blue);
tGlow.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), tgCol);
tGlow.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 35);
tFx.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), tGlow);

// Dark stroke
var tStroke = new ActionDescriptor();
tStroke.putBoolean(charIDToTypeID("enab"), true);
tStroke.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 3);
var stCol = new ActionDescriptor();
stCol.putDouble(charIDToTypeID("Rd  "), cDarkBlue.rgb.red);
stCol.putDouble(charIDToTypeID("Grn "), cDarkBlue.rgb.green);
stCol.putDouble(charIDToTypeID("Bl  "), cDarkBlue.rgb.blue);
tStroke.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), stCol);
tFx.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), tStroke);

tDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), tFx);
executeAction(charIDToTypeID("setd"), tDesc, DialogModes.NO);

// --- NEUMORPHIC DECORATIVE CIRCLES ---
var neuro = doc.layerSets.add();
neuro.name = "NEURO_ACCENTS";

function createNeuroCircle(x, y, radius) {
    var circle = doc.artLayers.add();
    circle.name = "NEURO_CIRCLE";
    circle.move(neuro, ElementPlacement.INSIDE);
    doc.activeLayer = circle;

    var pts = [];
    for (var i = 0; i < 60; i++) {
        var angle = (i / 60) * Math.PI * 2;
        pts.push([x + Math.cos(angle) * radius, y + Math.sin(angle) * radius]);
    }
    doc.selection.select(pts);
    doc.selection.fill(cLightGray);
    doc.selection.deselect();

    // Neumorphic effects (soft pressed)
    doc.activeLayer = circle;
    var nDesc = new ActionDescriptor();
    var nRef = new ActionReference();
    nRef.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
    nRef.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
    nDesc.putReference(charIDToTypeID("null"), nRef);

    var nFx = new ActionDescriptor();

    // Inner shadow (pressed)
    var nIS = new ActionDescriptor();
    nIS.putBoolean(charIDToTypeID("enab"), true);
    nIS.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
    nIS.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 30);
    nIS.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 120);
    nIS.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 5);
    nIS.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 12);
    nFx.putObject(charIDToTypeID("IrSh"), charIDToTypeID("IrSh"), nIS);

    // Highlight shadow (raised)
    var nDS = new ActionDescriptor();
    nDS.putBoolean(charIDToTypeID("enab"), true);
    nDS.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Scrn"));
    nDS.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 25);
    var dCol = new ActionDescriptor();
    dCol.putDouble(charIDToTypeID("Rd  "), 255); dCol.putDouble(charIDToTypeID("Grn "), 255); dCol.putDouble(charIDToTypeID("Bl  "), 255);
    nDS.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), dCol);
    nDS.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 300);
    nDS.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 5);
    nDS.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 12);
    nFx.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), nDS);

    nDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), nFx);
    executeAction(charIDToTypeID("setd"), nDesc, DialogModes.NO);
}

createNeuroCircle(cx - 600, cy - 300, 40);
createNeuroCircle(cx + 600, cy - 300, 40);
createNeuroCircle(cx - 600, cy + 300, 40);
createNeuroCircle(cx + 600, cy + 300, 40);

// --- GLASSMORPHIC ACCENT BARS ---
var glassBar = doc.artLayers.add();
glassBar.name = "GLASS_BAR_TOP";
glassBar.move(neuro, ElementPlacement.PLACEATBEGINNING);
doc.activeLayer = glassBar;

var barY = cy - shieldH / 2 - 80;
doc.selection.select([[cx - 200, barY], [cx + 200, barY], [cx + 200, barY + 6], [cx - 200, barY + 6]]);
doc.selection.fill(cGlass);
doc.selection.deselect();
glassBar.opacity = 60;
glassBar.blendMode = BlendMode.SCREEN;

var glassBar2 = doc.artLayers.add();
glassBar2.name = "GLASS_BAR_BOTTOM";
glassBar2.move(neuro, ElementPlacement.PLACEATBEGINNING);
doc.activeLayer = glassBar2;

var barY2 = cy + shieldH / 2 + 70;
doc.selection.select([[cx - 180, barY2], [cx + 180, barY2], [cx + 180, barY2 + 6], [cx - 180, barY2 + 6]]);
doc.selection.fill(cGlass);
doc.selection.deselect();
glassBar2.opacity = 60;
glassBar2.blendMode = BlendMode.SCREEN;
