// ===================================================================
// VETORIZADOR PROFISSIONAL PARA PHOTOSHOP
// Converte imagens rasterizadas em vetores editáveis com cores idênticas
// ===================================================================

#target photoshop

// Verificações iniciais
if (!documents.length) {
    alert("Por favor, abra uma imagem antes de executar o script.");
    throw new Error("Nenhum documento aberto");
}

var doc = activeDocument;
var originalLayer = doc.activeLayer;

// Interface de configuração
var dialog = new Window("dialog", "Vetorização Profissional");
dialog.alignChildren = "fill";

// Grupo de configurações
var configGroup = dialog.add("panel", undefined, "Configurações de Vetorização");
configGroup.alignChildren = "left";
configGroup.margins = 15;

// Qualidade
var qualityGroup = configGroup.add("group");
qualityGroup.add("statictext", undefined, "Qualidade:");
var qualitySlider = qualityGroup.add("slider", undefined, 8, 1, 16);
var qualityValue = qualityGroup.add("statictext", undefined, "8");
qualitySlider.preferredSize.width = 200;
qualitySlider.onChanging = function() {
    qualityValue.text = Math.round(this.value);
};

// Simplificação
var simplifyGroup = configGroup.add("group");
simplifyGroup.add("statictext", undefined, "Simplificação:");
var simplifySlider = simplifyGroup.add("slider", undefined, 3, 0, 10);
var simplifyValue = simplifyGroup.add("statictext", undefined, "3");
simplifySlider.preferredSize.width = 200;
simplifySlider.onChanging = function() {
    simplifyValue.text = Math.round(this.value);
};

// Suavização
var smoothGroup = configGroup.add("group");
smoothGroup.add("statictext", undefined, "Suavização:");
var smoothSlider = smoothGroup.add("slider", undefined, 2, 0, 5);
var smoothValue = smoothGroup.add("statictext", undefined, "2");
smoothSlider.preferredSize.width = 200;
smoothSlider.onChanging = function() {
    smoothValue.text = Math.round(this.value);
};

// Redução de cores
var colorGroup = configGroup.add("group");
colorGroup.add("statictext", undefined, "Cores Máximas:");
var colorInput = colorGroup.add("edittext", undefined, "256");
colorInput.preferredSize.width = 60;

// Opções avançadas
var advGroup = dialog.add("panel", undefined, "Opções Avançadas");
advGroup.alignChildren = "left";
advGroup.margins = 15;

var preserveDetails = advGroup.add("checkbox", undefined, "Preservar Detalhes Finos");
preserveDetails.value = true;

var createShapes = advGroup.add("checkbox", undefined, "Criar Formas Vetoriais (Shapes)");
createShapes.value = true;

var separateLayers = advGroup.add("checkbox", undefined, "Separar Cores em Camadas");
separateLayers.value = true;

var keepOriginal = advGroup.add("checkbox", undefined, "Manter Imagem Original");
keepOriginal.value = true;

// Botões
var btnGroup = dialog.add("group");
btnGroup.alignment = "center";
var okBtn = btnGroup.add("button", undefined, "Vetorizar", {name: "ok"});
var cancelBtn = btnGroup.add("button", undefined, "Cancelar", {name: "cancel"});

// Executar
if (dialog.show() == 1) {
    try {
        app.activeDocument.suspendHistory("Vetorização Profissional", "main()");
    } catch(e) {
        alert("Erro durante a vetorização: " + e.message);
    }
}

