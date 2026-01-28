// ===================================================================
// VETORIZADOR PROFISSIONAL PARA PHOTOSHOP
// Converte imagens em vetores com preenchimentos, pontos âncora e paths editáveis
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

// Tolerância de cor
var toleranceGroup = configGroup.add("group");
toleranceGroup.add("statictext", undefined, "Tolerância de Cor:");
var toleranceSlider = toleranceGroup.add("slider", undefined, 32, 0, 100);
var toleranceValue = toleranceGroup.add("statictext", undefined, "32");
toleranceSlider.preferredSize.width = 200;
toleranceSlider.onChanging = function() {
    toleranceValue.text = Math.round(this.value);
};

// Suavização de paths
var smoothGroup = configGroup.add("group");
smoothGroup.add("statictext", undefined, "Suavização de Paths:");
var smoothSlider = smoothGroup.add("slider", undefined, 2, 0.5, 10);
var smoothValue = smoothGroup.add("statictext", undefined, "2.0");
smoothSlider.preferredSize.width = 200;
smoothSlider.onChanging = function() {
    smoothValue.text = this.value.toFixed(1);
};

// Cores máximas
var colorGroup = configGroup.add("group");
colorGroup.add("statictext", undefined, "Cores Máximas:");
var colorInput = colorGroup.add("edittext", undefined, "32");
colorInput.preferredSize.width = 60;

// Opções
var optGroup = dialog.add("panel", undefined, "Opções");
optGroup.alignChildren = "left";
optGroup.margins = 15;

var keepOriginal = optGroup.add("checkbox", undefined, "Manter Imagem Original");
keepOriginal.value = true;

var simplifyImage = optGroup.add("checkbox", undefined, "Simplificar Imagem (Posterizar)");
simplifyImage.value = true;

// Botões
var btnGroup = dialog.add("group");
btnGroup.alignment = "center";
var okBtn = btnGroup.add("button", undefined, "Vetorizar", {name: "ok"});
var cancelBtn = btnGroup.add("button", undefined, "Cancelar", {name: "cancel"});

// Executar
if (dialog.show() == 1) {
    try {
        app.activeDocument.suspendHistory("Vetorização Profissional", "vectorize()");
    } catch(e) {
        alert("Erro durante a vetorização: " + e.message + "\nLinha: " + e.line);
    }
}

function vectorize() {
    var tolerance = Math.round(toleranceSlider.value);
    var smoothness = parseFloat(smoothValue.text);
    var maxColors = parseInt(colorInput.text);
    
    if (isNaN(maxColors) || maxColors < 2) maxColors = 32;
    if (maxColors > 256) maxColors = 256;
    
    // Criar grupo para organização
    var vectorGroup = doc.layerSets.add();
    vectorGroup.name = "Vetorização_" + getTimestamp();
    
    // Duplicar e preparar camada
    var workLayer = originalLayer.duplicate();
    workLayer.name = "Trabalho_Temp";
    
    // Simplificar cores se solicitado
    if (simplifyImage.value) {
        doc.activeLayer = workLayer;
        posterizeImage(maxColors);
    }
    
    // Achatar se necessário
    if (workLayer.typename != "ArtLayer") {
        workLayer = flattenLayer(workLayer);
    }
    
    // Extrair cores únicas
    var colorList = extractUniqueColors(workLayer, maxColors);
    
    if (colorList.length === 0) {
        alert("Nenhuma cor detectada na imagem!");
        workLayer.remove();
        vectorGroup.remove();
        return;
    }
    
    // Processar cada cor
    for (var i = 0; i < colorList.length; i++) {
        createVectorShapeFromColor(workLayer, colorList[i], vectorGroup, tolerance, smoothness, i + 1);
    }
    
    // Limpar
    workLayer.remove();
    
    // Gerenciar original
    if (keepOriginal.value) {
        originalLayer.visible = false;
    } else {
        originalLayer.remove();
    }
    
    alert("Vetorização concluída!\n\n" + 
          "Cores vetorizadas: " + colorList.length + "\n" +
          "Shapes criadas: " + vectorGroup.artLayers.length + "\n\n" +
          "Cada shape possui:\n" +
          "- Preenchimento de cor sólida\n" +
          "- Pontos âncora editáveis\n" +
          "- Paths vetoriais completos");
}

