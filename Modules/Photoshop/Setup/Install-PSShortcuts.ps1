<#
.SYNOPSIS
    ONI V23 - Instalador Automático de Shortcuts para Adobe Photoshop
    Agnóstico à versão, auto-detecta e instala sem interação.

.DESCRIPTION
    1. Detecta automaticamente QUALQUER versão do Photoshop (CC 2019-2025+)
    2. Faz backup do keyboard shortcuts atual
    3. Cria perfil ONI_Neural com shortcuts personalizados
    4. Aplica automaticamente

.NOTES
    Photoshop usa arquivos .kys (Keyboard Shortcut Sets) em:
    %APPDATA%\Adobe\Adobe Photoshop XXXX\Presets\Keyboard Shortcuts\

.EXAMPLE
    .\Install-PSShortcuts.ps1
    .\Install-PSShortcuts.ps1 -Restore
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
$ConfigPath = Join-Path $BaseDir "Config\ps_shortcuts.json"
$BackupDir = Join-Path $BaseDir "Backups"

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

function Get-PhotoshopVersions {
    <#
    .SYNOPSIS
        Detecta TODAS as versões do Photoshop instaladas (CC 2019+)
    #>
    $versions = @()
    $appData = [Environment]::GetFolderPath("ApplicationData")
    $adobeRoot = Join-Path $appData "Adobe"
    
    if (-not (Test-Path $adobeRoot)) {
        return $versions
    }
    
    # Padrão: Adobe Photoshop XXXX, Adobe Photoshop 2024, etc
    $psDirs = Get-ChildItem $adobeRoot -Directory | Where-Object { 
        $_.Name -match "^Adobe Photoshop" 
    }
    
    foreach ($dir in $psDirs) {
        $shortcutsDir = Join-Path $dir.FullName "Presets\Keyboard Shortcuts"
        
        # Criar diretório se não existir
        if (-not (Test-Path $shortcutsDir)) {
            New-Item -ItemType Directory -Path $shortcutsDir -Force | Out-Null
        }
        
        # Extrair ano/versão do nome
        $versionMatch = $null
        if ($dir.Name -match "(\d{4})") {
            $versionMatch = $Matches[1]
        }
        elseif ($dir.Name -match "CC (\d+)") {
            $versionMatch = $Matches[1]
        }
        
        $versions += @{
            Name         = $dir.Name
            Path         = $dir.FullName
            ShortcutsDir = $shortcutsDir
            Version      = if ($versionMatch) { $versionMatch } else { "Unknown" }
        }
    }
    
    return $versions
}

function Backup-Shortcuts {
    param([string]$ShortcutsDir, [string]$Version)
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "Photoshop_${Version}_${timestamp}"
    $backupPath = Join-Path $BackupDir $backupName
    
    if (Test-Path $ShortcutsDir) {
        $kysFiles = Get-ChildItem $ShortcutsDir -Filter "*.kys" -ErrorAction SilentlyContinue
        if ($kysFiles.Count -gt 0) {
            New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
            Copy-Item "$ShortcutsDir\*.kys" $backupPath -Force
            Write-Log "  Backup: $($kysFiles.Count) arquivos .kys" "DarkGray"
            return $backupPath
        }
    }
    
    return $null
}

function Convert-KeyToPhotoshopFormat {
    <#
    .SYNOPSIS
        Converte notação de tecla (Ctrl+Shift+D) para formato Photoshop
    #>
    param([string]$Keys)
    
    $parts = $Keys -split "\+"
    $result = @{
        Ctrl  = $false
        Shift = $false
        Alt   = $false
        Key   = ""
    }
    
    foreach ($part in $parts) {
        $p = $part.Trim()
        switch -Regex ($p) {
            "^Ctrl$" { $result.Ctrl = $true }
            "^Shift$" { $result.Shift = $true }
            "^Alt$" { $result.Alt = $true }
            default { $result.Key = $p }
        }
    }
    
    return $result
}

function Get-VirtualKeyCode {
    param([string]$Key)
    
    # Mapeamento de teclas para códigos virtuais
    $keyMap = @{
        "A" = 65; "B" = 66; "C" = 67; "D" = 68; "E" = 69
        "F" = 70; "G" = 71; "H" = 72; "I" = 73; "J" = 74
        "K" = 75; "L" = 76; "M" = 77; "N" = 78; "O" = 79
        "P" = 80; "Q" = 81; "R" = 82; "S" = 83; "T" = 84
        "U" = 85; "V" = 86; "W" = 87; "X" = 88; "Y" = 89; "Z" = 90
        "0" = 48; "1" = 49; "2" = 50; "3" = 51; "4" = 52
        "5" = 53; "6" = 54; "7" = 55; "8" = 56; "9" = 57
        "F1" = 112; "F2" = 113; "F3" = 114; "F4" = 115
        "F5" = 116; "F6" = 117; "F7" = 118; "F8" = 119
        "F9" = 120; "F10" = 121; "F11" = 122; "F12" = 123
        "Enter" = 13; "Escape" = 27; "Space" = 32
        "Tab" = 9; "Backspace" = 8; "Delete" = 46
    }
    
    if ($keyMap.ContainsKey($Key)) {
        return $keyMap[$Key]
    }
    return 0
}

