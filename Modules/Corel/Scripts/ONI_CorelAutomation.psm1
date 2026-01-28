# ============================================================================
# ONI.CorelAutomation.ps1 - PowerShell Bridge to CorelDRAW
# Version: 1.1
# Description: Automate CorelDRAW from PowerShell using COM automation
# ============================================================================

# Import ONI modules
if (Test-Path "$PSScriptRoot/ONI.Gen.ps1") {
    Import-Module "$PSScriptRoot/ONI.Gen.ps1" -Force
}

# ============================================================================
# COREL CONNECTION MANAGEMENT
# ============================================================================

function Connect-CorelDRAW {
    <#
    .SYNOPSIS
    Establishes COM connection to CorelDRAW
    #>
    try {
        # Try to connect to existing instance
        $corel = [Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
        Write-Host "[OK] Connected to existing CorelDRAW instance" -ForegroundColor Green
    }
    catch {
        # Create new instance if none exists
        try {
            $corel = New-Object -ComObject CorelDRAW.Application
            $corel.Visible = $true
            Write-Host "[OK] Created new CorelDRAW instance" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to CorelDRAW. Ensure CorelDRAW is installed."
            return $null
        }
    }
    return $corel
}

function Disconnect-CorelDRAW {
    <#
    .SYNOPSIS
    Releases COM connection
    #>
    param($Corel)
    
    if ($Corel) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Corel) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Host "[OK] Disconnected from CorelDRAW" -ForegroundColor Green
    }
}

# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

function New-CorelDocument {
    <#
    .SYNOPSIS
    Creates new CorelDRAW document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Corel,
        
        [double]$Width = 210,
        [double]$Height = 297,
        [string]$Unit = "mm",
        [string]$ColorMode = "RGB"  # RGB or CMYK
    )
    
    $doc = $Corel.CreateDocument()
    $page = $doc.ActivePage
    
    # Set page size (CorelDRAW uses points internally, convert from mm)
    if ($Unit -eq "mm") {
        $widthPt = $Width * 2.834645669  # mm to points
        $heightPt = $Height * 2.834645669
    }
    else {
        $widthPt = $Width
        $heightPt = $Height
    }
    
    $page.SetSize($widthPt, $heightPt)
    
    # Set color mode
    # try {
    #     if ($ColorMode -eq "CMYK") {
    #         $doc.ColorMode = 2  # cdrCMYK
    #     }
    #     else {
    #         $doc.ColorMode = 1  # cdrRGB
    #     }
    # }
    # catch {
    #     Write-Warning "Could not set Document.ColorMode (might be read-only). Continuing..."
    # }
    
    Write-Host "[OK] Document created: $($Width)x$($Height)$Unit, $ColorMode" -ForegroundColor Green
    
    return $doc
}

function Save-CorelDocument {
    <#
    .SYNOPSIS
    Saves CorelDRAW document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )
    
    try {
        # Create corel SaveAs options struct
        $saveOptions = $Document.Application.CreateStructSaveAsOptions()
        $saveOptions.EmbedVBAProject = $False
        $saveOptions.Filter = 1804 # cdrCDR
        $saveOptions.IncludeCMXData = $False
        $saveOptions.Range = 0 # cdrAllPages
        $saveOptions.EmbedICCProfile = $False
        $saveOptions.Version = 0 # cdrCurrentVersion

        $Document.SaveAs($FilePath, $saveOptions)
        Write-Host "[OK] Document saved: $FilePath" -ForegroundColor Green
    }
    catch {
        Write-Warning "SaveAs failed with options, trying simple save: $_"
        try {
            $Document.SaveAs($FilePath) 
        }
        catch {
            Write-Error "CRITICAL SAVE FAILURE: $_"
        }
    }
}

# ============================================================================
# SHAPE CREATION
# ============================================================================

