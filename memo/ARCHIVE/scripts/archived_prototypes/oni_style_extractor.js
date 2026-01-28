/**
 * ONI STYLE EXTRACTOR V4 - PHOTOSHOP ES3 COMPATIBLE
 * Extrai estilos e gera formato estruturado para IA aprender e replicar
 * CORRIGIDO: JSON Polyfill para ExtendScript
 */

// ============ JSON POLYFILL PARA EXTENDSCRIPT ============
if (typeof JSON !== 'object') {
    JSON = {};
}

(function () {
    'use strict';

    function f(n) {
        return n < 10 ? '0' + n : n;
    }

    if (typeof Date.prototype.toJSON !== 'function') {
        Date.prototype.toJSON = function () {
            return isFinite(this.valueOf())
                ? this.getUTCFullYear() + '-' +
                    f(this.getUTCMonth() + 1) + '-' +
                    f(this.getUTCDate()) + 'T' +
                    f(this.getUTCHours()) + ':' +
                    f(this.getUTCMinutes()) + ':' +
                    f(this.getUTCSeconds()) + 'Z'
                : null;
        };
    }

    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        meta = {
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"': '\\"',
            '\\': '\\\\'
        };

    function quote(string) {
        escapable.lastIndex = 0;
        return escapable.test(string) ? '"' + string.replace(escapable, function (a) {
            var c = meta[a];
            return typeof c === 'string'
                ? c
                : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
        }) + '"' : '"' + string + '"';
    }

    function str(key, holder) {
        var i, k, v, length, partial, value = holder[key];

        if (value && typeof value === 'object' && typeof value.toJSON === 'function') {
            value = value.toJSON(key);
        }

        switch (typeof value) {
            case 'string':
                return quote(value);
            case 'number':
                return isFinite(value) ? String(value) : 'null';
            case 'boolean':
            case 'null':
                return String(value);
            case 'object':
                if (!value) return 'null';
                partial = [];
                if (Object.prototype.toString.apply(value) === '[object Array]') {
                    length = value.length;
                    for (i = 0; i < length; i += 1) {
                        partial[i] = str(i, value) || 'null';
                    }
                    v = partial.length === 0
                        ? '[]'
                        : '[' + partial.join(',') + ']';
                    return v;
                }
                for (k in value) {
                    if (Object.prototype.hasOwnProperty.call(value, k)) {
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + ':' + v);
                        }
                    }
                }
                v = partial.length === 0
                    ? '{}'
                    : '{' + partial.join(',') + '}';
                return v;
        }
    }

    if (typeof JSON.stringify !== 'function') {
        JSON.stringify = function (value) {
            return str('', {'': value});
        };
    }
}());

// ============ FUNÇÕES DE CONVERSÃO ============
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }
function t2s(t) { 
    try {
        return app.typeIDToStringID(t);
    } catch(e) {
        return "unknown_" + t;
    }
}

// ============ OBJETO DE DADOS ============
var styleData = {
    metadata: {
        version: "4.0",
        extracted_at: new Date().toString(),
        source_file: "",
        layer_name: ""
    },
    effects: [],
    ai_instructions: []
};

// ============ UTILITÁRIOS MELHORADOS ============
function getUnitDouble(desc, key) {
    try {
        if (desc.hasKey(key)) {
            var val = desc.getUnitDoubleValue(key);
            var unit = desc.getUnitDoubleType(key);
            return { value: val, unit: t2s(unit) };
        }
    } catch(e) {}
    return null;
}

function getDouble(desc, key) {
    try {
        return desc.hasKey(key) ? desc.getDouble(key) : null;
    } catch(e) {
        return null;
    }
}

function getBoolean(desc, key) {
    try {
        return desc.hasKey(key) ? desc.getBoolean(key) : null;
    } catch(e) {
        return null;
    }
}

function getInteger(desc, key) {
    try {
        return desc.hasKey(key) ? desc.getInteger(key) : null;
    } catch(e) {
        return null;
    }
}

function getEnum(desc, key) {
    try {
        if (desc.hasKey(key)) {
            var enumType = desc.getEnumerationType(key);
            var enumValue = desc.getEnumerationValue(key);
            return {
                type: t2s(enumType),
                value: t2s(enumValue)
            };
        }
    } catch(e) {}
    return null;
}

