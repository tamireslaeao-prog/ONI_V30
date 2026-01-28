// ============================================================================
// ONI.Macros.jsx - Adobe Illustrator Automation Scripts
// Version: 1.0
// Description: Automate style application and effects in Adobe Illustrator
// ============================================================================
// 
// INSTALLATION:
// 1. Save this file as ONI.Macros.jsx
// 2. Place in: C:\Program Files\Adobe\Adobe Illustrator [VERSION]\Presets\en_US\Scripts\
// 3. Restart Illustrator
// 4. Access via: File > Scripts > ONI.Macros
// 
// OR run directly: File > Scripts > Other Script... > Select this file
// ============================================================================

#target illustrator

// ============================================================================
// SCRIPT 1: Apply Cyberpunk Neon Effect
// ============================================================================

function applyCyberpunkNeon() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var sel = doc.selection;
    
    if (sel.length === 0) {
        alert("Please select an object first!");
        return;
    }
    
    // Cyberpunk color palette
    var cyanNeon = new RGBColor();
    cyanNeon.red = 0;
    cyanNeon.green = 240;
    cyanNeon.blue = 255;
    
    var magentaShock = new RGBColor();
    magentaShock.red = 255;
    magentaShock.green = 0;
    magentaShock.blue = 85;
    
    // Apply to each selected object
    for (var i = 0; i < sel.length; i++) {
        var obj = sel[i];
        
        // Set fill color
        if (obj.typename === "TextFrame") {
            obj.textRange.characterAttributes.fillColor = cyanNeon;
        } else if (obj.filled) {
            obj.fillColor = cyanNeon;
        }
        
        // Set stroke
        obj.stroked = true;
        obj.strokeColor = cyanNeon;
        obj.strokeWidth = 2;
        
        // Apply outer glow effect
        try {
            var outerGlow = obj.liveEffects.add("Adobe Outer Glow");
            // Note: Live effects parameters are complex, basic application here
        } catch(e) {
            // Fallback: duplicate and blur
            var glowCopy = obj.duplicate();
            glowCopy.move(obj, ElementPlacement.PLACEBEFORE);
            glowCopy.opacity = 60;
            
            // Apply Gaussian Blur
            try {
                app.executeMenuCommand("Live Gaussian Blur");
            } catch(e2) {}
        }
    }
    
    alert("Cyberpunk Neon effect applied to " + sel.length + " object(s)!");
}

// ============================================================================
// SCRIPT 2: Create Technical Badge Layout
// ============================================================================

function createTechnicalBadge() {
    // Create new document (ID-1 standard: 85.6mm x 53.98mm)
    var docPreset = new DocumentPreset();
    docPreset.width = 242.646; // 85.6mm in points
    docPreset.height = 153; // 53.98mm in points
    docPreset.colorMode = DocumentColorSpace.RGB;
    docPreset.units = RulerUnits.Millimeters;
    
    var doc = app.documents.addDocument("ONI Badge", docPreset);
    var layer = doc.activeLayer;
    
    // Background
    var bg = layer.pathItems.rectangle(153, 0, 242.646, 153);
    var blackColor = new RGBColor();
    blackColor.red = 0;
    blackColor.green = 0;
    blackColor.blue = 0;
    bg.filled = true;
    bg.fillColor = blackColor;
    bg.stroked = false;
    
    // Photo container
    var photoFrame = layer.pathItems.rectangle(139, 14, 85, 113);
    var grayColor = new RGBColor();
    grayColor.red = 128;
    grayColor.green = 128;
    grayColor.blue = 128;
    photoFrame.filled = true;
    photoFrame.fillColor = grayColor;
    photoFrame.stroked = true;
    photoFrame.strokeWidth = 0.5;
    
    // Photo text
    var photoText = layer.textFrames.add();
    photoText.contents = "PHOTO";
    photoText.textRange.characterAttributes.size = 24;
    photoText.textRange.characterAttributes.fillColor = blackColor;
    photoText.position = [40, 80];
    
    // Name field
    var nameText = layer.textFrames.add();
    nameText.contents = "[NAME]";
    nameText.textRange.characterAttributes.size = 36;
    var whiteColor = new RGBColor();
    whiteColor.red = 255;
    whiteColor.green = 255;
    whiteColor.blue = 255;
    nameText.textRange.characterAttributes.fillColor = whiteColor;
    nameText.position = [105, 130];
    
    // Title field
    var titleText = layer.textFrames.add();
    titleText.contents = "[TITLE]";
    titleText.textRange.characterAttributes.size = 24;
    titleText.textRange.characterAttributes.fillColor = whiteColor;
    titleText.position = [105, 100];
    
    // ID field
    var idText = layer.textFrames.add();
    idText.contents = "ID: [00000]";
    idText.textRange.characterAttributes.size = 18;
    titleText.textRange.characterAttributes.fillColor = whiteColor;
    idText.position = [105, 75];
    
    // Barcode placeholder
    var barcode = layer.pathItems.rectangle(45, 14, 142, 28);
    barcode.filled = true;
    barcode.fillColor = whiteColor;
    barcode.stroked = true;
    barcode.strokeWidth = 0.25;
    
    // QR code placeholder
    var qr = layer.pathItems.rectangle(60, 170, 56, 56);
    qr.filled = true;
    qr.fillColor = whiteColor;
    qr.stroked = true;
    qr.strokeWidth = 0.25;
    
    alert("Technical badge layout created!\nReplace placeholders with actual data.");
}