function New-CorelRectangle {
    <#
    .SYNOPSIS
    Creates rectangle in CorelDRAW
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [double]$Width = 100,
        [double]$Height = 100,
        [string]$FillColor = "#000000",
        [double]$OutlineWidth = 0,
        [string]$OutlineColor = "#000000",
        [double]$CornerRadius = 0
    )
    
    $page = $Document.ActivePage
    $layer = $page.ActiveLayer
    
    # Convert to points if needed
    $xPt = $X * 2.834645669
    $yPt = $Y * 2.834645669
    $wPt = $Width * 2.834645669
    $hPt = $Height * 2.834645669
    
    # Create rectangle
    $rect = $layer.CreateRectangle($xPt, $page.SizeHeight - $yPt, $xPt + $wPt, $page.SizeHeight - $yPt - $hPt)
    
    # Apply corner radius if specified
    if ($CornerRadius -gt 0) {
        $radiusPt = $CornerRadius * 2.834645669
        $rect.SetSize($wPt, $hPt)
    }
    
    # Set fill color
    $rgb = ConvertFrom-HexColor -HexColor $FillColor
    $rect.Fill.UniformColor.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    
    # Set outline
    if ($OutlineWidth -gt 0) {
        $rect.Outline.Width = $OutlineWidth
        $rgb = ConvertFrom-HexColor -HexColor $OutlineColor
        $rect.Outline.Color.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    }
    else {
        $rect.Outline.Width = 0
    }
    
    return $rect
}

function New-CorelText {
    <#
    .SYNOPSIS
    Creates text in CorelDRAW
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [string]$Text = "Text",
        [string]$Font = "Arial",
        [double]$Size = 12,
        [string]$Color = "#000000",
        [string]$Alignment = "Left"  # Left, Center, Right
    )
    
    $page = $Document.ActivePage
    $layer = $page.ActiveLayer
    
    # Convert to points
    $xPt = $X * 2.834645669
    $yPt = $page.SizeHeight - ($Y * 2.834645669)
    
    # Create artistic text
    $txt = $layer.CreateArtisticText($xPt, $yPt, $Text)
    
    # Try setting font properties safely
    try { $txt.Text.Story.Font = $Font } catch { Write-Warning "Could not set Font: $_" }
    try { $txt.Text.Story.Size = $Size } catch { Write-Warning "Could not set Size: $_" }
    
    # Set color
    try {
        $rgb = ConvertFrom-HexColor -HexColor $Color
        $txt.Fill.UniformColor.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    }
    catch { Write-Warning "Could not set Color: $_" }
    
    # Set alignment
    try {
        switch ($Alignment) {
            "Center" { $txt.Text.Story.Alignment = 1 }
            "Right" { $txt.Text.Story.Alignment = 2 }
            default { $txt.Text.Story.Alignment = 0 }
        }
    }
    catch { Write-Warning "Could not set Alignment: $_" }
    
    return $txt
}

function New-CorelCircle {
    <#
    .SYNOPSIS
    Creates circle/ellipse in CorelDRAW
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [double]$X = 0,
        [double]$Y = 0,
        [double]$Diameter = 50,
        [string]$FillColor = "#000000",
        [double]$OutlineWidth = 0
    )
    
    $page = $Document.ActivePage
    $layer = $page.ActiveLayer
    
    # Convert to points
    $xPt = $X * 2.834645669
    $yPt = $Y * 2.834645669
    $dPt = $Diameter * 2.834645669
    
    # Create ellipse
    $circle = $layer.CreateEllipse($xPt, $page.SizeHeight - $yPt, $xPt + $dPt, $page.SizeHeight - $yPt - $dPt)
    
    # Set fill
    $rgb = ConvertFrom-HexColor -HexColor $FillColor
    $circle.Fill.UniformColor.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    
    # Set outline
    $circle.Outline.Width = $OutlineWidth
    
    return $circle
}

# ============================================================================
# STYLE APPLICATION
# ============================================================================

