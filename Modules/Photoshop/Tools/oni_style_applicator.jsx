/**
 * ONI STYLE APPLICATOR V2 - PHOTOSHOP ES3 COMPATIBLE
 * Aplica estilos extraídos pelo ONI Style Extractor
 * CORRIGIDO: JSON.parse polyfill para ExtendScript
 */

// ============ JSON POLYFILL PARA EXTENDSCRIPT ============
if (typeof JSON !== 'object') {
    JSON = {};
}

(function () {
    'use strict';

    var rx_one = /^[\],:{}\s]*$/;
    var rx_two = /\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g;
    var rx_three = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g;
    var rx_four = /(?:^|:|,)(?:\s*\[)+/g;

    if (typeof JSON.parse !== 'function') {
        JSON.parse = function (text) {
            text = String(text);
            
            if (
                rx_one.test(
                    text
                        .replace(rx_two, '@')
                        .replace(rx_three, ']')
                        .replace(rx_four, '')
                )
            ) {
                return eval('(' + text + ')');
            }
            
            throw new SyntaxError('JSON.parse');
        };
    }
}());

// ============ FUNÇÕES DE CONVERSÃO ============
function cTID(s) { return app.charIDToTypeID(s); }
function sTID(s) { return app.stringIDToTypeID(s); }

// ============ CARREGAR JSON ============
function loadStyleData() {
    var jsonFile = new File(Folder.desktop + "/ONI_STYLE_DATA.json");
    if (!jsonFile.exists) {
        alert("ERRO: Arquivo ONI_STYLE_DATA.json não encontrado no Desktop!\n\n" +
              "Execute primeiro o ONI Style Extractor no arquivo fonte.");
        return null;
    }
    
    try {
        jsonFile.encoding = "UTF-8";
        jsonFile.open("r");
        var content = jsonFile.read();
        jsonFile.close();
        
        return JSON.parse(content);
    } catch(e) {
        alert("ERRO ao ler JSON:\n" + e.toString());
        return null;
    }
}

// ============ APLICADORES DE EFEITOS ============
function applyBevel(effect) {
    var desc = new ActionDescriptor();
    desc.putBoolean(cTID('enab'), true);
    
    try {
        if (effect.style && effect.style.value) 
            desc.putEnumerated(cTID('bvlS'), cTID('BESl'), sTID(effect.style.value));
        if (effect.technique && effect.technique.value) 
            desc.putEnumerated(cTID('bvlT'), cTID('bvlT'), sTID(effect.technique.value));
        if (effect.depth && effect.depth.value !== null) 
            desc.putUnitDouble(cTID('Dpth'), cTID('#Prc'), effect.depth.value);
        if (effect.direction && effect.direction.value) 
            desc.putEnumerated(cTID('bvlD'), cTID('BESs'), sTID(effect.direction.value));
        if (effect.size && effect.size.value !== null) 
            desc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), effect.size.value);
        if (effect.soften && effect.soften.value !== null) 
            desc.putUnitDouble(cTID('Sftn'), cTID('#Pxl'), effect.soften.value);
        if (effect.angle && effect.angle.value !== null) 
            desc.putUnitDouble(cTID('Angl'), cTID('#Ang'), effect.angle.value);
        if (effect.altitude && effect.altitude.value !== null) 
            desc.putUnitDouble(cTID('Lald'), cTID('#Ang'), effect.altitude.value);
        if (effect.use_global_light !== null) 
            desc.putBoolean(cTID('uglg'), effect.use_global_light);
        
        // Highlight
        if (effect.highlight) {
            if (effect.highlight.mode && effect.highlight.mode.value) 
                desc.putEnumerated(cTID('hglM'), cTID('BlnM'), sTID(effect.highlight.mode.value));
            if (effect.highlight.color) {
                var hc = new ActionDescriptor();
                hc.putDouble(cTID('Rd  '), effect.highlight.color.r);
                hc.putDouble(cTID('Grn '), effect.highlight.color.g);
                hc.putDouble(cTID('Bl  '), effect.highlight.color.b);
                desc.putObject(cTID('hglC'), cTID('RGBC'), hc);
            }
            if (effect.highlight.opacity && effect.highlight.opacity.value !== null) 
                desc.putUnitDouble(cTID('hglO'), cTID('#Prc'), effect.highlight.opacity.value);
        }
        
        // Shadow
        if (effect.shadow) {
            if (effect.shadow.mode && effect.shadow.mode.value) 
                desc.putEnumerated(cTID('sdwM'), cTID('BlnM'), sTID(effect.shadow.mode.value));
            if (effect.shadow.color) {
                var sc = new ActionDescriptor();
                sc.putDouble(cTID('Rd  '), effect.shadow.color.r);
                sc.putDouble(cTID('Grn '), effect.shadow.color.g);
                sc.putDouble(cTID('Bl  '), effect.shadow.color.b);
                desc.putObject(cTID('sdwC'), cTID('RGBC'), sc);
            }
            if (effect.shadow.opacity && effect.shadow.opacity.value !== null) 
                desc.putUnitDouble(cTID('sdwO'), cTID('#Prc'), effect.shadow.opacity.value);
        }
    } catch(e) {}
    
    return desc;
}

