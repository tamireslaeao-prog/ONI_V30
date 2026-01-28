/*
 * ONI AE WATCHER v1.1 (Portable)
 * Installed in: Scripts/Startup/
 * Purpose: Monitor job folder and execute tasks from ONI
 */

(function () {
    // Portable path discovery:
    // 1. Try to read from config file next to this script
    // 2. Fallback to environment variable
    // 3. Fallback to common locations

    function discoverJobFolder() {
        // Try config file (created by install script)
        var scriptFile = new File($.fileName);
        var configFile = new File(scriptFile.parent + "/oni_config.json");
        if (configFile.exists) {
            configFile.open("r");
            var cfg = JSON.parse(configFile.read());
            configFile.close();
            return cfg.job_folder;
        }

        // Try environment variable (set by ONI server)
        var envPath = $.getenv("ONI_JOB_FOLDER");
        if (envPath) return envPath;

        // Fallback: search common locations
        var commonPaths = [
            Folder.userData + "/ONI/ae_jobs/",
            Folder.temp + "/oni_ae_jobs/",
            Folder.desktop + "/ONI/temp/ae_jobs/"
        ];
        for (var i = 0; i < commonPaths.length; i++) {
            var f = new Folder(commonPaths[i]);
            if (f.exists) return commonPaths[i];
        }

        // Ultimate fallback: create in temp
        var fallback = Folder.temp + "/oni_ae_jobs/";
        new Folder(fallback).create();
        return fallback;
    }

    var ONI_JOB_FOLDER = discoverJobFolder();
    var POLL_INTERVAL_MS = 2000; // Check every 2 seconds

    // Ensure job folder exists
    var jobFolder = new Folder(ONI_JOB_FOLDER);
    if (!jobFolder.exists) {
        jobFolder.create();
    }

    // Log function
    function log(msg) {
        $.writeln("[ONI_AE_WATCHER] " + msg);
    }

    // Process a single job file
    function processJob(jobFile) {
        log("Processing: " + jobFile.name);

        try {
            jobFile.open("r");
            var content = jobFile.read();
            jobFile.close();

            var job = JSON.parse(content);
            var result = { id: job.id, status: "error", message: "" };

            // Execute based on job type
            switch (job.type) {
                case "ping":
                    result.status = "pong";
                    result.message = "AE is alive!";
                    break;

                case "create_project":
                    app.newProject();
                    if (job.save_path) {
                        app.project.save(new File(job.save_path));
                    }
                    result.status = "success";
                    result.message = "Project created";
                    break;

                case "create_comp":
                    var comp = app.project.items.addComp(
                        job.name || "ONI_Comp",
                        job.width || 1920,
                        job.height || 1080,
                        1,
                        job.duration || 10,
                        job.fps || 30
                    );
                    result.status = "success";
                    result.message = "Comp created: " + comp.name;
                    result.comp_id = comp.id;
                    break;

                case "import_file":
                    var importOptions = new ImportOptions();
                    importOptions.file = new File(job.file_path);
                    var footage = app.project.importFile(importOptions);
                    result.status = "success";
                    result.message = "Imported: " + footage.name;
                    result.item_id = footage.id;
                    break;

                case "add_to_comp":
                    // Find comp by name or id
                    var targetComp = null;
                    for (var i = 1; i <= app.project.numItems; i++) {
                        if (app.project.item(i) instanceof CompItem) {
                            if (job.comp_name && app.project.item(i).name === job.comp_name) {
                                targetComp = app.project.item(i);
                                break;
                            }
                        }
                    }
                    if (targetComp && job.item_id) {
                        var item = app.project.itemByID(job.item_id);
                        if (item) {
                            var layer = targetComp.layers.add(item);
                            result.status = "success";
                            result.message = "Added layer: " + layer.name;
                        }
                    }
                    break;

                case "save_project":
                    if (job.path) {
                        app.project.save(new File(job.path));
                    } else {
                        app.project.save();
                    }
                    result.status = "success";
                    result.message = "Project saved";
                    break;

                case "run_script":
                    // Execute arbitrary JSX code (use with caution)
                    if (job.code) {
                        var evalResult = eval(job.code);
                        result.status = "success";
                        result.message = String(evalResult);
                    }
                    break;

                default:
                    result.status = "error";
                    result.message = "Unknown job type: " + job.type;
            }

            // Write result
            var resultFile = new File(ONI_JOB_FOLDER + "result_" + job.id + ".json");
            resultFile.open("w");
            resultFile.write(JSON.stringify(result, null, 2));
            resultFile.close();

            // Delete processed job
            jobFile.remove();

            log("Completed: " + job.id + " -> " + result.status);

        } catch (e) {
            log("ERROR: " + e.toString());
            // Write error result
            try {
                var errFile = new File(ONI_JOB_FOLDER + "result_error.json");
                errFile.open("w");
                errFile.write(JSON.stringify({ status: "error", message: e.toString() }));
                errFile.close();
            } catch (e2) { }
        }
    }

    // Check for new jobs
    function checkForJobs() {
        var files = jobFolder.getFiles("job_*.json");
        for (var i = 0; i < files.length; i++) {
            processJob(files[i]);
        }
    }

    // Initial check on startup
    log("ONI AE Watcher Started. Monitoring: " + ONI_JOB_FOLDER);
    checkForJobs();

    // Set up polling via app.scheduleTask (AE specific)
    // Note: scheduleTask runs in ms, and repeats
    app.scheduleTask("checkForJobs()", POLL_INTERVAL_MS, true);

    // Make checkForJobs global so scheduleTask can call it
    $.global.checkForJobs = checkForJobs;

})();
