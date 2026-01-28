// ONIV24 - 3D NEON SPHERE - V2 DEFENSIVE (CLEAN SLATE)
// Target: After Effects Scripting

(function () {
    // === 0. DYNAMIC PATH RESOLUTION ===
    var _scriptFile = new File($.fileName);
    var _oniRoot = _scriptFile.parent.parent.parent.parent.fsName.replace(/\\/g, "/");

    // === 1. SAFE PROTOCOL ===
    try {
        if (app.scriptPreferences) {
            app.scriptPreferences.enableDebugger = false;
        }
        app.displayDialogs = DialogModes.NO;
    } catch (err) { /* CLI Context: simple ignore */ }

    // === 2. LOGGING SYSTEM ===
    var logRoot = _oniRoot + "/logs";
    var logFile = new File(logRoot + "/ae_sphere_render.log");

    // Ensure log folder
    if (!Folder(logRoot).exists) Folder(logRoot).create();

    // Open Log (Append mode for debug, or Write for fresh)
    logFile.open("w");
    function log(msg) {
        // Timestamp
        var d = new Date();
        var timeStr = d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds();
        logFile.writeln("[" + timeStr + "] " + msg);
    }

    // === 3. HELPER: SAFE EFFECT ADDER ===
    function safeAdd(layer, matchName, setupCallback) {
        try {
            log("Attempting to add: " + matchName);
            var eff = layer.property("Effects").addProperty(matchName);

            if (eff) {
                log("  > Success: " + matchName);
                if (setupCallback) {
                    try {
                        setupCallback(eff);
                    } catch (setupErr) {
                        log("  > WARN: Effect added but setup failed: " + setupErr.toString());
                    }
                }
                return true;
            } else {
                log("  > FAIL: " + matchName + " returned null (Missing?)");
                return false;
            }
        } catch (e) {
            log("  > CRITICAL: Error adding " + matchName + ": " + e.toString());
            return false;
        }
    }

    try {
        log("=== SCRIPT START V2 ===");

        // === 4. PROJECT & COMP ===
        var COMP_W = 1920, COMP_H = 1080, FPS = 30, DUR = 10;
        var OUTPUT_FILE = new File(_oniRoot + "/output/neon_sphere_3d.mov");
        if (!OUTPUT_FILE.parent.exists) OUTPUT_FILE.parent.create();

        var proj = app.project;
        if (!proj) { throw "No Project open!"; }

        log("Creating Comp...");
        var comp = proj.items.addComp("Neon_Sphere_Final_V2", COMP_W, COMP_H, 1, DUR, FPS);

        // === 5. LAYERS ===
        log("Adding Background...");
        var bg = comp.layers.addSolid([0.02, 0.02, 0.05], "BG_Dark", COMP_W, COMP_H, 1, DUR);

        log("Adding Texture Layer...");
        var tex = comp.layers.addSolid([1, 1, 1], "Sphere_Map", COMP_W, COMP_H, 1, DUR);

        // === 6. EFFECTS ===

        // FRACTAL NOISE
        var noiseAdded = safeAdd(tex, "ADBE Fractal Noise", function (fn) {
            fn.property("Complexity").setValue(3);
            fn.property("Contrast").setValue(300);
            fn.property("Scale").setValue(150);
            fn.property("Evolution").setValueAtTime(0, 0);
            fn.property("Evolution").setValueAtTime(DUR, 720);
        });

        if (!noiseAdded) {
            log("Trying Backup: Turbulent Noise");
            safeAdd(tex, "ADBE Turbulent Noise", function (fn) {
                fn.property("Complexity").setValue(3);
            });
        }

        // TINT
        safeAdd(tex, "ADBE Tint", function (tint) {
            tint.property("Map White To").setValue([0, 0.9, 1]); // Neon Cyan
            tint.property("Map Black To").setValue([0, 0, 0.2]); // Dark Blue
        });

        // CC SPHERE
        var sphereAdded = safeAdd(tex, "CC Sphere", function (s) {
            s.property("Radius").setValue(250);
            s.property("Light Height").setValue(30);
            s.property("Rotation Y").setValueAtTime(0, 0);
            s.property("Rotation Y").setValueAtTime(DUR, 360);
        });

        if (!sphereAdded) {
            log("Fallback: Creating Circle Mask");
            var mask = tex.masks.addProperty("ADBE Mask Atom");
            var shape = new Shape();
            var s = 400; // Radius
            var c = [COMP_W / 2, COMP_H / 2];
            shape.vertices = [[c[0], c[1] - s], [c[0] + s, c[1]], [c[0], c[1] + s], [c[0] - s, c[1]]];
            shape.inTangents = [[0, 0], [0, -s * 0.55], [s * 0.55, 0], [0, s * 0.55]];
            shape.outTangents = [[s * 0.55, 0], [0, s * 0.55], [-s * 0.55, 0], [0, -s * 0.55]];
            shape.closed = true;
            mask.property("ADBE Mask Shape").setValue(shape);
        }

        // GLOW
        safeAdd(tex, "ADBE Glo2", function (g) {
            g.property("Glow Threshold").setValue(30);
            g.property("Glow Radius").setValue(60);
            g.property("Glow Intensity").setValue(0.6);
        });

        // === 7. ANIMATION ===
        log("Animating Position...");
        var p = tex.property("Transform").property("Position");
        var x1 = COMP_W * 0.3;
        var x2 = COMP_W * 0.7;
        var y = COMP_H / 2;
        p.setValueAtTime(0, [x1, y]);
        p.setValueAtTime(DUR / 2, [x2, y]);
        p.setValueAtTime(DUR, [x1, y]);

        // === 8. RENDER ===
        log("Setting up Render Queue...");
        var rq = proj.renderQueue.items.add(comp);
        var om = rq.outputModule(1);
        om.file = OUTPUT_FILE;

        // Smart Template Selection
        var validTemplate = false;
        var templates = om.templates;
        for (var i = 0; i < templates.length; i++) {
            var tName = templates[i];
            // Prefer H.264
            if (tName.indexOf("H.264") !== -1 || tName.indexOf("Youtube") !== -1 || tName.indexOf("High Quality") !== -1) {
                try {
                    om.applyTemplate(tName);
                    log("Selected Template: " + tName);
                    // Rename extension if needed
                    if (tName.indexOf("H.264") !== -1 && OUTPUT_FILE.name.indexOf(".mov") !== -1) {
                        var newPath = OUTPUT_FILE.fsName.replace(".mov", ".mp4");
                        om.file = new File(newPath);
                        log("Switched output to MP4: " + newPath);
                    }
                    validTemplate = true;
                    break;
                } catch (tempErr) {
                    log("Template " + tName + " failed: " + tempErr.message);
                }
            }
        }

        if (!validTemplate) log("Using Default Template.");

        log("Starting Render...");
        proj.renderQueue.render();
        log("RENDER FINISHED SUCCESSFULLY.");

    } catch (e) {
        log("FATAL ERROR (Global): " + e.toString());
    } finally {
        log("Cleanup & Exit.");
        logFile.close();
        app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); // Exit Clean
        app.quit();
    }
})();