function applyGradientOverlay(effect) {
    var desc = new ActionDescriptor();
    desc.putBoolean(cTID('enab'), true);
    
    try {
        if (effect.blend_mode && effect.blend_mode.value) 
            desc.putEnumerated(cTID('Md  '), cTID('BlnM'), sTID(effect.blend_mode.value));
        if (effect.opacity && effect.opacity.value !== null) 
            desc.putUnitDouble(cTID('Opct'), cTID('#Prc'), effect.opacity.value);
        if (effect.angle && effect.angle.value !== null) 
            desc.putUnitDouble(cTID('Angl'), cTID('#Ang'), effect.angle.value);
        if (effect.scale && effect.scale.value !== null) 
            desc.putUnitDouble(cTID('Scl '), cTID('#Prc'), effect.scale.value);
        if (effect.reverse !== null) 
            desc.putBoolean(cTID('Rvrs'), effect.reverse);
        if (effect.align_with_layer !== null) 
            desc.putBoolean(cTID('Algn'), effect.align_with_layer);
        if (effect.style && effect.style.value) 
            desc.putEnumerated(cTID('Type'), cTID('GrdT'), sTID(effect.style.value));
        
        // Gradient Data
        if (effect.gradient_data) {
            var gradDesc = new ActionDescriptor();
            var gd = effect.gradient_data;
            
            if (gd.name) gradDesc.putString(cTID('Nm  '), gd.name);
            if (gd.type && gd.type.value) 
                gradDesc.putEnumerated(cTID('GrdF'), cTID('GrdF'), sTID(gd.type.value));
            if (gd.smoothness !== null) 
                gradDesc.putDouble(cTID('Intr'), gd.smoothness);
            
            // Color Stops
            if (gd.color_stops && gd.color_stops.length > 0) {
                var colorList = new ActionList();
                for (var i = 0; i < gd.color_stops.length; i++) {
                    var stop = gd.color_stops[i];
                    var stopDesc = new ActionDescriptor();
                    
                    if (stop.color) {
                        var colorDesc = new ActionDescriptor();
                        colorDesc.putDouble(cTID('Rd  '), stop.color.r);
                        colorDesc.putDouble(cTID('Grn '), stop.color.g);
                        colorDesc.putDouble(cTID('Bl  '), stop.color.b);
                        stopDesc.putObject(cTID('Clr '), cTID('RGBC'), colorDesc);
                    }
                    
                    stopDesc.putEnumerated(cTID('Type'), cTID('Clry'), cTID('UsrS'));
                    stopDesc.putInteger(cTID('Lctn'), stop.location);
                    stopDesc.putInteger(cTID('Mdpn'), stop.midpoint || 50);
                    
                    colorList.putObject(cTID('Clrt'), stopDesc);
                }
                gradDesc.putList(cTID('Clrs'), colorList);
            }
            
            // Transparency Stops
            if (gd.opacity_stops && gd.opacity_stops.length > 0) {
                var transList = new ActionList();
                for (var i = 0; i < gd.opacity_stops.length; i++) {
                    var stop = gd.opacity_stops[i];
                    var stopDesc = new ActionDescriptor();
                    stopDesc.putUnitDouble(cTID('Opct'), cTID('#Prc'), stop.opacity);
                    stopDesc.putInteger(cTID('Lctn'), stop.location);
                    stopDesc.putInteger(cTID('Mdpn'), 50);
                    transList.putObject(cTID('TrnS'), stopDesc);
                }
                gradDesc.putList(cTID('Trns'), transList);
            }
            
            desc.putObject(cTID('Grad'), cTID('Grdn'), gradDesc);
        }
    } catch(e) {}
    
    return desc;
}

