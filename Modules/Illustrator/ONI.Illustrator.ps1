# ============================================================================
# ONI.IllustratorAutomation.ps1 - PowerShell Bridge to Adobe Illustrator
# Version: 1.0
# Description: Automate Adobe Illustrator from PowerShell using COM automation
# ============================================================================

# Import ONI modules
if (Test-Path "$PSScriptRoot/ONI.Gen.ps1") {
    Import-Module "$PSScriptRoot/ONI.Gen.ps1" -Force
}

# ============================================================================
# ILLUSTRATOR CONNECTION MANAGEMENT
# ============================================================================

function Connect-Illustrator {
    <#
    .SYNOPSIS
    Establishes COM connection to Adobe Illustrator
    
    .EXAMPLE
    $ai = Connect-Illustrator
    #>
    
    try {
        # Try to connect to existing instance
        $ai = [Runtime.InteropServices.Marshal]::GetActiveObject("Illustrator.Application")
        Write-Host "✓ Connected to existing Illustrator instance" -ForegroundColor Green
    }
    catch {
        # Create new instance if none exists
        try {
            $ai = New-Object -ComObject Illustrator.Application
            $ai.Visible = $true
            Write-Host "✓ Created new Illustrator instance" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to Illustrator. Ensure Adobe Illustrator is installed."
            return $null
        }
    }
    
    return $ai
}

function Disconnect-Illustrator {
    <#
    .SYNOPSIS
    Releases COM connection
    #>
    param($Illustrator)
    
    if ($Illustrator) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Illustrator) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Host "✓ Disconnected from Illustrator" -ForegroundColor Green
    }
}

# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

function New-IllustratorDocument {
    <#
    .SYNOPSIS
    Creates new Illustrator document
    
    .EXAMPLE
    New-IllustratorDocument -AI $ai -Width 90 -Height 140 -Unit "mm"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $AI,
        
        [double]$Width = 210,
        [double]$Height = 297,
        [string]$Unit = "mm",
        [string]$ColorMode = "RGB"  # RGB or CMYK
    )
    
    # Convert to points (Illustrator's internal unit)
    $widthPt = switch ($Unit) {
        "mm" { $Width * 2.834645669 }
        "in" { $Width * 72 }
        default { $Width }
    }
    
    $heightPt = switch ($Unit) {
        "mm" { $Height * 2.834645669 }
        "in" { $Height * 72 }
        default { $Height }
    }
    
    # Create document
    # aiDocumentColorSpace: 1=RGB, 2=CMYK
    $colorSpaceEnum = if ($ColorMode -eq "CMYK") { 2 } else { 1 }
    
    $doc = $AI.Documents.Add($colorSpaceEnum, $widthPt, $heightPt)
    
    Write-Host "✓ Document created: $($Width)x$($Height)$Unit, $ColorMode" -ForegroundColor Green
    
    return $doc
}

function Save-IllustratorDocument {
    <#
    .SYNOPSIS
    Saves Illustrator document
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [Parameter(Mandatory=$true)]
        [string]$FilePath
    )
    
    $Document.SaveAs($FilePath)
    Write-Host "✓ Document saved: $FilePath" -ForegroundColor Green
}

# ============================================================================
# SHAPE CREATION
# ============================================================================

function New-IllustratorRectangle {
    <#
    .SYNOPSIS
    Creates rectangle in Illustrator
    
    .EXAMPLE
    New-IllustratorRectangle -Document $doc -X 10 -Y 10 -Width 50 -Height 30 -FillColor "#FF0000"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [double]$Width = 100,
        [double]$Height = 100,
        [string]$FillColor = "#000000",
        [double]$StrokeWidth = 0,
        [string]$StrokeColor = "#000000",
        [double]$CornerRadius = 0
    )
    
    $layer = $Document.ActiveLayer
    
    # Convert to points
    $xPt = $X * 2.834645669
    $yPt = $Y * 2.834645669
    $wPt = $Width * 2.834645669
    $hPt = $Height * 2.834645669
    
    # Create rectangle
    # In Illustrator, Y coordinates are from bottom, need to adjust
    $rect = $layer.PathItems.Rectangle($yPt, $xPt, $wPt, $hPt)
    
    # Set fill color
    $rgb = ConvertFrom-HexColor -HexColor $FillColor
    $rgbColor = New-Object -ComObject Illustrator.RGBColor
    $rgbColor.Red = $rgb.R
    $rgbColor.Green = $rgb.G
    $rgbColor.Blue = $rgb.B
    
    $rect.Filled = $true
    $rect.FillColor = $rgbColor
    
    # Set stroke
    if ($StrokeWidth -gt 0) {
        $strokeRgb = ConvertFrom-HexColor -HexColor $StrokeColor
        $strokeColor = New-Object -ComObject Illustrator.RGBColor
        $strokeColor.Red = $strokeRgb.R
        $strokeColor.Green = $strokeRgb.G
        $strokeColor.Blue = $strokeRgb.B
        
        $rect.Stroked = $true
        $rect.StrokeColor = $strokeColor
        $rect.StrokeWidth = $StrokeWidth
    } else {
        $rect.Stroked = $false
    }
    
    return $rect
}

