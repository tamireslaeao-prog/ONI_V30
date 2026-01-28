/*
 * ONI CORE LIBRARY - PHOTOSHOP AUTOMATION
 * Version: 1.0.0
 * Date: 2026-01-14
 * 
 * Standardized High-Quality Functions for Image Processing & Design Automation.
 * Usage: Load via DoJavaScript from PowerShell or execute directly in Photoshop
 * 
 * Architecture follows oni_lib_aftereffects.jsx pattern for consistency
 */

#target photoshop

// ============ JSON POLYFILL (CRITICAL FOR automation) ============
if (typeof JSON !== 'object') { JSON = {}; }
(function () {
    'use strict';
    function f(n) { return n < 10 ? '0' + n : n; }
    if (typeof Date.prototype.toJSON !== 'function') {
        Date.prototype.toJSON = function () { return isFinite(this.valueOf()) ? this.getUTCFullYear() + '-' + f(this.getUTCMonth() + 1) + '-' + f(this.getUTCDate()) + 'T' + f(this.getUTCHours()) + ':' + f(this.getUTCMinutes()) + ':' + f(this.getUTCSeconds()) + 'Z' : null; };
    }
    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        meta = { '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r', '"': '\\"', '\\': '\\\\' };
    function quote(string) { escapable.lastIndex = 0; return escapable.test(string) ? '"' + string.replace(escapable, function (a) { var c = meta[a]; return typeof c === 'string' ? c : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4); }) + '"' : '"' + string + '"'; }
    function str(key, holder) {
        var i, k, v, length, partial, value = holder[key];
        if (value && typeof value === 'object' && typeof value.toJSON === 'function') { value = value.toJSON(key); }
        switch (typeof value) {
            case 'string': return quote(value);
            case 'number': return isFinite(value) ? String(value) : 'null';
            case 'boolean': case 'null': return String(value);
            case 'object': if (!value) return 'null'; partial = []; if (Object.prototype.toString.apply(value) === '[object Array]') { length = value.length; for (i = 0; i < length; i += 1) { partial[i] = str(i, value) || 'null'; } v = partial.length === 0 ? '[]' : '[' + partial.join(',') + ']'; return v; } for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = str(k, value); if (v) { partial.push(quote(k) + ':' + v); } } } v = partial.length === 0 ? '{}' : '{' + partial.join(',') + '}'; return v;
        }
    }
    if (typeof JSON.stringify !== 'function') { JSON.stringify = function (value) { return str('', { '': value }); }; }
    if (typeof JSON.parse !== 'function') {
        JSON.parse = function (text) { return eval('(' + text + ')'); }; // Simple unsafe parse for ExtendScript environment (usually safe local inputs)
    }
}());

var ONI_PS = ONI_PS || {};

// Library metadata
ONI_PS.VERSION = "1.0.0";
ONI_PS.LAST_UPDATED = "2026-01-14";
ONI_PS.AUTHOR = "ONI Team";

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI_PS.Core = {

    // Initialize - set preferences for automation
    Init: function () {
        // Set ruler units to pixels (required for precise automation)
        app.preferences.rulerUnits = Units.PIXELS;
        app.preferences.typeUnits = TypeUnits.PIXELS;

        // Disable dialogs for batch operations
        app.displayDialogs = DialogModes.NO;

        return true;
    },

    // Health check - verify Photoshop is ready
    Verify: function () {
        try {
            var version = app.version;
            var docs = app.documents.length;
            return {
                success: true,
                version: version,
                documentsOpen: docs,
                message: "Photoshop ready"
            };
        } catch (e) {
            return {
                success: false,
                error: e.message
            };
        }
    },

    // Color helper - RGB to SolidColor
    Color: function (r, g, b) {
        var color = new SolidColor();
        color.rgb.red = r;
        color.rgb.green = g;
        color.rgb.blue = b;
        return color;
    },

    // Hex to SolidColor
    HexColor: function (hex) {
        hex = hex.replace("#", "");
        var r = parseInt(hex.substring(0, 2), 16);
        var g = parseInt(hex.substring(2, 4), 16);
        var b = parseInt(hex.substring(4, 6), 16);
        return ONI_PS.Core.Color(r, g, b);
    },

    // RGB to Hex
    RGBToHex: function (r, g, b) {
        return "#" +
            ("0" + Math.round(r).toString(16)).slice(-2) +
            ("0" + Math.round(g).toString(16)).slice(-2) +
            ("0" + Math.round(b).toString(16)).slice(-2);
    },

    // Log helper (writes to ExtendScript console)
    Log: function (msg) {
        $.writeln("[ONI_PS] " + msg);
    },

    // Error handler
    HandleError: function (e, context) {
        var errorMsg = "[ONI_PS ERROR] " + context + ": " + e.message;
        $.writeln(errorMsg);
        return errorMsg;
    }
};

