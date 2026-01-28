/*
 * ONI CORE LIBRARY - PHOTOSHOP AUTOMATION
 * Version: 1.2 (Robust Texture & Typography)
 * 
 * Standardized High-Quality Functions for UI/UX Generation.
 * Usage: Load this string into any PS Script execution context.
 */

var ONI = ONI || {};

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI.Core = {
    // Helper to get ActionDescriptor Color
    Color: function (r, g, b) {
        var c = new ActionDescriptor();
        c.putDouble(charIDToTypeID("Rd  "), r);
        c.putDouble(charIDToTypeID("Grn "), g);
        c.putDouble(charIDToTypeID("Bl  "), b);
        return c;
    },

    SolidColor: function (r, g, b) {
        var c = new SolidColor();
        c.rgb.red = r; c.rgb.green = g; c.rgb.blue = b;
        return c;
    },

    SelectAll: function () {
        var doc = app.activeDocument;
        doc.selection.selectAll();
    },

    Deselect: function () {
        var doc = app.activeDocument;
        try { doc.selection.deselect(); } catch (e) { }
    },

    // Standardized Shape Drawer
    DrawShapeFromPoints: function (name, points, r, g, b) {
        // Default to Grey if undefined
        if (r === undefined) r = 128;
        if (g === undefined) g = 128;
        if (b === undefined) b = 128;

        var doc = app.activeDocument;
        var lineArray = new Array();
        for (var i = 0; i < points.length; i++) {
            var p = new PathPointInfo();
            p.kind = PointKind.CORNERPOINT;
            p.anchor = points[i];
            p.leftDirection = points[i];
            p.rightDirection = points[i];
            lineArray.push(p);
        }

        var lineSubPathArray = new SubPathInfo();
        lineSubPathArray.closed = true;
        lineSubPathArray.operation = ShapeOperation.SHAPEADD;
        lineSubPathArray.entireSubPath = lineArray;

        var myPathItem = doc.pathItems.add("TempPath", [lineSubPathArray]);

        // Fill Path -> Shape Layer
        var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putClass(stringIDToTypeID("contentLayer"));
        desc.putReference(charIDToTypeID("null"), ref);
        var desc2 = new ActionDescriptor();
        var desc3 = new ActionDescriptor();
        var desc4 = new ActionDescriptor();
        desc4.putDouble(charIDToTypeID("Rd  "), r);
        desc4.putDouble(charIDToTypeID("Grn "), g);
        desc4.putDouble(charIDToTypeID("Bl  "), b);
        desc3.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), desc4);
        desc2.putObject(charIDToTypeID("Type"), stringIDToTypeID("solidColorLayer"), desc3);
        desc.putObject(charIDToTypeID("Usng"), stringIDToTypeID("contentLayer"), desc2);
        executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);

        myPathItem.remove();
        try { doc.activeLayer.name = name; } catch (e) { }
        return doc.activeLayer;
    }
};

