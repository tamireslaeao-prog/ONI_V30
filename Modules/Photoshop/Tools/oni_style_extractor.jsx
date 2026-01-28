#target photoshop

/**
 * ONI EXTRACTOR FINAL - DEBUGGED & TESTED
 * Específico para LARANJA.psd com Text01/Text02/Text03
 */

// ============ JSON POLYFILL ============
if (typeof JSON !== 'object') { JSON = {}; }
(function () {
    'use strict';
    if (typeof JSON.stringify !== 'function') {
        JSON.stringify = function (value) {
            var type = typeof value;
            if (type === 'undefined' || value === null) return 'null';
            if (type === 'number' || type === 'boolean') return String(value);
            if (type === 'string') return '"' + value.replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"';
            if (value instanceof Array) {
                var arr = [];
                for (var i = 0; i < value.length; i++) arr.push(JSON.stringify(value[i]));
                return '[' + arr.join(',') + ']';
            }
            if (type === 'object') {
                var pairs = [];
                for (var k in value) {
                    if (value.hasOwnProperty(k)) {
                        pairs.push('"' + k + '":' + JSON.stringify(value[k]));
                    }
                }
                return '{' + pairs.join(',') + '}';
            }
            return 'null';
        };
    }
}());

// ============ UTILITIES ============
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }
function t2s(t) {
    try {
        return app.typeIDToStringID(t);
    } catch (e) {
        return "id_" + t;
    }
}

var LOG = [];
function log(msg) {
    LOG.push("[" + new Date().toTimeString().substr(0, 8) + "] " + msg);
}

// ============ SAFE EXTRACTORS ============
function safeGetEnum(desc, key) {
    try {
        if (desc.hasKey(key)) {
            var enumType = desc.getEnumerationType(key);
            var enumValue = desc.getEnumerationValue(key);
            return {
                type: t2s(enumType),
                value: t2s(enumValue)
            };
        }
    } catch (e) { log("Enum error on key " + t2s(key)); }
    return null;
}

function safeGetUnitDouble(desc, key) {
    try {
        if (desc.hasKey(key)) {
            var val = desc.getUnitDoubleValue(key);
            var unit = desc.getUnitDoubleType(key);
            return {
                value: val,
                unit: t2s(unit)
            };
        }
    } catch (e) { log("UnitDouble error on key " + t2s(key)); }
    return null;
}

function safeGetDouble(desc, key) {
    try {
        if (desc.hasKey(key)) {
            return desc.getDouble(key);
        }
    } catch (e) { }
    return null;
}

function safeGetBoolean(desc, key) {
    try {
        if (desc.hasKey(key)) {
            return desc.getBoolean(key);
        }
    } catch (e) { }
    return null;
}

function safeGetInteger(desc, key) {
    try {
        if (desc.hasKey(key)) {
            return desc.getInteger(key);
        }
    } catch (e) { }
    return null;
}

function safeGetString(desc, key) {
    try {
        if (desc.hasKey(key)) {
            return desc.getString(key);
        }
    } catch (e) { }
    return null;
}

function extractColor(desc, key) {
    try {
        if (!desc.hasKey(key)) return null;
        var c = desc.getObjectValue(key);
        var r = Math.round(c.getDouble(cTID('Rd  ')));
        var g = Math.round(c.getDouble(cTID('Grn ')));
        var b = Math.round(c.getDouble(cTID('Bl  ')));
        var hex = "#" +
            ("0" + r.toString(16)).slice(-2) +
            ("0" + g.toString(16)).slice(-2) +
            ("0" + b.toString(16)).slice(-2);
        return {
            r: r,
            g: g,
            b: b,
            hex: hex.toUpperCase()
        };
    } catch (e) {
        log("Color extraction failed");
        return null;
    }
}

