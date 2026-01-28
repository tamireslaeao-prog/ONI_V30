"""
ONI V23 - PROFESSIONAL LAYERED PSD GENERATOR
Creates a properly structured PSD with editable layers, groups, and shapes.
NO FLATTEN - Full editability preserved.
"""

import asyncio
import os
import win32com.client
import pythoncom


LAYERED_PSD_JSX = '''
// ================================================================================
// ONI PROFESSIONAL LAYERED PSD GENERATOR
// Creates EDITABLE layers, groups, and shape layers - NO FLATTEN!
// ================================================================================

// Create high-res document
var doc = app.documents.add(1920, 1080, 300, "ONI_LAYERED_LOGO", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

// ================================================================================
// HELPER FUNCTION: Create Layer Group
// ================================================================================
function createGroup(name) {
    var group = doc.layerSets.add();
    group.name = name;
    return group;
}

// ================================================================================
// LAYER GROUPS STRUCTURE
// ================================================================================
var grpForeground = createGroup("FOREGROUND");
var grpText = createGroup("TEXT");
var grpAccents = createGroup("ACCENTS");
var grpGrid = createGroup("GRID_LINES");
var grpBackground = createGroup("BACKGROUND");

// ================================================================================
// BACKGROUND GROUP
// ================================================================================
doc.activeLayer = grpBackground;

// Base background layer
var bgLayer = grpBackground.artLayers.add();
bgLayer.name = "Base_Color";
var bgColor = new SolidColor();
bgColor.rgb.red = 15;
bgColor.rgb.green = 12;
bgColor.rgb.blue = 30;
doc.selection.selectAll();
doc.selection.fill(bgColor);
doc.selection.deselect();

// Purple gradient corners
var gradCorner1 = grpBackground.artLayers.add();
gradCorner1.name = "Corner_Glow_TopLeft";
var purpleColor = new SolidColor();
purpleColor.rgb.red = 88;
purpleColor.rgb.green = 28;
purpleColor.rgb.blue = 135;
doc.selection.select([[0, 0], [500, 0], [0, 350]]);
doc.selection.fill(purpleColor);
doc.selection.deselect();
gradCorner1.applyGaussianBlur(120);
gradCorner1.blendMode = BlendMode.SCREEN;
gradCorner1.opacity = 50;

var gradCorner2 = grpBackground.artLayers.add();
gradCorner2.name = "Corner_Glow_BottomRight";
doc.selection.select([[1920, 1080], [1500, 1080], [1920, 750]]);
doc.selection.fill(purpleColor);
doc.selection.deselect();
gradCorner2.applyGaussianBlur(120);
gradCorner2.blendMode = BlendMode.SCREEN;
gradCorner2.opacity = 50;

// ================================================================================
// GRID LINES GROUP (Editable)
// ================================================================================
doc.activeLayer = grpGrid;

var gridColor = new SolidColor();
gridColor.rgb.red = 99;
gridColor.rgb.green = 102;
gridColor.rgb.blue = 241;

// Horizontal line top
var lineH1 = grpGrid.artLayers.add();
lineH1.name = "Line_Horizontal_Top";
doc.selection.select([[0, 350], [1920, 350], [1920, 352], [0, 352]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
lineH1.opacity = 40;

// Horizontal line bottom
var lineH2 = grpGrid.artLayers.add();
lineH2.name = "Line_Horizontal_Bottom";
doc.selection.select([[0, 730], [1920, 730], [1920, 732], [0, 732]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
lineH2.opacity = 40;

// Vertical left
var lineV1 = grpGrid.artLayers.add();
lineV1.name = "Line_Vertical_Left";
doc.selection.select([[200, 300], [202, 300], [202, 780], [200, 780]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
lineV1.opacity = 40;

// Vertical right
var lineV2 = grpGrid.artLayers.add();
lineV2.name = "Line_Vertical_Right";
doc.selection.select([[1718, 300], [1720, 300], [1720, 780], [1718, 780]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
lineV2.opacity = 40;

// ================================================================================
// ACCENTS GROUP
// ================================================================================
doc.activeLayer = grpAccents;

// Main accent bar
var accentBar = grpAccents.artLayers.add();
accentBar.name = "Main_Accent_Bar";
var accentColor = new SolidColor();
accentColor.rgb.red = 99;
accentColor.rgb.green = 102;
accentColor.rgb.blue = 241;
doc.selection.select([[300, 480], [1620, 480], [1620, 600], [300, 600]]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// Corner brackets - Top Left
var bracketTL = grpAccents.artLayers.add();
bracketTL.name = "Bracket_TopLeft";
doc.selection.select([[150, 200], [250, 200], [250, 205], [155, 205], [155, 300], [150, 300]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
bracketTL.opacity = 70;

// Corner brackets - Top Right
var bracketTR = grpAccents.artLayers.add();
bracketTR.name = "Bracket_TopRight";
doc.selection.select([[1670, 200], [1770, 200], [1770, 300], [1765, 300], [1765, 205], [1670, 205]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
bracketTR.opacity = 70;

// Corner brackets - Bottom Left
var bracketBL = grpAccents.artLayers.add();
bracketBL.name = "Bracket_BottomLeft";
doc.selection.select([[150, 780], [155, 780], [155, 875], [250, 875], [250, 880], [150, 880]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
bracketBL.opacity = 70;

// Corner brackets - Bottom Right
var bracketBR = grpAccents.artLayers.add();
bracketBR.name = "Bracket_BottomRight";
doc.selection.select([[1765, 780], [1770, 780], [1770, 880], [1670, 880], [1670, 875], [1765, 875]]);
doc.selection.fill(gridColor);
doc.selection.deselect();
bracketBR.opacity = 70;

// ================================================================================
// TEXT GROUP - All text layers EDITABLE
// ================================================================================
doc.activeLayer = grpText;

// Main Title "ONI"
var titleLayer = grpText.artLayers.add();
titleLayer.kind = LayerKind.TEXT;
titleLayer.name = "Title_ONI";
var titleText = titleLayer.textItem;
titleText.contents = "ONI";
titleText.font = "Impact";
titleText.size = new UnitValue(280, "px");
titleText.antiAliasMethod = AntiAlias.CRISP;
titleText.tracking = 100;
var whiteColor = new SolidColor();
whiteColor.rgb.red = 255;
whiteColor.rgb.green = 255;
whiteColor.rgb.blue = 255;
titleText.color = whiteColor;
titleText.justification = Justification.CENTER;
titleText.position = [960, 600];

// Apply Layer Style to Title (editable!)
doc.activeLayer = titleLayer;
var styleDesc = new ActionDescriptor();
var styleRef = new ActionReference();
styleRef.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
styleRef.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
styleDesc.putReference(charIDToTypeID("null"), styleRef);

var effectsDesc = new ActionDescriptor();
effectsDesc.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), 100);

// Drop Shadow
var drshDesc = new ActionDescriptor();
drshDesc.putBoolean(charIDToTypeID("enab"), true);
drshDesc.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Mltp"));
var drshColor = new ActionDescriptor();
drshColor.putDouble(charIDToTypeID("Rd  "), 0);
drshColor.putDouble(charIDToTypeID("Grn "), 0);
drshColor.putDouble(charIDToTypeID("Bl  "), 0);
drshDesc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), drshColor);
drshDesc.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 80);
drshDesc.putBoolean(charIDToTypeID("uglg"), true);
drshDesc.putUnitDouble(charIDToTypeID("lagl"), charIDToTypeID("#Ang"), 120);
drshDesc.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 12);
drshDesc.putUnitDouble(charIDToTypeID("Ckmt"), charIDToTypeID("#Pxl"), 0);
drshDesc.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 25);
effectsDesc.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), drshDesc);

// Outer Glow
var orglDesc = new ActionDescriptor();
orglDesc.putBoolean(charIDToTypeID("enab"), true);
orglDesc.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Scrn"));
var orglColor = new ActionDescriptor();
orglColor.putDouble(charIDToTypeID("Rd  "), 99);
orglColor.putDouble(charIDToTypeID("Grn "), 102);
orglColor.putDouble(charIDToTypeID("Bl  "), 241);
orglDesc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), orglColor);
orglDesc.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 60);
orglDesc.putUnitDouble(charIDToTypeID("blur"), charIDToTypeID("#Pxl"), 40);
effectsDesc.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), orglDesc);

styleDesc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), effectsDesc);
executeAction(charIDToTypeID("setd"), styleDesc, DialogModes.NO);

// Subtitle "SYSTEM"
var subLayer = grpText.artLayers.add();
subLayer.kind = LayerKind.TEXT;
subLayer.name = "Subtitle_SYSTEM";
var subText = subLayer.textItem;
subText.contents = "S Y S T E M";
subText.font = "HelveticaNeueLT-Thin";
subText.size = new UnitValue(50, "px");
subText.tracking = 400;
subText.antiAliasMethod = AntiAlias.SMOOTH;
subText.color = accentColor;
subText.justification = Justification.CENTER;
subText.position = [960, 690];

// Tagline
var tagLayer = grpText.artLayers.add();
tagLayer.kind = LayerKind.TEXT;
tagLayer.name = "Tagline";
var tagText = tagLayer.textItem;
tagText.contents = "OMEGA NEURAL INTERFACE";
tagText.font = "HelveticaNeueLT-Light";
tagText.size = new UnitValue(22, "px");
tagText.tracking = 250;
tagText.antiAliasMethod = AntiAlias.SMOOTH;
var grayColor = new SolidColor();
grayColor.rgb.red = 140;
grayColor.rgb.green = 140;
grayColor.rgb.blue = 160;
tagText.color = grayColor;
tagText.justification = Justification.CENTER;
tagText.position = [960, 770];

// ================================================================================
// DO NOT FLATTEN - Keep all layers editable!
// ================================================================================

// Save PSD with layers preserved
var psdPath = "C:/temp/genesis/oni_logo/ONI_LAYERED_EDITABLE.psd";
var psdFile = new File(psdPath);
var psdOpts = new PhotoshopSaveOptions();
psdOpts.embedColorProfile = true;
psdOpts.layers = true;  // CRITICAL: Keep layers!
psdOpts.alphaChannels = true;
doc.saveAs(psdFile, psdOpts, true);

// Also export a flattened PNG copy
var pngPath = "C:/temp/genesis/oni_logo/ONI_LAYERED_PREVIEW.png";
var pngDoc = doc.duplicate("ONI_PNG_Export");
pngDoc.flatten();
var pngFile = new File(pngPath);
var pngOpts = new PNGSaveOptions();
pngOpts.compression = 0;
pngDoc.saveAs(pngFile, pngOpts, true);
pngDoc.close(SaveOptions.DONOTSAVECHANGES);

alert("LAYERED PSD Created!\\n\\nPSD (Editable): " + psdPath + "\\n\\nLayer Structure:\\n• FOREGROUND\\n• TEXT (ONI, SYSTEM, Tagline)\\n• ACCENTS (Bars, Brackets)\\n• GRID_LINES\\n• BACKGROUND (Gradients)\\n\\nAll layers are EDITABLE!");
'''