// ============================================================================
// SCRIPT 3: Apply Random Tech Greebles
// ============================================================================

function applyRandomGreebles() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var layer = doc.activeLayer;
    var count = Math.floor(Math.random() * 10) + 10; // 10-20 greebles
    
    // Get document bounds
    var docWidth = doc.width;
    var docHeight = doc.height;
    
    var colors = [
        createRGBColor(0, 240, 255),      // Cyan
        createRGBColor(255, 0, 85),       // Magenta
        createRGBColor(57, 255, 20),      // Green
        createRGBColor(255, 255, 0)       // Yellow
    ];
    
    for (var i = 0; i < count; i++) {
        var x = Math.random() * docWidth;
        var y = Math.random() * docHeight;
        var size = Math.random() * 10 + 2;
        var rotation = Math.random() * 360;
        var greebleType = Math.floor(Math.random() * 5);
        var color = colors[Math.floor(Math.random() * colors.length)];
        
        var greeble;
        
        switch(greebleType) {
            case 0: // Square
                greeble = layer.pathItems.rectangle(y, x, size, size);
                greeble.filled = true;
                greeble.fillColor = color;
                greeble.stroked = false;
                break;
                
            case 1: // Circle
                greeble = layer.pathItems.ellipse(y, x, size, size);
                greeble.filled = true;
                greeble.fillColor = color;
                greeble.stroked = false;
                break;
                
            case 2: // Triangle
                var triangle = layer.pathItems.polygon(x + size/2, y - size/2, size/2, 3);
                triangle.filled = true;
                triangle.fillColor = color;
                triangle.stroked = false;
                greeble = triangle;
                break;
                
            case 3: // Line
                greeble = layer.pathItems.add();
                greeble.setEntirePath([[x, y], [x + size, y + size]]);
                greeble.stroked = true;
                greeble.strokeColor = color;
                greeble.strokeWidth = 0.5;
                greeble.filled = false;
                break;
                
            case 4: // Plus sign
                var plus = layer.textFrames.add();
                plus.contents = "+";
                plus.textRange.characterAttributes.size = size * 3;
                plus.textRange.characterAttributes.fillColor = color;
                plus.position = [x, y];
                greeble = plus;
                break;
        }
        
        // Apply rotation
        if (greeble && greeble.typename !== "TextFrame") {
            greeble.rotate(rotation);
        }
        
        // Apply transparency
        if (greeble) {
            greeble.opacity = 30 + Math.random() * 40;
        }
    }
    
    alert("Greebles applied! Total: " + count);
}

// ============================================================================
// SCRIPT 4: Create Synthwave Gradient Background
// ============================================================================

function createSynthwaveGradient() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var layer = doc.activeLayer;
    
    // Create full-page rectangle
    var bg = layer.pathItems.rectangle(doc.height, 0, doc.width, doc.height);
    
    // Create gradient
    var gradient = doc.gradients.add();
    gradient.name = "Synthwave Gradient";
    gradient.type = GradientType.LINEAR;
    
    // Hot Pink
    var stop1 = gradient.gradientStops.add();
    stop1.rampPoint = 0;
    stop1.color = createRGBColor(255, 0, 110);
    
    // Electric Purple
    var stop2 = gradient.gradientStops.add();
    stop2.rampPoint = 33;
    stop2.color = createRGBColor(131, 56, 236);
    
    // Cyber Blue
    var stop3 = gradient.gradientStops.add();
    stop3.rampPoint = 66;
    stop3.color = createRGBColor(58, 134, 255);
    
    // Cyan
    var stop4 = gradient.gradientStops.add();
    stop4.rampPoint = 100;
    stop4.color = createRGBColor(6, 255, 165);
    
    // Apply gradient to background
    var gradientColor = new GradientColor();
    gradientColor.gradient = gradient;
    gradientColor.angle = 90; // Vertical
    
    bg.filled = true;
    bg.fillColor = gradientColor;
    bg.stroked = false;
    
    // Send to back
    bg.zOrder(ZOrderMethod.SENDTOBACK);
    
    alert("Synthwave gradient created!");
}

