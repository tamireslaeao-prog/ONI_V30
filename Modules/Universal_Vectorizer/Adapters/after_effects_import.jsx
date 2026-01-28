
/*
    ONI After Effects Adapter - Universal SVG Import
*/

function importUniversalSVG(svgPath) {
    if (!app.project) {
        app.newProject();
    }

    var proj = app.project;
    var fileRef = new File(svgPath);

    if (!fileRef.exists) {
        alert("ONI Error: SVG file not found at " + svgPath);
        return;
    }

    try {
        // 1. Import File
        var importOptions = new ImportOptions(fileRef);
        var importedFootage = proj.importFile(importOptions);

        // 2. Add to Active Comp (or create one)
        var comp = proj.activeItem;
        if (!comp || !(comp instanceof CompItem)) {
            // Create default comp
            comp = proj.items.addComp("ONI_Vector_Comp", 1920, 1080, 1.0, 10, 30);
            comp.openInViewer();
        }

        var layer = comp.layers.add(importedFootage);

        // 3. Convert to Shapes (The Magic Step)
        // Command ID for "Create Shapes from Vector Layer" is 3973
        // Need to select the layer first.

        layer.selected = true;
        app.executeCommand(3973); // Create Shapes from Vector Layer

        // Optionally hide the original footage layer
        layer.enabled = false;

    } catch (e) {
        alert("ONI AE Import Failed: " + e);
    }
}

if (typeof oni_svg_path !== 'undefined') {
    importUniversalSVG(oni_svg_path);
}