function New-IllustratorText {
    <#
    .SYNOPSIS
    Creates text in Illustrator
    
    .EXAMPLE
    New-IllustratorText -Document $doc -X 50 -Y 50 -Text "Hello ONI" -FontFamily "Orbitron" -FontSize 24
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [string]$Text = "Text",
        [string]$FontFamily = "Arial",
        [double]$FontSize = 12,
        [string]$Color = "#000000"
    )
    
    $layer = $Document.ActiveLayer
    
    # Convert to points
    $xPt = $X * 2.834645669
    $yPt = $Y * 2.834645669
    
    # Create text frame
    $textFrame = $layer.TextFrames.Add()
    $textFrame.Contents = $Text
    $textFrame.Top = $yPt
    $textFrame.Left = $xPt
    
    # Set font
    try {
        $textFrame.TextRange.CharacterAttributes.TextFont = $Document.Parent.TextFonts.Item($FontFamily)
    } catch {
        Write-Warning "Font '$FontFamily' not found, using default"
    }
    
    $textFrame.TextRange.CharacterAttributes.Size = $FontSize
    
    # Set color
    $rgb = ConvertFrom-HexColor -HexColor $Color
    $rgbColor = New-Object -ComObject Illustrator.RGBColor
    $rgbColor.Red = $rgb.R
    $rgbColor.Green = $rgb.G
    $rgbColor.Blue = $rgb.B
    
    $textFrame.TextRange.CharacterAttributes.FillColor = $rgbColor
    
    return $textFrame
}

function New-IllustratorCircle {
    <#
    .SYNOPSIS
    Creates circle/ellipse in Illustrator
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [double]$Diameter = 50,
        [string]$FillColor = "#000000",
        [double]$StrokeWidth = 0
    )
    
    $layer = $Document.ActiveLayer
    
    # Convert to points
    $xPt = $X * 2.834645669
    $yPt = $Y * 2.834645669
    $dPt = $Diameter * 2.834645669
    
    # Create ellipse
    $circle = $layer.PathItems.Ellipse($yPt, $xPt, $dPt, $dPt)
    
    # Set fill
    $rgb = ConvertFrom-HexColor -HexColor $FillColor
    $rgbColor = New-Object -ComObject Illustrator.RGBColor
    $rgbColor.Red = $rgb.R
    $rgbColor.Green = $rgb.G
    $rgbColor.Blue = $rgb.B
    
    $circle.Filled = $true
    $circle.FillColor = $rgbColor
    
    # Set stroke
    $circle.Stroked = $StrokeWidth -gt 0
    if ($circle.Stroked) {
        $circle.StrokeWidth = $StrokeWidth
    }
    
    return $circle
}

# ============================================================================
# STYLE APPLICATION
# ============================================================================

