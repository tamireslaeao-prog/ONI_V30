"""
ONI V23 - Premium Logo Generator (Direct JSX)
Creates a modern professional logo directly in Photoshop.
"""

import asyncio
import sys
import os
import win32com.client
import pythoncom

sys.path.insert(0, r"C:\Users\user\Desktop\ONIV24")


PREMIUM_LOGO_JSX = '''
// ONI PREMIUM LOGO GENERATOR v2.0
// Modern, Professional, Tech-Forward

var doc = app.documents.add(1200, 800, 150, "ONI_Premium_Logo", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

// ============================================
// LAYER 1: Dark Gradient Background
// ============================================
var bgLayer = doc.artLayers.add();
bgLayer.name = "Background_Gradient";

// Create dark tech gradient (deep purple to black)
var startColor = new SolidColor();
startColor.rgb.red = 30;
startColor.rgb.green = 20;
startColor.rgb.blue = 60;

var endColor = new SolidColor();
endColor.rgb.red = 10;
endColor.rgb.green = 10;
endColor.rgb.blue = 20;

// Fill with start color first
doc.selection.selectAll();
doc.selection.fill(startColor);
doc.selection.deselect();

// ============================================
// LAYER 2: Accent Glow Bar
// ============================================
var glowLayer = doc.artLayers.add();
glowLayer.name = "Accent_Glow";

var accentColor = new SolidColor();
accentColor.rgb.red = 99;
accentColor.rgb.green = 102;
accentColor.rgb.blue = 241; // #6366f1 Indigo

// Draw center accent bar
doc.selection.select([
    [100, 350],
    [1100, 350],
    [1100, 450],
    [100, 450]
]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// ============================================
// LAYER 3: Main Title "ONI"
// ============================================
var titleLayer = doc.artLayers.add();
titleLayer.kind = LayerKind.TEXT;
titleLayer.name = "Title_ONI";

var titleText = titleLayer.textItem;
titleText.contents = "ONI";
titleText.font = "HelveticaNeueLT-Heavy";
titleText.size = new UnitValue(180, "px");
titleText.antiAliasMethod = AntiAlias.SMOOTH;

// White color for contrast
var titleColor = new SolidColor();
titleColor.rgb.red = 255;
titleColor.rgb.green = 255;
titleColor.rgb.blue = 255;
titleText.color = titleColor;

// Center horizontally
titleText.justification = Justification.CENTER;
titleText.position = [600, 450];

// ============================================
// LAYER 4: Subtitle "SYSTEM"
// ============================================
var subtitleLayer = doc.artLayers.add();
subtitleLayer.kind = LayerKind.TEXT;
subtitleLayer.name = "Subtitle_SYSTEM";

var subText = subtitleLayer.textItem;
subText.contents = "SYSTEM";
subText.font = "HelveticaNeueLT-Light";
subText.size = new UnitValue(48, "px");
subText.antiAliasMethod = AntiAlias.SMOOTH;
subText.color = accentColor;
subText.justification = Justification.CENTER;
subText.position = [600, 520];

// ============================================
// LAYER 5: Decorative Lines
// ============================================
var lineLayer = doc.artLayers.add();
lineLayer.name = "Decorative_Lines";

// Top line
doc.selection.select([
    [200, 270],
    [1000, 270],
    [1000, 272],
    [200, 272]
]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// Bottom line
doc.selection.select([
    [200, 560],
    [1000, 560],
    [1000, 562],
    [200, 562]
]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// ============================================
// LAYER 6: Accent Squares (instead of dots)
// ============================================
var dotsLayer = doc.artLayers.add();
dotsLayer.name = "Accent_Squares";

// Left square
doc.selection.select([
    [265, 385],
    [285, 385],
    [285, 405],
    [265, 405]
]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// Right square
doc.selection.select([
    [915, 385],
    [935, 385],
    [935, 405],
    [915, 405]
]);
doc.selection.fill(accentColor);
doc.selection.deselect();

// ============================================
// APPLY DROP SHADOW TO TITLE
// ============================================
doc.activeLayer = titleLayer;

// Drop shadow via Layer Styles (ActionDescriptor)
var idsetd = charIDToTypeID("setd");
var desc1 = new ActionDescriptor();
var idnull = charIDToTypeID("null");
var ref1 = new ActionReference();
var idPrpr = charIDToTypeID("Prpr");
var idLefx = charIDToTypeID("Lefx");
ref1.putProperty(idPrpr, idLefx);
var idLyr = charIDToTypeID("Lyr ");
var idOrdn = charIDToTypeID("Ordn");
var idTrgt = charIDToTypeID("Trgt");
ref1.putEnumerated(idLyr, idOrdn, idTrgt);
desc1.putReference(idnull, ref1);
var idT = charIDToTypeID("T   ");
var desc2 = new ActionDescriptor();
var idScl = charIDToTypeID("Scl ");
var idPrc = charIDToTypeID("#Prc");
desc2.putUnitDouble(idScl, idPrc, 100.000000);
var idDrSh = charIDToTypeID("DrSh");
var desc3 = new ActionDescriptor();
var idenab = charIDToTypeID("enab");
desc3.putBoolean(idenab, true);
var idMd = charIDToTypeID("Md  ");
var idBlnM = charIDToTypeID("BlnM");
var idMltp = charIDToTypeID("Mltp");
desc3.putEnumerated(idMd, idBlnM, idMltp);
var idClr = charIDToTypeID("Clr ");
var desc4 = new ActionDescriptor();
var idRd = charIDToTypeID("Rd  ");
desc4.putDouble(idRd, 0.000000);
var idGrn = charIDToTypeID("Grn ");
desc4.putDouble(idGrn, 0.000000);
var idBl = charIDToTypeID("Bl  ");
desc4.putDouble(idBl, 0.000000);
var idRGBC = charIDToTypeID("RGBC");
desc3.putObject(idClr, idRGBC, desc4);
var idOpct = charIDToTypeID("Opct");
desc3.putUnitDouble(idOpct, idPrc, 75.000000);
var iduglg = charIDToTypeID("uglg");
desc3.putBoolean(iduglg, true);
var idlagl = charIDToTypeID("lagl");
desc3.putUnitDouble(idlagl, charIDToTypeID("#Ang"), 120.000000);
var idDstn = charIDToTypeID("Dstn");
desc3.putUnitDouble(idDstn, charIDToTypeID("#Pxl"), 8.000000);
var idCkmt = charIDToTypeID("Ckmt");
desc3.putUnitDouble(idCkmt, charIDToTypeID("#Pxl"), 0.000000);
var idblur = charIDToTypeID("blur");
desc3.putUnitDouble(idblur, charIDToTypeID("#Pxl"), 15.000000);
var idNose = charIDToTypeID("Nose");
desc3.putUnitDouble(idNose, idPrc, 0.000000);
desc2.putObject(idDrSh, idDrSh, desc3);
desc1.putObject(idT, idLefx, desc2);
executeAction(idsetd, desc1, DialogModes.NO);

// ============================================
// FLATTEN AND EXPORT
// ============================================
doc.flatten();

// Save as PNG
var outputPath = "C:/temp/genesis/oni_logo/ONI_PREMIUM_LOGO.png";
var file = new File(outputPath);
var opts = new PNGSaveOptions();
opts.compression = 6;
opts.interlaced = false;
doc.saveAs(file, opts, true);

// Also keep PSD
var psdPath = "C:/temp/genesis/oni_logo/ONI_PREMIUM_LOGO.psd";
var psdFile = new File(psdPath);
var psdOpts = new PhotoshopSaveOptions();
psdOpts.embedColorProfile = true;
psdOpts.layers = false;
doc.saveAs(psdFile, psdOpts, true);

alert("ONI Premium Logo Created!\\nPNG: " + outputPath + "\\nPSD: " + psdPath);
'''


