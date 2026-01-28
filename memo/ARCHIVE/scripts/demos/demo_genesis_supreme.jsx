// ONI GENESIS SUPREME - THE MASTERPIECE
// Combining: Creativity Engine + Neural Fabrication + Glassmorphism + Neumorphism + Volumetric FX
// Date: 2026-01-11 - Estado Perfeito Integration Demo

// ============ STYLE DNA (Creativity Engine L3) ============
var STYLE_DNA = {
    palette: {
        cosmic_void: [5, 10, 25],        // Deep space background
        chrome_light: [220, 230, 240],   // Metallic highlights
        chrome_dark: [100, 110, 120],    // Metallic shadows
        neon_cyan: [0, 240, 255],        // Electric cyan
        neon_magenta: [255, 0, 180],     // Electric magenta
        gold_dust: [255, 215, 0],        // Golden particles
        glass_frost: [200, 220, 240]     // Frosted glass overlay
    },
    mood_vector: [0.9, 0.1, 0.95], // [Aggressive, Calm, Chaotic]
    complexity_level: 0.95          // Ultra-high detail
};

// ============ HELPER FUNCTIONS ============
function cTID(s) { return charIDToTypeID(s); }
function sTID(s) { return stringIDToTypeID(s); }

function rgbColor(r, g, b) {
    var c = new SolidColor();
    c.rgb.red = r;
    c.rgb.green = g;
    c.rgb.blue = b;
    return c;
}

function createGradient(colors, name) {
    var grad = new ActionDescriptor();
    var stopList = new ActionList();

    for (var i = 0; i < colors.length; i++) {
        var stop = new ActionDescriptor();
        stop.putDouble(sTID("location"), (i / (colors.length - 1)) * 4096);
        stop.putDouble(sTID("midpoint"), 50);
        var color = new ActionDescriptor();
        color.putDouble(sTID("red"), colors[i][0]);
        color.putDouble(sTID("green"), colors[i][1]);
        color.putDouble(sTID("blue"), colors[i][2]);
        stop.putObject(sTID("color"), sTID("RGBColor"), color);
        stopList.putObject(sTID("colorStop"), stop);
    }

    grad.putEnumerated(sTID("gradientForm"), sTID("gradientForm"), sTID("customStops"));
    grad.putList(sTID("colors"), stopList);
    grad.putString(sTID("name"), name);
    return grad;
}