function Apply-CyberpunkStyle {
    <#
    .SYNOPSIS
    Applies Cyberpunk style from styles_db.json to Illustrator object
    
    .EXAMPLE
    Apply-CyberpunkStyle -Document $doc -Object $text
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [Parameter(Mandatory=$true)]
        $Object,
        
        [string]$StylePath = "$PSScriptRoot/../data/styles_db.json"
    )
    
    # Load style database
    if (-not (Test-Path $StylePath)) {
        Write-Error "Style database not found: $StylePath"
        return
    }
    
    $styleDb = Get-Content $StylePath | ConvertFrom-Json
    $cyberpunkStyle = $styleDb.styles | Where-Object {$_.style_id -eq "cyberpunk_v1"}
    
    if (-not $cyberpunkStyle) {
        Write-Error "Cyberpunk style not found in database"
        return
    }
    
    # Get random primary color
    $primaryColor = Get-RandomChoice -Items $cyberpunkStyle.visual_dna.palette.primary
    
    # Apply fill color
    $rgb = ConvertFrom-HexColor -HexColor $primaryColor
    $rgbColor = New-Object -ComObject Illustrator.RGBColor
    $rgbColor.Red = $rgb.R
    $rgbColor.Green = $rgb.G
    $rgbColor.Blue = $rgb.B
    
    if ($Object.Filled) {
        $Object.FillColor = $rgbColor
    }
    
    # Apply stroke
    $accentColor = Get-RandomChoice -Items $cyberpunkStyle.visual_dna.palette.accent
    $strokeRgb = ConvertFrom-HexColor -HexColor $accentColor
    $strokeColor = New-Object -ComObject Illustrator.RGBColor
    $strokeColor.Red = $strokeRgb.R
    $strokeColor.Green = $strokeRgb.G
    $strokeColor.Blue = $strokeRgb.B
    
    $Object.Stroked = $true
    $Object.StrokeColor = $strokeColor
    $Object.StrokeWidth = 2
    
    Write-Host "✓ Cyberpunk style applied" -ForegroundColor Cyan
}

# ============================================================================
# BADGE GENERATION
# ============================================================================