// ============================================================================
// SCRIPT 5: Convert to Print-Safe CMYK
// ============================================================================

function convertToPrintSafeCMYK() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    
    // Convert document to CMYK
    doc.documentColorSpace = DocumentColorSpace.CMYK;
    
    var processedCount = 0;
    
    // Process all page items
    for (var i = 0; i < doc.pageItems.length; i++) {
        var item = doc.pageItems[i];
        
        // Convert fills
        if (item.filled && item.fillColor.typename === "RGBColor") {
            var rgbColor = item.fillColor;
            
            // Check if it's meant to be black
            if (rgbColor.red < 20 && rgbColor.green < 20 && rgbColor.blue < 20) {
                // Apply rich black
                var richBlack = new CMYKColor();
                richBlack.cyan = 60;
                richBlack.magenta = 40;
                richBlack.yellow = 40;
                richBlack.black = 100;
                item.fillColor = richBlack;
            } else {
                // Standard RGB to CMYK conversion (Illustrator handles this)
                // But we can force it by reassigning
                var cmykColor = convertRGBtoCMYK(rgbColor);
                item.fillColor = cmykColor;
            }
            processedCount++;
        }
        
        // Convert strokes
        if (item.stroked && item.strokeColor.typename === "RGBColor") {
            var rgbStroke = item.strokeColor;
            
            if (rgbStroke.red < 20 && rgbStroke.green < 20 && rgbStroke.blue < 20) {
                var richBlackStroke = new CMYKColor();
                richBlackStroke.cyan = 60;
                richBlackStroke.magenta = 40;
                richBlackStroke.yellow = 40;
                richBlackStroke.black = 100;
                item.strokeColor = richBlackStroke;
            } else {
                var cmykStroke = convertRGBtoCMYK(rgbStroke);
                item.strokeColor = cmykStroke;
            }
            processedCount++;
        }
    }
    
    // Set black text to overprint
    for (var j = 0; j < doc.textFrames.length; j++) {
        var textFrame = doc.textFrames[j];
        var fillColor = textFrame.textRange.characterAttributes.fillColor;
        
        if (fillColor.typename === "CMYKColor") {
            if (fillColor.cyan >= 60 && fillColor.black === 100) {
                textFrame.textRange.characterAttributes.overprintFill = true;
            }
        }
    }
    
    alert("Design converted to print-safe CMYK!\nProcessed " + processedCount + " objects.\nBlack text set to overprint.");
}

// ============================================================================
// SCRIPT 6: Create Scanline Effect (Cyberpunk)
// ============================================================================

function createScanlineEffect() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    
    // Create new layer for scanlines
    var scanlineLayer = doc.layers.add();
    scanlineLayer.name = "Scanlines";
    
    var docHeight = doc.height;
    var docWidth = doc.width;
    var spacing = 11.34; // 4mm in points
    var lineCount = Math.floor(docHeight / spacing);
    
    var cyanColor = createRGBColor(0, 240, 255);
    
    for (var i = 0; i < lineCount; i++) {
        var y = i * spacing;
        var line = scanlineLayer.pathItems.add();
        line.setEntirePath([[0, docHeight - y], [docWidth, docHeight - y]]);
        line.stroked = true;
        line.strokeColor = cyanColor;
        line.strokeWidth = 0.25;
        line.filled = false;
        line.opacity = 15; // 15% visible
    }
    
    // Set blend mode to Screen (if possible)
    try {
        scanlineLayer.blendingMode = BlendModes.SCREEN;
    } catch(e) {}
    
    alert("Scanlines created! Total lines: " + lineCount);
}

// ============================================================================
// SCRIPT 7: Batch Export (PDF, PNG, SVG)
// ============================================================================