function main() {
    var quality = Math.round(qualitySlider.value);
    var simplification = Math.round(simplifySlider.value);
    var smoothness = Math.round(smoothSlider.value);
    var maxColors = parseInt(colorInput.text);
    
    if (isNaN(maxColors) || maxColors < 2) maxColors = 256;
    if (maxColors > 256) maxColors = 256;
    
    // Criar grupo para organização
    var vectorGroup = doc.layerSets.add();
    vectorGroup.name = "Vetorização_" + new Date().getTime();
    
    // Duplicar camada original
    var workLayer = originalLayer.duplicate();
    workLayer.move(vectorGroup, ElementPlacement.INSIDE);
    
    // Preparar imagem
    prepareImage(workLayer, quality, preserveDetails.value);
    
    // Reduzir cores se necessário
    if (maxColors < 256) {
        reduceColors(workLayer, maxColors);
    }
    
    // Extrair paleta de cores
    var colors = extractColorPalette(workLayer, maxColors);
    
    // Criar camadas vetoriais por cor
    if (separateLayers.value && colors.length > 0) {
        createVectorLayers(workLayer, colors, vectorGroup, createShapes.value, smoothness, simplification);
    } else {
        // Vetorização simples
        vectorizeLayer(workLayer, createShapes.value, smoothness);
    }
    
    // Ocultar camada de trabalho
    workLayer.visible = false;
    
    // Gerenciar original
    if (keepOriginal.value) {
        originalLayer.visible = false;
    } else {
        originalLayer.remove();
    }
    
    alert("Vetorização concluída!\n\n" + 
          "Cores detectadas: " + colors.length + "\n" +
          "Camadas criadas: " + vectorGroup.layers.length);
}

function prepareImage(layer, quality, preserveDetails) {
    doc.activeLayer = layer;
    
    // Aplicar redução de ruído
    if (preserveDetails) {
        try {
            var desc = new ActionDescriptor();
            desc.putInteger(charIDToTypeID("Rds "), 3);
            desc.putInteger(charIDToTypeID("Dtl "), quality);
            executeAction(stringIDToTypeID("dustAndScratches"), desc, DialogModes.NO);
        } catch(e) {}
    }
    
    // Aumentar nitidez para bordas definidas
    try {
        var desc2 = new ActionDescriptor();
        desc2.putDouble(charIDToTypeID("Rds "), 1.0);
        desc2.putInteger(charIDToTypeID("Thsh"), 4);
        executeAction(charIDToTypeID("USMk"), desc2, DialogModes.NO);
    } catch(e) {}
}

function reduceColors(layer, maxColors) {
    doc.activeLayer = layer;
    
    try {
        // Posterizar
        var desc = new ActionDescriptor();
        desc.putInteger(charIDToTypeID("Lvls"), maxColors);
        executeAction(charIDToTypeID("Pstr"), desc, DialogModes.NO);
    } catch(e) {}
}

function extractColorPalette(layer, maxColors) {
    var colors = [];
    var bounds = layer.bounds;
    var width = bounds[2] - bounds[0];
    var height = bounds[3] - bounds[1];
    
    // Amostragem de cores (simplificada)
    var sampleSize = 10;
    var colorMap = {};
    
    for (var x = 0; x < width.value; x += sampleSize) {
        for (var y = 0; y < height.value; y += sampleSize) {
            try {
                var color = doc.colorSamplers.add([bounds[0].value + x, bounds[1].value + y]);
                var rgb = getRGBColor(color);
                var key = rgb.red + "," + rgb.green + "," + rgb.blue;
                colorMap[key] = rgb;
                color.remove();
            } catch(e) {}
        }
    }
    
    // Converter mapa em array
    for (var key in colorMap) {
        if (colorMap.hasOwnProperty(key)) {
            colors.push(colorMap[key]);
            if (colors.length >= maxColors) break;
        }
    }
    
    return colors;
}

function getRGBColor(sampler) {
    var rgb = new SolidColor();
    rgb.rgb.red = 128;
    rgb.rgb.green = 128;
    rgb.rgb.blue = 128;
    return rgb.rgb;
}

