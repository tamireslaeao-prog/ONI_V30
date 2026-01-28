/**
 * ONI STYLE STEALER (FX EXTRACTOR) - V3 ROBUST WITH LAYER SCANNING
 * Dumps Style Parameters to Desktop for Reverse Engineering.
 */

function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }
function t2s(t) { return app.typeIDToStringID(t); }

// DEBUG START
var debugFile = new File(Folder.desktop + "/ONI_DEBUG.txt");
debugFile.open("w");
debugFile.writeln("SCRIPT V3 STARTED");
debugFile.close();

var log = "";
function logLine(s) { log += s + "\n"; }

function getUnitDouble(desc, key) {
    if (desc.hasKey(key)) return desc.getUnitDoubleValue(key);
    return "N/A";
}
function getDouble(desc, key) {
    if (desc.hasKey(key)) return desc.getDouble(key);
    return "N/A";
}
function getBoolean(desc, key) {
    if (desc.hasKey(key)) return desc.getBoolean(key);
    return "N/A";
}
function getInteger(desc, key) {
    if (desc.hasKey(key)) return desc.getInteger(key);
    return "N/A";
}
function getEnum(desc, key) {
    if (desc.hasKey(key)) return t2s(desc.getEnumerationValue(key));
    return "N/A";
}

function dumpColor(desc, key) {
    if (!desc.hasKey(key)) return "No Color";
    var c = desc.getObjectValue(key);
    var r = c.getDouble(cTID('Rd  '));
    var g = c.getDouble(cTID('Grn '));
    var b = c.getDouble(cTID('Bl  '));
    return "RGB(" + Math.round(r) + "," + Math.round(g) + "," + Math.round(b) + ")";
}

function extractBevel(lefx) {
    if (!lefx.hasKey(cTID('ebbl'))) return;
    var d = lefx.getObjectValue(cTID('ebbl'));
    if (!d.getBoolean(cTID('enab'))) return;

    logLine("--- BEVEL ---");
    logLine("Style: " + getEnum(d, cTID('bvlS')));
    logLine("Technique: " + getEnum(d, cTID('bvlT'))); // Smooth, Chisel Hard
    logLine("Depth: " + getUnitDouble(d, cTID('Dpth')));
    logLine("Direction: " + getEnum(d, cTID('bvlD')));
    logLine("Size: " + getUnitDouble(d, cTID('Sz  ')));
    logLine("Soften: " + getUnitDouble(d, cTID('Sftn')));
    logLine("Angle: " + getUnitDouble(d, cTID('Angl')));
    logLine("Altitude: " + getUnitDouble(d, cTID('UseG'))); // Global light?

    logLine("Highlight Mode: " + getEnum(d, cTID('hglM')));
    logLine("Highlight Color: " + dumpColor(d, cTID('hglC')));
    logLine("Highlight Opacity: " + getUnitDouble(d, cTID('hglO')));

    logLine("Shadow Mode: " + getEnum(d, cTID('sdwM')));
    logLine("Shadow Color: " + dumpColor(d, cTID('sdwC')));
    logLine("Shadow Opacity: " + getUnitDouble(d, cTID('sdwO')));
}

function extractGradientOverlay(lefx) {
    if (!lefx.hasKey(cTID('GrOv'))) return;
    var d = lefx.getObjectValue(cTID('GrOv'));
    if (!d.getBoolean(cTID('enab'))) return;

    logLine("--- GRADIENT OVERLAY ---");
    logLine("Blend Mode: " + getEnum(d, cTID('Md  ')));
    logLine("Opacity: " + getUnitDouble(d, cTID('Opct')));
    logLine("Angle: " + getUnitDouble(d, cTID('Angl')));
    logLine("Scale: " + getUnitDouble(d, cTID('Scl ')));

    // Gradient Content
    if (d.hasKey(cTID('Grad'))) {
        var g = d.getObjectValue(cTID('Grad'));
        logLine("Gradient Name: " + g.getString(cTID('Nm  ')));

        if (g.hasKey(cTID('Clrs'))) {
            var colors = g.getList(cTID('Clrs'));
            logLine("Stops Count: " + colors.count);
            for (var i = 0; i < colors.count; i++) {
                var stop = colors.getObjectValue(i);
                var loc = stop.getInteger(cTID('Lctn'));
                var mid = stop.getInteger(cTID('Mdpn'));
                var col = dumpColor(stop, cTID('Clr '));
                logLine("  Stop " + i + ": Location=" + loc + " (" + (loc / 40.96).toFixed(1) + "%) Color=" + col);
            }
        }
    }
}