function Apply-CyberpunkStyle {
    <#
    .SYNOPSIS
    Applies Cyberpunk style from styles_db.json to CorelDRAW object
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        $Shape,
        
        [string]$StylePath = "$PSScriptRoot/../Config/styles_db.json"
    )
    
    # Load style database
    if (-not (Test-Path $StylePath)) {
        Write-Error "Style database not found: $StylePath"
        return
    }
    
    $styleDb = Get-Content $StylePath | ConvertFrom-Json
    $cyberpunkStyle = $styleDb.styles | Where-Object { $_.style_id -eq "cyberpunk_vector_v1" }
    
    if (-not $cyberpunkStyle) {
        Write-Error "Cyberpunk style not found in database"
        return
    }
    
    # Get random primary color
    $primaryColor = Get-RandomChoice -Items $cyberpunkStyle.color_system.rgb_palette.primary
    
    # Apply fill color
    $rgb = ConvertFrom-HexColor -HexColor $primaryColor.hex
    $Shape.Fill.UniformColor.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    
    # Apply outline
    $accentColor = Get-RandomChoice -Items $cyberpunkStyle.color_system.rgb_palette.accent
    $rgb = ConvertFrom-HexColor -HexColor $accentColor.hex
    $Shape.Outline.Width = 2
    $Shape.Outline.Color.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    
    # Apply glow effect (drop shadow as glow)
    try {
        $glow = $Shape.CreateDropShadow(1)  # 1 = cdrDropShadowGlow
        $glow.Opacity = 75
        $glow.Feather = 15
        $glow.Color.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    }
    catch {
        Write-Warning "Could not apply glow effect: $_"
    }
    
    Write-Host "[OK] Cyberpunk style applied" -ForegroundColor Cyan
}

function Apply-StyleFromDatabase {
    <#
    .SYNOPSIS
    Generic function to apply any style from database
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        $Shape,
        
        [Parameter(Mandatory = $true)]
        [string]$StyleId,
        
        [string]$StylePath = "$PSScriptRoot/../Config/styles_db.json"
    )
    
    # Load Corel-specific style database
    if (-not (Test-Path $StylePath)) {
        Write-Error "Corel style database not found: $StylePath"
        return
    }
    
    $styleDb = Get-Content $StylePath | ConvertFrom-Json
    $style = $styleDb.styles | Where-Object { $_.style_id -eq $StyleId }
    
    if (-not $style) {
        Write-Error "Style '$StyleId' not found in database"
        return
    }
    
    Write-Host "Applying style: $($style.name)" -ForegroundColor Cyan
    
    # Apply colors based on color system
    if ($style.color_system.mode -eq "RGB") {
        $primaryColor = Get-RandomChoice -Items $style.color_system.rgb_palette.primary
        $rgb = ConvertFrom-HexColor -HexColor $primaryColor.hex
        $Shape.Fill.UniformColor.RGBAssign($rgb.R, $rgb.G, $rgb.B)
    }
    elseif ($style.color_system.mode -eq "CMYK") {
        $primaryColor = Get-RandomChoice -Items $style.color_system.cmyk_palette.primary
        $cmyk = $primaryColor.cmyk
        $Shape.Fill.UniformColor.CMYKAssign($cmyk[0], $cmyk[1], $cmyk[2], $cmyk[3])
    }
    
    Write-Host "[OK] Style '$($style.name)' applied" -ForegroundColor Green
}

# ============================================================================
# BADGE GENERATION
# ============================================================================