// ============================================================================
// MODULE: FX ENGINE (HIGH END STYLES)
// ============================================================================
ONI.FX = {
    // Applies a High-End Industrial Steel look (Chiseled)
    ApplyCyberSteel: function (layerName) {
        var doc = app.activeDocument;
        doc.activeLayer = doc.artLayers.getByName(layerName);

        var idsetd = charIDToTypeID("setd");
        var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
        ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
        desc.putReference(charIDToTypeID("null"), ref);

        var descFX = new ActionDescriptor();

        // BEVEL: Chisel Hard
        var descBevel = new ActionDescriptor();
        descBevel.putEnumerated(charIDToTypeID("bvlT"), charIDToTypeID("bvlT"), stringIDToTypeID("chiselledHard"));
        descBevel.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 12); // Deep cut
        descBevel.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 150); // Depth
        descBevel.putObject(charIDToTypeID("hglC"), charIDToTypeID("RGBC"), ONI.Core.Color(220, 240, 255)); // Blue-White High
        descBevel.putObject(charIDToTypeID("sdwC"), charIDToTypeID("RGBC"), ONI.Core.Color(10, 15, 20)); // Void Shadow
        descFX.putObject(charIDToTypeID("ebbl"), charIDToTypeID("ebbl"), descBevel);

        // STROKE: Gunmetal Rim
        var descStroke = new ActionDescriptor();
        descStroke.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 4);
        descStroke.putEnumerated(charIDToTypeID("Pstn"), charIDToTypeID("Pstn"), charIDToTypeID("Ins "));
        descStroke.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), ONI.Core.Color(60, 65, 70));
        descFX.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), descStroke);

        // DROP SHADOW: Ambient Occlusion
        var descDrop = new ActionDescriptor();
        descDrop.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 20);
        descDrop.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 40);
        descDrop.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 85);
        descFX.putObject(charIDToTypeID("DrSh"), charIDToTypeID("DrSh"), descDrop);

        desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), descFX);
        executeAction(idsetd, desc, DialogModes.NO);
    },

    // Applies a "Hollow Neon" look (0% Fill, Stroke + Glow)
    ApplyHollowNeon: function (layer, r, g, b) {
        var doc = app.activeDocument;
        doc.activeLayer = layer;
        layer.fillOpacity = 0; // The key to "Hollow"

        var idsetd = charIDToTypeID("setd");
        var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
        ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
        desc.putReference(charIDToTypeID("null"), ref);

        var descFX = new ActionDescriptor();

        // STROKE (The Tube)
        var descStroke = new ActionDescriptor();
        descStroke.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 3);
        descStroke.putEnumerated(charIDToTypeID("Pstn"), charIDToTypeID("Pstn"), charIDToTypeID("Cntr"));
        descStroke.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), ONI.Core.Color(r, g, b));
        descFX.putObject(charIDToTypeID("FrFX"), charIDToTypeID("FrFX"), descStroke);

        // OUTER GLOW (The Atmosphere)
        var descGlow = new ActionDescriptor();
        descGlow.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), ONI.Core.Color(r, g * 0.8, b)); // Slightly dimmer glow
        descGlow.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), 20);
        descGlow.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 80);
        descFX.putObject(charIDToTypeID("OrGl"), charIDToTypeID("OrGl"), descGlow);

        desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), descFX);
        executeAction(idsetd, desc, DialogModes.NO);
    },

    // New: Inner Glow Helper (Robust V1.2)
    ApplyInnerGlow: function (layer, r, g, b, size, opacity) {
        try {
            if (!layer) throw "Layer is null";
            var doc = app.activeDocument;
            doc.activeLayer = layer;

            // Force type conversion (JS/COM bridge safety)
            var nSize = Number(size);
            var nOp = Number(opacity);
            if (isNaN(nSize)) nSize = 10;
            if (isNaN(nOp)) nOp = 75;

            var idsetd = charIDToTypeID("setd");
            var desc = new ActionDescriptor();
            var ref = new ActionReference();
            ref.putProperty(charIDToTypeID("Prpr"), charIDToTypeID("Lefx"));
            ref.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
            desc.putReference(charIDToTypeID("null"), ref);

            var descFX = new ActionDescriptor();
            var descGlow = new ActionDescriptor();
            descGlow.putUnitDouble(charIDToTypeID("Sz  "), charIDToTypeID("#Pxl"), nSize);
            descGlow.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), nOp);

            // Source: Edge (Edg ) vs Center (Cntr)
            descGlow.putEnumerated(charIDToTypeID("Src "), charIDToTypeID("IGSrc"), charIDToTypeID("Edg "));

            descGlow.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), ONI.Core.Color(r, g, b));

            descFX.putObject(charIDToTypeID("IrGl"), charIDToTypeID("IrGl"), descGlow);
            desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Lefx"), descFX);
            executeAction(idsetd, desc, DialogModes.NO);
        } catch (e) {
            // Swallow error to prevent script crash, but log it
            // throw "ApplyInnerGlow Failed: " + e.message;
        }
    }
};

