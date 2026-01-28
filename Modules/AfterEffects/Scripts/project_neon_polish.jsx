// ONIV24 - AUTO-GEN - FINAL SAFE
// Status: Production | Safe Mode | Null Checks

(function () {
    // Dynamic path resolution
    var _scriptFile = new File($.fileName);
    var _oniRoot = _scriptFile.parent.parent.parent.parent.fsName.replace(/\\/g, "/");

    app.scriptPreferences.enableDebugger = false;
    app.displayDialogs = DialogModes.NO;

    try {
        var INPUT_PATH = _oniRoot + "/temp/render_neon/frame_0001.png";
        var OUTPUT_PATH = _oniRoot + "/output/neon_loop_final.mov";

        if (!File(INPUT_PATH).exists) return; // Silent exit if no input

        var io = new ImportOptions(File(INPUT_PATH));
        io.sequence = true;

        var footage = app.project.importFile(io);
        if (!footage) return; // Silent exit if import fails

        var comp = app.project.items.addComp("Neon_Auto", 1920, 1080, 1, 5, 24);
        comp.layers.add(footage);

        var rq = app.project.renderQueue.items.add(comp);
        rq.outputModule(1).file = File(OUTPUT_PATH);

        rq.render();

    } catch (e) {
        // Silent error handling
    } finally {
        app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        app.quit();
    }
})();