// ============================================================================
// MODULE: DOCUMENT (CANVAS) MANAGEMENT
// ============================================================================
ONI_PS.Canvas = {

    // Create new document
    Create: function (width, height, name, resolution, colorMode) {
        resolution = resolution || 72;
        colorMode = colorMode || NewDocumentMode.RGB;
        name = name || "ONI_Document";

        try {
            var doc = app.documents.add(
                UnitValue(width, "px"),
                UnitValue(height, "px"),
                resolution,
                name,
                colorMode
            );
            ONI_PS.Core.Log("Created document: " + name + " (" + width + "x" + height + ")");
            return doc;
        } catch (e) {
            return ONI_PS.Core.HandleError(e, "Canvas.Create");
        }
    },

    // Get active document info
    GetInfo: function () {
        if (app.documents.length === 0) {
            return { error: "No document open" };
        }

        var doc = app.activeDocument;
        return {
            name: doc.name,
            width: doc.width.as("px"),
            height: doc.height.as("px"),
            resolution: doc.resolution,
            colorMode: doc.mode.toString(),
            layers: doc.layers.length,
            saved: doc.saved,
            path: doc.path ? doc.path.fsName : null
        };
    },

    // Resize canvas
    Resize: function (width, height, anchor) {
        anchor = anchor || AnchorPosition.MIDDLECENTER;
        var doc = app.activeDocument;
        doc.resizeCanvas(
            UnitValue(width, "px"),
            UnitValue(height, "px"),
            anchor
        );
        ONI_PS.Core.Log("Canvas resized to: " + width + "x" + height);
        return true;
    },

    // Resize image (with resampling)
    ResizeImage: function (width, height, resample) {
        resample = resample || ResampleMethod.BICUBIC;
        var doc = app.activeDocument;
        doc.resizeImage(
            UnitValue(width, "px"),
            UnitValue(height, "px"),
            doc.resolution,
            resample
        );
        ONI_PS.Core.Log("Image resized to: " + width + "x" + height);
        return true;
    },

    // Fill background with color
    FillBackground: function (color) {
        var doc = app.activeDocument;
        doc.selection.selectAll();
        doc.selection.fill(color);
        doc.selection.deselect();
        return true;
    }
};

