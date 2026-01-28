/**
 * ONI SMART HARVESTER
 * Duplicates the active layer/group from the current document to:
 * 1. A specific target document (by name)
 * 2. OR a new document if none specified
 */

#target photoshop

function main() {
    if (app.documents.length < 1) {
        alert("ONI: No source document open!");
        return;
    }

    var sourceDoc = app.activeDocument;
    var sourceLayer = sourceDoc.activeLayer;

    // Validate Layer
    if (sourceLayer.isBackgroundLayer) {
        alert("ONI: Cannot harvest Background layer. Unlock it first.");
        return;
    }

    // Determine Target
    var targetDoc = null;

    // Look for a document named "ONI_TARGET" or "Untitled-1" or just the *other* document
    if (app.documents.length > 1) {
        // Simple heuristic: The *other* document
        // If we have 2 docs, harvest to the other one.
        for (var i = 0; i < app.documents.length; i++) {
            if (app.documents[i] !== sourceDoc) {
                targetDoc = app.documents[i];
                break;
            }
        }
    }

    if (!targetDoc) {
        // Create new if needed
        targetDoc = app.documents.add(sourceDoc.width, sourceDoc.height, 72, "ONI_HARVEST_TARGET", NewDocumentMode.RGB);
        app.activeDocument = sourceDoc; // Switch back to grab layer
    }

    // DUPLICATE
    try {
        // duplicate(relativeObject, insertionLocation)
        // For documents, duplicate(targetDocument)

        var dupedLayer = sourceLayer.duplicate(targetDoc, ElementPlacement.PLACEATBEGINNING);

        // Switch to target to confirm
        app.activeDocument = targetDoc;

        // Select the duped layer
        targetDoc.activeLayer = dupedLayer;

        // Center it (Optional, but nice)
        // Smart Objects/Groups might have different centers. 
        // We leave it at original coordinates (preserves composition) or we could:
        // dupedLayer.translate(...)

        // alert("ONI: Element Harvested to " + targetDoc.name);

    } catch (e) {
        alert("ONI HARVEST ERROR: " + e);
    }
}

main();
