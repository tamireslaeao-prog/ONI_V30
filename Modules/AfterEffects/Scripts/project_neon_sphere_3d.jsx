// ONIV24 - 3D NEON SPHERE - FINAL PRODUCTION
// Target: After Effects Scripting
// Status: Ready for Render

(function () {
    // 0. DYNAMIC PATH RESOLUTION
    var _scriptFile = new File($.fileName);
    var _oniRoot = _scriptFile.parent.parent.parent.parent.fsName.replace(/\\/g, "/");

    // 1. SAFE PROTOCOL
    try {
        if (app.scriptPreferences) app.scriptPreferences.enableDebugger = false;
        app.displayDialogs = DialogModes.NO;
    } catch (err) { /* Ignore Prefs Error in CLI */ }

    // Logging Loop
    var logRoot = _oniRoot + "/logs";
    var logFile = new File(logRoot + "/ae_sphere_render.log");
    if (!Folder(logRoot).exists) Folder(logRoot).create();
    logFile.open("w"); // Overwrite previous logs
    function log(msg) { logFile.writeln(msg); }

    try {
        log("Init 3D Sphere Script...");

        // 2. CONFIG
        var COMP_W = 1920, COMP_H = 1080, FPS = 30, DUR = 10;
        var OUTPUT_FILE = new File(_oniRoot + "/output/neon_sphere_3d.mov");

        if (!OUTPUT_FILE.parent.exists) OUTPUT_FILE.parent.create();

        // 3. COMPOSITION
        var proj = app.project;
        var comp = proj.items.addComp("Neon_Sphere_Final", COMP_W, COMP_H, 1, DUR, FPS);

        // 4. BACKGROUND
        var bg = comp.layers.addSolid([0.02, 0.02, 0.05], "BG_Dark", COMP_W, COMP_H, 1, DUR);

        // 5. SPHERE TEXTURE (The "Neon" part)
        var tex = comp.layers.addSolid([1, 1, 1], "Sphere_Map", COMP_W, COMP_H, 1, DUR);
        // Fractal Noise
        var fn;
        try {
            fn = tex.property("Effects").addProperty("ADBE Fractal Noise");
        } catch (e) {
            log("Warning: Fractal Noise missing. Trying Turbulent.");
            try { fn = tex.property("Effects").addProperty("ADBE Turbulent Noise"); } catch (e2) { }
        }

        if (fn) {
            fn.property("Complexity").setValue(3);
            fn.property("Contrast").setValue(300);
            fn.property("Scale").setValue(150);
            fn.property("Evolution").setValueAtTime(0, 0);
            fn.property("Evolution").setValueAtTime(DUR, 720); // Animate texture
        }

        // Tint (Cyan Neon)
        var tint = tex.property("Effects").addProperty("ADBE Tint");
        tint.property("Map White To").setValue([0, 0.9, 1]); // Neon Cyan
        tint.property("Map Black To").setValue([0, 0, 0.2]); // Dark Blue

        // 6. CC SPHERE
        log("Applying CC Sphere...");
        var sphereInfo = tex.property("Effects").addProperty("CC Sphere");
        if (!sphereInfo) {
            log("ERROR: CC Sphere effect missing. Using Circle fallback.");
            // Fallback: Mask
            var mask = tex.masks.addProperty("ADBE Mask Atom");
            var shape = new Shape();
            var s = 400; // Radius
            var c = [COMP_W / 2, COMP_H / 2];
            shape.vertices = [[c[0], c[1] - s], [c[0] + s, c[1]], [c[0], c[1] + s], [c[0] - s, c[1]]];
            shape.inTangents = [[0, 0], [0, -s * 0.55], [s * 0.55, 0], [0, s * 0.55]]; // Approx circle
            shape.outTangents = [[s * 0.55, 0], [0, s * 0.55], [-s * 0.55, 0], [0, -s * 0.55]];
            shape.closed = true;
            mask.property("ADBE Mask Shape").setValue(shape);
        } else {
            sphereInfo.property("Radius").setValue(250);
            sphereInfo.property("Light Height").setValue(30);
            sphereInfo.property("Rotation Y").setValueAtTime(0, 0);
            sphereInfo.property("Rotation Y").setValueAtTime(DUR, 360);
        }

        // 7. GLOW
        var glow = tex.property("Effects").addProperty("ADBE Glo2");
        glow.property("Glow Threshold").setValue(30);
        glow.property("Glow Radius").setValue(60);
        glow.property("Glow Intensity").setValue(0.6);

        // 8. ANIMATION (Position Ping-Pong)
        var p = tex.property("Transform").property("Position");
        var x1 = COMP_W * 0.3;
        var x2 = COMP_W * 0.7;
        var y = COMP_H / 2;

        p.setValueAtTime(0, [x1, y]);
        p.setValueAtTime(DUR / 2, [x2, y]);
        p.setValueAtTime(DUR, [x1, y]);

        // 9. RENDER
        log("Setting up Render Queue...");
        var rq = proj.renderQueue.items.add(comp);
        var om = rq.outputModule(1);
        om.file = OUTPUT_FILE;

        // H.264 Check
        var templ = om.templates;
        for (var i = 0; i < templ.length; i++) {
            if (templ[i].indexOf("H.264") !== -1) {
                om.applyTemplate(templ[i]);
                if (OUTPUT_FILE.name.indexOf(".mov") !== -1) {
                    om.file = new File(OUTPUT_FILE.fsName.replace(".mov", ".mp4"));
                }
                log("Using H.264 Template: " + templ[i]);
                break;
            }
        }

        log("Rendering...");
        proj.renderQueue.render();
        log("DONE.");

    } catch (e) {
        log("FATAL ERROR: " + e.toString());
    } finally {
        logFile.close();
        app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); // Clean exit
        app.quit();
    }
})();
