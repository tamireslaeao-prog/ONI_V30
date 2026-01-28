#target photoshop
function main() {
    if (app.documents.length == 0) {
        alert("ONI DIAGNOSTIC: No documents open.");
        return;
    }
    var doc = app.activeDocument;
    var report = "=== ONI LAYER INSPECTOR ===\n";
    report += "Doc: " + doc.name + "\n";
    report += "Size: " + doc.width.as("px") + " x " + doc.height.as("px") + "\n";
    report += "Layers: " + doc.layers.length + "\n\n";

    for (var i = 0; i < doc.layers.length; i++) {
        var layer = doc.layers[i];
        report += "[" + i + "] " + layer.name + "\n";
        report += "    Visible: " + layer.visible + "\n";
        report += "    Opacity: " + layer.opacity + "\n";
        report += "    BlendMode: " + layer.blendMode + "\n";
        report += "    Bounds: " + layer.bounds.join(", ") + "\n";
        report += "    Kind: " + layer.kind + "\n";
        report += "\n";
    }
    // alert(report);
    var f = new File(Folder.desktop + "/ONI_LAYERS.txt");
    f.open("w");
    f.write(report);
    f.close();
}
main();
