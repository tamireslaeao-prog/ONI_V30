// ONI PHOTOSHOP: GOLD FORGE
// USES LOW-LEVEL ACTION DESCRIPTORS TO CREATE GOLD LAYER STYLES.

var ONI_PS = (function () {
    var self = {};
    self.hexToRgb = function (hex) {
        var r = parseInt(hex.substring(0, 2), 16);
        var g = parseInt(hex.substring(2, 4), 16);
        var b = parseInt(hex.substring(4, 6), 16);
        var col = new SolidColor();
        col.rgb.red = r; col.rgb.green = g; col.rgb.blue = b;
        return col;
    };
    return self;
})();

try {
    // 1. SETUP
    var width = 1920;
    var height = 1080;
    // FIX: DocumentFill.BLACK is often invalid. Use TRANSPARENT and fill manually.
    var doc = app.documents.add(width, height, 72, "ONI_GOLD_ASSET", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);

    // Fill Black
    doc.selection.selectAll();
    doc.selection.fill(ONI_PS.hexToRgb("000000"));
    doc.selection.deselect();

    // 2. TEXT LAYER
    var layer = doc.artLayers.add();
    layer.kind = LayerKind.TEXT;
    var txt = layer.textItem;
    txt.contents = "ONI GOLD";
    txt.size = 300;
    txt.font = "Arial-BoldMT";
    txt.justification = Justification.CENTER;
    txt.position = [width / 2, height / 2 + 100];
    txt.color = ONI_PS.hexToRgb("FFCC00"); // Base Yellow

    // 3. APPLY GOLD STYLES (THE HARD PART)
    // We need to manipulate the "LayerEffects" object via ActionManager

    function applyGold(layer) {
        doc.activeLayer = layer;
        var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
        ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
        desc.putReference(charIDToTypeID("null"), ref);

        var fxDesc = new ActionDescriptor();
        var globalScale = 100;
        fxDesc.putUnitDouble(charIDToTypeID("Scl "), charIDToTypeID("#Prc"), globalScale);

        // A. BEVEL & EMBOSS
        var bevelDesc = new ActionDescriptor();
        bevelDesc.putEnumerated(charIDToTypeID("bvlT"), charIDToTypeID("bvlT"), charIDToTypeID("InrB")); // Inner Bevel
        bevelDesc.putEnumerated(charIDToTypeID("bvlS"), charIDToTypeID("bvlS"), charIDToTypeID("Smth")); // Smooth
        bevelDesc.putUnitDouble(charIDToTypeID("Dpth"), charIDToTypeID("#Prc"), 300); // Depth 300%
        bevelDesc.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 15); // Size 15
        // Highlight Color (White)
        var hiCol = new ActionDescriptor();
        hiCol.putDouble(charIDToTypeID("Rd  "), 255);
        hiCol.putDouble(charIDToTypeID("Grn "), 255);
        hiCol.putDouble(charIDToTypeID("Bl  "), 255);
        bevelDesc.putObject(charIDToTypeID("hglC"), charIDToTypeID("RGBC"), hiCol);
        bevelDesc.putUnitDouble(charIDToTypeID("hglO"), charIDToTypeID("#Prc"), 100); // Opacity
        bevelDesc.putEnumerated(charIDToTypeID("hglM"), charIDToTypeID("BlnM"), charIDToTypeID("Scrn")); // Screen
        // Shadow Color (Dark Brown)
        var shCol = new ActionDescriptor();
        shCol.putDouble(charIDToTypeID("Rd  "), 50);
        shCol.putDouble(charIDToTypeID("Grn "), 20);
        shCol.putDouble(charIDToTypeID("Bl  "), 0);
        bevelDesc.putObject(charIDToTypeID("sdwC"), charIDToTypeID("RGBC"), shCol);
        bevelDesc.putUnitDouble(charIDToTypeID("sdwO"), charIDToTypeID("#Prc"), 75);

        bevelDesc.putBoolean(charIDToTypeID("enab"), true);
        fxDesc.putObject(charIDToTypeID("ebbl"), charIDToTypeID("ebbl"), bevelDesc);

        // B. GRADIENT OVERLAY (Metallic Look)
        var gradDesc = new ActionDescriptor();
        gradDesc.putBoolean(charIDToTypeID("enab"), true);
        gradDesc.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Nrml"));
        gradDesc.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);

        // Define Gradient
        var gradient = new ActionDescriptor();
        gradient.putString(charIDToTypeID("Nm  "), "Gold");
        gradient.putEnumerated(charIDToTypeID("GrdF"), charIDToTypeID("GrdF"), charIDToTypeID("CstS")); // Custom

        // Colors: Brown -> Yellow -> White -> Yellow -> Brown
        var colors = new ActionList();

        function addColor(pos, r, g, b) {
            var pt = new ActionDescriptor();
            var col = new ActionDescriptor();
            col.putDouble(charIDToTypeID("Rd  "), r);
            col.putDouble(charIDToTypeID("Grn "), g);
            col.putDouble(charIDToTypeID("Bl  "), b);
            pt.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), col);
            pt.putInteger(charIDToTypeID("Lctn"), pos); // 0-4096
            pt.putInteger(charIDToTypeID("Mdpn"), 50);
            colors.putObject(charIDToTypeID("Clrt"), pt);
        }

        addColor(0, 100, 60, 0);       // Dark Gold
        addColor(2048, 255, 220, 100); // Bright Gold
        addColor(4096, 120, 80, 0);    // Dark Gold

        gradient.putList(charIDToTypeID("Clrs"), colors);
        gradDesc.putObject(charIDToTypeID("Grad"), charIDToTypeID("Grdn"), gradient);

        fxDesc.putObject(charIDToTypeID("GrOv"), charIDToTypeID("GrOv"), gradDesc);

        // COMMIT
        desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), fxDesc);
        executeAction(charIDToTypeID("setd"), desc, DialogModes.NO);
    }

    applyGold(layer);

    // 4. SAVE
    // Dynamic Path Resolution
    var scriptFile = new File($.fileName);
    var scriptDir = scriptFile.parent; // Tools folder
    var moduleDir = scriptDir.parent;  // Photoshop folder
    var assetsDir = new Folder(moduleDir + "/Assets"); // Adjusted to case sensitivity if needed

    // Fallback if needed, but try relative first
    if (!assetsDir.exists) {
        alert("Assets folder not found at: " + assetsDir.fsName);
        return;
    }

    var folder = assetsDir;
    if (!folder.exists) folder.create();

    var file = new File(folder + "/ONI_GOLD_ASSET.psd");
    var opts = new PhotoshopSaveOptions();
    opts.layers = true; // KEEP LAYERS FOR AFTER EFFECTS
    opts.embedColorProfile = true;
    doc.saveAs(file, opts, true);

    // doc.close(SaveOptions.DONOTSAVECHANGES); // Keep open to show off?
    // Close to be clean.
    doc.close(SaveOptions.DONOTSAVECHANGES);

    // alert("GOLD FORGED: " + file.fsName);

} catch (e) {
    alert("PS FORGE ERROR: " + e.toString());
}