function applySatin(effect) {
    var desc = new ActionDescriptor();
    desc.putBoolean(cTID('enab'), true);
    
    try {
        if (effect.blend_mode && effect.blend_mode.value) 
            desc.putEnumerated(cTID('Md  '), cTID('BlnM'), sTID(effect.blend_mode.value));
        if (effect.opacity && effect.opacity.value !== null) 
            desc.putUnitDouble(cTID('Opct'), cTID('#Prc'), effect.opacity.value);
        if (effect.angle && effect.angle.value !== null) 
            desc.putUnitDouble(cTID('Angl'), cTID('#Ang'), effect.angle.value);
        if (effect.distance && effect.distance.value !== null) 
            desc.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), effect.distance.value);
        if (effect.size && effect.size.value !== null) 
            desc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), effect.size.value);
        if (effect.invert !== null) 
            desc.putBoolean(cTID('Invr'), effect.invert);
        
        if (effect.color) {
            var colorDesc = new ActionDescriptor();
            colorDesc.putDouble(cTID('Rd  '), effect.color.r);
            colorDesc.putDouble(cTID('Grn '), effect.color.g);
            colorDesc.putDouble(cTID('Bl  '), effect.color.b);
            desc.putObject(cTID('Clr '), cTID('RGBC'), colorDesc);
        }
    } catch(e) {}
    
    return desc;
}

function applyDropShadow(effect) {
    var desc = new ActionDescriptor();
    desc.putBoolean(cTID('enab'), true);
    
    try {
        if (effect.blend_mode && effect.blend_mode.value) 
            desc.putEnumerated(cTID('Md  '), cTID('BlnM'), sTID(effect.blend_mode.value));
        if (effect.opacity && effect.opacity.value !== null) 
            desc.putUnitDouble(cTID('Opct'), cTID('#Prc'), effect.opacity.value);
        if (effect.use_global_light !== null) 
            desc.putBoolean(cTID('uglg'), effect.use_global_light);
        if (effect.angle && effect.angle.value !== null) 
            desc.putUnitDouble(cTID('Angl'), cTID('#Ang'), effect.angle.value);
        if (effect.distance && effect.distance.value !== null) 
            desc.putUnitDouble(cTID('Dstn'), cTID('#Pxl'), effect.distance.value);
        if (effect.spread && effect.spread.value !== null) 
            desc.putUnitDouble(cTID('Ckmt'), cTID('#Prc'), effect.spread.value);
        if (effect.size && effect.size.value !== null) 
            desc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), effect.size.value);
        if (effect.noise && effect.noise.value !== null) 
            desc.putUnitDouble(cTID('Nose'), cTID('#Prc'), effect.noise.value);
        
        if (effect.color) {
            var colorDesc = new ActionDescriptor();
            colorDesc.putDouble(cTID('Rd  '), effect.color.r);
            colorDesc.putDouble(cTID('Grn '), effect.color.g);
            colorDesc.putDouble(cTID('Bl  '), effect.color.b);
            desc.putObject(cTID('Clr '), cTID('RGBC'), colorDesc);
        }
    } catch(e) {}
    
    return desc;
}