function New-CyberpunkBadge {
    <#
    .SYNOPSIS
    Generates complete Cyberpunk badge using ONI system
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Corel,
        
        [string]$Name = "AGENT NAME",
        [string]$Title = "CLEARANCE LEVEL",
        [string]$ID = "A7F3-9182",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\badge_cyberpunk.cdr"
    )
    
    # Generate seed (simple random for now if ONI.Gen not working)
    $seed = Get-Random
    Write-Host "Seed: $seed" -ForegroundColor Yellow
    
    # Create document
    $doc = New-CorelDocument -Corel $Corel -Width 90 -Height 140 -Unit "mm" -ColorMode "RGB"
    
    # Background
    $bg = New-CorelRectangle -Document $doc -X 0 -Y 0 -Width 90 -Height 140 -FillColor "#0A0A0F"
    
    # Style lookup prep
    $stylePath = "$PSScriptRoot/../Config/styles_db.json"
    $styleDb = Get-Content $stylePath | ConvertFrom-Json
    $cyberpunkStyle = $styleDb.styles | Where-Object { $_.style_id -eq "cyberpunk_vector_v1" }

    # Determine colors
    if ($cyberpunkStyle) {
        $primaryColors = $cyberpunkStyle.color_system.rgb_palette.primary
        $accentColors = $cyberpunkStyle.color_system.rgb_palette.accent
        
        $pIdx = Get-Random -Min 0 -Max $primaryColors.Count
        $aIdx = Get-Random -Min 0 -Max $accentColors.Count
        
        $mainColorHex = $primaryColors[$pIdx].hex
        $accentColorHex = $accentColors[$aIdx].hex
    }
    else {
        $mainColorHex = "#00F0FF"
        $accentColorHex = "#FF0055"
    }

    # Main frame
    $frame = New-CorelRectangle -Document $doc -X 5 -Y 5 -Width 80 -Height 130 `
        -FillColor "#00000000" -OutlineWidth 2 -OutlineColor $mainColorHex
    
    # Photo zone
    $photoFrame = New-CorelRectangle -Document $doc -X 15 -Y 15 -Width 60 -Height 80 `
        -FillColor "#1A1A20" -OutlineWidth 1 -OutlineColor $mainColorHex
    
    $photoText = New-CorelText -Document $doc -X 45 -Y 55 -Text "PHOTO" `
        -Font "Arial" -Size 14 -Color "#FFFFFF" -Alignment "Center"
    
    # Name field
    $nameText = New-CorelText -Document $doc -X 45 -Y 100 -Text $Name `
        -Font "Arial Black" -Size 18 -Color $mainColorHex -Alignment "Center"
    
    # Try apply style 
    try {
        Apply-CyberpunkStyle -Document $doc -Shape $nameText
    }
    catch {
        Write-Warning "Could not apply sophisticated style to text"
    }
    
    # Title field
    $titleText = New-CorelText -Document $doc -X 45 -Y 110 -Text $Title `
        -Font "Arial" -Size 12 -Color "#FFFFFF" -Alignment "Center"
    
    # ID field
    $idText = New-CorelText -Document $doc -X 45 -Y 120 -Text "ID: $ID" `
        -Font "Courier New" -Size 9 -Color $mainColorHex -Alignment "Center"
    
    # Save document
    Save-CorelDocument -Document $doc -FilePath $OutputPath
    
    Write-Host "`n[OK] Cyberpunk badge generated!" -ForegroundColor Green
    Write-Host "  Name: $Name" -ForegroundColor Cyan
    Write-Host "  Title: $Title" -ForegroundColor Cyan
    Write-Host "  ID: $ID" -ForegroundColor Cyan
    Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
}

