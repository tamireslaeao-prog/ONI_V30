# ================================================================
# ONI - Script de Desenho: Molde Caixa/Embalagem
# ================================================================
# Objetivo: Desenhar molde técnico idêntico à imagem de referência
# Unidades: Centímetros (cm)
# ================================================================

param(
    [switch]$Debug = $false
)

Write-Host "`n[ONI] =====================================" -ForegroundColor Cyan
Write-Host "[ONI] INICIANDO DESENHO DO MOLDE" -ForegroundColor Cyan
Write-Host "[ONI] =====================================" -ForegroundColor Cyan

# ----------------------------------------------------------------
# 1. CONECTAR AO CORELDRAW VIA COM
# ----------------------------------------------------------------
Write-Host "`n[ONI] Conectando ao CorelDRAW..." -ForegroundColor Yellow

try {
    $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
    Write-Host "[ONI] Conexão COM estabelecida!" -ForegroundColor Green
}
catch {
    Write-Host "[ONI] ERRO: CorelDRAW não está aberto ou COM falhou." -ForegroundColor Red
    Write-Host "[ONI] Erro: $_" -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------
# 2. CONFIGURAR DOCUMENTO
# ----------------------------------------------------------------
$doc = $corel.ActiveDocument
if (-not $doc) {
    Write-Host "[ONI] Criando novo documento..." -ForegroundColor Yellow
    $doc = $corel.CreateDocument()
}

$page = $doc.ActivePage
$layer = $page.ActiveLayer

# Otimização para desenho rápido
$corel.Optimization = $true

Write-Host "[ONI] Documento: $($doc.Name)" -ForegroundColor Gray
Write-Host "[ONI] Unidade: Centímetros" -ForegroundColor Gray

# ----------------------------------------------------------------
# 3. DEFINIR MEDIDAS DO MOLDE (em mm - CorelDRAW usa mm internamente)
# ----------------------------------------------------------------
# Converter cm para mm (multiplicar por 10)
$mm = 10

# Medidas principais (já em mm)
$corpoLargura = 9 * $mm      # 90mm = 9cm
$corpoAltura = 41.5 * $mm    # 415mm = 41.5cm

$topoAltura = 8.5 * $mm      # 85mm = 8.5cm
$topoMargemEsq = 0.5 * $mm   # 5mm = 0.5cm
$topoCurva = 5 * $mm         # 50mm = 5cm (raio do canto arredondado)

$abaEsqLargura = 8 * $mm     # 80mm = 8cm
$abaHorizLargura = 9.5 * $mm # 95mm = 9.5cm

$secaoVertical1 = 12 * $mm   # 120mm = 12cm
$secaoVertical2 = 9 * $mm    # 90mm = 9cm
$secaoVertical3 = 12 * $mm   # 120mm = 12cm

$abaInfLargura = 9 * $mm     # 90mm = 9cm
$abaInfAltura = 12 * $mm     # 120mm = 12cm

$circuloRaio = 3             # 3mm ~ 0.3cm

# Posição inicial (canto inferior esquerdo do corpo principal)
$origemX = 150  # mm do canto esquerdo da página
$origemY = 80   # mm do fundo da página

Write-Host "`n[ONI] Medidas configuradas:" -ForegroundColor Gray
Write-Host "  - Corpo: ${corpoLargura}mm x ${corpoAltura}mm" -ForegroundColor Gray
Write-Host "  - Origem: (${origemX}mm, ${origemY}mm)" -ForegroundColor Gray

# ----------------------------------------------------------------
# 4. DESENHAR FORMAS
# ----------------------------------------------------------------
Write-Host "`n[ONI] Desenhando formas..." -ForegroundColor Yellow

$shapes = @()

# 4.1 CORPO PRINCIPAL (retângulo vertical)
Write-Host "  [1/8] Corpo principal..." -ForegroundColor Cyan
$corpo = $layer.CreateRectangle(
    [double]$origemX,                           # X1 (esquerda)
    [double]($origemY + $corpoAltura),          # Y1 (topo) - CorelDRAW Y cresce para cima
    [double]($origemX + $corpoLargura),         # X2 (direita)
    [double]$origemY                            # Y2 (fundo)
)
$shapes += $corpo
Write-Host "    OK: Corpo principal criado" -ForegroundColor Green

# 4.2 SEÇÃO DO TOPO (com canto arredondado superior direito)
Write-Host "  [2/8] Topo com canto arredondado..." -ForegroundColor Cyan
$topoY1 = $origemY + $corpoAltura
$topoY2 = $topoY1 + $topoAltura + $topoCurva

# Criar retângulo do topo com canto arredondado
$topo = $layer.CreateRectangleRounded(
    [double]($origemX - $topoMargemEsq),        # X1 (com margem esquerda)
    [double]$topoY2,                            # Y1 (topo)
    [double]($origemX + $corpoLargura),         # X2 (direita)
    [double]$topoY1,                            # Y2 (fundo)
    [double]0,                                  # Canto inferior esquerdo
    [double]0,                                  # Canto inferior direito
    [double]0,                                  # Canto superior esquerdo
    [double]$topoCurva                          # Canto superior direito (arredondado)
)
$shapes += $topo
Write-Host "    OK: Topo com arredondamento criado" -ForegroundColor Green

# 4.3 ABA ESQUERDA
Write-Host "  [3/8] Aba esquerda..." -ForegroundColor Cyan
$abaEsqY = $origemY + $secaoVertical3 + $secaoVertical2  # Posição vertical da aba
$abaEsq = $layer.CreateRectangle(
    [double]($origemX - $abaEsqLargura),        # X1 (esquerda)
    [double]($abaEsqY + $secaoVertical2),       # Y1 (topo)
    [double]$origemX,                            # X2 (direita = corpo)
    [double]$abaEsqY                             # Y2 (fundo)
)
$shapes += $abaEsq
Write-Host "    OK: Aba esquerda criada" -ForegroundColor Green

# 4.4 ABA HORIZONTAL SUPERIOR
Write-Host "  [4/8] Aba horizontal superior..." -ForegroundColor Cyan
$abaHorizSupY = $origemY + $secaoVertical3 + $secaoVertical2 + $secaoVertical1
$abaHorizSup = $layer.CreateRectangle(
    [double]($origemX + $corpoLargura),         # X1 (direita do corpo)
    [double]($abaHorizSupY),                    # Y1 (topo)
    [double]($origemX + $corpoLargura + $abaHorizLargura), # X2 (extrema direita)
    [double]($abaHorizSupY - $secaoVertical1)   # Y2 (fundo)
)
$shapes += $abaHorizSup
Write-Host "    OK: Aba horizontal superior criada" -ForegroundColor Green

# 4.5 ABA HORIZONTAL INFERIOR
Write-Host "  [5/8] Aba horizontal inferior..." -ForegroundColor Cyan
$abaHorizInfY = $origemY + $secaoVertical3
$abaHorizInf = $layer.CreateRectangle(
    [double]($origemX + $corpoLargura),         # X1 (direita do corpo)
    [double]($abaHorizInfY + $secaoVertical2),  # Y1 (topo)
    [double]($origemX + $corpoLargura + $abaHorizLargura), # X2 (extrema direita)
    [double]$abaHorizInfY                       # Y2 (fundo)
)
$shapes += $abaHorizInf
Write-Host "    OK: Aba horizontal inferior criada" -ForegroundColor Green

# 4.6 ABA INFERIOR
Write-Host "  [6/8] Aba inferior..." -ForegroundColor Cyan
$abaInf = $layer.CreateRectangle(
    [double]$origemX,                           # X1 (esquerda)
    [double]$origemY,                           # Y1 (topo = fundo do corpo)
    [double]($origemX + $abaInfLargura),        # X2 (direita)
    [double]($origemY - $abaInfAltura)          # Y2 (fundo)
)
$shapes += $abaInf
Write-Host "    OK: Aba inferior criada" -ForegroundColor Green

# 4.7 CÍRCULO SUPERIOR DIREITO
Write-Host "  [7/8] Círculo superior..." -ForegroundColor Cyan
$circSupX = $origemX + $corpoLargura + $abaHorizLargura - 5
$circSupY = $topoY2 - 5
$circSup = $layer.CreateEllipse(
    [double]($circSupX - $circuloRaio),
    [double]($circSupY + $circuloRaio),
    [double]($circSupX + $circuloRaio),
    [double]($circSupY - $circuloRaio)
)
$shapes += $circSup
Write-Host "    OK: Círculo superior criado" -ForegroundColor Green

# 4.8 CÍRCULO INFERIOR DIREITO
Write-Host "  [8/8] Círculo inferior..." -ForegroundColor Cyan
$circInfX = $origemX + $abaInfLargura - 5
$circInfY = $origemY - $abaInfAltura + 5
$circInf = $layer.CreateEllipse(
    [double]($circInfX - $circuloRaio),
    [double]($circInfY + $circuloRaio),
    [double]($circInfX + $circuloRaio),
    [double]($circInfY - $circuloRaio)
)
$shapes += $circInf
Write-Host "    OK: Círculo inferior criado" -ForegroundColor Green

# ----------------------------------------------------------------
# 5. LINHA DE DOBRA (PLIURE)
# ----------------------------------------------------------------
Write-Host "`n[ONI] Adicionando linha de dobra (Pliure)..." -ForegroundColor Yellow

$pliureX = $origemX + $corpoLargura
$pliureLine = $layer.CreateLineSegment(
    [double]$pliureX,
    [double]($origemY - $abaInfAltura),
    [double]$pliureX,
    [double]$topoY2
)
# Aplicar estilo pontilhado
try {
    $pliureLine.Outline.Style = 2  # Dashed
    $pliureLine.Outline.Width = 0.5
}
catch {
    Write-Host "    AVISO: Não foi possível aplicar estilo pontilhado" -ForegroundColor Yellow
}
$shapes += $pliureLine
Write-Host "    OK: Linha de dobra criada" -ForegroundColor Green

# ----------------------------------------------------------------
# 6. FINALIZAR
# ----------------------------------------------------------------
$corel.Optimization = $false
$corel.Refresh

Write-Host "`n[ONI] =====================================" -ForegroundColor Green
Write-Host "[ONI] DESENHO CONCLUÍDO!" -ForegroundColor Green
Write-Host "[ONI] Total de formas: $($shapes.Count)" -ForegroundColor Green
Write-Host "[ONI] =====================================" -ForegroundColor Green
