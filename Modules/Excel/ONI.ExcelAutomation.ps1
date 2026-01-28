# ============================================================================
# ONI.ExcelAutomation.ps1 - PowerShell Bridge to Excel
# Version: 1.0
# Description: Automate Excel badge generation from PowerShell
# ============================================================================

# ============================================================================
# EXCEL CONNECTION MANAGEMENT
# ============================================================================

function Connect-Excel {
    <#
    .SYNOPSIS
    Establishes COM connection to Excel
    
    .EXAMPLE
    $excel = Connect-Excel
    #>
    
    try {
        # Try to connect to existing instance
        $excel = [Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
        Write-Host "✓ Connected to existing Excel instance" -ForegroundColor Green
    }
    catch {
        # Create new instance if none exists
        try {
            $excel = New-Object -ComObject Excel.Application
            $excel.Visible = $true
            Write-Host "✓ Created new Excel instance" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to Excel. Ensure Excel is installed."
            return $null
        }
    }
    
    return $excel
}

function Disconnect-Excel {
    <#
    .SYNOPSIS
    Releases COM connection
    #>
    param($Excel)
    
    if ($Excel) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Excel) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Host "✓ Disconnected from Excel" -ForegroundColor Green
    }
}

# ============================================================================
# WORKBOOK OPERATIONS
# ============================================================================

function New-ExcelWorkbook {
    <#
    .SYNOPSIS
    Creates new Excel workbook
    
    .EXAMPLE
    $wb = New-ExcelWorkbook -Excel $excel
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Excel
    )
    
    $workbook = $Excel.Workbooks.Add()
    Write-Host "✓ New workbook created" -ForegroundColor Green
    
    return $workbook
}

function Open-ExcelWorkbook {
    <#
    .SYNOPSIS
    Opens existing workbook
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Excel,
        
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    
    $workbook = $Excel.Workbooks.Open($Path)
    Write-Host "✓ Workbook opened: $Path" -ForegroundColor Green
    
    return $workbook
}

function Save-ExcelWorkbook {
    <#
    .SYNOPSIS
    Saves Excel workbook
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Workbook,
        
        [Parameter(Mandatory=$true)]
        [string]$FilePath
    )
    
    $Workbook.SaveAs($FilePath)
    Write-Host "✓ Workbook saved: $FilePath" -ForegroundColor Green
}

# ============================================================================
# BADGE GENERATION
# ============================================================================

