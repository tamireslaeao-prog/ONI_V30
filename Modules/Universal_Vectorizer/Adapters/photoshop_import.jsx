
/*
    ONI Photoshop Adapter - Universal SVG Import
    Places the SVG as an embedded Smart Object.
*/

function importUniversalSVG(svgPath) {
    if (!app.documents.length) {
        alert("ONI: No active document found. Please create one.");
        return;
    }

    var doc = app.activeDocument;
    var fileRef = new File(svgPath);

    if (!fileRef.exists) {
        alert("ONI Error: SVG file not found at " + svgPath);
        return;
    }

    try {
        // Place Embedded
        var idPlc = charIDToTypeID("Plc ");
        var desc2 = new ActionDescriptor();
        var idnull = charIDToTypeID("null");
        desc2.putPath(idnull, fileRef);
        var idFTcs = charIDToTypeID("FTcs");
        var idQCSt = charIDToTypeID("QCSt");
        var idQcsa = charIDToTypeID("Qcsa");
        desc2.putEnumerated(idFTcs, idQCSt, idQcsa);
        executeAction(idPlc, desc2, DialogModes.NO);

    } catch (e) {
        alert("ONI Import Failed: " + e);
    }
}

// Entry point (ONI usually injects the path variable or writes a specific wrapper)
// This file is meant to be called via `/api/photoshop/execute-jsx-file`
// with arguments via memory or temporary file if strictly needed,
// but usually we rely on editing the call or global vars.
// For now, checks if 'oni_svg_path' is defined in global scope.

if (typeof oni_svg_path !== 'undefined') {
    importUniversalSVG(oni_svg_path);
} else {
    // Fallback or explicit call required
    // alert("ONI: oni_svg_path variable not set.");
}