function batchExportFormats() {
    if (app.documents.length === 0) {
        alert("Please save the document first!");
        return;
    }
    
    var doc = app.activeDocument;
    
    if (!doc.saved) {
        alert("Please save the document first!");
        return;
    }
    
    var docPath = doc.path;
    var docName = doc.name.replace(/\.[^\.]+$/, ''); // Remove extension
    
    // Export PDF
    var pdfPath = new File(docPath + "/" + docName + "_print.pdf");
    var pdfOptions = new PDFSaveOptions();
    pdfOptions.compatibility = PDFCompatibility.ACROBAT7;
    pdfOptions.preserveEditability = false;
    doc.saveAs(pdfPath, pdfOptions);
    
    // Export PNG
    var pngPath = new File(docPath + "/" + docName + "_preview.png");
    var pngOptions = new ExportOptionsPNG24();
    pngOptions.artBoardClipping = true;
    pngOptions.transparency = true;
    pngOptions.horizontalScale = 300; // 300%
    pngOptions.verticalScale = 300;
    doc.exportFile(pngPath, ExportType.PNG24, pngOptions);
    
    // Export SVG
    var svgPath = new File(docPath + "/" + docName + "_vector.svg");
    var svgOptions = new ExportOptionsSVG();
    svgOptions.embedRasterImages = true;
    svgOptions.cssProperties = SVGCSSPropertyLocation.PRESENTATIONATTRIBUTES;
    doc.exportFile(svgPath, ExportType.SVG, svgOptions);
    
    alert("Batch export complete!\nFiles saved to: " + docPath.fsName);
}

// ============================================================================
// SCRIPT 8: Create Tech Border Frame
// ============================================================================

function createTechBorderFrame() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var layer = doc.activeLayer;
    var margin = 28.35; // 10mm in points
    
    var cyanColor = createRGBColor(0, 240, 255);
    var magentaColor = createRGBColor(255, 0, 85);
    
    // Outer rectangle
    var outerRect = layer.pathItems.rectangle(
        doc.height - margin,
        margin,
        doc.width - (margin * 2),
        doc.height - (margin * 2)
    );
    outerRect.stroked = true;
    outerRect.strokeColor = cyanColor;
    outerRect.strokeWidth = 3;
    outerRect.filled = false;
    
    // Inner rectangle
    var innerRect = layer.pathItems.rectangle(
        doc.height - margin - 14.17,
        margin + 14.17,
        doc.width - (margin * 2) - 28.34,
        doc.height - (margin * 2) - 28.34
    );
    innerRect.stroked = true;
    innerRect.strokeColor = cyanColor;
    innerRect.strokeWidth = 1;
    innerRect.filled = false;
    
    // Corner decorations
    var cornerSize = 22.68; // 8mm
    var corners = [
        [margin, doc.height - margin, margin + cornerSize, doc.height - margin - cornerSize], // Top-left
        [doc.width - margin, doc.height - margin, doc.width - margin - cornerSize, doc.height - margin - cornerSize], // Top-right
        [margin, margin, margin + cornerSize, margin + cornerSize], // Bottom-left
        [doc.width - margin, margin, doc.width - margin - cornerSize, margin + cornerSize] // Bottom-right
    ];
    
    for (var i = 0; i < corners.length; i++) {
        var corner = layer.pathItems.add();
        corner.setEntirePath([[corners[i][0], corners[i][1]], [corners[i][2], corners[i][3]]]);
        corner.stroked = true;
        corner.strokeColor = magentaColor;
        corner.strokeWidth = 2;
        corner.filled = false;
    }
    
    alert("Tech border frame created!");
}

// ============================================================================
// SCRIPT 9: Create Vertical Japanese Text
// ============================================================================

function createVerticalJapaneseText() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var layer = doc.activeLayer;
    
    var inputText = prompt("Enter Japanese text:", "テキスト");
    
    if (!inputText) return;
    
    // Create vertical text frame
    var textFrame = layer.textFrames.areaText(
        [[doc.width - 141.73, doc.height - 141.73],
         [doc.width - 141.73, 141.73],
         [doc.width - 70.87, 141.73],
         [doc.width - 70.87, doc.height - 141.73]]
    );
    
    textFrame.contents = inputText;
    textFrame.textRange.characterAttributes.size = 136; // 48pt
    
    // Try to set Japanese font
    try {
        textFrame.textRange.characterAttributes.textFont = app.textFonts.getByName("Noto Sans JP");
    } catch(e) {
        // Fallback to system font
        textFrame.textRange.characterAttributes.textFont = app.textFonts[0];
    }
    
    // Set vertical orientation
    textFrame.orientation = TextOrientation.VERTICAL;
    
    // Set color to Japan Red
    var japanRed = new CMYKColor();
    japanRed.cyan = 0;
    japanRed.magenta = 100;
    japanRed.yellow = 100;
    japanRed.black = 0;
    textFrame.textRange.characterAttributes.fillColor = japanRed;
    
    // Add outline
    textFrame.textRange.characterAttributes.strokeColor = createCMYKColor(60, 40, 40, 100);
    textFrame.textRange.characterAttributes.strokeWeight = 1;
    
    alert("Vertical Japanese text created!\nAdjust position as needed.");
}