function New-CyberpunkBadge {
    <#
    .SYNOPSIS
    Generates cyberpunk badge in Excel
    
    .EXAMPLE
    New-CyberpunkBadge -Excel $excel -Name "JOHN SMITH" -Title "SECURITY" -ID "SEC-001"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Excel,
        
        [string]$Name = "AGENT NAME",
        [string]$Title = "SECURITY",
        [string]$ID = "A7F3-9182",
        [int]$StartRow = 2,
        [int]$StartCol = 2,
        [string]$OutputPath = ""
    )
    
    # Get or create workbook
    if ($Excel.Workbooks.Count -eq 0) {
        $wb = New-ExcelWorkbook -Excel $Excel
    } else {
        $wb = $Excel.Workbooks.Item(1)
    }
    
    $ws = $wb.Worksheets.Item(1)
    $ws.Name = "ONI_Badges"
    
    # Generate seed
    $seed = New-ONISeed -StylePrefix "CYB"
    Write-Host "Seed: $seed" -ForegroundColor Yellow
    
    # Get random colors from palette
    $primaryColors = @(
        [System.Drawing.Color]::FromArgb(0, 240, 255),    # Cyan
        [System.Drawing.Color]::FromArgb(255, 0, 85),     # Magenta
        [System.Drawing.Color]::FromArgb(176, 38, 255),   # Purple
        [System.Drawing.Color]::FromArgb(57, 255, 20)     # Acid Green
    )
    
    $accentColors = @(
        [System.Drawing.Color]::FromArgb(255, 255, 0),    # Yellow
        [System.Drawing.Color]::FromArgb(0, 255, 136),    # Green
        [System.Drawing.Color]::FromArgb(255, 107, 0)     # Orange
    )
    
    $primaryColor = Get-RandomChoice -Items $primaryColors
    $accentColor = Get-RandomChoice -Items $accentColors
    $bgColor = [System.Drawing.Color]::FromArgb(10, 10, 15)
    
    # Convert colors to Excel RGB
    $primaryRGB = $primaryColor.R + ($primaryColor.G * 256) + ($primaryColor.B * 65536)
    $accentRGB = $accentColor.R + ($accentColor.G * 256) + ($accentColor.B * 65536)
    $bgRGB = $bgColor.R + ($bgColor.G * 256) + ($bgColor.B * 65536)
    
    # Create badge structure (10 rows x 6 columns)
    $badgeRange = $ws.Range($ws.Cells($StartRow, $StartCol), $ws.Cells($StartRow + 9, $StartCol + 5))
    
    # Main border
    $badgeRange.Borders.LineStyle = 1  # xlContinuous
    $badgeRange.Borders.Weight = 4     # xlThick
    $badgeRange.Borders.Color = $primaryRGB
    $badgeRange.Interior.Color = $bgRGB
    
    # Header
    $headerRange = $ws.Range($ws.Cells($StartRow, $StartCol), $ws.Cells($StartRow + 1, $StartCol + 5))
    $headerRange.Merge()
    $headerRange.Value2 = "◢ CYBERPUNK ID ◣"
    $headerRange.Font.Bold = $true
    $headerRange.Font.Size = 14
    $headerRange.Font.Name = "Consolas"
    $headerRange.HorizontalAlignment = -4108  # xlCenter
    $headerRange.VerticalAlignment = -4108
    $headerRange.Interior.Color = $primaryRGB
    $headerRange.Font.Color = $bgRGB
    
    # Photo area
    $photoRange = $ws.Range($ws.Cells($StartRow + 2, $StartCol), $ws.Cells($StartRow + 5, $StartCol + 1))
    $photoRange.Merge()
    $photoRange.Value2 = "█▓▒░ PHOTO ░▒▓█"
    $photoRange.HorizontalAlignment = -4108
    $photoRange.VerticalAlignment = -4108
    $photoRange.Interior.Color = [System.Drawing.Color]::FromArgb(26, 26, 32).ToArgb()
    $photoRange.Font.Color = $primaryRGB
    $photoRange.Font.Size = 10
    $photoRange.Font.Name = "Consolas"
    $photoRange.Borders.LineStyle = 1
    $photoRange.Borders.Color = $accentRGB
    
    # Name label
    $ws.Cells($StartRow + 2, $StartCol + 3).Value2 = "▸ NAME"
    $ws.Cells($StartRow + 2, $StartCol + 3).Font.Bold = $true
    $ws.Cells($StartRow + 2, $StartCol + 3).Font.Color = $accentRGB
    $ws.Cells($StartRow + 2, $StartCol + 3).Font.Size = 9
    
    # Name value
    $nameRange = $ws.Range($ws.Cells($StartRow + 3, $StartCol + 2), $ws.Cells($StartRow + 3, $StartCol + 5))
    $nameRange.Merge()
    $nameRange.Value2 = $Name.ToUpper()
    $nameRange.Font.Bold = $true
    $nameRange.Font.Size = 12
    $nameRange.Font.Color = $primaryRGB
    $nameRange.HorizontalAlignment = -4108
    
    # Title label
    $ws.Cells($StartRow + 4, $StartCol + 3).Value2 = "▸ CLEARANCE"
    $ws.Cells($StartRow + 4, $StartCol + 3).Font.Bold = $true
    $ws.Cells($StartRow + 4, $StartCol + 3).Font.Color = $accentRGB
    $ws.Cells($StartRow + 4, $StartCol + 3).Font.Size = 8
    
    # Title value
    $titleRange = $ws.Range($ws.Cells($StartRow + 5, $StartCol + 2), $ws.Cells($StartRow + 5, $StartCol + 5))
    $titleRange.Merge()
    $titleRange.Value2 = $Title.ToUpper()
    $titleRange.Font.Size = 10
    $titleRange.Font.Color = [System.Drawing.Color]::White.ToArgb()
    $titleRange.HorizontalAlignment = -4108
    
    # ID
    $idRange = $ws.Range($ws.Cells($StartRow + 6, $StartCol), $ws.Cells($StartRow + 6, $StartCol + 5))
    $idRange.Merge()
    $idRange.Value2 = "━━━ ID: $ID ━━━"
    $idRange.Font.Name = "Courier New"
    $idRange.Font.Size = 10
    $idRange.Font.Color = $accentRGB
    $idRange.HorizontalAlignment = -4108
    $idRange.Interior.Color = [System.Drawing.Color]::FromArgb(16, 16, 21).ToArgb()
    
    # Greebles (random decorative elements)
    $greebleChars = @("▪", "▫", "▸", "◂", "●", "○")
    for ($i = 0; $i -lt 3; $i++) {
        $gRow = $StartRow + 7 + (Get-Random -Minimum 0 -Maximum 2)
        $gCol = $StartCol + (Get-Random -Minimum 0 -Maximum 6)
        $ws.Cells($gRow, $gCol).Value2 = Get-RandomChoice -Items $greebleChars
        $ws.Cells($gRow, $gCol).Font.Color = $accentRGB
        $ws.Cells($gRow, $gCol).Font.Size = 8
    }
    
    # Barcode
    $barcodeRange = $ws.Range($ws.Cells($StartRow + 8, $StartCol), $ws.Cells($StartRow + 8, $StartCol + 5))
    $barcodeRange.Merge()
    $barcodeRange.Value2 = "║││║│││║║││║││║│║││"
    $barcodeRange.Font.Name = "Courier New"
    $barcodeRange.Font.Size = 14
    $barcodeRange.Font.Color = [System.Drawing.Color]::Black.ToArgb()
    $barcodeRange.HorizontalAlignment = -4108
    $barcodeRange.Interior.Color = [System.Drawing.Color]::White.ToArgb()
    
    # Footer
    $ws.Cells($StartRow + 9, $StartCol).Value2 = "SEED: $seed"
    $ws.Cells($StartRow + 9, $StartCol).Font.Size = 7
    $ws.Cells($StartRow + 9, $StartCol).Font.Color = [System.Drawing.Color]::Gray.ToArgb()
    
    $ws.Cells($StartRow + 9, $StartCol + 4).Value2 = (Get-Date -Format "MM/yyyy")
    $ws.Cells($StartRow + 9, $StartCol + 4).Font.Size = 7
    $ws.Cells($StartRow + 9, $StartCol + 4).Font.Color = [System.Drawing.Color]::Gray.ToArgb()
    $ws.Cells($StartRow + 9, $StartCol + 4).HorizontalAlignment = -4152  # xlRight
    
    # Auto-fit columns
    $ws.Columns.AutoFit() | Out-Null
    
    # Save if output path provided
    if ($OutputPath) {
        Save-ExcelWorkbook -Workbook $wb -FilePath $OutputPath
    }
    
    Write-Host "`n✓ Cyberpunk badge generated!" -ForegroundColor Green
    Write-Host "  Name: $Name" -ForegroundColor Cyan
    Write-Host "  Title: $Title" -ForegroundColor Cyan
    Write-Host "  ID: $ID" -ForegroundColor Cyan
    Write-Host "  Seed: $seed" -ForegroundColor Yellow
    
    return @{
        Workbook = $wb
        Worksheet = $ws
        Seed = $seed
        Range = $badgeRange
    }
}

function New-MinimalBadge {
    <#
    .SYNOPSIS
    Generates minimal corporate badge in Excel
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Excel,
        
        [string]$Name = "EMPLOYEE NAME",
        [string]$Title = "POSITION",
        [string]$ID = "EMP-001",
        [int]$StartRow = 2,
        [int]$StartCol = 2,
        [string]$OutputPath = ""
    )
    
    # Get or create workbook
    if ($Excel.Workbooks.Count -eq 0) {
        $wb = New-ExcelWorkbook -Excel $Excel
    } else {
        $wb = $Excel.Workbooks.Item(1)
    }
    
    $ws = $wb.Worksheets.Item(1)
    $ws.Name = "ONI_Badges_Minimal"
    
    $seed = New-ONISeed -StylePrefix "MIN"
    Write-Host "Seed: $seed" -ForegroundColor Yellow
    
    $corporateBlue = [System.Drawing.Color]::FromArgb(0, 82, 165).ToArgb()
    $lightGray = [System.Drawing.Color]::FromArgb(245, 245, 245).ToArgb()
    
    # Main badge (10 rows x 6 columns)
    $badgeRange = $ws.Range($ws.Cells($StartRow, $StartCol), $ws.Cells($StartRow + 9, $StartCol + 5))
    $badgeRange.Borders.LineStyle = 1
    $badgeRange.Borders.Weight = 2  # xlMedium
    $badgeRange.Borders.Color = [System.Drawing.Color]::FromArgb(200, 200, 200).ToArgb()
    $badgeRange.Interior.Color = [System.Drawing.Color]::White.ToArgb()
    
    # Header
    $headerRange = $ws.Range($ws.Cells($StartRow, $StartCol), $ws.Cells($StartRow + 1, $StartCol + 5))
    $headerRange.Merge()
    $headerRange.Value2 = "EMPLOYEE BADGE"
    $headerRange.Font.Bold = $true
    $headerRange.Font.Size = 12
    $headerRange.Font.Name = "Calibri"
    $headerRange.HorizontalAlignment = -4108
    $headerRange.VerticalAlignment = -4108
    $headerRange.Interior.Color = $corporateBlue
    $headerRange.Font.Color = [System.Drawing.Color]::White.ToArgb()
    
    # Photo area
    $photoRange = $ws.Range($ws.Cells($StartRow + 2, $StartCol), $ws.Cells($StartRow + 5, $StartCol + 1))
    $photoRange.Merge()
    $photoRange.Value2 = "PHOTO"
    $photoRange.HorizontalAlignment = -4108
    $photoRange.VerticalAlignment = -4108
    $photoRange.Interior.Color = $lightGray
    $photoRange.Font.Color = [System.Drawing.Color]::FromArgb(150, 150, 150).ToArgb()
    
    # Name
    $ws.Cells($StartRow + 2, $StartCol + 3).Value2 = "Name:"
    $ws.Cells($StartRow + 2, $StartCol + 3).Font.Bold = $true
    $ws.Cells($StartRow + 3, $StartCol + 3).Value2 = $Name
    $ws.Cells($StartRow + 3, $StartCol + 3).Font.Bold = $true
    $ws.Cells($StartRow + 3, $StartCol + 3).Font.Size = 11
    
    # Title
    $ws.Cells($StartRow + 4, $StartCol + 3).Value2 = "Title:"
    $ws.Cells($StartRow + 4, $StartCol + 3).Font.Bold = $true
    $ws.Cells($StartRow + 5, $StartCol + 3).Value2 = $Title
    
    # ID
    $idRange = $ws.Range($ws.Cells($StartRow + 6, $StartCol), $ws.Cells($StartRow + 6, $StartCol + 5))
    $idRange.Merge()
    $idRange.Value2 = "ID: $ID"
    $idRange.HorizontalAlignment = -4108
    $idRange.Interior.Color = $lightGray
    
    # Barcode
    $barcodeRange = $ws.Range($ws.Cells($StartRow + 7, $StartCol), $ws.Cells($StartRow + 8, $StartCol + 5))
    $barcodeRange.Merge()
    $barcodeRange.Value2 = "| | || ||| | || | ||| ||"
    $barcodeRange.Font.Name = "Courier New"
    $barcodeRange.Font.Size = 16
    $barcodeRange.HorizontalAlignment = -4108
    
    # Footer
    $ws.Cells($StartRow + 9, $StartCol).Value2 = "Valid: $(Get-Date -Format 'MM/dd/yyyy')"
    $ws.Cells($StartRow + 9, $StartCol).Font.Size = 8
    
    $ws.Columns.AutoFit() | Out-Null
    
    if ($OutputPath) {
        Save-ExcelWorkbook -Workbook $wb -FilePath $OutputPath
    }
    
    Write-Host "`n✓ Minimal badge generated!" -ForegroundColor Green
    Write-Host "  Seed: $seed" -ForegroundColor Yellow
    
    return @{
        Workbook = $wb
        Worksheet = $ws
        Seed = $seed
        Range = $badgeRange
    }
}

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

