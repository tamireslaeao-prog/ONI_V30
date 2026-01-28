# AutoCAD 3D ISO Part Workflow
# Executa o script SCR para criar a peça 3D com cotas
# ONIV24 - 2026-01-09

param(
    [string]$ModulePath = "$PSScriptRoot\AutoCAD_Adapter.psm1",
    [string]$ScriptPath = "$PSScriptRoot\draw_iso_part_3d.scr"
)

Write-Host "=== ONI AutoCAD 3D Workflow ===" -ForegroundColor Cyan
Write-Host "Importando modulo..." -ForegroundColor Gray

Import-Module $ModulePath -Force

# 1. Conectar ao AutoCAD
Write-Host "Conectando ao AutoCAD..." -ForegroundColor Yellow
$acad = Connect-AutoCAD

if (-not $acad) {
    Write-Error "Falha ao conectar ao AutoCAD. Verifique se esta instalado."
    exit 1
}

Write-Host "AutoCAD conectado: $($acad.Name)" -ForegroundColor Green

# 2. Criar novo documento (se necessario)
try {
    $doc = $acad.ActiveDocument
    $docName = $doc.Name
    Write-Host "Documento ativo: $docName" -ForegroundColor Green
}
catch {
    Write-Host "Criando novo documento..." -ForegroundColor Yellow
    $acad.Documents.Add() | Out-Null
    Start-Sleep -Seconds 2
}

# 3. Configurar unidades para milimetros
Write-Host "Configurando unidades (mm)..." -ForegroundColor Gray
Send-Command -ACAD $acad -Command "_UNITS 2 4 1 4 0 N"

# 4. Executar script SCR
if (Test-Path $ScriptPath) {
    Write-Host "Executando script: $ScriptPath" -ForegroundColor Cyan
    Invoke-Script -ACAD $acad -ScriptPath $ScriptPath
    Write-Host "Script enviado com sucesso!" -ForegroundColor Green
}
else {
    Write-Error "Script nao encontrado: $ScriptPath"
    exit 1
}

# 5. Aguardar conclusao
Write-Host "Aguardando execucao do AutoCAD..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 6. Zoom Extents final
Send-Command -ACAD $acad -Command "_ZOOM _E"

Write-Host ""
Write-Host "=== CONCLUIDO ===" -ForegroundColor Green
Write-Host "Peca 3D criada com sucesso!" -ForegroundColor Green
Write-Host "Dimensoes: 50x15x30mm" -ForegroundColor White
Write-Host "Recorte L: 15x10mm" -ForegroundColor White
Write-Host "Furo: O10mm" -ForegroundColor White
