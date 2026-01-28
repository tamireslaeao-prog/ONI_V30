<#
.SYNOPSIS
    ONI V27 - AutoCAD Shortcut Installer (PGP Injector)
    Injects ONI aliases into acad.pgp

.DESCRIPTION
    Locates acad.pgp in User Support path and appends aliases correctly.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path (Get-Item $ScriptDir).Parent.FullName "Config\autocad_shortcuts.json"

function Write-Log { param($Msg, $Color = "White") Write-Host "[AUTO-CAD] $Msg" -ForegroundColor $Color }

Write-Log "Starting AutoCAD PGP Injection..." "Magenta"

if (-not (Test-Path $ConfigPath)) { throw "Config not found at $ConfigPath" }
$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json

# Locate acad.pgp
$appData = [Environment]::GetFolderPath("ApplicationData")
$autodesk = Join-Path $appData "Autodesk"

if (-not (Test-Path $autodesk)) {
    Write-Log "Autodesk folder not found in AppData." "Red"
    exit 1
}

# Find latest acad.pgp
$pgpFiles = Get-ChildItem -Path $autodesk -Recurse -Filter "acad.pgp" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

if ($pgpFiles.Count -eq 0) {
    Write-Log "acad.pgp not found. Is AutoCAD installed/run at least once?" "Yellow"
    exit 0
}

$targetPgp = $pgpFiles[0].FullName
Write-Log "Target PGP: $targetPgp" "Cyan"

# Load PGP content
$content = Get-Content $targetPgp -Raw

# Prepare ONI Section
$oniSectionHeader = ";; --- ONI NEURAL SHORTCUTS START ---"
$oniSectionFooter = ";; --- ONI NEURAL SHORTCUTS END ---"
$newAliases = ""

foreach ($s in $config.shortcuts) {
    if ($s.type -eq "alias") {
        # Format: ALIAS, *COMMAND
        $newAliases += "$($s.keys), *$($s.command)`r`n"
    }
}

# Check if already exists
if ($content -match "ONI NEURAL SHORTCUTS START") {
    Write-Log "Updating existing ONI section..." "Yellow"
    # Regex replacement logic would be complex here, so we append to end for override (AutoCAD respects last entry)
    $content += "`r`n$oniSectionHeader`r`n$newAliases$oniSectionFooter`r`n"
}
else {
    Write-Log "Injecting new ONI section..." "Green"
    $content += "`r`n`r`n$oniSectionHeader`r`n$newAliases$oniSectionFooter`r`n"
}

try {
    Set-Content -Path $targetPgp -Value $content -Force
    Write-Log "✅ Success! Aliases injected." "Green"
    Write-Log "Run 'REINIT' in AutoCAD to apply changes." "White"
}
catch {
    Write-Log "Failed to write PGP: $_" "Red"
}