async def create_premium_oni_logo():
    """Create premium ONI logo using direct JSX."""
    
    print("=" * 70)
    print("🌋 ONI PREMIUM LOGO GENERATOR")
    print("=" * 70)
    
    # Ensure output directory
    os.makedirs(r"C:\temp\genesis\oni_logo", exist_ok=True)
    
    try:
        # Connect to Photoshop
        print("\n⚡ Connecting to Photoshop...")
        pythoncom.CoInitialize()
        ps = win32com.client.Dispatch("Photoshop.Application")
        print(f"✅ Connected to Photoshop {ps.Version}")
        
        # Execute the premium JSX
        print("\n🎨 Creating premium logo...")
        ps.DoJavaScript(PREMIUM_LOGO_JSX)
        
        print("\n" + "=" * 70)
        print("✨ LOGO CRIADO COM SUCESSO!")
        print("=" * 70)
        print("📁 PNG: C:\\temp\\genesis\\oni_logo\\ONI_PREMIUM_LOGO.png")
        print("📁 PSD: C:\\temp\\genesis\\oni_logo\\ONI_PREMIUM_LOGO.psd")
        
        # Open folder
        os.startfile(r"C:\temp\genesis\oni_logo")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando Premium Logo Generator...")
    print("⚠️  IMPORTANTE: Photoshop deve estar ABERTO!\n")
    
    asyncio.run(create_premium_oni_logo())
