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
# ONI CORELDRAW HARVESTER - Vector Design Analyzer
# Version: 1.0
# Description: Opens CDR files via COM and extracts objects, text, pages
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

Write-Host "[CORELDRAW HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Connect to CorelDRAW
try {
    $corel = New-Object -ComObject CorelDRAW.Application
    Write-Host "   [OK] CorelDRAW Connected (v$($corel.VersionMajor).$($corel.VersionMinor))" -ForegroundColor Green
}
catch {
    Write-Host "   [FAIL] CorelDRAW not available: $_" -ForegroundColor Red
    exit 1
}

$cdrFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.cdr" -ErrorAction SilentlyContinue
Write-Host "   Found $($cdrFiles.Count) CDR files" -ForegroundColor Yellow

$harvestResults = @()

foreach ($file in $cdrFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    try {
        $doc = $corel.OpenDocument($file.FullName)
        
        $docInfo = @{
            filename     = $file.Name
            path         = $file.FullName
            harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            pages        = @()
            text_objects = @()
            symbols      = @()
            total_shapes = 0
            total_groups = 0
        }
        
        # Pages
        try {
            foreach ($page in $doc.Pages) {
                $pageInfo = @{
                    name         = $page.Name
                    width        = $page.SizeWidth
                    height       = $page.SizeHeight
                    shapes_count = $page.Shapes.Count
                }
                $docInfo.pages += $pageInfo
                $docInfo.total_shapes += $page.Shapes.Count
                Write-Host "      [PAGE] $($page.Name) - $($page.Shapes.Count) shapes" -ForegroundColor Blue
                
                # Traverse shapes on this page
                foreach ($shape in $page.Shapes) {
                    # Text shapes
                    try {
                        if ($shape.Type -eq 6) {
                            # cdrTextShape
                            $content = $shape.Text.Story.Text
                            if ($content.Length -gt 50) { $content = $content.Substring(0, 50) + "..." }
                            $docInfo.text_objects += @{
                                page    = $page.Name
                                content = $content
                            }
                            Write-Host "         [TEXT] $content" -ForegroundColor Yellow
                        }
                    }
                    catch {}
                    
                    # Groups
                    try {
                        if ($shape.Type -eq 7) {
                            # cdrGroupShape
                            $docInfo.total_groups++
                        }
                    }
                    catch {}
                }
            }
        }
        catch {}
        
        # Symbols in Document
        try {
            foreach ($sym in $doc.SymbolLibrary.Symbols) {
                $docInfo.symbols += @{
                    name = $sym.Name
                }
                Write-Host "      [SYMBOL] $($sym.Name)" -ForegroundColor Magenta
            }
        }
        catch {}
        
        Write-Host "   Pages: $($docInfo.pages.Count) | Text: $($docInfo.text_objects.Count) | Shapes: $($docInfo.total_shapes) | Groups: $($docInfo.total_groups)" -ForegroundColor Green
        
        $doc.Close()
        $harvestResults += $docInfo
        
    }
    catch {
        Write-Host "   [ERROR] $($file.Name): $_" -ForegroundColor Red
    }
}

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] CorelDRAW harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