// ============ MAIN EXECUTION ============
try {
    // Preferences
    app.preferences.rulerUnits = Units.PIXELS;

    // Create document (3000x2000 - High Resolution)
    var doc = app.documents.add(3000, 2000, 72, "ONI_GENESIS_SUPREME", NewDocumentMode.RGB);

    // ===== LAYER 1: COSMIC VOID BACKGROUND =====
    var bgLayer = doc.artLayers.add();
    bgLayer.name = "COSMIC_VOID";
    doc.activeLayer = bgLayer;

    var bgColor = rgbColor(STYLE_DNA.palette.cosmic_void[0],
        STYLE_DNA.palette.cosmic_void[1],
        STYLE_DNA.palette.cosmic_void[2]);
    doc.selection.selectAll();
    doc.selection.fill(bgColor);
    doc.selection.deselect();

    // Add cosmic stars (Noise)
    doc.activeLayer.applyAddNoise(3, NoiseDistribution.GAUSSIAN, true);

    // ===== LAYER 2: HEX GRID (Neural Fabrication) =====
    var hexLayer = doc.artLayers.add();
    hexLayer.name = "HEX_GRID_NEURO";
    doc.activeLayer = hexLayer;

    // Draw procedural hex grid (simplified - actual hex grid would use paths)
    var hexSize = 80;
    var hexColor = rgbColor(STYLE_DNA.palette.neon_cyan[0],
        STYLE_DNA.palette.neon_cyan[1],
        STYLE_DNA.palette.neon_cyan[2]);

    // Create line pattern (simulating hex grid)
    for (var y = 0; y < 2000; y += hexSize * 1.5) {
        var lineRegion = [[0, y], [3000, y], [3000, y + 2], [0, y + 2]];
        doc.selection.select(lineRegion);
        doc.selection.fill(hexColor);
        doc.selection.deselect();
    }

    for (var x = 0; x < 3000; x += hexSize * 0.866) { // sqrt(3)/2
        var lineRegion = [[x, 0], [x + 2, 0], [x + 2, 2000], [x, 2000]];
        doc.selection.select(lineRegion);
        doc.selection.fill(hexColor);
        doc.selection.deselect();
    }

    hexLayer.opacity = 15;
    hexLayer.blendMode = BlendMode.SCREEN;

    // ===== LAYER 3: VOLUMETRIC RINGS (Neon) =====
    var ringsGroup = doc.layerSets.add();
    ringsGroup.name = "VOLUMETRIC_RINGS";

    var centerX = 1500;
    var centerY = 1000;

    for (var i = 0; i < 5; i++) {
        var ringLayer = ringsGroup.artLayers.add();
        ringLayer.name = "RING_" + (i + 1);
        doc.activeLayer = ringLayer;

        var radius = 200 + (i * 120);
        var thickness = 20 - (i * 2);

        // Outer circle
        var outerRegion = [];
        var segments = 64;
        for (var a = 0; a < segments; a++) {
            var angle = (a / segments) * Math.PI * 2;
            outerRegion.push([
                centerX + Math.cos(angle) * radius,
                centerY + Math.sin(angle) * radius
            ]);
        }
        doc.selection.select(outerRegion);

        // Inner circle (to subtract)
        var innerRegion = [];
        for (var a = 0; a < segments; a++) {
            var angle = (a / segments) * Math.PI * 2;
            innerRegion.push([
                centerX + Math.cos(angle) * (radius - thickness),
                centerY + Math.sin(angle) * (radius - thickness)
            ]);
        }
        doc.selection.subtract(innerRegion);

        var ringColor = rgbColor(
            i % 2 == 0 ? STYLE_DNA.palette.neon_cyan[0] : STYLE_DNA.palette.neon_magenta[0],
            i % 2 == 0 ? STYLE_DNA.palette.neon_cyan[1] : STYLE_DNA.palette.neon_magenta[1],
            i % 2 == 0 ? STYLE_DNA.palette.neon_cyan[2] : STYLE_DNA.palette.neon_magenta[2]
        );
        doc.selection.fill(ringColor);
        doc.selection.deselect();

        ringLayer.opacity = 80 - (i * 12);
        ringLayer.blendMode = BlendMode.LINEARDODGE;
    }

    // Apply Gaussian Blur for volumetric effect
    doc.activeLayer = ringsGroup;
    // Note: Can't blur group directly in JSX, would need to merge or blur individually

    // ===== LAYER 4: CHROME ORB (Glassmorphic) =====
    var orbLayer = doc.artLayers.add();
    orbLayer.name = "CHROME_ORB_GLASS";
    doc.activeLayer = orbLayer;

    var orbRegion = [];
    var orbRadius = 300;
    for (var a = 0; a < 64; a++) {
        var angle = (a / 64) * Math.PI * 2;
        orbRegion.push([
            centerX + Math.cos(angle) * orbRadius,
            centerY + Math.sin(angle) * orbRadius
        ]);
    }
    doc.selection.select(orbRegion);

    var chromeGrad = createGradient([
        STYLE_DNA.palette.chrome_light,
        STYLE_DNA.palette.chrome_dark,
        STYLE_DNA.palette.chrome_light
    ], "Chrome_Gradient");

    // Fill with gradient (using Action Manager would be needed for custom gradient)
    var gradFill = new GradientColor();
    gradFill.name = "Chrome";
    doc.selection.fill(gradFill); // Simplified - would need ActionManager for custom
    doc.selection.deselect();

    orbLayer.blendMode = BlendMode.SCREEN;
    orbLayer.opacity = 60;

    // ===== LAYER 5: GLASS OVERLAY (Glassmorphism) =====
    var glassLayer = doc.artLayers.add();
    glassLayer.name = "GLASS_FROST_OVERLAY";
    doc.activeLayer = glassLayer;

    var glassRegion = [[600, 300], [2400, 300], [2400, 1700], [600, 1700]];
    doc.selection.select(glassRegion);

    var glassColor = rgbColor(STYLE_DNA.palette.glass_frost[0],
        STYLE_DNA.palette.glass_frost[1],
        STYLE_DNA.palette.glass_frost[2]);
    doc.selection.fill(glassColor);
    doc.selection.deselect();

    glassLayer.opacity = 30;
    glassLayer.blendMode = BlendMode.NORMAL;

    // Apply Gaussian Blur for frosted effect
    glassLayer.applyGaussianBlur(20);

    // ===== LAYER 6: GOLDEN PARTICLES =====
    var particlesLayer = doc.artLayers.add();
    particlesLayer.name = "GOLD_PARTICLES";
    doc.activeLayer = particlesLayer;

    var goldColor = rgbColor(STYLE_DNA.palette.gold_dust[0],
        STYLE_DNA.palette.gold_dust[1],
        STYLE_DNA.palette.gold_dust[2]);

    // Create random particles
    for (var p = 0; p < 50; p++) {
        var px = Math.random() * 3000;
        var py = Math.random() * 2000;
        var psize = 2 + Math.random() * 6;

        var particle = [[px, py], [px + psize, py], [px + psize, py + psize], [px, py + psize]];
        doc.selection.select(particle);
        doc.selection.fill(goldColor);
        doc.selection.deselect();
    }

    particlesLayer.blendMode = BlendMode.SCREEN;
    particlesLayer.opacity = 70;

    // ===== LAYER 7: TEXT TITLE =====
    var titleLayer = doc.artLayers.add();
    titleLayer.kind = LayerKind.TEXT;
    titleLayer.name = "ONI_TITLE";

    var textItem = titleLayer.textItem;
    textItem.contents = "ONIV24";
    textItem.size = 180;
    textItem.font = "Arial";
    textItem.justification = Justification.CENTER;
    textItem.position = [centerX, centerY - 100];
    textItem.color = rgbColor(255, 255, 255);

    // ===== LAYER 8: SUBTITLE =====
    var subtitleLayer = doc.artLayers.add();
    subtitleLayer.kind = LayerKind.TEXT;
    subtitleLayer.name = "SUBTITLE";

    var subTextItem = subtitleLayer.textItem;
    subTextItem.contents = "ESTADO PERFEITO";
    subTextItem.size = 60;
    subTextItem.font = "Arial";
    subTextItem.justification = Justification.CENTER;
    subTextItem.position = [centerX, centerY + 150];
    subTextItem.color = rgbColor(STYLE_DNA.palette.neon_cyan[0],
        STYLE_DNA.palette.neon_cyan[1],
        STYLE_DNA.palette.neon_cyan[2]);

    // Success message
    "ONI GENESIS SUPREME created successfully! Layers: " + doc.artLayers.length + " | Resolution: 3000x2000px | Style DNA: Cosmic/Chrome/Neon";

} catch (e) {
    "ERROR: " + e + " (Line: " + e.line + ")";
}