function New-BatchBadges {
    <#
    .SYNOPSIS
    Generates multiple badges from CSV data
    
    .EXAMPLE
    New-BatchBadges -Excel $excel -CSVPath "employees.csv" -Style "cyberpunk"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Excel,
        
        [Parameter(Mandatory=$true)]
        [string]$CSVPath,
        
        [ValidateSet("cyberpunk", "minimal")]
        [string]$Style = "cyberpunk",
        
        [string]$OutputFolder = "$env:USERPROFILE\Desktop\badges"
    )
    
    if (-not (Test-Path $CSVPath)) {
        Write-Error "CSV file not found: $CSVPath"
        return
    }
    
    # Create output folder
    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder | Out-Null
    }
    
    # Load CSV
    $employees = Import-Csv -Path $CSVPath
    
    Write-Host "Processing $($employees.Count) badges..." -ForegroundColor Cyan
    
    $currentRow = 2
    
    foreach ($emp in $employees) {
        $outputPath = Join-Path $OutputFolder "$($emp.ID)_$($emp.Name -replace ' ','_').xlsx"
        
        if ($Style -eq "cyberpunk") {
            New-CyberpunkBadge -Excel $Excel `
                -Name $emp.Name `
                -Title $emp.Title `
                -ID $emp.ID `
                -StartRow $currentRow `
                -OutputPath $outputPath
        }
        else {
            New-MinimalBadge -Excel $Excel `
                -Name $emp.Name `
                -Title $emp.Title `
                -ID $emp.ID `
                -StartRow $currentRow `
                -OutputPath $outputPath
        }
        
        $currentRow += 12  # Space between badges
        
        Write-Host "  ✓ Generated: $($emp.Name)" -ForegroundColor Green
    }
    
    Write-Host "`n✓ Batch complete! Total: $($employees.Count)" -ForegroundColor Green
}

# ============================================================================
# EXPORT MODULE
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-Excel',
    'Disconnect-Excel',
    'New-ExcelWorkbook',
    'Open-ExcelWorkbook',
    'Save-ExcelWorkbook',
    'New-CyberpunkBadge',
    'New-MinimalBadge',
    'New-BatchBadges'
)

Write-Host "ONI.ExcelAutomation module loaded" -ForegroundColor Green
