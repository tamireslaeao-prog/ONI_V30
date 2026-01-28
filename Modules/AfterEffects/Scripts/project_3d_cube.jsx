// ONIV24 - 3D ILLUMINATED CUBE
// Target: After Effects Scripting

(function () {
    // === 0. DYNAMIC PATH RESOLUTION ===
    var _scriptFile = new File($.fileName);
    var _oniRoot = _scriptFile.parent.parent.parent.parent.fsName.replace(/\\/g, "/");

    // === 1. SAFE PROTOCOL ===
    try {
        if (app.scriptPreferences) app.scriptPreferences.enableDebugger = false;
        app.displayDialogs = DialogModes.ALL;
    } catch (err) { }

    // === 2. LOGGING ===
    var logRoot = _oniRoot + "/logs";
    var logFile = new File(logRoot + "/ae_cube_render.log");
    if (!Folder(logRoot).exists) Folder(logRoot).create();
    logFile.open("w");
    function log(msg) {
        var d = new Date();
        logFile.writeln("[" + d.toTimeString().split(' ')[0] + "] " + msg);
    }

    // === 3. HELPERS ===
    function safeAdd(layer, matchName, callback) {
        try {
            log("Adding Effect: " + matchName);
            var eff = layer.property("Effects").addProperty(matchName);
            if (eff && callback) callback(eff);
            return true;
        } catch (e) {
            log("WARN: Failed to add " + matchName + ": " + e.toString());
            return false;
        }
    }

    try {
        log("=== CUBE SCRIPT START ===");

        // CONFIG
        var W = 1920, H = 1080, DUR = 10, FPS = 30;
        var CUBE_SIZE = 400;
        var HALF_SIZE = CUBE_SIZE / 2;
        var OUTPUT_FILE = new File(_oniRoot + "/output/neon_cube_3d.mov");
        if (!OUTPUT_FILE.parent.exists) OUTPUT_FILE.parent.create();

        var proj = app.project;
        if (!proj) throw "No Project";

        var comp = proj.items.addComp("Neon_Cube_3D", W, H, 1, DUR, FPS);

        // BG
        comp.layers.addSolid([0.05, 0.05, 0.1], "BG", W, H, 1, DUR).moveToEnd();

        // CONTROLLER
        var masterNull = comp.layers.addNull();
        masterNull.name = "Cube_Controller";
        masterNull.threeDLayer = true;
        masterNull.position.setValue([W / 2, H / 2, 0]);

        // FACE BUILDER
        function buildFace(name, color, posArr, rotArr) {
            var face = comp.layers.addSolid(color, name, CUBE_SIZE, CUBE_SIZE, 1, DUR);
            face.threeDLayer = true;
            face.parent = masterNull;

            // Transform (Order matters in scripting, but setting properties directly is safe)
            face.position.setValue(posArr);
            face.orientation.setValue(rotArr);

            // Style: Grid
            safeAdd(face, "ADBE Grid", function (g) {
                g.property("Corner").setValue([0, 0]); // Reset
                g.property("Width").setValue(50); // Grid Size
                g.property("Border").setValue(10); // Thickness
                g.property("Color").setValue([0, 1, 1]); // Neon Cyan
            });

            // Style: Glow
            safeAdd(face, "ADBE Glo2", function (g) {
                g.property("Glow Radius").setValue(30);
                g.property("Glow Intensity").setValue(1.0);
            });

            // Transparency
            face.opacity.setValue(60);

            return face;
        }

        log("Building Geometry...");
        // Colors: R, G, B used for base, but Grid overrides.
        // Front (Z = -HALF)
        buildFace("Front", [0, 0, 0], [0, 0, -HALF_SIZE], [0, 0, 0]);
        // Back (Z = HALF)
        buildFace("Back", [0, 0, 0], [0, 0, HALF_SIZE], [0, 0, 0]);
        // Left (X = -HALF, Rot Y = -90)
        buildFace("Left", [0, 0, 0], [-HALF_SIZE, 0, 0], [0, -90, 0]);
        // Right (X = HALF, Rot Y = 90)
        buildFace("Right", [0, 0, 0], [HALF_SIZE, 0, 0], [0, 90, 0]);
        // Top (Y = -HALF, Rot X = 90)
        buildFace("Top", [0, 0, 0], [0, -HALF_SIZE, 0], [90, 0, 0]);
        // Bottom (Y = HALF, Rot X = -90)
        buildFace("Bottom", [0, 0, 0], [0, HALF_SIZE, 0], [-90, 0, 0]);

        // LIGHTING
        log("Adding Lights...");
        var light = comp.layers.addLight("Key_Light", [W / 2, H / 2]);
        light.lightType = LightType.POINT;
        light.intensity.setValue(150);
        light.position.setValue([W / 2 - 500, H / 2 - 500, -500]);

        // ANIMATION (Spin Controller)
        log("Animating...");
        var rotX = masterNull.rotationX;
        var rotY = masterNull.rotationY;
        var rotZ = masterNull.rotationZ; // Orientation is better but Rotation works for spin

        rotX.setValueAtTime(0, 0);
        rotX.setValueAtTime(DUR, 360);

        rotY.setValueAtTime(0, 0);
        rotY.setValueAtTime(DUR, 720);

        masterNull.position.setValueAtTime(0, [W / 2, H / 2, 500]); // Start far
        masterNull.position.setValueAtTime(DUR, [W / 2, H / 2, 0]); // Zoom in

        // RENDER
        log("Render Setup...");
        var rq = proj.renderQueue.items.add(comp);
        var om = rq.outputModule(1);
        om.file = OUTPUT_FILE;

        var templates = om.templates;
        for (var i = 0; i < templates.length; i++) {
            if (templates[i].indexOf("H.264") !== -1) {
                try {
                    om.applyTemplate(templates[i]);
                    if (OUTPUT_FILE.name.indexOf(".mov") !== -1)
                        om.file = new File(OUTPUT_FILE.fsName.replace(".mov", ".mp4"));
                    log("Template: " + templates[i]);
                    break;
                } catch (e) { }
            }
        }

        log("Rendering...");
        proj.renderQueue.render();
        log("SUCCESS: Cube Rendered.");

    } catch (e) {
        log("FATAL: " + e.toString());
    } finally {
        logFile.close();
        // INTERACTIVE MODE: Keep Project Open
        var saveFile = new File(_oniRoot + "/output/Neon_Cube_Interactive.aep");
        app.project.save(saveFile);
        alert("ONI: Cube Generated.\nCheck the 'Neon_Cube_3D' Composition.");
        // app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        // app.quit();
    }
})();