function New-CyberpunkBadge {
    <#
    .SYNOPSIS
    Generates complete Cyberpunk badge using ONI system
    
    .EXAMPLE
    $ai = Connect-Illustrator
    New-CyberpunkBadge -AI $ai -Name "JOHN SMITH" -Title "SECURITY"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $AI,
        
        [string]$Name = "AGENT NAME",
        [string]$Title = "CLEARANCE LEVEL",
        [string]$ID = "A7F3-9182",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\badge_cyberpunk.ai"
    )
    
    # Generate seed
    $seed = New-ONISeed -StylePrefix "CYB"
    Write-Host "Seed: $seed" -ForegroundColor Yellow
    
    # Create document
    $doc = New-IllustratorDocument -AI $AI -Width 90 -Height 140 -Unit "mm" -ColorMode "RGB"
    
    # Background
    $bg = New-IllustratorRectangle -Document $doc -X 0 -Y 0 -Width 90 -Height 140 -FillColor "#0A0A0F"
    
    # Main frame
    $color = Get-RandomColor -FromPalette "cyberpunk_v1" -Category "primary"
    $frame = New-IllustratorRectangle -Document $doc -X 5 -Y 5 -Width 80 -Height 130 `
        -FillColor "#00000000" -StrokeWidth 2 -StrokeColor $color
    
    # Photo zone
    $photoFrame = New-IllustratorRectangle -Document $doc -X 15 -Y 15 -Width 60 -Height 80 `
        -FillColor "#1A1A20" -StrokeWidth 1 -StrokeColor $color
    
    $photoText = New-IllustratorText -Document $doc -X 30 -Y 55 -Text "PHOTO 60x80mm" `
        -FontFamily "Arial" -FontSize 14 -Color "#FFFFFF"
    
    # Name field
    $nameText = New-IllustratorText -Document $doc -X 15 -Y 100 -Text $Name `
        -FontFamily "Arial" -FontSize 18 -Color $color
    
    try {
        Apply-CyberpunkStyle -Document $doc -Object $nameText
    } catch {
        Write-Warning "Could not apply full Cyberpunk style: $_"
    }
    
    # Title field
    $titleText = New-IllustratorText -Document $doc -X 15 -Y 110 -Text $Title `
        -FontFamily "Arial" -FontSize 12 -Color "#FFFFFF"
    
    # ID field
    $idText = New-IllustratorText -Document $doc -X 15 -Y 120 -Text "ID: $ID" `
        -FontFamily "Courier New" -FontSize 9 -Color $color
    
    # Random greebles (decorative elements)
    for ($i = 0; $i -lt 10; $i++) {
        $x = Get-RandomInt -Min 5 -Max 85
        $y = Get-RandomInt -Min 5 -Max 135
        $size = Get-RandomInt -Min 2 -Max 8
        
        # Avoid photo area
        if ($x -gt 15 -and $x -lt 75 -and $y -gt 15 -and $y -lt 95) {
            continue
        }
        
        $greebleColor = Get-RandomColor -FromPalette "cyberpunk_v1" -Category "accent"
        
        try {
            $greeble = New-IllustratorCircle -Document $doc -X $x -Y $y -Diameter $size `
                -FillColor $greebleColor
            
            # Apply opacity
            $greeble.Opacity = Get-RandomFloat -Min 30 -Max 80
        } catch {
            Write-Warning "Could not create greeble: $_"
        }
    }
    
    # Save document
    Save-IllustratorDocument -Document $doc -FilePath $OutputPath
    
    Write-Host "`n✓ Cyberpunk badge generated!" -ForegroundColor Green
    Write-Host "  Name: $Name" -ForegroundColor Cyan
    Write-Host "  Title: $Title" -ForegroundColor Cyan
    Write-Host "  ID: $ID" -ForegroundColor Cyan
    Write-Host "  Seed: $seed" -ForegroundColor Yellow
    Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
}

function New-PrintBadge {
    <#
    .SYNOPSIS
    Generates print-ready badge in CMYK
    #>
    param(
        [Parameter(Mandatory=$true)]
        $AI,
        
        [string]$Name = "JOHN SMITH",
        [string]$Title = "EMPLOYEE",
        [string]$EmployeeID = "00000",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\badge_print.ai"
    )
    
    # Create document (ID-1 standard size)
    $doc = New-IllustratorDocument -AI $AI -Width 85.6 -Height 53.98 -Unit "mm" -ColorMode "CMYK"
    
    # Background
    $bg = New-IllustratorRectangle -Document $doc -X 0 -Y 0 -Width 85.6 -Height 53.98 -FillColor "#FFFFFF"
    
    # Photo frame
    $photo = New-IllustratorRectangle -Document $doc -X 5 -Y 5 -Width 25 -Height 30 `
        -FillColor "#D0D0D0" -StrokeWidth 0.5 -StrokeColor "#000000"
    
    # Name
    $nameText = New-IllustratorText -Document $doc -X 35 -Y 15 -Text $Name `
        -FontFamily "Arial" -FontSize 12 -Color "#000000"
    
    # Title
    $titleText = New-IllustratorText -Document $doc -X 35 -Y 23 -Text $Title `
        -FontFamily "Arial" -FontSize 9 -Color "#000000"
    
    # Employee ID
    $idText = New-IllustratorText -Document $doc -X 35 -Y 30 -Text "ID: $EmployeeID" `
        -FontFamily "Arial" -FontSize 8 -Color "#000000"
    
    # Barcode placeholder
    $barcode = New-IllustratorRectangle -Document $doc -X 5 -Y 40 -Width 45 -Height 10 `
        -FillColor "#FFFFFF" -StrokeWidth 0.5 -StrokeColor "#000000"
    
    # Save
    Save-IllustratorDocument -Document $doc -FilePath $OutputPath
    
    Write-Host "`n✓ Print badge generated!" -ForegroundColor Green
    Write-Host "  Format: ID-1 (85.6x53.98mm)" -ForegroundColor Cyan
    Write-Host "  Color Mode: CMYK" -ForegroundColor Cyan
    Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
}

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

function New-BatchBadges {
    <#
    .SYNOPSIS
    Generates multiple badges from CSV data
    
    .EXAMPLE
    New-BatchBadges -AI $ai -CSVPath "employees.csv" -Style "cyberpunk"
    #>
    param(
        [Parameter(Mandatory=$true)]
        $AI,
        
        [Parameter(Mandatory=$true)]
        [string]$CSVPath,
        
        [string]$Style = "cyberpunk",  # cyberpunk or print
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
    
    foreach ($emp in $employees) {
        $outputPath = Join-Path $OutputFolder "$($emp.ID)_$($emp.Name -replace ' ','_').ai"
        
        if ($Style -eq "cyberpunk") {
            New-CyberpunkBadge -AI $AI -Name $emp.Name -Title $emp.Title `
                -ID $emp.ID -OutputPath $outputPath
        }
        else {
            New-PrintBadge -AI $AI -Name $emp.Name -Title $emp.Title `
                -EmployeeID $emp.ID -OutputPath $outputPath
        }
        
        Write-Host "  ✓ Generated: $($emp.Name)" -ForegroundColor Green
        
        # Close document to avoid memory issues
        $AI.ActiveDocument.Close(2) # aiDoNotSaveChanges
    }
    
    Write-Host "`n✓ Batch complete! Total: $($employees.Count)" -ForegroundColor Green
}

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

function Export-IllustratorToPDF {
    <#
    .SYNOPSIS
    Exports Illustrator document to PDF
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [Parameter(Mandatory=$true)]
        [string]$OutputPath
    )
    
    # aiPDFCompatibility1_7 = 13
    $pdfSaveOptions = New-Object -ComObject Illustrator.PDFSaveOptions
    $pdfSaveOptions.Compatibility = 13
    $pdfSaveOptions.PreserveEditability = $false
    
    $Document.SaveAs($OutputPath, $pdfSaveOptions)
    Write-Host "✓ Exported to PDF: $OutputPath" -ForegroundColor Green
}

function Export-IllustratorToPNG {
    <#
    .SYNOPSIS
    Exports Illustrator document to PNG
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [Parameter(Mandatory=$true)]
        [string]$OutputPath,
        
        [int]$DPI = 300
    )
    
    # aiPNG24 = 5
    $exportOptions = New-Object -ComObject Illustrator.ExportOptionsPNG24
    $exportOptions.ArtBoardClipping = $true
    $exportOptions.Transparency = $true
    $exportOptions.HorizontalScale = ($DPI / 72) * 100
    $exportOptions.VerticalScale = ($DPI / 72) * 100
    
    $Document.Export($OutputPath, 5, $exportOptions)
    Write-Host "✓ Exported to PNG ($DPI DPI): $OutputPath" -ForegroundColor Green
}

