# ONI V23 - Desenho Tecnico Extra04 (Nexus Protocol)
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path $MyInvocation.MyCommand.Path
$invokeVbaPath = Join-Path $scriptDir "core\Invoke-CorelVBA.ps1"
$basPath = Join-Path $scriptDir "core\Draw_Extra04.bas"

if (-not (Test-Path $invokeVbaPath)) { throw "Motor Nexus (Invoke-CorelVBA) nao encontrado." }
if (-not (Test-Path $basPath)) { throw "Logica VBA (Draw_Extra04.bas) nao encontrada." }

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " ONI V23 - Desenhando Molde Extra04 (1:1)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Prepare Wrapper
$bootloader = @"
Sub Bootloader()
    ONI_DrawExtra04
End Sub
"@

$basContent = Get-Content $basPath -Raw
$payload = $basContent + "`n`n" + $bootloader

try {
    & $invokeVbaPath -VbaCode $payload -EntryPoint "Bootloader" -WaitForCorel 30
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Desenho Concluido com Sucesso!" -ForegroundColor Green
    } else {
        Write-Error "Falha na execucao do VBA (Exit Code $LASTEXITCODE)"
    }
}
catch {
    Write-Error "FATAL: $_"
}
