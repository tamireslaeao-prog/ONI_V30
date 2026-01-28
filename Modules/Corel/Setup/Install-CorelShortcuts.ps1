<#
.SYNOPSIS
    ONI V23 - Instalador Automático de Shortcuts para CorelDRAW
    Agnóstico à versão, auto-detecta e instala sem interação.

.DESCRIPTION
    1. Detecta automaticamente QUALQUER versão do CorelDRAW instalada
    2. Faz backup do workspace atual
    3. Injeta shortcuts diretamente no workspace ativo
    4. Aplica imediatamente (sem necessidade de importar)

.EXAMPLE
    .\Install-CorelShortcuts.ps1
    .\Install-CorelShortcuts.ps1 -Restore  # Para restaurar backup
#>

param(
    [switch]$Restore,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURAÇÃO
# ============================================================
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$BaseDir = (Get-Item $ScriptDir).Parent.FullName
$ConfigPath = Join-Path $BaseDir "Config\corel_shortcuts.json"
$BackupDir = Join-Path $BaseDir "Backups"
$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) "ONI_CorelShortcuts_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# ============================================================
# FUNÇÕES
# ============================================================

function Write-Log {
    param([string]$Msg, [string]$Color = "White", [switch]$NoNewline)
    $timestamp = Get-Date -Format "HH:mm:ss"
    if ($NoNewline) {
        Write-Host "[$timestamp] $Msg" -ForegroundColor $Color -NoNewline
    }
    else {
        Write-Host "[$timestamp] $Msg" -ForegroundColor $Color
    }
}

function Get-CorelVersions {
    <#
    .SYNOPSIS
        Detecta TODAS as versões do CorelDRAW instaladas
    #>
    $versions = @()
    $appData = [Environment]::GetFolderPath("ApplicationData")
    $corelRoot = Join-Path $appData "Corel"
    
    if (-not (Test-Path $corelRoot)) {
        return $versions
    }
    
    # Padrão: CorelDRAW Graphics Suite XX
    $versionDirs = Get-ChildItem $corelRoot -Directory | Where-Object { 
        $_.Name -match "CorelDRAW" -or $_.Name -match "Graphics Suite"
    }
    
    foreach ($dir in $versionDirs) {
        $workspaceDir = Join-Path $dir.FullName "Draw\Workspace"
        if (Test-Path $workspaceDir) {
            $versions += @{
                Name         = $dir.Name
                Path         = $dir.FullName
                WorkspaceDir = $workspaceDir
                Version      = if ($dir.Name -match "(\d+)") { $Matches[1] } else { "Unknown" }
            }
        }
    }
    
    return $versions
}

function Get-ActiveWorkspace {
    param([string]$WorkspaceDir)
    
    # Prioridade: _default.cdws > Default.cdws > primeiro encontrado
    $candidates = @(
        (Join-Path $WorkspaceDir "_default.cdws"),
        (Join-Path $WorkspaceDir "Default.cdws"),
        (Join-Path $WorkspaceDir "Default (TM).cdws")
    )
    
    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # Fallback: primeiro .cdws
    $first = Get-ChildItem $WorkspaceDir -Filter "*.cdws" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($first) {
        return $first.FullName
    }
    
    return $null
}

function Backup-Workspace {
    param([string]$WorkspacePath, [string]$Version)
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "CorelDRAW_${Version}_${timestamp}.cdws.bak"
    $backupPath = Join-Path $BackupDir $backupName
    
    Copy-Item $WorkspacePath $backupPath -Force
    Write-Log "  Backup: $backupName" "DarkGray"
    
    return $backupPath
}

