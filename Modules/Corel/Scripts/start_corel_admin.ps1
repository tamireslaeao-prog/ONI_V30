
# Script para Iniciar CorelDRAW com Elevação e Garantir COM pronto
# Salvo como: start_corel_admin.ps1

$corelPath = "c:\Program Files\Corel\CorelDRAW Graphics Suite\26\Programs64\CorelDRW.exe"

Write-Host "Tentando iniciar CorelDRAW com Privilégios Elevados..."

if (Test-Path $corelPath) {
    # Inicia o processo com Verb RunAs (Admin)
    Start-Process -FilePath $corelPath -Verb RunAs
    
    Write-Host "Processo iniciado. Aguardando carregamento (20s)..."
    Start-Sleep -Seconds 20
    
    # Verifica se apareceu
    $proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" }
    if ($proc) {
        Write-Host "SUCESSO: CorelDRAW detectado (PID: $($proc.Id))"
    }
    else {
        Write-Host "ERRO: Processo não encontrado após espera."
    }
}
else {
    Write-Host "ERRO: Executável não encontrado em: $corelPath"
}
