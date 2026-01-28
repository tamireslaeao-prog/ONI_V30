// ONI Premiere Bridge - Import Subtitles
// Target: Adobe Premiere Pro 2024/2025

function main() {
    var project = app.project;
    if (!project) {
        alert("ONI: No active project.");
        return;
    }

    // 1. Get Active Sequence
    var sequence = project.activeSequence;
    if (!sequence) {
        alert("ONI: Open a sequence first.");
        return;
    }

    // 2. Ask for SRT file (or automate via args if we could pass them easily)
    // For now, we assume the SRT is next to the project or on Desktop/ONI
    var srtFile = File.openDialog("ONI: Select the generated .srt file");

    if (!srtFile) return;

    // 3. Import File
    var importedItems = project.importFiles([srtFile.fsName], true, project.rootItem, false);

    if (!importedItems) {
        alert("Failed to import SRT.");
        return;
    }

    alert("ONI: Subtitles Imported! Drag the caption item to the timeline.");

    // Note: Automating "Drag to Timeline" in recent Premiere versions via API is restricted/undocumented.
    // The "Hacker" way is to use pyautogui to drag it if needed, but import is the API limit usually.
}

main();
