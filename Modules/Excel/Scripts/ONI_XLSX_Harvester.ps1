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
# ONI EXCEL HARVESTER - Spreadsheet Analyzer
# Version: 1.0
# Description: Opens XLSX files via COM and extracts sheets, tables, ranges
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

Write-Host "[EXCEL HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Connect to Excel
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    Write-Host "   [OK] Excel Connected (v$($excel.Version))" -ForegroundColor Green
}
catch {
    Write-Host "   [FAIL] Excel not available: $_" -ForegroundColor Red
    exit 1
}

$xlsxFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.xlsx" -ErrorAction SilentlyContinue
$xlsFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.xls" -ErrorAction SilentlyContinue
$csvFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.csv" -ErrorAction SilentlyContinue

$allFiles = @($xlsxFiles) + @($xlsFiles) + @($csvFiles)
Write-Host "   Found $($allFiles.Count) spreadsheet files" -ForegroundColor Yellow

$harvestResults = @()

foreach ($file in $allFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    try {
        $workbook = $excel.Workbooks.Open($file.FullName)
        
        $docInfo = @{
            filename         = $file.Name
            path             = $file.FullName
            format           = $file.Extension.ToUpper().Replace(".", "")
            harvested_at     = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            sheets           = @()
            named_ranges     = @()
            tables           = @()
            charts           = @()
            total_cells_used = 0
        }
        
        # Sheets
        foreach ($sheet in $workbook.Worksheets) {
            $usedRange = $sheet.UsedRange
            $rowCount = 0
            $colCount = 0
            try {
                $rowCount = $usedRange.Rows.Count
                $colCount = $usedRange.Columns.Count
            }
            catch {}
            
            $sheetInfo = @{
                name     = $sheet.Name
                rows     = $rowCount
                columns  = $colCount
                has_data = ($rowCount -gt 0 -and $colCount -gt 0)
            }
            $docInfo.sheets += $sheetInfo
            $docInfo.total_cells_used += ($rowCount * $colCount)
            Write-Host "      [SHEET] $($sheet.Name) - ${rowCount}x${colCount}" -ForegroundColor Blue
            
            # Tables (ListObjects)
            try {
                foreach ($table in $sheet.ListObjects) {
                    $docInfo.tables += @{
                        name    = $table.Name
                        sheet   = $sheet.Name
                        rows    = $table.Range.Rows.Count
                        columns = $table.Range.Columns.Count
                    }
                    Write-Host "         [TABLE] $($table.Name)" -ForegroundColor Magenta
                }
            }
            catch {}
            
            # Charts
            try {
                foreach ($chart in $sheet.ChartObjects()) {
                    $docInfo.charts += @{
                        name       = $chart.Name
                        sheet      = $sheet.Name
                        chart_type = $chart.Chart.ChartType
                    }
                    Write-Host "         [CHART] $($chart.Name)" -ForegroundColor Cyan
                }
            }
            catch {}
        }
        
        # Named Ranges
        try {
            foreach ($name in $workbook.Names) {
                $docInfo.named_ranges += @{
                    name      = $name.Name
                    refers_to = $name.RefersTo
                }
                Write-Host "      [NAMED] $($name.Name)" -ForegroundColor Yellow
            }
        }
        catch {}
        
        Write-Host "   Sheets: $($docInfo.sheets.Count) | Tables: $($docInfo.tables.Count) | Charts: $($docInfo.charts.Count) | Named: $($docInfo.named_ranges.Count)" -ForegroundColor Green
        
        $workbook.Close($false)
        $harvestResults += $docInfo
        
    }
    catch {
        Write-Host "   [ERROR] $($file.Name): $_" -ForegroundColor Red
    }
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Excel harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