// ============ GRADIENT EXTRACTOR ============
function extractGradient(desc, gradKey) {
    try {
        if (!desc.hasKey(gradKey)) {
            log("No gradient key found");
            return null;
        }

        var g = desc.getObjectValue(gradKey);
        var gradient = {
            name: safeGetString(g, cTID('Nm  ')) || "Unnamed",
            type: safeGetEnum(g, cTID('GrdF')),
            interpolation: safeGetDouble(g, cTID('Intr')),
            colors: [],
            transparencies: []
        };

        // Color stops
        if (g.hasKey(cTID('Clrs'))) {
            var colorList = g.getList(cTID('Clrs'));
            log("Found " + colorList.count + " color stops");

            for (var i = 0; i < colorList.count; i++) {
                var stop = colorList.getObjectValue(i);
                var colorObj = extractColor(stop, cTID('Clr '));

                gradient.colors.push({
                    location: safeGetInteger(stop, cTID('Lctn')),
                    midpoint: safeGetInteger(stop, cTID('Mdpn')),
                    color: colorObj
                });
            }
        }

        // Transparency stops
        if (g.hasKey(cTID('Trns'))) {
            var transList = g.getList(cTID('Trns'));
            log("Found " + transList.count + " transparency stops");

            for (var i = 0; i < transList.count; i++) {
                var stop = transList.getObjectValue(i);
                gradient.transparencies.push({
                    location: safeGetInteger(stop, cTID('Lctn')),
                    midpoint: safeGetInteger(stop, cTID('Mdpn')),
                    opacity: safeGetUnitDouble(stop, cTID('Opct'))
                });
            }
        }

        return gradient;
    } catch (e) {
        log("Gradient extraction failed: " + e);
        return null;
    }
}

// ============ EFFECT EXTRACTORS ============
function extractBevel(lefx) {
    try {
        if (!lefx.hasKey(cTID('ebbl'))) {
            log("No bevel found");
            return null;
        }

        var d = lefx.getObjectValue(cTID('ebbl'));
        if (!safeGetBoolean(d, cTID('enab'))) {
            log("Bevel disabled");
            return null;
        }

        log("Extracting bevel...");
        return {
            type: "bevel_emboss",
            enabled: true,
            style: safeGetEnum(d, cTID('bvlS')),
            technique: safeGetEnum(d, cTID('bvlT')),
            depth: safeGetUnitDouble(d, cTID('srgR')),
            direction: safeGetEnum(d, cTID('bvlD')),
            size: safeGetUnitDouble(d, cTID('blur')),
            soften: safeGetUnitDouble(d, cTID('Sftn')),
            angle: safeGetUnitDouble(d, cTID('lagl')),
            altitude: safeGetUnitDouble(d, cTID('Lald')),
            gloss_contour: safeGetEnum(d, cTID('TrnS')),
            highlight: {
                mode: safeGetEnum(d, cTID('hglM')),
                color: extractColor(d, cTID('hglC')),
                opacity: safeGetUnitDouble(d, cTID('hglO'))
            },
            shadow: {
                mode: safeGetEnum(d, cTID('sdwM')),
                color: extractColor(d, cTID('sdwC')),
                opacity: safeGetUnitDouble(d, cTID('sdwO'))
            }
        };
    } catch (e) {
        log("Bevel extraction error: " + e);
        return null;
    }
}