// ============================================================================
// MODULE: LAYER MANAGEMENT
// ============================================================================
ONI_PS.Layers = {

    // Create new layer
    Create: function (name, opacity) {
        opacity = opacity || 100;
        var doc = app.activeDocument;
        var layer = doc.artLayers.add();
        layer.name = name;
        layer.opacity = opacity;
        ONI_PS.Core.Log("Created layer: " + name);
        return layer;
    },

    // Create text layer
    CreateText: function (name, text, x, y, fontSize, color) {
        var doc = app.activeDocument;
        var textLayer = doc.artLayers.add();
        textLayer.kind = LayerKind.TEXT;
        textLayer.name = name;

        var textItem = textLayer.textItem;
        textItem.contents = text;
        textItem.position = [UnitValue(x, "px"), UnitValue(y, "px")];
        textItem.size = UnitValue(fontSize, "px");

        if (color) {
            textItem.color = color;
        }

        ONI_PS.Core.Log("Created text layer: " + name);
        return textLayer;
    },

    // Duplicate layer
    Duplicate: function (layer, newName) {
        var dup = layer.duplicate();
        if (newName) {
            dup.name = newName;
        }
        return dup;
    },

    // Get layer by name
    GetByName: function (name) {
        var doc = app.activeDocument;
        try {
            return doc.artLayers.getByName(name);
        } catch (e) {
            // Try layer sets (groups)
            try {
                return doc.layerSets.getByName(name);
            } catch (e2) {
                return null;
            }
        }
    },

    // Move layer (translate)
    Move: function (layer, deltaX, deltaY) {
        layer.translate(UnitValue(deltaX, "px"), UnitValue(deltaY, "px"));
        return true;
    },

    // Rasterize layer
    Rasterize: function (layer, rasterizeType) {
        rasterizeType = rasterizeType || RasterizeType.ENTIRELAYER;
        layer.rasterize(rasterizeType);
        return true;
    },

    // Merge visible layers
    MergeVisible: function () {
        var doc = app.activeDocument;
        return doc.mergeVisibleLayers();
    },

    // Flatten image
    Flatten: function () {
        var doc = app.activeDocument;
        doc.flatten();
        return true;
    },

    // Create layer group
    CreateGroup: function (name) {
        var doc = app.activeDocument;
        var group = doc.layerSets.add();
        group.name = name;
        return group;
    },

    // Lock/unlock layer
    Lock: function (layer, locked) {
        layer.allLocked = locked;
        return true;
    }
};

// ============================================================================
// MODULE: EFFECTS & FILTERS
// ============================================================================
ONI_PS.Effects = {

    // Apply Gaussian Blur
    GaussianBlur: function (radius) {
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        layer.applyGaussianBlur(radius);
        ONI_PS.Core.Log("Applied Gaussian Blur: " + radius + "px");
        return true;
    },

    // Apply Add Noise
    AddNoise: function (amount, distribution, monochrome) {
        distribution = distribution || NoiseDistribution.GAUSSIAN;
        monochrome = monochrome || false;
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        layer.applyAddNoise(amount, distribution, monochrome);
        return true;
    },

    // Apply Unsharp Mask
    UnsharpMask: function (amount, radius, threshold) {
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        layer.applyUnSharpMask(amount, radius, threshold);
        return true;
    },

    // Apply Motion Blur
    MotionBlur: function (angle, distance) {
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        layer.applyMotionBlur(angle, distance);
        return true;
    },

    // Set layer blend mode
    SetBlendMode: function (layer, mode) {
        // mode should be BlendMode constant
        layer.blendMode = mode;
        return true;
    },

    // Set layer opacity
    SetOpacity: function (layer, opacity) {
        layer.opacity = opacity;
        return true;
    },

    // Manual Shadow Effect (no layer styles needed)
    CreateShadow: function (sourceLayer, offsetX, offsetY, blurRadius, color, opacity) {
        color = color || ONI_PS.Core.Color(0, 0, 0);
        opacity = opacity || 50;

        var doc = app.activeDocument;

        // Duplicate source
        var shadow = sourceLayer.duplicate();
        shadow.name = sourceLayer.name + "_Shadow";

        // Move below source
        shadow.move(sourceLayer, ElementPlacement.PLACEAFTER);

        // Fill with shadow color
        doc.activeLayer = shadow;
        doc.selection.selectAll();
        doc.selection.fill(color);
        doc.selection.deselect();

        // Apply blur
        shadow.applyGaussianBlur(blurRadius);

        // Set blend mode and opacity
        shadow.blendMode = BlendMode.MULTIPLY;
        shadow.opacity = opacity;

        // Offset
        shadow.translate(UnitValue(offsetX, "px"), UnitValue(offsetY, "px"));

        ONI_PS.Core.Log("Created shadow for: " + sourceLayer.name);
        return shadow;
    },

    // Vignette Effect
    CreateVignette: function (feather, opacity) {
        feather = feather || 100;
        opacity = opacity || 50;

        var doc = app.activeDocument;
        var vignetteLayer = doc.artLayers.add();
        vignetteLayer.name = "Vignette";

        // Create ellipse selection
        var selBounds = [
            [doc.width * 0.1, doc.height * 0.1],
            [doc.width * 0.9, doc.height * 0.1],
            [doc.width * 0.9, doc.height * 0.9],
            [doc.width * 0.1, doc.height * 0.9]
        ];
        doc.selection.select(selBounds, SelectionType.REPLACE, feather, true);

        // Invert and fill
        doc.selection.invert();
        doc.selection.fill(ONI_PS.Core.Color(0, 0, 0));
        doc.selection.deselect();

        // Set blend mode
        vignetteLayer.blendMode = BlendMode.MULTIPLY;
        vignetteLayer.opacity = opacity;

        return vignetteLayer;
    }
};