function posterizeImage(levels) {
    try {
        var desc = new ActionDescriptor();
        desc.putInteger(charIDToTypeID("Lvls"), levels);
        executeAction(charIDToTypeID("Pstr"), desc, DialogModes.NO);
    } catch(e) {}
}

function flattenLayer(layer) {
    doc.activeLayer = layer;
    var newLayer = layer.duplicate();
    layer.remove();
    return newLayer;
}

function extractUniqueColors(layer, maxColors) {
    doc.activeLayer = layer;
    var colors = [];
    var colorMap = {};
    
    // Rasterizar se necessário
    if (layer.kind != LayerKind.NORMAL) {
        layer.rasterize(RasterizeType.ENTIRELAYER);
    }
    
    var bounds = layer.bounds;
    var left = parseInt(bounds[0].value);
    var top = parseInt(bounds[1].value);
    var right = parseInt(bounds[2].value);
    var bottom = parseInt(bounds[3].value);
    var width = right - left;
    var height = bottom - top;
    
    // Amostragem inteligente
    var step = Math.max(1, Math.floor(Math.max(width, height) / 100));
    
    for (var x = left; x < right; x += step) {
        for (var y = top; y < bottom; y += step) {
            try {
                var sampleColor = sampleColorAtPoint(x, y);
                if (sampleColor) {
                    var colorKey = rgbToKey(sampleColor);
                    if (!colorMap[colorKey]) {
                        colorMap[colorKey] = sampleColor;
                        colors.push(sampleColor);
                        if (colors.length >= maxColors) {
                            return colors;
                        }
                    }
                }
            } catch(e) {}
        }
    }
    
    return colors;
}

function sampleColorAtPoint(x, y) {
    try {
        var samplerRef = doc.colorSamplers.add([x, y]);
        var foreColor = app.foregroundColor;
        
        // Selecionar um pixel
        var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putProperty(charIDToTypeID("Clr "), charIDToTypeID("frgC"));
        desc.putReference(charIDToTypeID("null"), ref);
        
        var pointDesc = new ActionDescriptor();
        pointDesc.putUnitDouble(charIDToTypeID("Hrzn"), charIDToTypeID("#Pxl"), x);
        pointDesc.putUnitDouble(charIDToTypeID("Vrtc"), charIDToTypeID("#Pxl"), y);
        desc.putObject(charIDToTypeID("T   "), charIDToTypeID("Pnt "), pointDesc);
        
        executeAction(charIDToTypeID("setd"), desc, DialogModes.NO);
        
        var rgb = new SolidColor();
        rgb.rgb.red = app.foregroundColor.rgb.red;
        rgb.rgb.green = app.foregroundColor.rgb.green;
        rgb.rgb.blue = app.foregroundColor.rgb.blue;
        
        samplerRef.remove();
        
        return rgb;
    } catch(e) {
        return null;
    }
}

function rgbToKey(color) {
    return Math.round(color.rgb.red) + "," + 
           Math.round(color.rgb.green) + "," + 
           Math.round(color.rgb.blue);
}