function Export-IllustratorToSVG {
    <#
    .SYNOPSIS
    Exports Illustrator document to SVG
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Document,
        
        [Parameter(Mandatory=$true)]
        [string]$OutputPath
    )
    
    # aiSVG = 6
    $exportOptions = New-Object -ComObject Illustrator.ExportOptionsSVG
    $exportOptions.EmbedRasterImages = $true
    
    $Document.Export($OutputPath, 6, $exportOptions)
    Write-Host "✓ Exported to SVG: $OutputPath" -ForegroundColor Green
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function ConvertFrom-HexColor {
    <#
    .SYNOPSIS
    Converts hex color to RGB values
    #>
    param([string]$HexColor)
    
    $hex = $HexColor.TrimStart('#')
    
    return @{
        R = [Convert]::ToInt32($hex.Substring(0,2), 16)
        G = [Convert]::ToInt32($hex.Substring(2,2), 16)
        B = [Convert]::ToInt32($hex.Substring(4,2), 16)
    }
}

function Run-IllustratorScript {
    <#
    .SYNOPSIS
    Executes an ExtendScript (.jsx) file in Illustrator
    #>
    param(
        [Parameter(Mandatory=$true)]
        $AI,
        
        [Parameter(Mandatory=$true)]
        [string]$ScriptPath
    )
    
    if (-not (Test-Path $ScriptPath)) {
        Write-Error "Script not found: $ScriptPath"
        return
    }
    
    $AI.DoJavaScript((Get-Content $ScriptPath -Raw))
    Write-Host "✓ Script executed: $ScriptPath" -ForegroundColor Green
}

# ============================================================================
# EXPORT MODULE
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-Illustrator',
    'Disconnect-Illustrator',
    'New-IllustratorDocument',
    'Save-IllustratorDocument',
    'New-IllustratorRectangle',
    'New-IllustratorText',
    'New-IllustratorCircle',
    'Apply-CyberpunkStyle',
    'New-CyberpunkBadge',
    'New-PrintBadge',
    'New-BatchBadges',
    'Export-IllustratorToPDF',
    'Export-IllustratorToPNG',
    'Export-IllustratorToSVG',
    'Run-IllustratorScript'
)

Write-Host "ONI.IllustratorAutomation module loaded" -ForegroundColor Green
Write-Host "Use: Get-Command -Module ONI.IllustratorAutomation" -ForegroundColor Yellow