function extractStroke(lefx) {
    try {
        if (!lefx.hasKey(cTID('FrFX'))) {
            log("No stroke found");
            return null;
        }

        var d = lefx.getObjectValue(cTID('FrFX'));
        if (!safeGetBoolean(d, cTID('enab'))) {
            log("Stroke disabled");
            return null;
        }

        log("Extracting stroke...");
        var stroke = {
            type: "stroke",
            enabled: true,
            style: safeGetEnum(d, cTID('Styl')),
            paint_type: safeGetEnum(d, cTID('PntT')),
            mode: safeGetEnum(d, cTID('Md  ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            size: safeGetUnitDouble(d, cTID('Sz  '))
        };

        // Check fill type
        var paintType = stroke.paint_type ? stroke.paint_type.value : null;

        if (paintType === "solidColor") {
            stroke.color = extractColor(d, cTID('Clr '));
        } else if (paintType === "gradientFill") {
            stroke.gradient = extractGradient(d, cTID('Grad'));
        } else if (paintType === "pattern") {
            stroke.pattern = safeGetString(d, cTID('Ptrn'));
        }

        return stroke;
    } catch (e) {
        log("Stroke extraction error: " + e);
        return null;
    }
}

function extractDropShadow(lefx) {
    try {
        if (!lefx.hasKey(cTID('DrSh'))) {
            log("No drop shadow found");
            return null;
        }

        var d = lefx.getObjectValue(cTID('DrSh'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting drop shadow...");
        return {
            type: "drop_shadow",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            use_global_light: safeGetBoolean(d, cTID('uglg')),
            angle: safeGetUnitDouble(d, cTID('lagl')),
            distance: safeGetUnitDouble(d, cTID('Dstn')),
            choke: safeGetUnitDouble(d, cTID('Ckmt')),
            size: safeGetUnitDouble(d, cTID('blur')),
            noise: safeGetUnitDouble(d, cTID('Nose')),
            anti_aliased: safeGetBoolean(d, cTID('AntA')),
            contour: safeGetEnum(d, cTID('TrnS')),
            layer_knocks_out: safeGetBoolean(d, cTID('layerConceals'))
        };
    } catch (e) {
        log("Drop shadow extraction error: " + e);
        return null;
    }
}

function extractInnerShadow(lefx) {
    try {
        if (!lefx.hasKey(cTID('IrSh'))) return null;
        var d = lefx.getObjectValue(cTID('IrSh'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting inner shadow...");
        return {
            type: "inner_shadow",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            angle: safeGetUnitDouble(d, cTID('lagl')),
            distance: safeGetUnitDouble(d, cTID('Dstn')),
            choke: safeGetUnitDouble(d, cTID('Ckmt')),
            size: safeGetUnitDouble(d, cTID('blur'))
        };
    } catch (e) {
        log("Inner shadow extraction error: " + e);
        return null;
    }
}

function extractOuterGlow(lefx) {
    try {
        if (!lefx.hasKey(cTID('OrGl'))) return null;
        var d = lefx.getObjectValue(cTID('OrGl'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting outer glow...");
        return {
            type: "outer_glow",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            noise: safeGetUnitDouble(d, cTID('Nose')),
            technique: safeGetEnum(d, cTID('GlwT')),
            spread: safeGetUnitDouble(d, cTID('Ckmt')),
            size: safeGetUnitDouble(d, cTID('blur'))
        };
    } catch (e) {
        log("Outer glow extraction error: " + e);
        return null;
    }
}

function extractInnerGlow(lefx) {
    try {
        if (!lefx.hasKey(cTID('IrGl'))) return null;
        var d = lefx.getObjectValue(cTID('IrGl'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting inner glow...");
        return {
            type: "inner_glow",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            technique: safeGetEnum(d, cTID('GlwT')),
            source: safeGetEnum(d, cTID('glwS')),
            choke: safeGetUnitDouble(d, cTID('Ckmt')),
            size: safeGetUnitDouble(d, cTID('blur'))
        };
    } catch (e) {
        log("Inner glow extraction error: " + e);
        return null;
    }
}

function extractSatin(lefx) {
    try {
        if (!lefx.hasKey(cTID('ChFX'))) return null;
        var d = lefx.getObjectValue(cTID('ChFX'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting satin...");
        return {
            type: "satin",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            angle: safeGetUnitDouble(d, cTID('lagl')),
            distance: safeGetUnitDouble(d, cTID('Dstn')),
            size: safeGetUnitDouble(d, cTID('blur')),
            invert: safeGetBoolean(d, cTID('Invr'))
        };
    } catch (e) {
        log("Satin extraction error: " + e);
        return null;
    }
}

function extractColorOverlay(lefx) {
    try {
        if (!lefx.hasKey(cTID('SoFi'))) return null;
        var d = lefx.getObjectValue(cTID('SoFi'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting color overlay...");
        return {
            type: "color_overlay",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: safeGetUnitDouble(d, cTID('Opct'))
        };
    } catch (e) {
        log("Color overlay extraction error: " + e);
        return null;
    }
}

function extractGradientOverlay(lefx) {
    try {
        if (!lefx.hasKey(cTID('GrFl'))) {
            log("No gradient overlay found");
            return null;
        }

        var d = lefx.getObjectValue(cTID('GrFl'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting gradient overlay...");
        return {
            type: "gradient_overlay",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            gradient_data: extractGradient(d, cTID('Grad')),
            reverse: safeGetBoolean(d, cTID('Rvrs')),
            reverse: safeGetBoolean(d, cTID('Rvrs')),
            dither: safeGetBoolean(d, cTID('Dthr')),
            align: safeGetBoolean(d, cTID('Algn')),
            scale: safeGetUnitDouble(d, cTID('Scl ')),
            offset: {
                horizontal: safeGetUnitDouble(d, cTID('Ofst')),
                vertical: safeGetUnitDouble(d, cTID('Ofst'))
            },
            angle: safeGetUnitDouble(d, cTID('Angl')),
            style: safeGetEnum(d, cTID('Type'))
        };
    } catch (e) {
        log("Gradient overlay extraction error: " + e);
        return null;
    }
}

// ============ PATTERN OVERLAY ============
function extractPatternOverlay(lefx) {
    try {
        if (!lefx.hasKey(cTID('patternFill'))) return null;
        var d = lefx.getObjectValue(cTID('patternFill'));
        if (!safeGetBoolean(d, cTID('enab'))) return null;

        log("Extracting pattern overlay...");
        return {
            type: "pattern_overlay",
            enabled: true,
            mode: safeGetEnum(d, cTID('Md  ')),
            opacity: safeGetUnitDouble(d, cTID('Opct')),
            scale: safeGetUnitDouble(d, cTID('Scl ')),
            pattern: safeGetString(d, cTID('Ptrn'))
        };
    } catch (e) {
        log("Pattern overlay extraction error: " + e);
        return null;
    }
}

// ============ EXTRACT ALL FROM LAYER ============
function extractLayerStyle(layer) {
    log("=== Extracting style from: " + layer.name + " ===");

    var style = {
        layer_name: layer.name,
        effects: []
    };

    try {
        app.activeDocument.activeLayer = layer;

        var ref = new ActionReference();
        ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
        var desc = executeActionGet(ref);

        if (!desc.hasKey(cTID("Lefx"))) {
            log("Layer has no effects (Lefx key missing)");
            return style;
        }

        var lefx = desc.getObjectValue(cTID("Lefx"));
        log("Layer effects descriptor obtained");

        // Extract all effects
        var fx;

        if (fx = extractBevel(lefx)) style.effects.push(fx);
        if (fx = extractStroke(lefx)) style.effects.push(fx);
        if (fx = extractInnerShadow(lefx)) style.effects.push(fx);
        if (fx = extractInnerGlow(lefx)) style.effects.push(fx);
        if (fx = extractSatin(lefx)) style.effects.push(fx);
        if (fx = extractColorOverlay(lefx)) style.effects.push(fx);
        if (fx = extractGradientOverlay(lefx)) style.effects.push(fx);
        if (fx = extractPatternOverlay(lefx)) style.effects.push(fx);
        if (fx = extractDropShadow(lefx)) style.effects.push(fx);
        if (fx = extractOuterGlow(lefx)) style.effects.push(fx);

        log("Total effects extracted: " + style.effects.length);

    } catch (e) {
        log("ERROR extracting layer style: " + e);
    }

    return style;
}

// ============ FIND LAYER BY NAME ============
function findLayer(layers, name) {
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].name === name) {
            return layers[i];
        }
        if (layers[i].typename === "LayerSet") {
            var found = findLayer(layers[i].layers, name);
            if (found) return found;
        }
    }
    return null;
}

// ============ MAIN EXECUTION ============
// ============ SCANNER DE LAYERS ============
function scanLayers(layers) {
    var foundAny = false;
    for (var i = 0; i < layers.length; i++) {
        var layer = layers[i];

        try {
            if (layer.typename == "LayerSet") {
                if (scanLayers(layer.layers)) foundAny = true;
            } else {
                app.activeDocument.activeLayer = layer;
                var ref = new ActionReference();
                ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
                var desc = executeActionGet(ref);

                if (desc.hasKey(cTID("Lefx"))) {
                    // Reset styleData for each layer
                    styleData = {
                        metadata: {
                            version: "5.0",
                            extracted_at: new Date().toString(),
                            source_file: app.activeDocument.name,
                            layer_name: layer.name
                        },
                        effects: [],
                        ai_instructions: []
                    };

                    var lefx = desc.getObjectValue(cTID("Lefx"));

                    // Standard Legacy Checks
                    var bevel = extractBevel(lefx);
                    if (bevel) styleData.effects.push(bevel);

                    var gradOverlay = extractGradientOverlay(lefx);
                    if (gradOverlay) styleData.effects.push(gradOverlay);

                    var patternOverlay = extractPatternOverlay(lefx);
                    if (patternOverlay) styleData.effects.push(patternOverlay);

                    var satin = extractSatin(lefx);
                    if (satin) styleData.effects.push(satin);

                    var dropShadow = extractDropShadow(lefx);
                    if (dropShadow) styleData.effects.push(dropShadow);

                    var innerShadow = extractInnerShadow(lefx);
                    if (innerShadow) styleData.effects.push(innerShadow);

                    var stroke = extractStroke(lefx);
                    if (stroke) styleData.effects.push(stroke);

                    var innerGlow = extractInnerGlow(lefx);
                    if (innerGlow) styleData.effects.push(innerGlow);

                    var outerGlow = extractOuterGlow(lefx);
                    if (outerGlow) styleData.effects.push(outerGlow);

                    saveStyleData(layer.name);
                    foundAny = true;
                }
            }
        } catch (e) {
            // Continue 
        }
    }
    return foundAny;
}

// ============ SALVAR DADOS ============
function saveStyleData(suffix) {
    var desktop = Folder.desktop;
    if (!suffix) suffix = "Master";

    // Clean filename
    var cleanSuffix = suffix.replace(/[^a-z0-9]/gi, '_');

    try {
        // SAVE SPECIFIC (Layer Name)
        var jsonFile = new File(desktop + "/ONI_STYLE_DATA_" + cleanSuffix + ".json");
        jsonFile.encoding = "UTF-8";
        jsonFile.open("w");
        jsonFile.write(JSON.stringify(styleData));
        jsonFile.close();

        // SAVE MASTER (Clipboard for Applicator)
        var jsonMaster = new File(desktop + "/ONI_STYLE_DATA.json");
        jsonMaster.encoding = "UTF-8";
        jsonMaster.open("w");
        jsonMaster.write(JSON.stringify(styleData));
        jsonMaster.close();

    } catch (e) {
        alert("ERRO ao salvar arquivos:\n" + e.toString());
    }
}
try {
    if (!app.documents.length) {
        // Silent or Log. Alert blocks automation.
        // alert("ONI: No document open.");
    } else {
        var doc = app.activeDocument;

        // Reset Global Data
        styleData = {
            metadata: {
                version: "5.0-PhD",
                extracted_at: new Date().toString(),
                source_file: doc.name,
                layer_name: "Master"
            },
            effects: [],
            ai_instructions: []
        };

        if (scanLayers(doc.layers)) {
            // Success - scanLayers saves files
        }
    }
} catch (e) {
    alert("ONI EXTRACTOR FAULT:\n" + e.toString());
}