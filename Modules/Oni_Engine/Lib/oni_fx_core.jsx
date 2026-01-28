/**
 * ONI FX LIBRARY - ACTION MANAGER INJECTION
 * Provides programmatic access to Layer Styles (Effects) without presets.
 * V6: Added applyPerfectGold (Reflected Gradient + Satin + Bevel)
 */

// --- UTILS ---
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }

/**
 * Creates the "Cosmic Void" background.
 */
function createCosmicBG() {
    try {
        var doc = app.activeDocument;
        var layer = doc.artLayers.add();
        layer.name = "COSMIC_VOID";
        doc.activeLayer = layer;
        layer.move(doc.layers[doc.layers.length - 1], ElementPlacement.PLACEAFTER);

        var color = new SolidColor();
        color.rgb.red = 5; color.rgb.green = 10; color.rgb.blue = 25; // Deep Space Blue
        doc.selection.selectAll();
        doc.selection.fill(color);
        doc.selection.deselect();

        // Add subtle noise for "Stars"
        layer.applyAddNoise(3, NoiseDistribution.GAUSSIAN, true);
    } catch (e) { }
}

/**
 * Applies a Chrome Material (Gradient Overlay + Satin + Bevel).
 */
function applyChromeFX() {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();

    // 1. BEVEL & EMBOSS
    var bevel = new ActionDescriptor();
    bevel.putBoolean(cTID('enab'), true);
    bevel.putEnumerated(cTID('bvlS'), cTID('bvlS'), cTID('InrB')); // Inner Bevel
    bevel.putEnumerated(cTID('bvlT'), cTID('bvlT'), cTID('CslH')); // Chisel Hard
    bevel.putUnitDouble(cTID('Dpth'), cTID('#Prc'), 300); // 300% Depth
    bevel.putEnumerated(cTID('bvlD'), cTID('bvlD'), cTID('Up  '));
    bevel.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 3);
    bevel.putUnitDouble(cTID('Sftn'), cTID('#Pxl'), 0);
    layerEffects.putObject(cTID('ebbl'), cTID('ebbl'), bevel);

    // 2. GRADIENT OVERLAY
    var gradOv = new ActionDescriptor();
    gradOv.putBoolean(cTID('enab'), true);
    gradOv.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Nrml'));
    gradOv.putUnitDouble(cTID('Opct'), cTID('#Prc'), 100);

    // Construct Gradient
    var grad = new ActionDescriptor();
    grad.putString(cTID('Nm  '), "Chrome");
    grad.putEnumerated(cTID('GrdF'), cTID('GrdF'), cTID('CstS'));
    var stops = new ActionList();

    // Stop 1: White
    var s1 = new ActionDescriptor();
    var c1 = new ActionDescriptor(); c1.putDouble(cTID('Rd  '), 220); c1.putDouble(cTID('Grn '), 220); c1.putDouble(cTID('Bl  '), 230);
    s1.putObject(cTID('Clr '), cTID('RGBC'), c1);
    s1.putInteger(cTID('Lctn'), 0); s1.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s1);

    // Stop 2: Grey
    var s2 = new ActionDescriptor();
    var c2 = new ActionDescriptor(); c2.putDouble(cTID('Rd  '), 120); c2.putDouble(cTID('Grn '), 130); c2.putDouble(cTID('Bl  '), 140);
    s2.putObject(cTID('Clr '), cTID('RGBC'), c2);
    s2.putInteger(cTID('Lctn'), 2048); s2.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s2);

    // Stop 3: White
    var s3 = new ActionDescriptor();
    var c3 = new ActionDescriptor(); c3.putDouble(cTID('Rd  '), 240); c3.putDouble(cTID('Grn '), 245); c3.putDouble(cTID('Bl  '), 255);
    s3.putObject(cTID('Clr '), cTID('RGBC'), c3);
    s3.putInteger(cTID('Lctn'), 4096); s3.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s3);

    grad.putList(cTID('Clrs'), stops);
    gradOv.putObject(cTID('Grad'), cTID('Grad'), grad);
    gradOv.putUnitDouble(cTID('Angl'), cTID('#Ang'), 90);

    layerEffects.putObject(cTID('GrOv'), cTID('GrOv'), gradOv);

    // 3. SATIN
    var satin = new ActionDescriptor();
    satin.putBoolean(cTID('enab'), true);
    satin.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Mltp'));
    var satColor = new ActionDescriptor(); satColor.putDouble(cTID('Rd  '), 0); satColor.putDouble(cTID('Grn '), 0); satColor.putDouble(cTID('Bl  '), 0);
    satin.putObject(cTID('Clr '), cTID('RGBC'), satColor);
    satin.putUnitDouble(cTID('Opct'), cTID('#Prc'), 30);
    satin.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), 10);
    satin.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 15);
    layerEffects.putObject(cTID('ChFX'), cTID('ChFX'), satin);

    // 4. INNER GLOW
    var innerGlow = new ActionDescriptor();
    innerGlow.putBoolean(cTID('enab'), true);
    innerGlow.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Scrn'));
    innerGlow.putUnitDouble(cTID('Opct'), cTID('#Prc'), 60);
    var igColor = new ActionDescriptor(); igColor.putDouble(cTID('Rd  '), 255); igColor.putDouble(cTID('Grn '), 255); igColor.putDouble(cTID('Bl  '), 255);
    innerGlow.putObject(cTID('Clr '), cTID('RGBC'), igColor);
    innerGlow.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 2);
    layerEffects.putObject(cTID('IrGl'), cTID('IrGl'), innerGlow);

    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}