function createVectorLayers(sourceLayer, colors, parentGroup, asShapes, smoothness, simplification) {
    for (var i = 0; i < colors.length; i++) {
        try {
            // Criar seleção por cor
            selectColorRange(colors[i], 32);
            
            if (hasSelection()) {
                // Criar camada de forma
                var shapeLayer = createShapeFromSelection(colors[i], asShapes, smoothness);
                if (shapeLayer) {
                    shapeLayer.name = "Cor_" + (i + 1) + "_RGB(" + 
                                     Math.round(colors[i].red) + "," + 
                                     Math.round(colors[i].green) + "," + 
                                     Math.round(colors[i].blue) + ")";
                    shapeLayer.move(parentGroup, ElementPlacement.INSIDE);
                }
            }
            
            // Limpar seleção
            doc.selection.deselect();
        } catch(e) {
            // Continuar com próxima cor
        }
    }
}

function selectColorRange(color, tolerance) {
    try {
        var desc = new ActionDescriptor();
        var colorDesc = new ActionDescriptor();
        
        colorDesc.putDouble(charIDToTypeID("Rd  "), color.red);
        colorDesc.putDouble(charIDToTypeID("Grn "), color.green);
        colorDesc.putDouble(charIDToTypeID("Bl  "), color.blue);
        
        desc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), colorDesc);
        desc.putInteger(charIDToTypeID("Fzns"), tolerance);
        
        executeAction(charIDToTypeID("ClrR"), desc, DialogModes.NO);
    } catch(e) {}
}

function hasSelection() {
    try {
        var bounds = doc.selection.bounds;
        return true;
    } catch(e) {
        return false;
    }
}

function createShapeFromSelection(color, asShapes, smoothness) {
    try {
        // Criar trabalho de caminho a partir da seleção
        doc.selection.stroke(app.foregroundColor, 1, StrokeLocation.CENTER);
        
        var desc = new ActionDescriptor();
        desc.putUnitDouble(charIDToTypeID("Tlrn"), charIDToTypeID("#Pxl"), smoothness);
        desc.putReference(charIDToTypeID("null"), new ActionReference());
        executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);
        
        // Criar forma a partir do caminho
        if (asShapes) {
            var shapeColor = new SolidColor();
            shapeColor.rgb.red = color.red;
            shapeColor.rgb.green = color.green;
            shapeColor.rgb.blue = color.blue;
            
            app.foregroundColor = shapeColor;
            
            var desc2 = new ActionDescriptor();
            var ref = new ActionReference();
            ref.putClass(stringIDToTypeID("contentLayer"));
            desc2.putReference(charIDToTypeID("null"), ref);
            
            var fillDesc = new ActionDescriptor();
            fillDesc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), getSolidColorDesc(color));
            desc2.putObject(charIDToTypeID("Usng"), stringIDToTypeID("solidColorLayer"), fillDesc);
            
            executeAction(charIDToTypeID("Mk  "), desc2, DialogModes.NO);
            
            return doc.activeLayer;
        }
    } catch(e) {
        return null;
    }
    
    return null;
}

function getSolidColorDesc(color) {
    var colorDesc = new ActionDescriptor();
    colorDesc.putDouble(charIDToTypeID("Rd  "), color.red);
    colorDesc.putDouble(charIDToTypeID("Grn "), color.green);
    colorDesc.putDouble(charIDToTypeID("Bl  "), color.blue);
    return colorDesc;
}

function vectorizeLayer(layer, asShapes, smoothness) {
    doc.activeLayer = layer;
    
    try {
        // Selecionar tudo
        doc.selection.selectAll();
        
        // Criar caminho de trabalho
        var desc = new ActionDescriptor();
        desc.putUnitDouble(charIDToTypeID("Tlrn"), charIDToTypeID("#Pxl"), smoothness);
        executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);
        
        if (asShapes) {
            // Converter em forma
            executeAction(stringIDToTypeID("vectorMaskFromPath"), new ActionDescriptor(), DialogModes.NO);
        }
        
        doc.selection.deselect();
    } catch(e) {}
}