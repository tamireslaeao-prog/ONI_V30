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
# ONI ILLUSTRATOR HARVESTER - Vector Asset Analyzer
# Version: 1.0
# Description: Opens AI files via COM and extracts artboards, symbols, text
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

Write-Host "[ILLUSTRATOR HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Connect to Illustrator
try {
    $ai = New-Object -ComObject Illustrator.Application
    Write-Host "   [OK] Illustrator Connected (v$($ai.Version))" -ForegroundColor Green
}
catch {
    Write-Host "   [FAIL] Illustrator not available: $_" -ForegroundColor Red
    exit 1
}

$aiFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.ai" -ErrorAction SilentlyContinue
$epsFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.eps" -ErrorAction SilentlyContinue
$svgFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.svg" -ErrorAction SilentlyContinue

$allFiles = @($aiFiles) + @($epsFiles) + @($svgFiles)
Write-Host "   Found $($allFiles.Count) vector files" -ForegroundColor Yellow

$harvestResults = @()

foreach ($file in $allFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    try {
        $doc = $ai.Open($file.FullName)
        
        $docInfo = @{
            filename       = $file.Name
            path           = $file.FullName
            format         = $file.Extension.ToUpper().Replace(".", "")
            harvested_at   = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            width          = $null
            height         = $null
            artboards      = @()
            symbols        = @()
            text_frames    = @()
            path_items     = 0
            compound_paths = 0
            groups         = 0
        }
        
        try {
            $docInfo.width = $doc.Width
            $docInfo.height = $doc.Height
        }
        catch {}
        
        # Artboards
        try {
            foreach ($ab in $doc.Artboards) {
                $docInfo.artboards += @{
                    name = $ab.Name
                    rect = @($ab.ArtboardRect)
                }
                Write-Host "      [ARTBOARD] $($ab.Name)" -ForegroundColor Blue
            }
        }
        catch {}
        
        # Symbols
        try {
            foreach ($sym in $doc.Symbols) {
                $docInfo.symbols += @{
                    name = $sym.Name
                }
                Write-Host "      [SYMBOL] $($sym.Name)" -ForegroundColor Magenta
            }
        }
        catch {}
        
        # Text Frames
        try {
            foreach ($tf in $doc.TextFrames) {
                $content = $tf.Contents
                if ($content.Length -gt 50) { $content = $content.Substring(0, 50) + "..." }
                $docInfo.text_frames += @{
                    name    = $tf.Name
                    content = $content
                }
                Write-Host "      [TEXT] $content" -ForegroundColor Yellow
            }
        }
        catch {}
        
        # Counts
        try { $docInfo.path_items = $doc.PathItems.Count } catch {}
        try { $docInfo.compound_paths = $doc.CompoundPathItems.Count } catch {}
        try { $docInfo.groups = $doc.GroupItems.Count } catch {}
        
        Write-Host "   Artboards: $($docInfo.artboards.Count) | Symbols: $($docInfo.symbols.Count) | Text: $($docInfo.text_frames.Count) | Paths: $($docInfo.path_items)" -ForegroundColor Green
        
        $doc.Close(2) # Don't save
        $harvestResults += $docInfo
        
    }
    catch {
        Write-Host "   [ERROR] $($file.Name): $_" -ForegroundColor Red
    }
}

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Illustrator harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