/**
 * Applies a Neon Glow (Outer Glow) to the active layer.
 */
function applyNeonGlow(r, g, b, size, opacity) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();
    var outerGlow = new ActionDescriptor();

    outerGlow.putBoolean(cTID('enab'), true);
    outerGlow.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('LnrD'));
    outerGlow.putUnitDouble(cTID('Opct'), cTID('#Prc'), opacity);
    var color = new ActionDescriptor();
    color.putDouble(cTID('Rd  '), r);
    color.putDouble(cTID('Grn '), g);
    color.putDouble(cTID('Bl  '), b);
    outerGlow.putObject(cTID('Clr '), cTID('RGBC'), color);
    outerGlow.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), size);

    layerEffects.putObject(cTID('OrGl'), cTID('OrGl'), outerGlow);
    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}

/**
 * Applies a "Tech Armor" Bevel (Chisel Hard).
 */
function applyTechBevel(depth, size) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();
    var bevel = new ActionDescriptor();

    bevel.putBoolean(cTID('enab'), true);
    bevel.putEnumerated(cTID('bvlS'), cTID('bvlS'), cTID('InrB'));
    bevel.putEnumerated(cTID('bvlT'), cTID('bvlT'), cTID('CslH'));
    bevel.putUnitDouble(cTID('Dpth'), cTID('#Prc'), depth);
    bevel.putEnumerated(cTID('bvlD'), cTID('bvlD'), cTID('Up  '));
    bevel.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), size);
    bevel.putUnitDouble(cTID('Sftn'), cTID('#Pxl'), 0);

    layerEffects.putObject(cTID('ebbl'), cTID('ebbl'), bevel);
    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}

/**
 * Applies a Solid Stroke.
 */
function applyStroke(size, r, g, b) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();
    var stroke = new ActionDescriptor();

    stroke.putBoolean(cTID('enab'), true);
    stroke.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), size);
    stroke.putEnumerated(cTID('Pstn'), cTID('Pstn'), cTID('OutF'));
    stroke.putEnumerated(cTID('Opct'), cTID('#Prc'), 100);

    var color = new ActionDescriptor();
    color.putDouble(cTID('Rd  '), r);
    color.putDouble(cTID('Grn '), g);
    color.putDouble(cTID('Bl  '), b);
    stroke.putObject(cTID('Clr '), cTID('RGBC'), color);

    layerEffects.putObject(cTID('FrFX'), cTID('FrFX'), stroke);
    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}

/**
 * Applies a Drop Shadow for depth.
 */
function applyDropShadow(dist, size, opacity) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();
    var shadow = new ActionDescriptor();

    shadow.putBoolean(cTID('enab'), true);
    shadow.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Mltp'));
    shadow.putUnitDouble(cTID('Opct'), cTID('#Prc'), opacity);

    var color = new ActionDescriptor();
    color.putDouble(cTID('Rd  '), 0);
    color.putDouble(cTID('Grn '), 0);
    color.putDouble(cTID('Bl  '), 0);
    shadow.putObject(cTID('Clr '), cTID('RGBC'), color);

    shadow.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), dist);
    shadow.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), size);

    layerEffects.putObject(cTID('DrSh'), cTID('DrSh'), shadow);
    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}

/**
 * Applies the "PERFECT GOLD" style extracted from user's PSD.
 * PHYSICALLY CORRECT: Reflected Gradient + Satin + Bevel.
 */