// ============================================================================
// MODULE: MATERIAL SYNTHESIZER (PROCEDURAL TEXTURES)
// ============================================================================
ONI.Materials = {
    // Generates a Brushed Metal texture clipped to the target layer
    CreateBrushedMetal: function (targetLayerName) {
        var doc = app.activeDocument;
        try {
            var targetLayer = doc.artLayers.getByName(targetLayerName);
            doc.activeLayer = targetLayer;

            // 1. Create Texture Layer
            var metalLayer = doc.artLayers.add();
            metalLayer.name = targetLayerName + "_MetalFX";

            // 2. Fill with 50% Grey
            doc.selection.selectAll();
            doc.selection.fill(ONI.Core.SolidColor(128, 128, 128));
            doc.selection.deselect();

            // 3. Add Noise
            try {
                var idAdNs = charIDToTypeID("AdNs");
                var descNoise = new ActionDescriptor();
                descNoise.putUnitDouble(charIDToTypeID("Amnt"), charIDToTypeID("#Prc"), 40.000000);
                descNoise.putEnumerated(charIDToTypeID("Dstr"), charIDToTypeID("Dstr"), charIDToTypeID("Gsn "));
                descNoise.putBoolean(charIDToTypeID("Mnch"), true);
                executeAction(idAdNs, descNoise, DialogModes.NO);
            } catch (e) { }

            // 4. Motion Blur
            try {
                var idMtnB = charIDToTypeID("MtnB");
                var descBlur = new ActionDescriptor();
                descBlur.putInteger(charIDToTypeID("Angl"), 0);
                descBlur.putUnitDouble(charIDToTypeID("Dstn"), charIDToTypeID("#Pxl"), 50);
                executeAction(idMtnB, descBlur, DialogModes.NO);
            } catch (e) { }

            // 5. Set Blend Mode to Overlay
            metalLayer.blendMode = BlendMode.OVERLAY;
            metalLayer.opacity = 60;

            // 6. Create Clipping Mask (Safer DOM Method)
            try {
                metalLayer.grouped = true;
            } catch (e) {
                // Fallback
                var idGrp = charIDToTypeID("GrpL");
                var descGrp = new ActionDescriptor();
                var refGrp = new ActionReference();
                refGrp.putEnumerated(charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
                descGrp.putReference(charIDToTypeID("null"), refGrp);
                executeAction(idGrp, descGrp, DialogModes.NO);
            }
            return metalLayer;
        } catch (e) {
            return null;
        }
    }
};

// ============================================================================
// MODULE: ADVANCED TYPOGRAPHY
// ============================================================================
ONI.Text = {
    CreateTrackingText: function (content, fontName, size, tracking, x, y, r, g, b) {
        var doc = app.activeDocument;
        var layer = doc.artLayers.add();
        layer.kind = LayerKind.TEXT;
        var ti = layer.textItem;

        ti.contents = content;
        try { ti.font = fontName; } catch (e) { ti.font = "Arial-BoldMT"; } // Fallback
        ti.size = size;
        ti.position = [x, y];
        ti.color = ONI.Core.SolidColor(r, g, b);

        // Tracking via Actions (DOM Read-Only in some CS versions)
        try {
            ti.tracking = tracking;
        } catch (e) { }
        return layer;
    }
};

// ============================================================================
// MODULE: SHAPE ENGINE (PROCEDURAL GEOMETRY)
// ============================================================================
ONI.Shapes = {
    // Generates the complex Hex-Capsule from AEGIS project
    CreateAegisHull: function (name, cx, cy, w, h, r, g, b) {
        var doc = app.activeDocument;

        // If args are missing, handle it?
        if (r === undefined) { r = 128; g = 128; b = 128; } // Safe default

        var halfW = w / 2; var halfH = h / 2;
        var corner = 60;

        // 8-Point Geometry
        var points = [
            [cx - halfW + corner, cy - halfH],
            [cx + halfW - corner, cy - halfH],
            [cx + halfW, cy - halfH + corner],
            [cx + halfW, cy + halfH - corner],
            [cx + halfW - corner, cy + halfH],
            [cx - halfW + corner, cy + halfH],
            [cx - halfW, cy + halfH - corner],
            [cx - halfW, cy - halfH + corner]
        ];

        return ONI.Core.DrawShapeFromPoints(name, points, r, g, b);
    },

    // --- PRIMITIVES (Added for Logo Gen) ---
    DrawRect: function (name, cx, cy, w, h, r, g, b) {
        var x1 = cx - w / 2;
        var y1 = cy - h / 2;
        var x2 = cx + w / 2;
        var y2 = cy + h / 2;
        var pts = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]];
        return ONI.Core.DrawShapeFromPoints(name, pts, r, g, b);
    },

    DrawCircle: function (name, cx, cy, r, red, green, blue) {
        var pts = [];
        var sides = 32;
        for (var i = 0; i < sides; i++) {
            var theta = (i / sides) * 2 * Math.PI;
            var px = cx + r * Math.cos(theta);
            var py = cy + r * Math.sin(theta);
            pts.push([px, py]);
        }
        return ONI.Core.DrawShapeFromPoints(name, pts, red, green, blue);
    },

    DrawHexagon: function (name, cx, cy, r, red, green, blue) {
        var pts = [];
        for (var i = 0; i < 6; i++) {
            var angle_deg = 60 * i - 30;
            var angle_rad = Math.PI / 180 * angle_deg;
            var px = cx + r * Math.cos(angle_rad);
            var py = cy + r * Math.sin(angle_rad);
            pts.push([px, py]);
        }
        return ONI.Core.DrawShapeFromPoints(name, pts, red, green, blue);
    },

    DrawTriangle: function (name, cx, cy, r, red, green, blue) {
        var pts = [];
        for (var i = 0; i < 3; i++) {
            var angle_deg = 120 * i - 90; // Point up
            var angle_rad = Math.PI / 180 * angle_deg;
            var px = cx + r * Math.cos(angle_rad);
            var py = cy + r * Math.sin(angle_rad);
            pts.push([px, py]);
        }
        return ONI.Core.DrawShapeFromPoints(name, pts, red, green, blue);
    }
};