function extractSatin(lefx) {
    if (!lefx.hasKey(cTID('ChFX'))) return;
    var d = lefx.getObjectValue(cTID('ChFX'));
    if (!d.getBoolean(cTID('enab'))) return;

    logLine("--- SATIN ---");
    logLine("Blend Mode: " + getEnum(d, cTID('Md  ')));
    logLine("Color: " + dumpColor(d, cTID('Clr ')));
    logLine("Opacity: " + getUnitDouble(d, cTID('Opct')));
    logLine("Angle: " + getUnitDouble(d, cTID('Angl')));
    logLine("Distance: " + getUnitDouble(d, cTID('Dstn')));
    logLine("Size: " + getUnitDouble(d, cTID('Sz  ')));
    logLine("Invert: " + getBoolean(d, cTID('Invr')));
}

function extractDropShadow(lefx) {
    if (!lefx.hasKey(cTID('DrSh'))) return;
    var d = lefx.getObjectValue(cTID('DrSh'));
    if (!d.getBoolean(cTID('enab'))) return;

    logLine("--- DROP SHADOW ---");
    logLine("Blend Mode: " + getEnum(d, cTID('Md  ')));
    logLine("Color: " + dumpColor(d, cTID('Clr ')));
    logLine("Opacity: " + getUnitDouble(d, cTID('Opct')));
    logLine("Angle: " + getUnitDouble(d, cTID('Angl')));
    logLine("Distance: " + getUnitDouble(d, cTID('Dstn')));
    logLine("Size: " + getUnitDouble(d, cTID('Sz  ')));
    logLine("Spread: " + getUnitDouble(d, cTID('Ckmt')));
}

function extractStroke(lefx) {
    if (!lefx.hasKey(cTID('FrFX'))) return;
    var d = lefx.getObjectValue(cTID('FrFX'));
    if (!d.getBoolean(cTID('enab'))) return;

    logLine("--- STROKE ---");
    logLine("Size: " + getUnitDouble(d, cTID('Sz  ')));
    logLine("Position: " + getEnum(d, cTID('Pstn')));
    logLine("Fill Type: " + getEnum(d, cTID('FlTp'))); // Color, Gradient, Pattern
    logLine("Color: " + dumpColor(d, cTID('Clr ')));
}

// MAIN EXECUTION WITH LAYER SCANNING
try {
    var doc = app.activeDocument;
    var foundStyle = false;

    // Helper to get descriptor for a specific layer by index would be complex in AM.
    // Simpler approach: Iterate DOM layers, make active, check AM.

    function scanLayers(layers) {
        for (var i = 0; i < layers.length; i++) {
            var layer = layers[i];
            if (layer.typename == "LayerSet") {
                if (scanLayers(layer.layers)) return true;
            } else {
                // Select the layer
                doc.activeLayer = layer;

                // Check for FX via AM
                var ref = new ActionReference();
                ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
                var desc = executeActionGet(ref);

                if (desc.hasKey(cTID("Lefx"))) {
                    var lefx = desc.getObjectValue(cTID("Lefx"));
                    logLine("STYLE FOUND ON LAYER: " + layer.name);

                    extractBevel(lefx);
                    extractGradientOverlay(lefx);
                    extractSatin(lefx);
                    extractDropShadow(lefx);
                    extractStroke(lefx);

                    var f = new File(Folder.desktop + "/oni_extracted_style.txt");
                    f.open("w");
                    f.write(log);
                    f.close();

                    alert("SUCCESS! Style extracted from layer: '" + layer.name + "'\nSaved to Desktop/oni_extracted_style.txt");
                    return true;
                }
            }
        }
        return false;
    }

    if (!scanLayers(doc.layers)) {
        alert("FAILED: Scanned all layers in '" + doc.name + "' and found NO Styles.");
    }

} catch (e) {
    alert("CRITICAL ERROR: " + e);
}