// ============================================================================
// MODULE: STYLE SYSTEM
// ============================================================================
ONI_PS.Styles = {

    // Extract all layer effects as JSON
    ExtractEffects: function (layer) {
        // This requires Action Manager for full extraction
        // Basic implementation returns layer properties
        return {
            name: layer.name,
            opacity: layer.opacity,
            blendMode: layer.blendMode.toString(),
            visible: layer.visible,
            bounds: layer.bounds
        };
    },

    // Apply style from JSON object
    ApplyStyle: function (layer, styleObj) {
        try {
            if (styleObj.opacity !== undefined) {
                layer.opacity = styleObj.opacity;
            }
            if (styleObj.blendMode !== undefined) {
                // Note: blendMode needs proper constant mapping
                layer.blendMode = eval(styleObj.blendMode);
            }
            if (styleObj.visible !== undefined) {
                layer.visible = styleObj.visible;
            }
            return true;
        } catch (e) {
            return ONI_PS.Core.HandleError(e, "Styles.ApplyStyle");
        }
    },

    // Copy layer style (uses Action Manager)
    CopyStyle: function (fromLayer) {
        app.activeDocument.activeLayer = fromLayer;

        var idCpFX = stringIDToTypeID("copyEffects");
        executeAction(idCpFX, undefined, DialogModes.NO);
        return true;
    },

    // Paste layer style (uses Action Manager)
    PasteStyle: function (toLayer) {
        app.activeDocument.activeLayer = toLayer;

        var idPaFX = stringIDToTypeID("pasteEffects");
        executeAction(idPaFX, undefined, DialogModes.NO);
        return true;
    }
};