function Create-KysFile {
    <#
    .SYNOPSIS
        Cria arquivo .kys do Photoshop com shortcuts personalizados
    #>
    param(
        [string]$OutputPath,
        [string]$ProfileName,
        [array]$Shortcuts
    )
    
    # Estrutura básica do .kys (XML)
    $xml = @"
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>$ProfileName</key>
    <dict>
"@
    
    foreach ($shortcut in $Shortcuts) {
        $keyData = Convert-KeyToPhotoshopFormat -Keys $shortcut.keys
        $vk = Get-VirtualKeyCode -Key $keyData.Key
        
        # Calcular modificadores
        $modifiers = 0
        if ($keyData.Shift) { $modifiers += 1 }
        if ($keyData.Ctrl) { $modifiers += 2 }
        if ($keyData.Alt) { $modifiers += 4 }
        
        $id = $shortcut.id
        
        $xml += @"
        
        <key>$id</key>
        <dict>
            <key>key</key>
            <integer>$vk</integer>
            <key>modifiers</key>
            <integer>$modifiers</integer>
        </dict>
"@
    }
    
    $xml += @"

    </dict>
</dict>
</plist>
"@
    
    $xml | Out-File -FilePath $OutputPath -Encoding UTF8 -Force
}

function Install-PsShortcuts {
    param(
        [string]$ShortcutsDir,
        [string]$ProfileName,
        [array]$Shortcuts
    )
    
    $kysPath = Join-Path $ShortcutsDir "${ProfileName}.kys"
    
    # Criar arquivo .kys
    Create-KysFile -OutputPath $kysPath -ProfileName $ProfileName -Shortcuts $Shortcuts
    
    Write-Log "  Criado: ${ProfileName}.kys" "Gray"
    
    foreach ($shortcut in $Shortcuts) {
        Write-Log "    + $($shortcut.keys) -> $($shortcut.name)" "DarkGray"
    }
    
    return $Shortcuts.Count
}

function Restore-Backup {
    $backups = Get-ChildItem $BackupDir -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    
    if ($backups.Count -eq 0) {
        Write-Log "Nenhum backup encontrado em $BackupDir" "Yellow"
        return
    }
    
    Write-Log "Backups disponíveis:" "Cyan"
    for ($i = 0; $i -lt [Math]::Min(5, $backups.Count); $i++) {
        Write-Log "  [$i] $($backups[$i].Name)" "White"
    }
    
    $latest = $backups[0]
    Write-Log "Restaurando: $($latest.Name)" "Yellow"
    
    # Detectar versão pelo nome
    if ($latest.Name -match "Photoshop_(\d+)_") {
        $version = $Matches[1]
        $versions = Get-PhotoshopVersions
        $target = $versions | Where-Object { $_.Version -eq $version } | Select-Object -First 1
        
        if ($target) {
            Copy-Item "$($latest.FullName)\*.kys" $target.ShortcutsDir -Force
            Write-Log "Restaurado para: $($target.ShortcutsDir)" "Green"
        }
    }
}

# ============================================================
# MAIN
# ============================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  ONI V23 - PHOTOSHOP SHORTCUTS INSTALLER (Agnostic Ed.)  ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
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
    $profileName = $config.profile_name
    Write-Log "Perfil: $profileName" "White"
    Write-Log "Shortcuts definidos: $($config.shortcuts.Count)" "White"
    
    # 2. Detectar versões do Photoshop
    Write-Log "Detectando versões do Photoshop..." "Magenta"
    $versions = Get-PhotoshopVersions
    
    if ($versions.Count -eq 0) {
        throw "Nenhuma instalação do Photoshop encontrada"
    }
    
    Write-Log "Encontradas $($versions.Count) versão(ões):" "Green"
    foreach ($v in $versions) {
        Write-Log "  - $($v.Name)" "White"
    }
    
    # 3. Processar cada versão
    $totalInstalled = 0
    foreach ($version in $versions) {
        Write-Host ""
        Write-Log "Processando: $($version.Name)" "Yellow"
        
        # Backup
        Backup-Shortcuts -ShortcutsDir $version.ShortcutsDir -Version $version.Version
        
        # Instalar
        $count = Install-PsShortcuts -ShortcutsDir $version.ShortcutsDir -ProfileName $profileName -Shortcuts $config.shortcuts
        $totalInstalled += $count
        
        Write-Log "  OK: $count shortcuts instalados" "Green"
    }
    
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ INSTALAÇÃO CONCLUÍDA                                  ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  Para ativar no Photoshop:                               ║" -ForegroundColor Green
    Write-Host "║  Edit > Keyboard Shortcuts > Set: $profileName              ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  Backups salvos em: backups\photoshop_shortcuts          ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
}
catch {
    Write-Host ""
    Write-Log "ERRO: $_" "Red"
    Write-Log $_.ScriptStackTrace "DarkRed"
    exit 1
}