function extractColor(desc, key) {
    try {
        if (!desc.hasKey(key)) return null;
        var c = desc.getObjectValue(key);
        var r = Math.round(c.getDouble(cTID('Rd  ')));
        var g = Math.round(c.getDouble(cTID('Grn ')));
        var b = Math.round(c.getDouble(cTID('Bl  ')));
        return {
            r: r,
            g: g,
            b: b,
            hex: rgbToHex(r, g, b)
        };
    } catch(e) {
        return null;
    }
}

function rgbToHex(r, g, b) {
    var hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    return hex;
}

// ============ EXTRATORES DE EFEITOS ============
function extractBevel(lefx) {
    try {
        if (!lefx.hasKey(cTID('ebbl'))) return null;
        var d = lefx.getObjectValue(cTID('ebbl'));
        if (!d.getBoolean(cTID('enab'))) return null;

        var bevel = {
            type: "bevel_emboss",
            enabled: true,
            style: getEnum(d, cTID('bvlS')),
            technique: getEnum(d, cTID('bvlT')),
            depth: getUnitDouble(d, cTID('Dpth')),
            direction: getEnum(d, cTID('bvlD')),
            size: getUnitDouble(d, cTID('Sz  ')),
            soften: getUnitDouble(d, cTID('Sftn')),
            angle: getUnitDouble(d, cTID('Angl')),
            altitude: getUnitDouble(d, cTID('Lald')),
            use_global_light: getBoolean(d, cTID('uglg')),
            highlight: {
                mode: getEnum(d, cTID('hglM')),
                color: extractColor(d, cTID('hglC')),
                opacity: getUnitDouble(d, cTID('hglO'))
            },
            shadow: {
                mode: getEnum(d, cTID('sdwM')),
                color: extractColor(d, cTID('sdwC')),
                opacity: getUnitDouble(d, cTID('sdwO'))
            }
        };

        styleData.ai_instructions.push({
            effect: "bevel_emboss",
            description: "Cria profundidade 3D com highlight e shadow",
            key_params: ["depth", "size", "technique", "angle"],
            visual_impact: "Alto - define o relevo principal"
        });

        return bevel;
    } catch(e) {
        return null;
    }
}

function extractGradientOverlay(lefx) {
    try {
        if (!lefx.hasKey(cTID('GrOv'))) return null;
        var d = lefx.getObjectValue(cTID('GrOv'));
        if (!d.getBoolean(cTID('enab'))) return null;

        var gradient = {
            type: "gradient_overlay",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            angle: getUnitDouble(d, cTID('Angl')),
            scale: getUnitDouble(d, cTID('Scl ')),
            reverse: getBoolean(d, cTID('Rvrs')),
            style: getEnum(d, cTID('Type')),
            align_with_layer: getBoolean(d, cTID('Algn')),
            gradient_data: null
        };

        if (d.hasKey(cTID('Grad'))) {
            var g = d.getObjectValue(cTID('Grad'));
            var gradData = {
                name: g.hasKey(cTID('Nm  ')) ? g.getString(cTID('Nm  ')) : "Custom",
                type: getEnum(g, cTID('GrdF')),
                smoothness: getDouble(g, cTID('Intr')),
                color_stops: [],
                opacity_stops: []
            };

            if (g.hasKey(cTID('Clrs'))) {
                var colors = g.getList(cTID('Clrs'));
                for (var i = 0; i < colors.count; i++) {
                    var stop = colors.getObjectValue(i);
                    gradData.color_stops.push({
                        location: stop.getInteger(cTID('Lctn')),
                        location_percent: (stop.getInteger(cTID('Lctn')) / 40.96).toFixed(2),
                        midpoint: stop.getInteger(cTID('Mdpn')),
                        color: extractColor(stop, cTID('Clr '))
                    });
                }
            }

            if (g.hasKey(cTID('Trns'))) {
                var trans = g.getList(cTID('Trns'));
                for (var i = 0; i < trans.count; i++) {
                    var stop = trans.getObjectValue(i);
                    gradData.opacity_stops.push({
                        location: stop.getInteger(cTID('Lctn')),
                        opacity: stop.getUnitDoubleValue(cTID('Opct'))
                    });
                }
            }

            gradient.gradient_data = gradData;
        }

        styleData.ai_instructions.push({
            effect: "gradient_overlay",
            description: "Aplica gradiente sobre a layer",
            key_params: ["colors", "angle", "scale", "blend_mode"],
            visual_impact: "Muito Alto - define a cor principal do efeito"
        });

        return gradient;
    } catch(e) {
        return null;
    }
}

