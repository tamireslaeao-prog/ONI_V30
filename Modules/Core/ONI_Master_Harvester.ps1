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
# ONI MASTER HARVESTER - Universal Asset Scanner
# Version: 1.0
# Description: Orchestrates all module harvesters from a single command
# ============================================================================

param(
    [string]$ModulesRoot,
    [switch]$All,
    [switch]$Photoshop,
    [switch]$Illustrator,
    [switch]$Corel,
    [switch]$Excel,
    [switch]$Word,
    [switch]$AfterEffects,
    [switch]$Blender,
    [switch]$Chrome,
    [switch]$Asana,
    [switch]$Edge,
    [switch]$Windows
)

if ([string]::IsNullOrEmpty($ModulesRoot)) {
    $ModulesRoot = $PSScriptRoot
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ONI MASTER HARVESTER" -ForegroundColor Cyan
Write-Host "  Universal Asset Scanner v1.4" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Define harvesters
$harvesters = @{
    "Photoshop"    = "$ModulesRoot\Photoshop\Scripts\ONI_PSD_Harvester.ps1"
    "Illustrator"  = "$ModulesRoot\Illustrator\Scripts\ONI_AI_Harvester.ps1"
    "Corel"        = "$ModulesRoot\Corel\Scripts\ONI_CDR_Harvester.ps1"
    "Excel"        = "$ModulesRoot\Excel\Scripts\ONI_XLSX_Harvester.ps1"
    "Word"         = "$ModulesRoot\Word\Scripts\ONI_DOCX_Harvester.ps1"
    "AfterEffects" = "$ModulesRoot\AfterEffects\Scripts\ONI_AEP_Harvester.ps1"
    "Blender"      = "$ModulesRoot\Blender\Scripts\ONI_BLEND_Harvester.ps1"
    "Chrome"       = "$ModulesRoot\Chrome\Scripts\ONI_Chrome_Harvester.ps1"
    "Asana"        = "$ModulesRoot\Asana\Scripts\ONI_Asana_Harvester.ps1"
    "Edge"         = "$ModulesRoot\Edge\Scripts\ONI_Edge_Harvester.ps1"
    "Windows"      = "$ModulesRoot\Windows\Scripts\ONI_Windows_Harvester.ps1"
}

# Determine which to run
$toRun = @()

if ($All) {
    $toRun = $harvesters.Keys
}
else {
    if ($Photoshop) { $toRun += "Photoshop" }
    if ($Illustrator) { $toRun += "Illustrator" }
    if ($Corel) { $toRun += "Corel" }
    if ($Excel) { $toRun += "Excel" }
    if ($Word) { $toRun += "Word" }
    if ($AfterEffects) { $toRun += "AfterEffects" }
    if ($Blender) { $toRun += "Blender" }
    if ($Chrome) { $toRun += "Chrome" }
    if ($Asana) { $toRun += "Asana" }
    if ($Edge) { $toRun += "Edge" }
    if ($Windows) { $toRun += "Windows" }
}

if ($toRun.Count -eq 0) {
    Write-Host "Usage: ONI_Master_Harvester.ps1 -All" -ForegroundColor Yellow
    Write-Host "   or: ONI_Master_Harvester.ps1 -Photoshop -Excel -Word" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available modules:" -ForegroundColor Gray
    foreach ($key in $harvesters.Keys) {
        Write-Host "   -$key" -ForegroundColor White
    }
    exit 0
}

Write-Host "Modules to harvest: $($toRun -join ', ')" -ForegroundColor Yellow
Write-Host ""

$results = @{}

foreach ($module in $toRun) {
    $script = $harvesters[$module]
    
    if (-not (Test-Path $script)) {
        Write-Host "[SKIP] $module - Script not found" -ForegroundColor DarkYellow
        $results[$module] = "SCRIPT_MISSING"
        continue
    }
    
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "[RUN] $module Harvester" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    
    try {
        & $script
        $results[$module] = "SUCCESS"
    }
    catch {
        Write-Host "[ERROR] $module failed: $_" -ForegroundColor Red
        $results[$module] = "FAILED"
    }
    
    Write-Host ""
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  HARVEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

foreach ($module in $results.Keys) {
    $status = $results[$module]
    $color = switch ($status) {
        "SUCCESS" { "Green" }
        "FAILED" { "Red" }
        "SCRIPT_MISSING" { "Yellow" }
        default { "Gray" }
    }
    Write-Host "  $module : $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "  Duration: $($duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan

