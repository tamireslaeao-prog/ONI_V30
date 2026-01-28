// ONI ILLUSTRATOR LIBRARY (v1.0)
// GEOMETRY & VECTOR PRIMITIVES

var ONI = (function () {
    var self = {};

    // COLOR HELPER (RGB ONLY)
    self.RGB = function (r, g, b) {
        var col = new RGBColor();
        col.red = r;
        col.green = g;
        col.blue = b;
        return col;
    };

    // DOCUMENT
    self.Doc = {
        getOrCreate: function (name, w, h) {
            if (app.documents.length > 0) {
                return app.activeDocument;
            } else {
                // Preset: Width, Height, Units, ColorMode
                // Units: 6 (Pixels)? No, AI API uses points by default.
                // 1920px width = 1920 points if separate?
                // Let's create specific preset
                var preset = new DocumentPreset();
                preset.title = name;
                preset.width = w;
                preset.height = h;
                preset.colorMode = DocumentColorSpace.RGB;
                preset.units = RulerUnits.Pixels;
                return app.documents.addDocument(DocumentColorSpace.RGB, preset);
            }
        },
        clean: function () {
            // Delete all items?
            var doc = app.activeDocument;
            doc.selection = null;
            var items = doc.pageItems;
            for (var i = items.length - 1; i >= 0; i--) {
                items[i].remove();
            }
        }
    };

    // LAYERS
    self.Layer = {
        getOrCreate: function (doc, name) {
            try {
                return doc.layers.getByName(name);
            } catch (e) {
                var l = doc.layers.add();
                l.name = name;
                return l;
            }
        }
    };

    // SHAPES
    self.Shape = {
        rect: function (doc, layer, x, y, w, h, color) {
            // AI Coord System: Y is UP in some versions?
            // Usually: top, left, width, height
            // Top is Y. Left is X.
            // Wait, .rectangle(top, left, width, height)
            var rect = doc.pathItems.rectangle(y, x, w, h);
            rect.fillColor = color;
            rect.stroked = false;
            // Move to layer?
            // Created in active layer usually.
            rect.move(layer, ElementPlacement.PLACEATEND);
            return rect;
        },
        circle: function (doc, layer, centerX, centerY, radius, color) {
            // .ellipse(top, left, width, height)
            // top = centerY + radius
            // left = centerX - radius
            var top = centerY + radius;
            var left = centerX - radius;
            var size = radius * 2;
            var e = doc.pathItems.ellipse(top, left, size, size);
            e.fillColor = color;
            e.stroked = false;
            e.move(layer, ElementPlacement.PLACEATEND);
            return e;
        }
    };

    // TEXT
    self.Text = {
        create: function (doc, layer, content, x, y, size, color) {
            var tf = doc.textFrames.add();
            tf.contents = content;
            // Position: top, left
            tf.top = y;
            tf.left = x;

            var range = tf.textRange;
            range.characterAttributes.size = size;
            range.characterAttributes.fillColor = color;
            // Font?
            try {
                range.characterAttributes.textFont = textFonts.getByName("Arial-BoldMT");
            } catch (e) { }

            tf.move(layer, ElementPlacement.PLACEATEND);
            return tf;
        },
        outline: function (textFrame) {
            return textFrame.createOutline();
        }
    };

    return self;
})();