function extractSatin(lefx) {
    try {
        if (!lefx.hasKey(cTID('ChFX'))) return null;
        var d = lefx.getObjectValue(cTID('ChFX'));
        if (!d.getBoolean(cTID('enab'))) return null;

        var satin = {
            type: "satin",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            angle: getUnitDouble(d, cTID('Angl')),
            distance: getUnitDouble(d, cTID('Dstn')),
            size: getUnitDouble(d, cTID('Sz  ')),
            invert: getBoolean(d, cTID('Invr'))
        };

        styleData.ai_instructions.push({
            effect: "satin",
            description: "Efeito de textura acetinada com ondulações",
            key_params: ["color", "distance", "size", "angle"],
            visual_impact: "Médio - adiciona textura interna"
        });

        return satin;
    } catch(e) {
        return null;
    }
}

function extractDropShadow(lefx) {
    try {
        if (!lefx.hasKey(cTID('DrSh'))) return null;
        var d = lefx.getObjectValue(cTID('DrSh'));
        if (!d.getBoolean(cTID('enab'))) return null;

        var shadow = {
            type: "drop_shadow",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            use_global_light: getBoolean(d, cTID('uglg')),
            angle: getUnitDouble(d, cTID('Angl')),
            distance: getUnitDouble(d, cTID('Dstn')),
            spread: getUnitDouble(d, cTID('Ckmt')),
            size: getUnitDouble(d, cTID('Sz  ')),
            noise: getUnitDouble(d, cTID('Nose')),
            layer_knocks_out: getBoolean(d, cTID('layerConceals'))
        };

        styleData.ai_instructions.push({
            effect: "drop_shadow",
            description: "Sombra projetada para criar profundidade",
            key_params: ["distance", "size", "angle", "opacity"],
            visual_impact: "Alto - define separação do fundo"
        });

        return shadow;
    } catch(e) {
        return null;
    }
}

function extractInnerShadow(lefx) {
    try {
        if (!lefx.hasKey(cTID('IrSh'))) return null;
        var d = lefx.getObjectValue(cTID('IrSh'));
        if (!d.getBoolean(cTID('enab'))) return null;

        return {
            type: "inner_shadow",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            angle: getUnitDouble(d, cTID('Angl')),
            distance: getUnitDouble(d, cTID('Dstn')),
            choke: getUnitDouble(d, cTID('Ckmt')),
            size: getUnitDouble(d, cTID('Sz  '))
        };
    } catch(e) {
        return null;
    }
}