async def create_layered_psd():
    """Create properly layered PSD."""
    
    print("=" * 70)
    print("📁 ONI PROFESSIONAL LAYERED PSD GENERATOR")
    print("=" * 70)
    
    os.makedirs(r"C:\temp\genesis\oni_logo", exist_ok=True)
    
    try:
        print("\n⚡ Connecting to Photoshop...")
        pythoncom.CoInitialize()
        ps = win32com.client.Dispatch("Photoshop.Application")
        print(f"✅ Connected to Photoshop {ps.Version}")
        
        print("\n📁 Creating LAYERED PSD with:")
        print("   ├── 📂 FOREGROUND (group)")
        print("   ├── 📂 TEXT (group)")
        print("   │   ├── Title_ONI (text layer + layer styles)")
        print("   │   ├── Subtitle_SYSTEM (text layer)")
        print("   │   └── Tagline (text layer)")
        print("   ├── 📂 ACCENTS (group)")
        print("   │   ├── Main_Accent_Bar")
        print("   │   └── Bracket_* (4 layers)")
        print("   ├── 📂 GRID_LINES (group)")
        print("   │   └── Line_* (4 layers)")
        print("   └── 📂 BACKGROUND (group)")
        print("       ├── Base_Color")
        print("       └── Corner_Glow_* (2 layers)")
        print("")
        print("   ⚠️  NO FLATTEN - All layers editable!")
        
        ps.DoJavaScript(LAYERED_PSD_JSX)
        
        print("\n" + "=" * 70)
        print("✅ LAYERED PSD CRIADO!")
        print("=" * 70)
        print("📁 PSD: C:\\temp\\genesis\\oni_logo\\ONI_LAYERED_EDITABLE.psd")
        print("📁 PNG: C:\\temp\\genesis\\oni_logo\\ONI_LAYERED_PREVIEW.png")
        print("\n💡 O PSD tem todas as camadas editáveis!")
        
        os.startfile(r"C:\temp\genesis\oni_logo")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando Layered PSD Generator...")
    print("⚠️  Photoshop deve estar ABERTO!\n")
    
    asyncio.run(create_layered_psd())