// ============================================================================
// SCRIPT 10: Smart Duplicate with Variation
// ============================================================================

function smartDuplicateWithVariation() {
    if (app.documents.length === 0) {
        alert("Please open a document first!");
        return;
    }
    
    var doc = app.activeDocument;
    var sel = doc.selection;
    
    if (sel.length === 0) {
        alert("Please select an object first!");
        return;
    }
    
    var original = sel[0];
    var variationCount = 5;
    
    for (var i = 0; i < variationCount; i++) {
        var duplicate = original.duplicate();
        
        // Random offset
        var offsetX = (Math.random() - 0.5) * 141.73; // 50mm
        var offsetY = (Math.random() - 0.5) * 141.73;
        duplicate.translate(offsetX, offsetY);
        
        // Random scale (80% to 120%)
        var scaleFactor = 0.8 + (Math.random() * 0.4);
        duplicate.resize(scaleFactor * 100, scaleFactor * 100);
        
        // Random rotation
        var rotateDegrees = (Math.random() - 0.5) * 60;
        duplicate.rotate(rotateDegrees);
        
        // Random transparency
        duplicate.opacity = 20 + (Math.random() * 40);
        
        // Slight color variation
        if (duplicate.filled && duplicate.fillColor.typename === "RGBColor") {
            var brighten = 0.8 + (Math.random() * 0.4);
            var color = duplicate.fillColor;
            color.red = Math.min(255, Math.round(color.red * brighten));
            color.green = Math.min(255, Math.round(color.green * brighten));
            color.blue = Math.min(255, Math.round(color.blue * brighten));
            duplicate.fillColor = color;
        }
    }
    
    alert("Created " + variationCount + " variations!");
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function createRGBColor(r, g, b) {
    var color = new RGBColor();
    color.red = r;
    color.green = g;
    color.blue = b;
    return color;
}

function createCMYKColor(c, m, y, k) {
    var color = new CMYKColor();
    color.cyan = c;
    color.magenta = m;
    color.yellow = y;
    color.black = k;
    return color;
}

function convertRGBtoCMYK(rgbColor) {
    // Simple RGB to CMYK conversion
    var r = rgbColor.red / 255;
    var g = rgbColor.green / 255;
    var b = rgbColor.blue / 255;
    
    var k = 1 - Math.max(r, g, b);
    var c = (1 - r - k) / (1 - k) || 0;
    var m = (1 - g - k) / (1 - k) || 0;
    var y = (1 - b - k) / (1 - k) || 0;
    
    var cmykColor = new CMYKColor();
    cmykColor.cyan = c * 100;
    cmykColor.magenta = m * 100;
    cmykColor.yellow = y * 100;
    cmykColor.black = k * 100;
    
    return cmykColor;
}

// ============================================================================
// MAIN MENU - Display all available scripts
// ============================================================================

function showMainMenu() {
    var menuItems = [
        "1. Apply Cyberpunk Neon Effect",
        "2. Create Technical Badge Layout",
        "3. Apply Random Tech Greebles",
        "4. Create Synthwave Gradient Background",
        "5. Convert to Print-Safe CMYK",
        "6. Create Scanline Effect",
        "7. Batch Export (PDF/PNG/SVG)",
        "8. Create Tech Border Frame",
        "9. Create Vertical Japanese Text",
        "10. Smart Duplicate with Variation"
    ];
    
    var choice = prompt("ONI Illustrator Macros\n\n" + menuItems.join("\n") + "\n\nEnter script number (1-10):", "1");
    
    if (!choice) return;
    
    switch(choice) {
        case "1": applyCyberpunkNeon(); break;
        case "2": createTechnicalBadge(); break;
        case "3": applyRandomGreebles(); break;
        case "4": createSynthwaveGradient(); break;
        case "5": convertToPrintSafeCMYK(); break;
        case "6": createScanlineEffect(); break;
        case "7": batchExportFormats(); break;
        case "8": createTechBorderFrame(); break;
        case "9": createVerticalJapaneseText(); break;
        case "10": smartDuplicateWithVariation(); break;
        default: alert("Invalid choice!");
    }
}

// Run main menu
showMainMenu();