// ============================================================================
// MODULE: EXPORT
// ============================================================================
ONI_PS.Export = {

    // Save as PSD
    SavePSD: function (path, maximize) {
        maximize = maximize || true;
        var doc = app.activeDocument;
        var opts = new PhotoshopSaveOptions();
        opts.layers = true;
        opts.embedColorProfile = true;
        opts.maximizeCompatibility = maximize;

        var file = new File(path);
        doc.saveAs(file, opts, true, Extension.LOWERCASE);
        ONI_PS.Core.Log("Saved PSD: " + path);
        return true;
    },

    // Save as PNG
    SavePNG: function (path, interlaced) {
        interlaced = interlaced || false;
        var doc = app.activeDocument;
        var opts = new PNGSaveOptions();
        opts.interlaced = interlaced;
        opts.compression = 6;

        var file = new File(path);
        doc.saveAs(file, opts, true, Extension.LOWERCASE);
        ONI_PS.Core.Log("Saved PNG: " + path);
        return true;
    },

    // Save as JPEG
    SaveJPEG: function (path, quality) {
        quality = quality || 10; // 0-12
        var doc = app.activeDocument;
        var opts = new JPEGSaveOptions();
        opts.quality = quality;
        opts.embedColorProfile = true;

        var file = new File(path);
        doc.saveAs(file, opts, true, Extension.LOWERCASE);
        ONI_PS.Core.Log("Saved JPEG: " + path);
        return true;
    },

    // Export for Web (PNG-24)
    ExportForWeb: function (path, format) {
        format = format || "PNG-24";
        var doc = app.activeDocument;

        var opts = new ExportOptionsSaveForWeb();
        if (format === "PNG-24") {
            opts.format = SaveDocumentType.PNG;
            opts.PNG8 = false;
        } else if (format === "PNG-8") {
            opts.format = SaveDocumentType.PNG;
            opts.PNG8 = true;
        } else if (format === "JPEG") {
            opts.format = SaveDocumentType.JPEG;
            opts.quality = 80;
        }

        var file = new File(path);
        doc.exportDocument(file, ExportType.SAVEFORWEB, opts);
        ONI_PS.Core.Log("Exported for web: " + path);
        return true;
    },

    // Quick save (auto-detect format)
    QuickSave: function () {
        var doc = app.activeDocument;
        if (doc.saved && doc.path) {
            doc.save();
            return doc.fullName.fsName;
        }
        return null;
    }
};

// ============================================================================
// MODULE: SELECTION
// ============================================================================
ONI_PS.Selection = {

    // Select all
    SelectAll: function () {
        app.activeDocument.selection.selectAll();
        return true;
    },

    // Deselect
    Deselect: function () {
        app.activeDocument.selection.deselect();
        return true;
    },

    // Select rectangular region
    SelectRect: function (x, y, width, height) {
        var doc = app.activeDocument;
        var region = [[x, y], [x + width, y], [x + width, y + height], [x, y + height]];
        doc.selection.select(region);
        return true;
    },

    // Invert selection
    Invert: function () {
        app.activeDocument.selection.invert();
        return true;
    },

    // Feather selection
    Feather: function (radius) {
        app.activeDocument.selection.feather(radius);
        return true;
    },

    // Fill selection
    Fill: function (color) {
        app.activeDocument.selection.fill(color);
        return true;
    }
};

// ============================================================================
// MODULE: BATCH / UTILITIES
// ============================================================================
ONI_PS.Utils = {

    // Open file
    OpenFile: function (path) {
        var file = new File(path);
        if (file.exists) {
            var doc = app.open(file);
            return doc;
        }
        return null;
    },

    // Close active document
    Close: function (save) {
        save = save || false;
        var doc = app.activeDocument;
        if (save) {
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }
        return true;
    },

    // Close all documents
    CloseAll: function (save) {
        save = save || false;
        while (app.documents.length > 0) {
            if (save) {
                app.activeDocument.close(SaveOptions.SAVECHANGES);
            } else {
                app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
            }
        }
        return true;
    },

    // Suspend history for performance
    SuspendHistory: function (name, code) {
        app.activeDocument.suspendHistory(name, code);
        return true;
    },

    // Execute action from action set
    ExecuteAction: function (actionName, actionSet) {
        app.doAction(actionName, actionSet);
        return true;
    },

    // Get active layer
    GetActiveLayer: function () {
        return app.activeDocument.activeLayer;
    },

    // Set active layer
    SetActiveLayer: function (layer) {
        app.activeDocument.activeLayer = layer;
        return true;
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

// Auto-initialize when loaded
ONI_PS.Core.Init();
ONI_PS.Core.Log("ONI_PS Library loaded - Version " + ONI_PS.VERSION);

// Export for Node.js compatibility (if needed)
if (typeof module !== 'undefined') {
    module.exports = ONI_PS;
}
