// ONI System Verification Script - Photoshop
#target photoshop

app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
app.displayDialogs = DialogModes.NO;

try {
    // 1. Create Document
    var doc = app.documents.add(UnitValue(1920, "px"), UnitValue(1080, "px"), 72, "ONI_SYSTEM_TEST_01");

    // 2. Fill Background (Dark Hex: #1a1a2e)
    var color = new SolidColor();
    color.rgb.hexValue = "1a1a2e";
    doc.selection.selectAll();
    doc.selection.fill(color);
    doc.selection.deselect();

    // 3. Add Text
    var textLayer = doc.artLayers.add();
    textLayer.kind = LayerKind.TEXT;
    var textItem = textLayer.textItem;
    textItem.contents = "ONI: PHOTOSHOP OPERATIONAL";
    textItem.position = [UnitValue(400, "px"), UnitValue(540, "px")];
    textItem.size = UnitValue(100, "px");

    var textColor = new SolidColor();
    textColor.rgb.hexValue = "00ff00"; // Green
    textItem.color = textColor;

    // 4. Verification Check
    if (doc.transparency) {
        // Just to do something valid
    }

} catch (e) {
    alert("Error: " + e.message);
}