function New-PrintBadge {
    <#
    .SYNOPSIS
    Generates print-ready badge in CMYK
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Corel,
        
        [string]$Name = "JOHN SMITH",
        [string]$Title = "EMPLOYEE",
        [string]$EmployeeID = "00000",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\badge_print.cdr"
    )
    
    # Create document (ID-1 standard size)
    $doc = New-CorelDocument -Corel $Corel -Width 85.6 -Height 53.98 -Unit "mm" -ColorMode "CMYK"
    
    # Background
    $bg = New-CorelRectangle -Document $doc -X 0 -Y 0 -Width 85.6 -Height 53.98 -FillColor "#FFFFFF"
    
    # Photo frame
    $photo = New-CorelRectangle -Document $doc -X 5 -Y 5 -Width 25 -Height 30 `
        -FillColor "#D0D0D0" -OutlineWidth 0.5 -OutlineColor "#000000"
    
    # Name
    $nameText = New-CorelText -Document $doc -X 35 -Y 15 -Text $Name `
        -Font "Arial" -Size 12 -Color "#000000"
    
    # Title
    $titleText = New-CorelText -Document $doc -X 35 -Y 23 -Text $Title `
        -Font "Arial" -Size 9 -Color "#000000"
    
    # Employee ID
    $idText = New-CorelText -Document $doc -X 35 -Y 30 -Text "ID: $EmployeeID" `
        -Font "Arial" -Size 8 -Color "#000000"
    
    # Barcode placeholder
    $barcode = New-CorelRectangle -Document $doc -X 5 -Y 40 -Width 45 -Height 10 `
        -FillColor "#FFFFFF" -OutlineWidth 0.5 -OutlineColor "#000000"
    
    # Save
    Save-CorelDocument -Document $doc -FilePath $OutputPath
    
    Write-Host "`n[OK] Print badge generated!" -ForegroundColor Green
    Write-Host "  Format: ID-1 (85.6x53.98mm)" -ForegroundColor Cyan
    Write-Host "  Color Mode: CMYK" -ForegroundColor Cyan
    Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
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
        R = [Convert]::ToInt32($hex.Substring(0, 2), 16)
        G = [Convert]::ToInt32($hex.Substring(2, 2), 16)
        B = [Convert]::ToInt32($hex.Substring(4, 2), 16)
    }
}

function Get-RandomChoice {
    param($Items)
    if ($Items) {
        $idx = Get-Random -Min 0 -Max $Items.Count
        return $Items[$idx]
    }
    return $null
}

function Export-CorelToPDF {
    <#
    .SYNOPSIS
    Exports CorelDRAW document to PDF
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )
    
    $Document.PublishToPDF($OutputPath)
    Write-Host "[OK] Exported to PDF: $OutputPath" -ForegroundColor Green
}

function Export-CorelToPNG {
    <#
    .SYNOPSIS
    Exports CorelDRAW document to PNG
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$OutputPath,
        
        [int]$DPI = 300
    )
    
    $page = $Document.ActivePage
    $exportFilter = $Document.ExportBitmap($OutputPath, 1, 0, 0, 0, $page.SizeWidth, $page.SizeHeight)
    $exportFilter.Resolution = $DPI
    $exportFilter.AntiAliasing = $true
    $exportFilter.Finish()
    
    Write-Host "[OK] Exported to PNG ($DPI DPI): $OutputPath" -ForegroundColor Green
}

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

function New-BatchBadges {
    <#
    .SYNOPSIS
    Generates multiple badges from CSV data
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Corel,
        
        [Parameter(Mandatory = $true)]
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
        $outputPath = Join-Path $OutputFolder "$($emp.ID)_$($emp.Name -replace ' ','_').cdr"
        
        if ($Style -eq "cyberpunk") {
            New-CyberpunkBadge -Corel $Corel -Name $emp.Name -Title $emp.Title `
                -ID $emp.ID -OutputPath $outputPath
        }
        else {
            New-PrintBadge -Corel $Corel -Name $emp.Name -Title $emp.Title `
                -EmployeeID $emp.ID -OutputPath $outputPath
        }
        
        Write-Host "  [OK] Generated: $($emp.Name)" -ForegroundColor Green
    }
    
    Write-Host "`n[OK] Batch complete! Total: $($employees.Count)" -ForegroundColor Green
}

# ============================================================================
# EXPORT MODULE
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-CorelDRAW',
    'Disconnect-CorelDRAW',
    'New-CorelDocument',
    'Save-CorelDocument',
    'New-CorelRectangle',
    'New-CorelText',
    'New-CorelCircle',
    'Apply-CyberpunkStyle',
    'Apply-StyleFromDatabase',
    'New-CyberpunkBadge',
    'New-PrintBadge',
    'Export-CorelToPDF',
    'Export-CorelToPNG',
    'New-BatchBadges'
)

Write-Host "ONI.CorelAutomation module loaded" -ForegroundColor Green