function createVectorShapeFromColor(sourceLayer, color, parentGroup, tolerance, smoothness, index) {
    doc.activeLayer = sourceLayer;
    
    try {
        // Selecionar pixels da cor específica
        selectByColor(color, tolerance);
        
        // Verificar se há seleção
        var hasSel = false;
        try {
            var selBounds = doc.selection.bounds;
            hasSel = true;
        } catch(e) {
            return;
        }
        
        if (!hasSel) return;
        
        // Criar Work Path a partir da seleção
        makeWorkPath(smoothness);
        
        // Criar Shape Layer com preenchimento
        var shapeName = "Shape_" + index + "_RGB(" + 
                        Math.round(color.rgb.red) + "," + 
                        Math.round(color.rgb.green) + "," + 
                        Math.round(color.rgb.blue) + ")";
        
        createShapeLayerFromPath(color, shapeName);
        
        // Mover para o grupo
        doc.activeLayer.move(parentGroup, ElementPlacement.INSIDE);
        
        // Limpar seleção
        doc.selection.deselect();
        
        // Deletar work path
        try {
            var pathRef = new ActionReference();
            pathRef.putEnumerated(charIDToTypeID("Path"), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
            var deleteDesc = new ActionDescriptor();
            deleteDesc.putReference(charIDToTypeID("null"), pathRef);
            executeAction(charIDToTypeID("Dlt "), deleteDesc, DialogModes.NO);
        } catch(e) {}
        
    } catch(e) {
        // Limpar seleção em caso de erro
        try { doc.selection.deselect(); } catch(err) {}
    }
}

function selectByColor(color, tolerance) {
    // Criar cor de amostra
    var desc1 = new ActionDescriptor();
    var ref1 = new ActionReference();
    ref1.putProperty(charIDToTypeID("Clr "), charIDToTypeID("frgC"));
    desc1.putReference(charIDToTypeID("null"), ref1);
    
    var colorDesc = new ActionDescriptor();
    colorDesc.putDouble(charIDToTypeID("Rd  "), color.rgb.red);
    colorDesc.putDouble(charIDToTypeID("Grn "), color.rgb.green);
    colorDesc.putDouble(charIDToTypeID("Bl  "), color.rgb.blue);
    desc1.putObject(charIDToTypeID("T   "), charIDToTypeID("RGBC"), colorDesc);
    
    executeAction(charIDToTypeID("setd"), desc1, DialogModes.NO);
    
    // Selecionar por intervalo de cores
    var desc2 = new ActionDescriptor();
    desc2.putInteger(charIDToTypeID("Fzns"), tolerance);
    desc2.putBoolean(charIDToTypeID("Invr"), false);
    executeAction(charIDToTypeID("ClrR"), desc2, DialogModes.NO);
}

function makeWorkPath(tolerance) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putClass(charIDToTypeID("Path"));
    desc.putReference(charIDToTypeID("null"), ref);
    
    var selRef = new ActionReference();
    selRef.putProperty(charIDToTypeID("csel"), charIDToTypeID("fsel"));
    desc.putReference(charIDToTypeID("From"), selRef);
    
    desc.putUnitDouble(charIDToTypeID("Tlrn"), charIDToTypeID("#Pxl"), tolerance);
    executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);
}

function createShapeLayerFromPath(color, layerName) {
    // Criar Shape Layer com preenchimento
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putClass(stringIDToTypeID("contentLayer"));
    desc.putReference(charIDToTypeID("null"), ref);
    
    // Configurar preenchimento de cor
    var fillDesc = new ActionDescriptor();
    var colorDesc = new ActionDescriptor();
    colorDesc.putDouble(charIDToTypeID("Rd  "), color.rgb.red);
    colorDesc.putDouble(charIDToTypeID("Grn "), color.rgb.green);
    colorDesc.putDouble(charIDToTypeID("Bl  "), color.rgb.blue);
    fillDesc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), colorDesc);
    
    desc.putObject(charIDToTypeID("Usng"), stringIDToTypeID("solidColorLayer"), fillDesc);
    
    // Usar work path
    var pathRef = new ActionReference();
    pathRef.putEnumerated(charIDToTypeID("Path"), charIDToTypeID("Path"), stringIDToTypeID("workPath"));
    desc.putReference(stringIDToTypeID("path"), pathRef);
    
    executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);
    
    // Renomear
    doc.activeLayer.name = layerName;
}

function getTimestamp() {
    var now = new Date();
    return now.getFullYear() + 
           pad(now.getMonth() + 1) + 
           pad(now.getDate()) + "_" + 
           pad(now.getHours()) + 
           pad(now.getMinutes()) + 
           pad(now.getSeconds());
}

function pad(num) {
    return (num < 10 ? "0" : "") + num;
}