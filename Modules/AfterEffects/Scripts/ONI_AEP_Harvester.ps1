<#
    .SYNOPSIS
        ONI V24 Module Component.
    .DESCRIPTION
        Part of the ONI Automation Framework.
        Managed by The Jewel Polishing Protocol.
    .AUTHOR
        Antigravity Engine (Google DeepMind)
    .DATE
        2026-01-10
#>
# ============================================================================
# ONI AFTER EFFECTS HARVESTER - Composition Analyzer
# Version: 1.0
# Description: Opens AEP projects via ExtendScript and extracts comps, layers
# Note: After Effects doesn't have direct COM, uses scripting bridge
# ============================================================================

param(
    [string]$AssetsFolder,
    [string]$OutputFile
)

if ([string]::IsNullOrEmpty($AssetsFolder)) {
    $AssetsFolder = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
}
if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[AFTER EFFECTS HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# After Effects uses ExtendScript, not COM directly
# We'll create a JSX script and run it via AfterFX.exe -r

$aepFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.aep" -ErrorAction SilentlyContinue
Write-Host "   Found $($aepFiles.Count) AEP files" -ForegroundColor Yellow

if ($aepFiles.Count -eq 0) {
    Write-Host "   No AEP files to process" -ForegroundColor DarkYellow
    @() | ConvertTo-Json | Set-Content $OutputFile -Encoding UTF8
    exit 0
}

$harvestResults = @()

foreach ($file in $aepFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    # For AE, we need to generate a basic structure without opening
    # (Full AE scripting requires AE to be running)
    
    $docInfo = @{
        filename      = $file.Name
        path          = $file.FullName
        format        = "AEP"
        harvested_at  = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        file_size_mb  = [math]::Round($file.Length / 1MB, 2)
        status        = "PENDING_AE_SCAN"
        note          = "Full scan requires After Effects running with JSX bridge"
        compositions  = @()
        footage_items = @()
        expressions   = @()
    }
    
    Write-Host "   [INFO] File indexed - full scan requires AE running" -ForegroundColor Yellow
    Write-Host "   Size: $($docInfo.file_size_mb) MB" -ForegroundColor Gray
    
    $harvestResults += $docInfo
}

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] After Effects harvest finished (metadata only)" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray
Write-Host "   Note: Run full scan with AE open for composition details" -ForegroundColor DarkYellow

