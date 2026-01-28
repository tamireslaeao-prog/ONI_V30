/**
 * ONI LAYER INSPECTOR
 * Dumps full layer hierarchy to text file for debugging.
 */

function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }

var logFile = new File(Folder.desktop + "/ONI_LAYER_TREE.txt");
logFile.open("w");

function log(msg) {
    logFile.writeln(msg);
}

function hasEffects(layer) {
    try {
        app.activeDocument.activeLayer = layer;
        var ref = new ActionReference();
        ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
        var desc = executeActionGet(ref);
        return desc.hasKey(cTID("Lefx"));
    } catch (e) {
        return false;
    }
}

function traverse(layers, indent) {
    for (var i = 0; i < layers.length; i++) {
        var layer = layers[i];
        var info = indent + "+ [" + layer.typename + "] '" + layer.name + "'";

        if (layer.visible) info += " (VISIBLE)";
        else info += " (HIDDEN)";

        if (layer.typename != "LayerSet") {
            if (hasEffects(layer)) info += " *** HAS EFFECTS ***";
        }

        log(info);

        if (layer.typename == "LayerSet") {
            traverse(layer.layers, indent + "  ");
        }
    }
}

try {
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        log("DOCUMENT: " + doc.name);
        log("---------------------------------------------------");
        traverse(doc.layers, "");
        log("---------------------------------------------------");
        log("DONE.");
    } else {
        log("NO DOCUMENTS OPEN");
    }
} catch (e) {
    log("ERROR: " + e);
}

logFile.close();
alert("Layer Tree Dumped to Desktop/ONI_LAYER_TREE.txt");
