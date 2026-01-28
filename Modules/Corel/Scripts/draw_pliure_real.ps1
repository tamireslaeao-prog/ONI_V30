# ONIV24 - Script de Cotagem Molde Pliure
# Adiciona dimensões lineares e de raio conforme imagem técnica

function Add-Dimensions-Pliure {
    try {
        $acad = [System.Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
        $doc = $acad.ActiveDocument
    } catch {
        Write-Error "AutoCAD não encontrado."
        return
    }

    function Send-Cmd($cmd) {
        $doc.SendCommand("$cmd`n")
    }

    Write-Host "Iniciando Cotagem Técnica..." -ForegroundColor Cyan

    # Configurar Estilo de Cota (DimStyle) para visualização clara
    Send-Cmd "-DIMSTYLE S ONI_V22 "
    Send-Cmd "DIMSCALE 1"
    Send-Cmd "DIMASZ 2" # Tamanho da seta
    Send-Cmd "DIMTXT 3" # Tamanho do texto
    
    # 1. Cotas Horizontais (Larguras)
    # Base (90mm)
    Send-Cmd "_DIMLINEAR -90,0 0,0 -90,-20 "
    # Corpo Central (95mm)
    Send-Cmd "_DIMLINEAR -95,120 0,120 -95,140 "
    # Flap Lateral (95mm)
    Send-Cmd "_DIMLINEAR -190,125 -95,125 -190,145 "
    
    # 2. Cotas Verticais (Alturas)
    # Altura Total (415mm)
    Send-Cmd "_DIMLINEAR 0,0 0,415 40,207 "
    # Segmento 12cm
    Send-Cmd "_DIMLINEAR -10,0 -10,120 -30,60 "
    # Segmento 9cm (corpo central)
    Send-Cmd "_DIMLINEAR -10,120 -10,210 -30,165 "
    # Segmento 12cm superior
    Send-Cmd "_DIMLINEAR -10,210 -10,330 -30,270 "
    # Aba Topo 8.5cm
    Send-Cmd "_DIMLINEAR -10,330 -10,415 -30,372 "

    # 3. Cota de Raio (Fillet 5cm)
    Send-Cmd "_DIMRADIUS -88,412 -120,450 "

    # 4. Cota da largura da aba lateral (8cm na ponta)
    Send-Cmd "_DIMLINEAR -190,125 -190,205 -210,165 "

    Send-Cmd "_ZOOM E"
    
    Write-Host "✅ [V22] Cotagem concluída com sucesso!" -ForegroundColor Green
}

Add-Dimensions-Pliure
