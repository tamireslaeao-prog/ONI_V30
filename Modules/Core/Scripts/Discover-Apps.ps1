<#
.SYNOPSIS
    ONI Application Discovery Service
.DESCRIPTION
    Scans Windows Registry to find actual installation paths for supported applications.
    Generates app_paths.json for the ONI system.
.AUTHOR
    Antigravity Engine
#>

$ErrorActionPreference = "SilentlyContinue"

# List of Executables to Search in App Paths
# Format: NameInONI = ExecutableName
$AppMap = @{
    "Photoshop"    = "Photoshop.exe"
    "Illustrator"  = "Illustrator.exe"
    "AfterEffects" = "AfterFX.exe"
    "Premiere Pro" = "Adobe Premiere Pro.exe"
    "Blender"      = "blender.exe"
    "Maya"         = "maya.exe"
    "AutoCAD"      = "acad.exe"
    "CorelDRAW"    = "CorelDRW.exe"
    "Chrome"       = "chrome.exe"
    "Firefox"      = "firefox.exe"
    "Word"         = "WINWORD.EXE"
    "Excel"        = "EXCEL.EXE"
    "PowerPoint"   = "POWERPNT.EXE"
    "Acrobat"      = "Acrobat.exe"
    "Foxit"        = "FoxitPDFEditor.exe"
}

$RegistryBase = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
$DetectedApps = @{}

Write-Host "Starting ONI App Discovery..." -ForegroundColor Cyan

foreach ($App in $AppMap.Keys) {
    $ExeName = $AppMap[$App]
    $Path = $null
    
    # Try standard App Paths registry
    $RegPath = Join-Path $RegistryBase $ExeName
    if (Test-Path $RegPath) {
        $Path = (Get-ItemProperty -Path $RegPath -Name "(default)")."(default)"
    }
    
    # Validation
    if ($Path -and (Test-Path $Path)) {
        Write-Host "  [FOUND] $App -> $Path" -ForegroundColor Green
        $DetectedApps[$App] = @{
            path = $Path
            args_script = $null
        }
    } else {
        Write-Host "  [MISSING] $App ($ExeName)" -ForegroundColor DarkGray
    }
}

# Construct Final JSON Object
$FinalObject = @{
    description = "ONI Knowledge Base - Known Application Paths (Auto-Learned)"
    updated_at  = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    apps        = $DetectedApps
}

# Output File
$OutputPath = Join-Path $PSScriptRoot "..\Knowledge\app_paths.json"
# Resolve to absolute path
$OutputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)

Write-Host ""
Write-Host "Writing configuration to: $OutputPath" -ForegroundColor Cyan

$FinalObject | ConvertTo-Json -Depth 3 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "Discovery Complete." -ForegroundColor Green