function applyPerfectGold() {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putProperty(cTID('Prpr'), cTID('Lefx'));
    ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
    desc.putReference(cTID('null'), ref);

    var layerEffects = new ActionDescriptor();

    // 1. BEVEL & EMBOSS
    var bevel = new ActionDescriptor();
    bevel.putBoolean(cTID('enab'), true);
    bevel.putEnumerated(cTID('bvlS'), cTID('bvlS'), cTID('InrB'));
    bevel.putEnumerated(cTID('bvlT'), cTID('bvlT'), cTID('CslH')); // Chisel Hard
    bevel.putUnitDouble(cTID('Dpth'), cTID('#Prc'), 100);
    bevel.putEnumerated(cTID('bvlD'), cTID('bvlD'), cTID('Up  '));
    bevel.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 5);
    bevel.putUnitDouble(cTID('Sftn'), cTID('#Pxl'), 0);

    // Highlight
    var hClr = new ActionDescriptor(); hClr.putDouble(cTID('Rd  '), 255); hClr.putDouble(cTID('Grn '), 255); hClr.putDouble(cTID('Bl  '), 255);
    bevel.putObject(cTID('hglC'), cTID('RGBC'), hClr);
    bevel.putEnumerated(cTID('hglM'), cTID('BlnM'), cTID('Scrn'));
    bevel.putUnitDouble(cTID('hglO'), cTID('#Prc'), 50);

    // Shadow
    var sClr = new ActionDescriptor(); sClr.putDouble(cTID('Rd  '), 147); sClr.putDouble(cTID('Grn '), 147); sClr.putDouble(cTID('Bl  '), 147);
    bevel.putObject(cTID('sdwC'), cTID('RGBC'), sClr);
    bevel.putEnumerated(cTID('sdwM'), cTID('BlnM'), cTID('Mltp'));
    bevel.putUnitDouble(cTID('sdwO'), cTID('#Prc'), 50);

    layerEffects.putObject(cTID('ebbl'), cTID('ebbl'), bevel);

    // 2. STROKE
    var stroke = new ActionDescriptor();
    stroke.putBoolean(cTID('enab'), true);
    stroke.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 9);
    stroke.putEnumerated(cTID('Pstn'), cTID('Pstn'), cTID('OutF'));
    stroke.putEnumerated(cTID('Opct'), cTID('#Prc'), 100);

    var strColor = new ActionDescriptor();
    strColor.putDouble(cTID('Rd  '), 253);
    strColor.putDouble(cTID('Grn '), 155);
    strColor.putDouble(cTID('Bl  '), 0);
    stroke.putObject(cTID('Clr '), cTID('RGBC'), strColor);

    layerEffects.putObject(cTID('FrFX'), cTID('FrFX'), stroke);

    // 3. GRADIENT OVERLAY (THE REAL DEAL - Reflected)
    var gradOv = new ActionDescriptor();
    gradOv.putBoolean(cTID('enab'), true);
    gradOv.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Nrml'));
    gradOv.putUnitDouble(cTID('Opct'), cTID('#Prc'), 100);

    var grad = new ActionDescriptor();
    grad.putString(cTID('Nm  '), "Gold 24k");
    grad.putEnumerated(cTID('GrdF'), cTID('GrdF'), cTID('CstS'));
    var stops = new ActionList();

    // Stop 1: Dark Bronze/Gold (RGB 139, 95, 15)
    var s1 = new ActionDescriptor();
    var c1 = new ActionDescriptor(); c1.putDouble(cTID('Rd  '), 139); c1.putDouble(cTID('Grn '), 95); c1.putDouble(cTID('Bl  '), 15);
    s1.putObject(cTID('Clr '), cTID('RGBC'), c1);
    s1.putInteger(cTID('Lctn'), 0); s1.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s1);

    // Stop 2: Bright Gold (RGB 255, 215, 0)
    var s2 = new ActionDescriptor();
    var c2 = new ActionDescriptor(); c2.putDouble(cTID('Rd  '), 255); c2.putDouble(cTID('Grn '), 215); c2.putDouble(cTID('Bl  '), 0);
    s2.putObject(cTID('Clr '), cTID('RGBC'), c2);
    s2.putInteger(cTID('Lctn'), 2048); s2.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s2);

    // Stop 3: Deep Gold (RGB 184, 134, 11)
    var s3 = new ActionDescriptor();
    var c3 = new ActionDescriptor(); c3.putDouble(cTID('Rd  '), 184); c3.putDouble(cTID('Grn '), 134); c3.putDouble(cTID('Bl  '), 11);
    s3.putObject(cTID('Clr '), cTID('RGBC'), c3);
    s3.putInteger(cTID('Lctn'), 4096); s3.putInteger(cTID('Mdpn'), 50);
    stops.putObject(cTID('Clrt'), s3);

    grad.putList(cTID('Clrs'), stops);
    gradOv.putObject(cTID('Grad'), cTID('Grad'), grad);
    gradOv.putUnitDouble(cTID('Angl'), cTID('#Ang'), 90);

    // VITAL: Reflection Style
    gradOv.putEnumerated(cTID('Type'), cTID('GrdT'), cTID('Rflc'));
    gradOv.putUnitDouble(cTID('Scl '), cTID('#Prc'), 100);

    layerEffects.putObject(cTID('GrOv'), cTID('GrOv'), gradOv);

    // 4. SATIN (Inner metallic shadows)
    var satin = new ActionDescriptor();
    satin.putBoolean(cTID('enab'), true);
    satin.putEnumerated(cTID('Md  '), cTID('BlnM'), cTID('Mltp'));
    var satColor = new ActionDescriptor(); satColor.putDouble(cTID('Rd  '), 118); satColor.putDouble(cTID('Grn '), 70); satColor.putDouble(cTID('Bl  '), 14);
    satin.putObject(cTID('Clr '), cTID('RGBC'), satColor);
    satin.putUnitDouble(cTID('Opct'), cTID('#Prc'), 40);
    satin.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), 12);
    satin.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), 14);
    satin.putBoolean(cTID('Invr'), true);
    layerEffects.putObject(cTID('ChFX'), cTID('ChFX'), satin);

    desc.putObject(cTID('T   '), cTID('Lefx'), layerEffects);

    try {
        executeAction(cTID('setd'), desc, DialogModes.NO);
    } catch (e) { }
}
