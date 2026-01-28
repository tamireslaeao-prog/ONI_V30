/**
 * ONI SMART TEXT REPLACER
 * Scans the active document (assumed to be an opened Smart Object)
 * Finds the first visible Text Layer and changes content to the argument.
 */

#target photoshop

function main() {
    var newText = "ONI"; // Default

    // Recursive finder
    function findTextLayer(layers) {
        for (var i = 0; i < layers.length; i++) {
            var layer = layers[i];
            if (layer.visible) {
                if (layer.kind == LayerKind.TEXT) {
                    return layer;
                }
                if (layer.typename == "LayerSet") {
                    var found = findTextLayer(layer.layers);
                    if (found) return found;
                }
            }
        }
        return null;
    }

    if (app.documents.length == 0) return;

    var doc = app.activeDocument;
    var targetLayer = findTextLayer(doc.layers);

    if (targetLayer) {
        // Change Text
        targetLayer.textItem.contents = newText;

        // Optional: Resize to fit if huge? 
        // For now, trust the template's font settings.

        // alert("ONI: Updated text to '" + newText + "'");
    } else {
        alert("ONI: No visible text layer found in Smart Object!");
    }
}

main();
