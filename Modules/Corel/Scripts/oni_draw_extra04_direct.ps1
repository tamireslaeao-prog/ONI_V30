# ONI V23 - Desenho Tecnico Extra04 (Direct COM)
# Fallback Protocol para quando VBA Injection esta bloqueado.

$ErrorActionPreference = "Stop"

function Write-ONILog {
    param([string]$Msg, [string]$Color = "Cyan")
    Write-Host "[ONI] $Msg" -ForegroundColor $Color
}

try {
    Write-ONILog "Iniciando Protocolo Direct-Draw..."
    
    # 1. Connect to Corel
    Write-ONILog "Conectando ao CorelDRAW..."
    try {
        $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
    }
    catch {
        Write-ONILog "CorelDRAW nao encontrado. Tentando abrir..." "Yellow"
        $corel = New-Object -ComObject CorelDRAW.Application
        $corel.Visible = $true
        Start-Sleep -Seconds 10
    }
    
    # 2. Setup Doc
    $doc = $corel.ActiveDocument
    if ($null -eq $doc) { $doc = $corel.CreateDocument() }
    
    # Configurar Unidades (cdrCentimeter = 6)
    $doc.Unit = 6 
    $doc.DrawingOriginX = 0
    $doc.DrawingOriginY = 0
    
    $lr = $doc.ActiveLayer
    
    # =========================================================
    # 3. Desenho (Logica Traduzida do VBA)
    # =========================================================
    
    # Painel 1 (Base): 9x12
    Write-ONILog "Desenhando Paineis..."
    $p1 = $lr.CreateRectangle(0, 0, 9, 12)
    
    # Painel 2 (Meio): 9x9 (y=12 a 21)
    $p2 = $lr.CreateRectangle(0, 12, 9, 21)
    
    # Painel 3 (Topo): 9x12 (y=21 a 33)
    $p3 = $lr.CreateRectangle(0, 21, 9, 33)
    
    # Painel 4 (Cabeca): 9x8.5 (y=33 a 41.5)
    $p4 = $lr.CreateRectangle(0, 33, 9, 41.5)
    
    # Arredondar Canto (CornerType = 2 (Round), CornerUpperRight = 40)
    # Em COM Powershell, propriedades sao acessadas diretamente
    $p4.Rectangle.CornerType = 2
    # Tentar definir corner relativo (0-100)
    $p4.Rectangle.CornerUpperRight = 50 
    
    # Soldar corpo principal
    Write-ONILog "Soldando Corpo..."
    $sMain = $p1.Weld($p2)
    $sMain = $sMain.Weld($p3)
    $sMain = $sMain.Weld($p4)
    
    # Aba Lateral (Curve Segment)
    Write-ONILog "Criando Aba Lateral..."
    # Pontos: (0, 12), (0, 21), (-12, 20.5), (-12, 12.5)
    # Usar CreateLineSegment para iniciar
    $sFlap = $lr.CreateLineSegment(0, 12, 0, 21)
    
    # No PowerShell COM, arrays e indexadores podem ser tricky.
    # Acessar Nodes
    $nodes = $sFlap.Curve.Nodes
    $lastNode = $nodes.Item($nodes.Count)
    $lastNode.AppendSegmentLine(-12, 20.5)
    
    $nodes = $sFlap.Curve.Nodes
    $lastNode = $nodes.Item($nodes.Count)
    $lastNode.AppendSegmentLine(-12, 12.5)
    
    $nodes = $sFlap.Curve.Nodes
    $lastNode = $nodes.Item($nodes.Count)
    $lastNode.AppendSegmentLine(0, 12)
    
    $sFlap.Curve.Closed = $true
    
    # Soldar Aba
    $sFinal = $sMain.Weld($sFlap)
    
    # Furos 
    Write-ONILog "Cortando Furos..."
    # Furo 1: (8, 1) raio 0.25 (diam 0.5)
    # CreateEllipse2(CenterX, CenterY, Radius1, Radius2, StartAngle, EndAngle, Pie)
    # Passar apenas obrigatorios se possivel, ou todos.
    # Radius2 default = Radius1.
    $sHole1 = $lr.CreateEllipse2(8, 1, 0.25)
    $sHole2 = $lr.CreateEllipse2(8, 38, 0.25)
    
    # Trim (Cortar)
    # Source.Trim(Target, LeaveSource, LeaveTarget)
    # Queremos usar o furo (Source) para cortar o corpo (Target)
    # E deletar o furo depois (LeaveSource=False)
    $result1 = $sHole1.Trim($sFinal, $false, $false) 
    # Trim retorna o novo shape resultante (objeto cortado)
    # Mas em Corel Automation as vezes altera in-place ou retorna void dependendo da versao.
    # Se Trim retornar void, sFinal continua valido? Sim.
    # Vamos verificar se result1 eh nulo
    if ($result1) { $sFinal = $result1 }
    
    # O objeto sFinal mudou ID provavelmente.
    # Furo 2 no novo sFinal
    $result2 = $sHole2.Trim($sFinal, $false, $false)
    if ($result2) { $sFinal = $result2 }
    
    # Estilo
    $sFinal.Fill.UniformColor.CMYKAssign(0, 0, 0, 10)
    $sFinal.Outline.SetProperties(0.05) # Hairline
    
    # Zoom
    $doc.ActiveWindow.ActiveView.ZoomToShape($sFinal)
    
    # Cotas (LinearDimension)
    Write-ONILog "Adicionando Cotas..."
    # CreateLinearDimension(Type, x1, y1, x2, y2, TextCentered, TextX, TextY)
    # cdrDimensionVertical = 1, cdrDimensionHorizontal = 0
    $lr.CreateLinearDimension(1, 10, 0, 10, 41.5, $true, 11, 20.75)
    $lr.CreateLinearDimension(0, 0, 12, -12, 12, $true, -6, 10)

    Write-Host "===================================================" -ForegroundColor Green
    Write-Host " Desenho Direto Concluido!" -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Green
    
    # Release Cleanly
    if ($corel) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($corel) | Out-Null }
    
}
catch {
    Write-Error "FALHA DIRECT COM: $_"
    exit 1
}
