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
# Test Runner for ONI CorelDRAW Automation
$ScriptPath = Join-Path $PSScriptRoot "ONI_CorelAutomation.psm1"
$ScriptPath = [System.IO.Path]::GetFullPath($ScriptPath)
Remove-Module ONI.CorelAutomation -ErrorAction SilentlyContinue
Write-Host "Loading module from: $ScriptPath"
Import-Module $ScriptPath -Force

Write-Host "Attempting to connect to CorelDRAW..."
$corel = Connect-CorelDRAW

if ($corel) {
    Write-Host "Connection Successful!" -ForegroundColor Green
    
    $outputPath = "$env:USERPROFILE\Desktop\ONI_Turbo_Test.cdr"
    Write-Host "Generating Turbo Test Badge to: $outputPath"
    
    try {
        New-CyberpunkBadge -Corel $corel -Name "TURBO MODE" -Title "ACTIVE" -ID "ONI-001" -OutputPath $outputPath
        Write-Host "Badge Generation Successful!" -ForegroundColor Green
    }
    catch {
        Write-Error "Badge Generation Failed: $_"
    }
}
else {
    Write-Error "Could not connect to CorelDRAW. Is it installed?"
}

