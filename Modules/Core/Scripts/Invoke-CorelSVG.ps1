# =============================================================================
# ONIV24 - INVOKE-CORELSVG (Engine VIP)
# =============================================================================
# Autor: ONI (Antigravity)
# Data: 09/01/2026
# Descricao: Injeta geometria vetorial no CorelDRAW burlando bloqueios de macro.
# =============================================================================

param(
    [Parameter(Mandatory = $false)]
    [string]$SvgContent,
    
    [Parameter(Mandatory = $false)]
    [string]$SvgPath,
    
    [string]$FileName = "oni_injection",
    [switch]$AutoLaunch = $true
)

$ErrorActionPreference = "Stop"

function Write-ONILog {
    param([string]$Msg, [string]$Color = "Cyan")
    Write-Host "[VIP] $Msg" -ForegroundColor $Color
}

try {
    Write-ONILog "Iniciando Motor de Injecao Vetorial..."
    
    # 0. Resolver Input (Content vs Path)
    if ([string]::IsNullOrWhiteSpace($SvgContent) -and -not [string]::IsNullOrWhiteSpace($SvgPath)) {
        if (Test-Path $SvgPath) {
            Write-ONILog "Lendo payload de arquivo: $SvgPath"
            $SvgContent = Get-Content -Path $SvgPath -Raw -Encoding UTF8
        }
        else {
            throw "Arquivo SVG nao encontrado: $SvgPath"
        }
    }
    
    if ([string]::IsNullOrWhiteSpace($SvgContent)) {
        throw "Nenhum conteudo SVG fornecido (Use -SvgContent ou -SvgPath)"
    }
    
    # 1. Sanitizar Content
    if (-not $SvgContent.Contains("<?xml")) {
        # Adicionar Header Padrao se faltar
        $header = '<?xml version="1.0" encoding="UTF-8"?>' + "`n" + 
        '<svg xmlns="http://www.w3.org/2000/svg">'
        # Nota: Idealmente o caller deve fornecer SVG completo. Apenas aviso.
        Write-Warning "SVG parece incompleto. Injetando raw content."
    }

    # 2. Criar Payload
    $tempDir = "$env:TEMP\ONI_VIP_Buffer"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $fullPath = Join-Path $tempDir "${FileName}_${timestamp}.svg"
    
    $SvgContent | Set-Content -Path $fullPath -Encoding UTF8
    Write-ONILog "Payload Criado: $fullPath" "Green"
    
    # 3. Executar Payload (Launch)
    if ($AutoLaunch) {
        Write-ONILog "Disparando CorelDRAW..."
        
        # Tentar detectar executavel
        $corelPaths = @(
            "C:\Program Files\Corel\CorelDRAW Graphics Suite\26\Programs64\CorelDRW.exe",
            "C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Programs64\CorelDRW.exe",
            "C:\Program Files\Corel\CorelDRAW Graphics Suite 2024\Programs64\CorelDRW.exe"
        )
        
        $exe = $null
        foreach ($p in $corelPaths) {
            if (Test-Path $p) { $exe = $p; break }
        }
        
        if ($exe) {
            Start-Process -FilePath $exe -ArgumentList "`"$fullPath`""
            Write-ONILog "Comando enviado para: $exe"
        }
        else {
            Write-Warning "Executavel do Corel nao encontrado em locais padrao. Usando Default Handler."
            Start-Process $fullPath
        }
    }
    
    return $fullPath

}
catch {
    Write-Error "[VIP FATAL] $_"
    exit 1
}
