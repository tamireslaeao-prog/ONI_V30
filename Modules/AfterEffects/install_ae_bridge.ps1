
<#
.SYNOPSIS
    ONI AE Bridge Installer v1.0
    Installs the After Effects watcher script and configures the job folder.
    
.DESCRIPTION
    This script:
    1. Creates the job folder (temp/ae_jobs)
    2. Copies oni_ae_watcher.jsx to AE's Scripts/Startup folder
    3. Verifies installation
    
.NOTES
    Run this script ONCE to set up the bridge.
    Requires Administrator privileges to write to Program Files.
#>

$ErrorActionPreference = "Stop"

# Configuration - Portable paths using $PSScriptRoot
# This script is at: ONIV24/Modules/AfterEffects/install_ae_bridge.ps1
$ONI_ROOT = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$WATCHER_SOURCE = Join-Path $ONI_ROOT "Modules\AfterEffects\oni_ae_watcher.jsx"
$JOB_FOLDER = Join-Path $ONI_ROOT "temp\ae_jobs"

# Detect AE version
$AE_VERSIONS = @(
    "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\Scripts\Startup",
    "C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\Scripts\Startup",
    "C:\Program Files\Adobe\Adobe After Effects CC 2023\Support Files\Scripts\Startup"
)

Write-Host "=== ONI AE BRIDGE INSTALLER ===" -ForegroundColor Cyan
Write-Host ""

# 1. Create Job Folder
Write-Host "[1/3] Creating Job Folder..." -ForegroundColor Yellow
if (!(Test-Path $JOB_FOLDER)) {
    New-Item -ItemType Directory -Force -Path $JOB_FOLDER | Out-Null
    Write-Host "      Created: $JOB_FOLDER" -ForegroundColor Green
}
else {
    Write-Host "      Already exists: $JOB_FOLDER" -ForegroundColor Gray
}

# 2. Find AE Startup Folder
Write-Host "[2/3] Locating After Effects..." -ForegroundColor Yellow
$AE_STARTUP = $null
foreach ($path in $AE_VERSIONS) {
    if (Test-Path $path) {
        $AE_STARTUP = $path
        break
    }
}

if (-not $AE_STARTUP) {
    Write-Host "      ERROR: After Effects not found!" -ForegroundColor Red
    Write-Host "      Checked paths:" -ForegroundColor Red
    $AE_VERSIONS | ForEach-Object { Write-Host "        - $_" -ForegroundColor Gray }
    exit 1
}

Write-Host "      Found: $AE_STARTUP" -ForegroundColor Green

# 3. Copy Watcher Script
Write-Host "[3/3] Installing Watcher Script..." -ForegroundColor Yellow
$DEST = Join-Path $AE_STARTUP "oni_ae_watcher.jsx"

if (!(Test-Path $WATCHER_SOURCE)) {
    Write-Host "      ERROR: Source file not found: $WATCHER_SOURCE" -ForegroundColor Red
    exit 1
}

try {
    Copy-Item -Path $WATCHER_SOURCE -Destination $DEST -Force
    Write-Host "      Installed: $DEST" -ForegroundColor Green
}
catch {
    Write-Host "      ERROR: Failed to copy. Try running as Administrator." -ForegroundColor Red
    Write-Host "      $_" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "=== INSTALLATION COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Restart After Effects (if running)" -ForegroundColor White
Write-Host "  2. In AE, go to: Edit > Preferences > Scripting" -ForegroundColor White
Write-Host "  3. Enable: 'Allow Scripts to Write Files and Access Network'" -ForegroundColor White
Write-Host "  4. Test with: python Modules\AfterEffects\oni_ae_bridge.py" -ForegroundColor White
Write-Host ""
Write-Host "The ONI AE Bridge is now installed." -ForegroundColor Green
