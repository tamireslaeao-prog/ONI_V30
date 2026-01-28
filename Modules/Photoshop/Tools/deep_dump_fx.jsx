/**
 * ONI DEEP FX DUMPER
 * Serializes the full ActionDescriptor structure of Layer Effects.
 */

function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }
function t2s(t) { return app.typeIDToStringID(t); }

var log = "";
function logLine(s) { log += s + "\n"; }

// --- SERIALIZER ---
function paramsToLog(desc, indent) {
    if (!indent) indent = "";

    // We cannot iterate keys easily in JSX ActionDescriptor without knowledge.
    // BUT we can check for specific "Hidden" keys for Metallic looks.

    // BEVEL KEYS
    if (desc.hasKey(cTID('ebbl'))) {
        logLine(indent + "--- BEVEL OBJECT ---");
        var b = desc.getObjectValue(cTID('ebbl'));

        // CONTOUR (The Secret Sauce)
        // 'TrnS' = Transfer Spec? 'MpgS' = Mapping? 
        // Usually Gloss Contour is not exposed directly as a simple enum, 
        // it's often a custom curve descriptor or a preset name.

        // Let's check typical contour keys
        // 'TrnS' -> Transparency Shape?
        // 'Glos' -> Gloss?

        // Try to dump known Bevel keys explicitly with types
        var keys = [
            'enab', 'hglM', 'hglC', 'hglO', 'sdwM', 'sdwC', 'sdwO',
            'bvlT', 'bvlS', 'bvlD', 'Dpth', 'Sz  ', 'Sftn',
            'Angl', 'UseG'
        ];

        // CHECK FOR CONTOUR
        // The key for Gloss Contour in Bevel is often hidden or 'TrnS' (TransferSpec) inside the bevel object
        // Actually it is 'TrnS' (Contour) usually containing 'Nm  ' (Name) and 'Crv ' (Curve)

        if (b.hasKey(cTID('TrnS'))) {
            logLine(indent + "  [!] GLOSS CONTOUR DETECTED (TrnS)");
            var curve = b.getObjectValue(cTID('TrnS'));
            if (curve.hasKey(cTID('Nm  '))) logLine(indent + "    Name: " + curve.getString(cTID('Nm  ')));
            // Ideally we want the name like "Ring - Double" or "Linear"
        } else {
            logLine(indent + "  [!] NO GLOSS CONTOUR FOUND");
        }

        for (var i = 0; i < keys.length; i++) {
            var k = keys[i];
            var tid = cTID(k);
            if (b.hasKey(tid)) {
                logLine(indent + "  Key: " + k + " Exists");
                // We could get values but we did that in V2.
                // We mostly care about what we MISSED.
            }
        }
    }

    // GRADIENT KEYS
    if (desc.hasKey(cTID('GrOv'))) {
        logLine(indent + "--- GRADIENT OVERLAY ---");
        // ...
    }
}

// MAIN EXECUTION
try {
    // Force open LARANJA if needed
    var docName = "LARANJA.psd";
    var doc = null;
    for (var i = 0; i < app.documents.length; i++) {
        if (app.documents[i].name == docName) doc = app.documents[i];
    }
    if (!doc) {
        var f = new File(Folder.desktop + "/ONIV24/temp/" + docName);
        if (f.exists) doc = app.open(f);
    }

    if (doc) {
        app.activeDocument = doc;
        var surf = doc.layerSets.getByName("SURFACE");
        var target = surf.artLayers.getByName("Text02");
        doc.activeLayer = target;

        var ref = new ActionReference();
        ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
        var desc = executeActionGet(ref);

        if (desc.hasKey(cTID("Lefx"))) {
            var lefx = desc.getObjectValue(cTID("Lefx"));
            logLine("DEEP DUMP: " + doc.activeLayer.name + " (" + doc.name + ")");
            paramsToLog(lefx, "");

            var f = new File(Folder.desktop + "/oni_deep_dump.txt");
            f.open("w");
            f.write(log);
            f.close();
            alert("Deep Dump Saved!");
        }
    } else {
        alert("LARANJA.psd not found for deep dump!");
    }
} catch (e) {
    alert("Deep Dump Fail: " + e);
}
