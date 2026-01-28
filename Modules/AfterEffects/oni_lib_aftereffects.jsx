/*
 * ONI CORE LIBRARY - AFTER EFFECTS AUTOMATION
 * Version: 1.0
 * 
 * Standardized High-Quality Functions for Motion Graphics & VFX Generation.
 * Usage: Load this into ExtendScript Toolkit or as .jsx in After Effects
 */

var ONI = ONI || {};

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI.Core = {
    // Get or create composition
    GetOrCreateComp: function(name, width, height, fps, duration) {
        var comp = null;
        
        // Search existing
        for (var i = 1; i <= app.project.numItems; i++) {
            if (app.project.item(i) instanceof CompItem && 
                app.project.item(i).name === name) {
                comp = app.project.item(i);
                break;
            }
        }
        
        // Create if not found
        if (!comp) {
            comp = app.project.items.addComp(name, width, height, 1.0, duration, fps);
        }
        
        return comp;
    },
    
    // Color helper (0-1 range for AE)
    Color: function(r, g, b, a) {
        if (a === undefined) a = 1.0;
        return [r / 255, g / 255, b / 255, a];
    },
    
    // RGB to Hex
    RGBToHex: function(r, g, b) {
        return "#" + 
            ("0" + Math.round(r).toString(16)).slice(-2) +
            ("0" + Math.round(g).toString(16)).slice(-2) +
            ("0" + Math.round(b).toString(16)).slice(-2);
    },
    
    // Apply expression to property
    ApplyExpression: function(property, expression) {
        property.expression = expression;
    },
    
    // Center layer in comp
    CenterLayer: function(layer, comp) {
        layer.position.setValue([comp.width / 2, comp.height / 2]);
    }
};

// ============================================================================
// MODULE: SHAPE LAYER ENGINE
// ============================================================================
ONI.Shapes = {
    // Create shape layer with solid fill
    CreateRect: function(comp, name, x, y, width, height, fillColor, strokeColor, strokeWidth) {
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = name;
        
        // Add rectangle
        var rectGroup = shapeLayer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        rectGroup.name = name + "_Group";
        
        var rect = rectGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue([width, height]);
        
        // Add fill
        var fill = rectGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(fillColor);
        
        // Add stroke if specified
        if (strokeColor && strokeWidth > 0) {
            var stroke = rectGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeColor);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth);
        }
        
        // Position
        shapeLayer.position.setValue([x, y]);
        
        return shapeLayer;
    },
    
    // Create circle/ellipse
    CreateCircle: function(comp, name, x, y, diameter, fillColor) {
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = name;
        
        var circleGroup = shapeLayer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        circleGroup.name = name + "_Group";
        
        var ellipse = circleGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([diameter, diameter]);
        
        var fill = circleGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(fillColor);
        
        shapeLayer.position.setValue([x, y]);
        
        return shapeLayer;
    },
    
    // Create polygon (hexagon, triangle, etc)
    CreatePolygon: function(comp, name, x, y, radius, points, fillColor) {
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = name;
        
        var polyGroup = shapeLayer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        polyGroup.name = name + "_Group";
        
        var poly = polyGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Star");
        poly.property("ADBE Vector Star Type").setValue(1); // Polygon
        poly.property("ADBE Vector Star Points").setValue(points);
        poly.property("ADBE Vector Star Outer Radius").setValue(radius);
        
        var fill = polyGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(fillColor);
        
        shapeLayer.position.setValue([x, y]);
        
        return shapeLayer;
    }
};

// ============================================================================
// MODULE: TEXT ENGINE
// ============================================================================
ONI.Text = {
    // Create text layer with styling
    CreateText: function(comp, text, x, y, fontSize, fontName, fillColor) {
        var textLayer = comp.layers.addText(text);
        var textProp = textLayer.property("ADBE Text Properties").property("ADBE Text Document");
        var textDoc = textProp.value;
        
        // Apply styling
        textDoc.resetCharStyle();
        textDoc.fontSize = fontSize;
        textDoc.fillColor = fillColor;
        
        try {
            textDoc.font = fontName;
        } catch(e) {
            textDoc.font = "Arial-BoldMT"; // Fallback
        }
        
        textProp.setValue(textDoc);
        
        // Position
        textLayer.position.setValue([x, y]);
        
        return textLayer;
    },
    
    // Animate text in (character by character)
    AnimateTextIn: function(textLayer, startTime, duration) {
        // Add animator
        var textProp = textLayer.property("ADBE Text Properties");
        var animator = textProp.property("ADBE Text Animators").addProperty("ADBE Text Animator");
        
        // Add opacity property
        var opacity = animator.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity");
        opacity.setValue(0);
        
        // Animate range selector
        var selector = animator.property("ADBE Text Selectors").property("ADBE Text Selector");
        var start = selector.property("ADBE Text Range Start");
        
        start.setValueAtTime(startTime, 0);
        start.setValueAtTime(startTime + duration, 100);
        
        return textLayer;
    }
};

