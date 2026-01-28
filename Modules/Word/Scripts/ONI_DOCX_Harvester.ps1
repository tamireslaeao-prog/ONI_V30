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
# ONI WORD HARVESTER - Document Analyzer
# Version: 1.0
# Description: Opens DOCX files via COM and extracts styles, sections, tables
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

Write-Host "[WORD HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Connect to Word
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    Write-Host "   [OK] Word Connected (v$($word.Version))" -ForegroundColor Green
}
catch {
    Write-Host "   [FAIL] Word not available: $_" -ForegroundColor Red
    exit 1
}

$docxFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.docx" -ErrorAction SilentlyContinue
$docFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.doc" -ErrorAction SilentlyContinue

$allFiles = @($docxFiles) + @($docFiles)
Write-Host "   Found $($allFiles.Count) document files" -ForegroundColor Yellow

$harvestResults = @()

foreach ($file in $allFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    try {
        $doc = $word.Documents.Open($file.FullName)
        
        $docInfo = @{
            filename     = $file.Name
            path         = $file.FullName
            format       = $file.Extension.ToUpper().Replace(".", "")
            harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            pages        = 0
            words        = 0
            paragraphs   = 0
            sections     = @()
            tables       = @()
            images       = 0
            styles_used  = @()
            headings     = @()
        }
        
        # Basic stats
        try {
            $docInfo.pages = $doc.ComputeStatistics(2) # wdStatisticPages
            $docInfo.words = $doc.ComputeStatistics(0) # wdStatisticWords
            $docInfo.paragraphs = $doc.Paragraphs.Count
        }
        catch {}
        
        # Sections
        try {
            foreach ($section in $doc.Sections) {
                $docInfo.sections += @{
                    start_page    = $section.Range.Information(3) # wdActiveEndPageNumber
                    header_exists = ($section.Headers.Item(1).Range.Text.Trim().Length -gt 0)
                    footer_exists = ($section.Footers.Item(1).Range.Text.Trim().Length -gt 0)
                }
            }
            Write-Host "      [SECTIONS] $($docInfo.sections.Count)" -ForegroundColor Blue
        }
        catch {}
        
        # Tables
        try {
            foreach ($table in $doc.Tables) {
                $docInfo.tables += @{
                    rows    = $table.Rows.Count
                    columns = $table.Columns.Count
                }
            }
            Write-Host "      [TABLES] $($docInfo.tables.Count)" -ForegroundColor Magenta
        }
        catch {}
        
        # Images
        try {
            $docInfo.images = $doc.InlineShapes.Count + $doc.Shapes.Count
            Write-Host "      [IMAGES] $($docInfo.images)" -ForegroundColor Cyan
        }
        catch {}
        
        # Headings (H1, H2, H3)
        try {
            foreach ($para in $doc.Paragraphs) {
                $styleName = $para.Style.NameLocal
                if ($styleName -match "Heading|Titulo|Cabeçalho") {
                    $content = $para.Range.Text.Trim()
                    if ($content.Length -gt 50) { $content = $content.Substring(0, 50) + "..." }
                    $docInfo.headings += @{
                        style = $styleName
                        text  = $content
                    }
                }
                # Track unique styles
                if ($docInfo.styles_used -notcontains $styleName) {
                    $docInfo.styles_used += $styleName
                }
            }
            Write-Host "      [HEADINGS] $($docInfo.headings.Count)" -ForegroundColor Yellow
        }
        catch {}
        
        Write-Host "   Pages: $($docInfo.pages) | Words: $($docInfo.words) | Tables: $($docInfo.tables.Count) | Images: $($docInfo.images)" -ForegroundColor Green
        
        $doc.Close($false)
        $harvestResults += $docInfo
        
    }
    catch {
        Write-Host "   [ERROR] $($file.Name): $_" -ForegroundColor Red
    }
}

$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Word harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