function extractStroke(lefx) {
    try {
        if (!lefx.hasKey(cTID('FrFX'))) return null;
        var d = lefx.getObjectValue(cTID('FrFX'));
        if (!d.getBoolean(cTID('enab'))) return null;

        return {
            type: "stroke",
            enabled: true,
            size: getUnitDouble(d, cTID('Sz  ')),
            position: getEnum(d, cTID('Styl')),
            blend_mode: getEnum(d, cTID('Md  ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            fill_type: getEnum(d, cTID('PntT')),
            color: extractColor(d, cTID('Clr '))
        };
    } catch(e) {
        return null;
    }
}

function extractInnerGlow(lefx) {
    try {
        if (!lefx.hasKey(cTID('IrGl'))) return null;
        var d = lefx.getObjectValue(cTID('IrGl'));
        if (!d.getBoolean(cTID('enab'))) return null;

        return {
            type: "inner_glow",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            color: extractColor(d, cTID('Clr ')),
            technique: getEnum(d, cTID('GlwT')),
            source: getEnum(d, cTID('glwS')),
            choke: getUnitDouble(d, cTID('Ckmt')),
            size: getUnitDouble(d, cTID('Sz  '))
        };
    } catch(e) {
        return null;
    }
}

function extractOuterGlow(lefx) {
    try {
        if (!lefx.hasKey(cTID('OrGl'))) return null;
        var d = lefx.getObjectValue(cTID('OrGl'));
        if (!d.getBoolean(cTID('enab'))) return null;

        return {
            type: "outer_glow",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            opacity: getUnitDouble(d, cTID('Opct')),
            color: extractColor(d, cTID('Clr ')),
            technique: getEnum(d, cTID('GlwT')),
            spread: getUnitDouble(d, cTID('Ckmt')),
            size: getUnitDouble(d, cTID('Sz  ')),
            noise: getUnitDouble(d, cTID('Nose'))
        };
    } catch(e) {
        return null;
    }
}

function extractColorOverlay(lefx) {
    try {
        if (!lefx.hasKey(cTID('SoFi'))) return null;
        var d = lefx.getObjectValue(cTID('SoFi'));
        if (!d.getBoolean(cTID('enab'))) return null;

        return {
            type: "color_overlay",
            enabled: true,
            blend_mode: getEnum(d, cTID('Md  ')),
            color: extractColor(d, cTID('Clr ')),
            opacity: getUnitDouble(d, cTID('Opct'))
        };
    } catch(e) {
        return null;
    }
}

// ============ SCANNER DE LAYERS ============
function scanLayers(layers) {
    for (var i = 0; i < layers.length; i++) {
        var layer = layers[i];
        
        try {
            if (layer.typename == "LayerSet") {
                if (scanLayers(layer.layers)) return true;
            } else {
                app.activeDocument.activeLayer = layer;
                var ref = new ActionReference();
                ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
                var desc = executeActionGet(ref);

                if (desc.hasKey(cTID("Lefx"))) {
                    var lefx = desc.getObjectValue(cTID("Lefx"));
                    
                    styleData.metadata.layer_name = layer.name;
                    styleData.metadata.source_file = app.activeDocument.name;

                    var bevel = extractBevel(lefx);
                    if (bevel) styleData.effects.push(bevel);

                    var gradOverlay = extractGradientOverlay(lefx);
                    if (gradOverlay) styleData.effects.push(gradOverlay);

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

                    var colorOverlay = extractColorOverlay(lefx);
                    if (colorOverlay) styleData.effects.push(colorOverlay);

                    saveStyleData();
                    return true;
                }
            }
        } catch(e) {
            // Continue mesmo se houver erro em uma layer
        }
    }
    return false;
}

// ============ SALVAR DADOS ============
function saveStyleData() {
    var desktop = Folder.desktop;
    
    try {
        // JSON usando o polyfill
        var jsonFile = new File(desktop + "/ONI_STYLE_DATA.json");
        jsonFile.encoding = "UTF-8";
        jsonFile.open("w");
        jsonFile.write(JSON.stringify(styleData));
        jsonFile.close();

        // TXT legível
        var txtFile = new File(desktop + "/ONI_STYLE_GUIDE.txt");
        txtFile.encoding = "UTF-8";
        txtFile.open("w");
        txtFile.writeln("=".repeat(60));
        txtFile.writeln("  ONI STYLE EXTRACTION - AI TRAINING FORMAT");
        txtFile.writeln("=".repeat(60));
        txtFile.writeln("");
        txtFile.writeln("SOURCE: " + styleData.metadata.source_file);
        txtFile.writeln("LAYER: " + styleData.metadata.layer_name);
        txtFile.writeln("EXTRACTED: " + styleData.metadata.extracted_at);
        txtFile.writeln("");
        txtFile.writeln("TOTAL EFFECTS: " + styleData.effects.length);
        txtFile.writeln("");

        for (var i = 0; i < styleData.effects.length; i++) {
            var effect = styleData.effects[i];
            txtFile.writeln("-".repeat(60));
            txtFile.writeln("EFFECT " + (i+1) + ": " + effect.type.toUpperCase());
            txtFile.writeln("-".repeat(60));
            txtFile.writeln("");
        }

        txtFile.close();

        alert("SUCCESS!\n\n" +
              "Estilo extraído da layer: '" + styleData.metadata.layer_name + "'\n\n" +
              "Arquivos salvos no Desktop:\n" +
              "• ONI_STYLE_DATA.json\n" +
              "• ONI_STYLE_GUIDE.txt\n\n" +
              "Total de efeitos: " + styleData.effects.length);
              
    } catch(e) {
        alert("ERRO ao salvar arquivos:\n" + e.toString());
    }
}

// ============ EXECUÇÃO PRINCIPAL ============
try {
    if (!app.documents.length) {
        alert("ERRO: Nenhum documento aberto!");
    } else {
        var doc = app.activeDocument;
        
        if (!scanLayers(doc.layers)) {
            alert("FALHA: Nenhum Layer Style encontrado no documento:\n'" + doc.name + "'");
        }
    }
} catch (e) {
    alert("ERRO CRÍTICO:\n\n" + e.toString() + "\n\nLinha: " + (e.line || "desconhecida"));
}