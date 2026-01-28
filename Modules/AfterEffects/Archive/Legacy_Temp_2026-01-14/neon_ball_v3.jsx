// Neon Ball Animation - Debug & Robust Render
// Author: Antigravity

(function () {
    // Logging helper
    var logFile = new File("C:/Users/user/Desktop/ae_debug_log.txt");
    logFile.open("w");
    function log(msg) { logFile.writeln(new Date().toTimeString() + ": " + msg); }

    try {
        log("Script Started");

        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        app.newProject();
        log("Project Created");

        var comp = app.project.items.addComp("Neon Jump Final", 1920, 1080, 1, 10, 30);
        comp.openInViewer();

        // Background
        comp.layers.addSolid([0, 0, 0], "Background", 1920, 1080, 1, 10);

        // Ball
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = "Neon Ball";
        var shapeGroup = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([100, 100]);
        var fill = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("Color").setValue([0, 1, 1]);

        // Anim
        var posProp = shapeLayer.property("Transform").property("Position");
        for (var t = 0; t < 10; t += 1) {
            posProp.setValueAtTime(t, [960, 900]);
            posProp.setValueAtTime(t + 0.5, [960, 300]);
        }
        posProp.setValueAtTime(10, [960, 900]);
        log("Animation Created");

        // Render Setup
        var rq = app.project.renderQueue;
        var rqItem = rq.items.add(comp);
        var om = rqItem.outputModule(1);

        // Log Templates
        var templates = om.templates;
        log("Available Templates: " + templates.join(", "));

        // Find Best Template
        var safeTemplate = "";
        // Look for Lossless or Sem perdas explicitly (AVI usually)
        for (var i = 0; i < templates.length; i++) {
            var t = templates[i].toLowerCase();
            if (t === "lossless" || t === "sem perdas" || t === "ideal") {
                safeTemplate = templates[i];
                break;
            }
        }

        if (safeTemplate !== "") {
            log("Applying Template: " + safeTemplate);
            om.applyTemplate(safeTemplate);
        } else {
            log("No known safe template found, using default.");
        }

        // Force AVI extension logic check
        var targetFile = new File("C:/Users/user/Desktop/neon_ball_final.avi");
        log("Target File: " + targetFile.fsName);

        // Explicitly set
        om.file = targetFile;
        log("File set successfully");

        // Save AEP
        var projectFile = new File("C:/Users/user/Desktop/ONI V24/temp/neon_debug_project.aep");
        app.project.save(projectFile);
        log("Project Saved");

        // Render
        rq.render();
        log("Render Complete");

    } catch (e) {
        log("ERROR: " + e.toString());
        alert("Script Error: " + e.toString());
    } finally {
        logFile.close();
        // Don't close immediately so we can see result if needed, or close:
        app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        app.quit();
    }
})();