// ============================================================================
// MODULE: FX ENGINE (EFFECTS)
// ============================================================================
ONI.FX = {
    // Apply glow effect (Cyberpunk style)
    ApplyGlow: function(layer, intensity, threshold, radius, color) {
        var glow = layer.property("ADBE Effect Parade").addProperty("ADBE Glo2");
        glow.property("ADBE Glo2-0001").setValue(intensity || 100); // Glow Threshold
        glow.property("ADBE Glo2-0002").setValue(radius || 50); // Glow Radius
        glow.property("ADBE Glo2-0003").setValue(threshold || 50); // Glow Intensity
        
        return glow;
    },
    
    // Apply drop shadow
    ApplyDropShadow: function(layer, distance, softness, angle, opacity) {
        var shadow = layer.property("ADBE Effect Parade").addProperty("ADBE Drop Shadow");
        shadow.property("ADBE Drop Shadow-0001").setValue(distance || 10); // Distance
        shadow.property("ADBE Drop Shadow-0002").setValue(softness || 20); // Softness
        shadow.property("ADBE Drop Shadow-0003").setValue(angle || 135); // Direction
        shadow.property("ADBE Drop Shadow-0005").setValue(opacity || 0.75); // Opacity
        
        return shadow;
    },
    
    // Apply stroke
    ApplyStroke: function(layer, width, color, position) {
        var stroke = layer.property("ADBE Effect Parade").addProperty("ADBE Stroke");
        stroke.property("ADBE Stroke-0001").setValue(color); // Color
        stroke.property("ADBE Stroke-0002").setValue(width || 3); // Brush Size
        stroke.property("ADBE Stroke-0007").setValue(position || 2); // Paint Style (2 = On Transparent)
        
        return stroke;
    },
    
    // Add noise/grain
    ApplyNoise: function(layer, amount) {
        var noise = layer.property("ADBE Effect Parade").addProperty("ADBE Noise");
        noise.property("ADBE Noise-0001").setValue(amount || 25); // Amount of Noise
        
        return noise;
    },
    
    // CC Light Burst (for neon effects)
    ApplyLightBurst: function(layer, intensity, rayLength) {
        try {
            var burst = layer.property("ADBE Effect Parade").addProperty("CC Light Burst 2.5");
            burst.property("CC Light Burst 2.5-0001").setValue(intensity || 50);
            burst.property("CC Light Burst 2.5-0002").setValue(rayLength || 100);
            return burst;
        } catch(e) {
            return null;
        }
    }
};

// ============================================================================
// MODULE: ANIMATION ENGINE
// ============================================================================
ONI.Animate = {
    // Fade in animation
    FadeIn: function(layer, startTime, duration) {
        var opacity = layer.property("ADBE Transform Group").property("ADBE Opacity");
        opacity.setValueAtTime(startTime, 0);
        opacity.setValueAtTime(startTime + duration, 100);
        
        return layer;
    },
    
    // Fade out animation
    FadeOut: function(layer, startTime, duration) {
        var opacity = layer.property("ADBE Transform Group").property("ADBE Opacity");
        opacity.setValueAtTime(startTime, 100);
        opacity.setValueAtTime(startTime + duration, 0);
        
        return layer;
    },
    
    // Scale bounce in
    BounceIn: function(layer, startTime, duration) {
        var scale = layer.property("ADBE Transform Group").property("ADBE Scale");
        
        scale.setValueAtTime(startTime, [0, 0]);
        scale.setValueAtTime(startTime + duration * 0.6, [110, 110]);
        scale.setValueAtTime(startTime + duration, [100, 100]);
        
        // Add easing
        var key1 = scale.nearestKeyIndex(startTime);
        var key2 = scale.nearestKeyIndex(startTime + duration);
        
        scale.setInterpolationTypeAtKey(key1, KeyframeInterpolationType.BEZIER);
        scale.setInterpolationTypeAtKey(key2, KeyframeInterpolationType.BEZIER);
        
        return layer;
    },
    
    // Slide in from side
    SlideIn: function(layer, comp, startTime, duration, direction) {
        var position = layer.property("ADBE Transform Group").property("ADBE Position");
        var finalPos = position.value;
        var startPos = [finalPos[0], finalPos[1]];
        
        // Calculate start position based on direction
        switch(direction) {
            case "left":
                startPos[0] = -layer.width;
                break;
            case "right":
                startPos[0] = comp.width + layer.width;
                break;
            case "top":
                startPos[1] = -layer.height;
                break;
            case "bottom":
                startPos[1] = comp.height + layer.height;
                break;
        }
        
        position.setValueAtTime(startTime, startPos);
        position.setValueAtTime(startTime + duration, finalPos);
        
        return layer;
    },
    
    // Wiggle expression
    AddWiggle: function(property, frequency, amplitude) {
        property.expression = "wiggle(" + frequency + ", " + amplitude + ")";
    },
    
    // Loop expression
    AddLoop: function(property, loopType) {
        // loopType: "cycle", "pingpong", "offset", "continue"
        property.expression = "loopOut(type = '" + (loopType || "cycle") + "')";
    }
};