function applyStroke(effect) {
    var desc = new ActionDescriptor();
    desc.putBoolean(cTID('enab'), true);
    
    try {
        if (effect.size && effect.size.value !== null) 
            desc.putUnitDouble(cTID('Sz  '), cTID('#Pxl'), effect.size.value);
        if (effect.position && effect.position.value) 
            desc.putEnumerated(cTID('Styl'), cTID('FStl'), sTID(effect.position.value));
        if (effect.blend_mode && effect.blend_mode.value) 
            desc.putEnumerated(cTID('Md  '), cTID('BlnM'), sTID(effect.blend_mode.value));
        if (effect.opacity && effect.opacity.value !== null) 
            desc.putUnitDouble(cTID('Opct'), cTID('#Prc'), effect.opacity.value);
        if (effect.fill_type && effect.fill_type.value) 
            desc.putEnumerated(cTID('PntT'), cTID('FrFl'), sTID(effect.fill_type.value));
        
        if (effect.color) {
            var colorDesc = new ActionDescriptor();
            colorDesc.putDouble(cTID('Rd  '), effect.color.r);
            colorDesc.putDouble(cTID('Grn '), effect.color.g);
            colorDesc.putDouble(cTID('Bl  '), effect.color.b);
            desc.putObject(cTID('Clr '), cTID('RGBC'), colorDesc);
        }
    } catch(e) {}
    
    return desc;
}

// ============ APLICAR ESTILO COMPLETO ============
function applyCompleteStyle(styleData) {
    try {
        if (!app.documents.length) {
            alert("ERRO: Nenhum documento aberto!");
            return;
        }
        
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        
        if (layer.kind != LayerKind.NORMAL && layer.kind != LayerKind.TEXT) {
            alert("ERRO: Selecione uma layer normal ou de texto.\n\nTipo atual: " + layer.kind);
            return;
        }
        
        var styleDesc = new ActionDescriptor();
        var appliedCount = 0;
        
        for (var i = 0; i < styleData.effects.length; i++) {
            var effect = styleData.effects[i];
            
            try {
                switch (effect.type) {
                    case "bevel_emboss":
                        styleDesc.putObject(cTID('ebbl'), cTID('ebbl'), applyBevel(effect));
                        appliedCount++;
                        break;
                    case "gradient_overlay":
                        styleDesc.putObject(cTID('GrOv'), cTID('GrOv'), applyGradientOverlay(effect));
                        appliedCount++;
                        break;
                    case "satin":
                        styleDesc.putObject(cTID('ChFX'), cTID('ChFX'), applySatin(effect));
                        appliedCount++;
                        break;
                    case "drop_shadow":
                        styleDesc.putObject(cTID('DrSh'), cTID('DrSh'), applyDropShadow(effect));
                        appliedCount++;
                        break;
                    case "stroke":
                        styleDesc.putObject(cTID('FrFX'), cTID('FrFX'), applyStroke(effect));
                        appliedCount++;
                        break;
                }
            } catch (e) {
                // Continue mesmo se um efeito falhar
            }
        }
        
        // Aplicar todos os efeitos de uma vez
        var applyDesc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putEnumerated(cTID('Lyr '), cTID('Ordn'), cTID('Trgt'));
        applyDesc.putReference(cTID('null'), ref);
        applyDesc.putObject(cTID('T   '), cTID('Lefx'), styleDesc);
        executeAction(cTID('setd'), applyDesc, DialogModes.NO);
        
        alert("SUCCESS!\n\n" +
              "Estilo aplicado com sucesso!\n\n" +
              "Layer: " + layer.name + "\n" +
              "Efeitos aplicados: " + appliedCount + "/" + styleData.effects.length + "\n\n" +
              "Fonte original: " + styleData.metadata.source_file);
        
    } catch (e) {
        alert("ERRO ao aplicar estilo:\n\n" + e.toString() + "\n\nLinha: " + (e.line || "desconhecida"));
    }
}

// ============ EXECUÇÃO PRINCIPAL ============
try {
    var styleData = loadStyleData();
    
    if (styleData) {
        applyCompleteStyle(styleData);
    }
    
} catch (e) {
    alert("ERRO CRÍTICO:\n\n" + e.toString() + "\n\nLinha: " + (e.line || "desconhecida"));
}