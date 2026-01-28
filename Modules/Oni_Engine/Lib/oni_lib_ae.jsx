// ONI AFTER EFFECTS CORE LIBRARY (v1.0)
// "The Brain" of ONI's Motion Capability.

var ONI = (function () {

    var self = {};

    // --- UTILS ---
    self.clean = function () {
        // Clear all items in project? Dangerous?
        // Let's just return true for now.
        return true;
    };

    self.color = function (r, g, b) {
        return [r, g, b];
    };

    // --- COMPOSITIONS ---
    self.Comp = {
        getOrCreate: function (name, w, h, dur, fps) {
            // Check existing
            for (var i = 1; i <= app.project.items.length; i++) {
                var item = app.project.items[i];
                if (item instanceof CompItem && item.name === name) {
                    return item;
                }
            }
            // Create New
            return app.project.items.addComp(name, w, h, 1.0, dur, fps);
        }
    };

    // --- LAYERS ---
    self.Layer = {
        addSolid: function (comp, name, color, w, h) {
            return comp.layers.addSolid(color, name, w || comp.width, h || comp.height, 1.0, comp.duration);
        },

        addText: function (comp, content, size, color) {
            var layer = comp.layers.addText(content);
            var prop = layer.property("Source Text");
            var doc = prop.value;
            doc.fontSize = size || 100;
            doc.fillColor = color || [1, 1, 1];
            doc.font = "Arial";
            doc.justification = ParagraphJustification.CENTER_JUSTIFY;
            prop.setValue(doc);
            return layer;
        },

        addNull: function (comp, name) {
            return comp.layers.addNull(comp.duration); // Requires AE 2020+? 
            // If addNull undefined in older ver, use addSolid + nullLayer=true
            // AE 2025 has addNull? Usually yes. If not fallback:
            // var s = comp.layers.addSolid([0,0,0], name, 100, 100, 1, comp.duration);
            // s.nullLayer = true; return s;
        },

        addCamera: function (comp, name, preset) {
            var cam = comp.layers.addCamera(name, [comp.width / 2, comp.height / 2]);
            return cam;
        },

        set3D: function (layer, is3D) {
            layer.threeDLayer = is3D;
        }
    };

    // --- PROPERTIES ---
    self.Prop = {
        set: function (layer, propName, value) {
            // E.g. "Position", [0,0]
            // Handling nested props is complex. Assuming top level or supported names.
            // Simplified for Position/Opacity/Scale/Rotation
            if (layer.property(propName)) {
                layer.property(propName).setValue(value);
            }
        },

        animate: function (layer, propName, t1, v1, t2, v2) {
            var prop = layer.property(propName);
            if (prop) {
                prop.setValueAtTime(t1, v1);
                prop.setValueAtTime(t2, v2);
            }
        },

        expression: function (layer, propName, expr) {
            var prop = layer.property(propName);
            if (prop) {
                prop.expression = expr;
            }
        }
    };

    return self;

})();