function Inject-Shortcuts {
    param(
        [string]$WorkspacePath,
        [array]$Shortcuts
    )
    
    # Criar diretório temporário
    if (-not (Test-Path $TempDir)) {
        New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    }
    
    # Copiar e descompactar (.cdws é um ZIP)
    $zipPath = Join-Path $TempDir "workspace.zip"
    Copy-Item $WorkspacePath $zipPath -Force
    
    $extractDir = Join-Path $TempDir "extracted"
    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
    
    # Encontrar workspace.xml
    $xmlPath = Join-Path $extractDir "content\workspace.xml"
    if (-not (Test-Path $xmlPath)) {
        throw "workspace.xml não encontrado no arquivo .cdws"
    }
    
    # Carregar e modificar XML
    $xml = New-Object System.Xml.XmlDocument
    $xml.PreserveWhitespace = $true
    $xml.Load($xmlPath)
    
    # Encontrar ou criar nó de items
    $uiConfig = $xml.SelectSingleNode("//uiConfig")
    if (-not $uiConfig) {
        throw "Estrutura XML inválida: uiConfig não encontrado"
    }
    
    $itemsNode = $uiConfig.SelectSingleNode("items")
    if (-not $itemsNode) {
        $itemsNode = $xml.CreateElement("items")
        $uiConfig.AppendChild($itemsNode) | Out-Null
    }
    
    # Injetar cada shortcut
    $injected = 0
    foreach ($shortcut in $Shortcuts) {
        $xpath = "itemData[@guid='$($shortcut.guid)']"
        $item = $itemsNode.SelectSingleNode($xpath)
        
        if (-not $item) {
            $item = $xml.CreateElement("itemData")
            $item.SetAttribute("guid", $shortcut.guid)
            $itemsNode.AppendChild($item) | Out-Null
        }
        
        # Remover keySequence antigo se existir
        $oldSeq = $item.SelectSingleNode("keySequence")
        if ($oldSeq) { 
            $item.RemoveChild($oldSeq) | Out-Null 
        }
        
        # Adicionar novo keySequence
        $newSeq = $xml.CreateElement("keySequence")
        $newSeq.InnerText = $shortcut.keys
        $item.AppendChild($newSeq) | Out-Null
        
        Write-Log "  + $($shortcut.keys) -> $($shortcut.name)" "Gray"
        $injected++
    }
    
    # Salvar XML
    $xml.Save($xmlPath)
    
    # Recompactar
    $outputZip = Join-Path $TempDir "output.zip"
    
    # Identificar conteúdo do ZIP
    $contents = Get-ChildItem $extractDir
    Compress-Archive -Path $contents.FullName -DestinationPath $outputZip -Force
    
    # Sobrescrever workspace original
    Copy-Item $outputZip $WorkspacePath -Force
    
    return $injected
}

function Restore-Backup {
    $backups = Get-ChildItem $BackupDir -Filter "*.bak" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    
    if ($backups.Count -eq 0) {
        Write-Log "Nenhum backup encontrado em $BackupDir" "Yellow"
        return
    }
    
    Write-Log "Backups disponíveis:" "Cyan"
    for ($i = 0; $i -lt [Math]::Min(5, $backups.Count); $i++) {
        Write-Log "  [$i] $($backups[$i].Name)" "White"
    }
    
    # Para automação, restaurar o mais recente
    $latest = $backups[0]
    Write-Log "Restaurando: $($latest.Name)" "Yellow"
    
    # Detectar versão do backup pelo nome
    if ($latest.Name -match "CorelDRAW_(\d+)_") {
        $version = $Matches[1]
        $versions = Get-CorelVersions
        $target = $versions | Where-Object { $_.Version -eq $version } | Select-Object -First 1
        
        if ($target) {
            $workspace = Get-ActiveWorkspace -WorkspaceDir $target.WorkspaceDir
            Copy-Item $latest.FullName $workspace -Force
            Write-Log "Restaurado para: $workspace" "Green"
        }
    }
}

# ============================================================
# MAIN
# ============================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ONI V23 - COREL SHORTCUTS INSTALLER (Agnostic Edition)  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

try {
    if ($Restore) {
        Restore-Backup
        exit 0
    }
    
    # 1. Carregar configuração
    if (-not (Test-Path $ConfigPath)) {
        throw "Arquivo de configuração não encontrado: $ConfigPath"
    }
    
    $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    Write-Log "Shortcuts definidos: $($config.shortcuts.Count)" "White"
    
    # 2. Detectar versões do CorelDRAW
    Write-Log "Detectando versões do CorelDRAW..." "Cyan"
    $versions = Get-CorelVersions
    
    if ($versions.Count -eq 0) {
        throw "Nenhuma instalação do CorelDRAW encontrada"
    }
    
    Write-Log "Encontradas $($versions.Count) versão(ões):" "Green"
    foreach ($v in $versions) {
        Write-Log "  - $($v.Name) (v$($v.Version))" "White"
    }
    
    # 3. Processar cada versão
    $totalInjected = 0
    foreach ($version in $versions) {
        Write-Host ""
        Write-Log "Processando: $($version.Name)" "Yellow"
        
        $workspace = Get-ActiveWorkspace -WorkspaceDir $version.WorkspaceDir
        if (-not $workspace) {
            Write-Log "  SKIP: Nenhum workspace encontrado" "DarkYellow"
            continue
        }
        
        Write-Log "  Workspace: $(Split-Path $workspace -Leaf)" "White"
        
        # Backup
        $backup = Backup-Workspace -WorkspacePath $workspace -Version $version.Version
        
        # Injetar
        $count = Inject-Shortcuts -WorkspacePath $workspace -Shortcuts $config.shortcuts
        $totalInjected += $count
        
        Write-Log "  OK: $count shortcuts injetados" "Green"
    }
    
    # Cleanup
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ INSTALAÇÃO CONCLUÍDA                                  ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  Shortcuts instalados em $($versions.Count) versão(ões) do CorelDRAW        ║" -ForegroundColor Green
    Write-Host "║  Backups salvos em: backups\corel_workspaces             ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  ⚠️  Reinicie o CorelDRAW para aplicar as mudanças       ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
}
catch {
    Write-Host ""
    Write-Log "ERRO: $_" "Red"
    Write-Log $_.ScriptStackTrace "DarkRed"
    
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    exit 1
}