// ============================================================================
// MODULE: COMPOSITION PRESETS
// ============================================================================
ONI.Presets = {
    // Create cyberpunk composition
    CreateCyberpunkComp: function(name, width, height) {
        var comp = ONI.Core.GetOrCreateComp(name || "Cyberpunk_Comp", 
            width || 1920, height || 1080, 30, 10);
        
        // Add background
        var bg = ONI.Shapes.CreateRect(comp, "BG", comp.width/2, comp.height/2, 
            comp.width, comp.height, ONI.Core.Color(10, 10, 15), null, 0);
        
        return comp;
    },
    
    // Create badge composition
    CreateBadgeComp: function(name) {
        // 90mm x 140mm at 150 DPI = 531 x 827 px
        var comp = ONI.Core.GetOrCreateComp(name || "Badge_Comp", 531, 827, 30, 5);
        
        return comp;
    },
    
    // Create title sequence
    CreateTitleSequence: function(name) {
        var comp = ONI.Core.GetOrCreateComp(name || "Title_Sequence", 1920, 1080, 30, 5);
        
        return comp;
    }
};

// ============================================================================
// MODULE: PROCEDURAL GENERATION
// ============================================================================
ONI.Generate = {
    // Generate tech grid background
    CreateTechGrid: function(comp, spacing, lineWidth, color) {
        var grid = comp.layers.addShape();
        grid.name = "Tech_Grid";
        
        var gridGroup = grid.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        
        // Vertical lines
        for (var x = 0; x < comp.width; x += spacing) {
            var line = gridGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Group");
            // Shape creation logic here
        }
        
        return grid;
    },
    
    // Generate random particles
    CreateParticles: function(comp, count, color) {
        var particleLayer = comp.layers.addShape();
        particleLayer.name = "Particles";
        
        for (var i = 0; i < count; i++) {
            var x = Math.random() * comp.width;
            var y = Math.random() * comp.height;
            var size = Math.random() * 10 + 2;
            
            var particle = ONI.Shapes.CreateCircle(comp, "Particle_" + i, x, y, size, color);
            
            // Add random movement
            ONI.Animate.AddWiggle(particle.property("ADBE Transform Group").property("ADBE Position"), 
                0.5, 50);
        }
        
        return particleLayer;
    },
    
    // Create scanlines overlay
    CreateScanlines: function(comp, spacing, opacity) {
        var scanlines = comp.layers.addShape();
        scanlines.name = "Scanlines";
        
        var scanlinesGroup = scanlines.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        
        // Create horizontal lines
        for (var y = 0; y < comp.height; y += spacing) {
            var rect = scanlinesGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
            rect.property("ADBE Vector Rect Size").setValue([comp.width, 1]);
            rect.property("ADBE Vector Rect Position").setValue([0, y - comp.height/2]);
        }
        
        var fill = scanlinesGroup.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(ONI.Core.Color(0, 240, 255));
        
        scanlines.property("ADBE Transform Group").property("ADBE Opacity").setValue(opacity || 15);
        scanlines.blendingMode = BlendingMode.SCREEN;
        
        return scanlines;
    }
};

// ============================================================================
// MODULE: EXPORT & RENDER
// ============================================================================
ONI.Export = {
    // Add to render queue
    AddToRenderQueue: function(comp, outputPath, format) {
        var renderQueue = app.project.renderQueue;
        var item = renderQueue.items.add(comp);
        
        // Set output module
        var outputModule = item.outputModules[1];
        
        if (format === "png") {
            outputModule.applyTemplate("PNG Sequence");
        } else if (format === "mov") {
            outputModule.applyTemplate("Best Settings");
        }
        
        outputModule.file = new File(outputPath);
        
        return item;
    }
};

// ============================================================================
// EXPORT
// ============================================================================

// Main initialization
(function() {
    try {
        $.writeln("ONI After Effects Library Loaded v1.0");
    } catch(e) {
        alert("ONI Library Load Error: " + e.toString());
    }
})();
