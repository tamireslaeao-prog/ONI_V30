# ============================================================================
# ONI.Gen.ps1 - Procedural Generation Engine
# Version: 2.0
# Description: Core randomization and generation functions for ONI creativity
# ============================================================================

# Global state for reproducibility
$Script:ONI_CurrentSeed = $null
$Script:ONI_Random = $null

# ============================================================================
# SEED SYSTEM - Reproducible Randomness
# ============================================================================

function New-ONISeed {
    <#
    .SYNOPSIS
    Generates a unique seed for reproducible randomness
    
    .DESCRIPTION
    Creates a seed string in format: ONI-[STYLE]-[DATE]-[HASH]
    Example: ONI-CYB-20260104-A3F7
    #>
    param(
        [string]$StylePrefix = "GEN",
        [string]$CustomSuffix = ""
    )
    
    $date = Get-Date -Format "yyyyMMdd"
    $hash = if ($CustomSuffix) {
        $CustomSuffix
    }
    else {
        -join ((65..90) + (48..57) | Get-Random -Count 4 | ForEach-Object { [char]$_ })
    }
    
    $seed = "ONI-$StylePrefix-$date-$hash"
    Set-ONISeed -Seed $seed
    return $seed
}

function Set-ONISeed {
    <#
    .SYNOPSIS
    Sets the random seed for reproducible generation
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Seed
    )
    
    # Convert seed string to integer for Random object
    $hashCode = 0
    foreach ($char in $Seed.ToCharArray()) {
        $hashCode = ($hashCode * 31 + [int]$char) % [int]::MaxValue
    }
    
    $Script:ONI_CurrentSeed = $Seed
    $Script:ONI_Random = New-Object System.Random($hashCode)
    
    Write-Verbose "ONI Seed set: $Seed (Hash: $hashCode)"
}

function Get-ONISeed {
    <#
    .SYNOPSIS
    Returns current seed
    #>
    return $Script:ONI_CurrentSeed
}

# ============================================================================
# LEVEL 1: BASIC RANDOMIZATION
# ============================================================================

function Get-RandomFloat {
    <#
    .SYNOPSIS
    Generate random float with optional base and deviation
    
    .EXAMPLE
    Get-RandomFloat -Min 0 -Max 1
    # Returns: 0.743
    
    .EXAMPLE
    Get-RandomFloat -Base 500 -Deviation 10
    # Returns: 495.3 (between 490-510)
    #>
    param(
        [double]$Min = 0.0,
        [double]$Max = 1.0,
        [double]$Base = $null,
        [double]$Deviation = $null,
        [int]$Decimals = 2
    )
    
    if ($null -eq $Script:ONI_Random) {
        New-ONISeed | Out-Null
    }
    
    if ($null -ne $Base -and $null -ne $Deviation) {
        $Min = $Base - $Deviation
        $Max = $Base + $Deviation
    }
    
    $value = $Min + ($Script:ONI_Random.NextDouble() * ($Max - $Min))
    return [Math]::Round($value, $Decimals)
}

function Get-RandomInt {
    <#
    .SYNOPSIS
    Generate random integer in range
    #>
    param(
        [int]$Min = 0,
        [int]$Max = 100
    )
    
    if ($null -eq $Script:ONI_Random) {
        New-ONISeed | Out-Null
    }
    
    return $Script:ONI_Random.Next($Min, $Max + 1)
}

function Get-RandomBool {
    <#
    .SYNOPSIS
    Generate random boolean with probability
    
    .EXAMPLE
    Get-RandomBool -Probability 0.3
    # Returns: $true 30% of the time
    #>
    param(
        [double]$Probability = 0.5
    )
    
    return (Get-RandomFloat) -lt $Probability
}

function Get-RandomChoice {
    <#
    .SYNOPSIS
    Select random item from array
    
    .EXAMPLE
    Get-RandomChoice -Items @("Red", "Blue", "Green")
    # Returns: "Blue"
    #>
    param(
        [Parameter(Mandatory = $true)]
        [array]$Items
    )
    
    if ($Items.Count -eq 0) {
        return $null
    }
    
    $index = Get-RandomInt -Min 0 -Max ($Items.Count - 1)
    return $Items[$index]
}

function Get-RandomWeighted {
    <#
    .SYNOPSIS
    Select item based on weights
    
    .EXAMPLE
    $items = @(
        @{Value="Common"; Weight=70},
        @{Value="Rare"; Weight=25},
        @{Value="Epic"; Weight=5}
    )
    Get-RandomWeighted -Items $items
    #>
    param(
        [Parameter(Mandatory = $true)]
        [array]$Items  # Array of hashtables with Value and Weight
    )
    
    $totalWeight = ($Items | Measure-Object -Property Weight -Sum).Sum
    $randomValue = Get-RandomFloat -Min 0 -Max $totalWeight
    
    $cumulative = 0
    foreach ($item in $Items) {
        $cumulative += $item.Weight
        if ($randomValue -le $cumulative) {
            return $item.Value
        }
    }
    
    return $Items[-1].Value
}

# ============================================================================
# LEVEL 2: COLOR GENERATION
# ============================================================================

function Get-RandomColor {
    <#
    .SYNOPSIS
    Generate random color from style palette or custom range
    
    .EXAMPLE
    Get-RandomColor -FromPalette "cyberpunk_v1" -Category "primary"
    # Returns: "#00F0FF"
    
    .EXAMPLE
    Get-RandomColor -HueRange @(180, 240) -Saturation 0.8
    # Returns: Blue-cyan range color
    #>
    param(
        [string]$FromPalette = $null,
        [string]$Category = "primary",
        [array]$HueRange = @(0, 360),
        [double]$Saturation = 1.0,
        [double]$Lightness = 0.5,
        [string]$Format = "hex"  # hex, rgb, hsl
    )
    
    if ($FromPalette) {
        # Load from style database
        $stylePath = "$PSScriptRoot/../data/styles_db.json"
        if (Test-Path $stylePath) {
            $db = Get-Content $stylePath | ConvertFrom-Json
            $style = $db.styles | Where-Object { $_.style_id -eq $FromPalette }
            
            if ($style -and $style.visual_dna.palette.$Category) {
                return Get-RandomChoice -Items $style.visual_dna.palette.$Category
            }
        }
    }
    
    # Generate from HSL
    $hue = Get-RandomInt -Min $HueRange[0] -Max $HueRange[1]
    $sat = $Saturation
    $light = $Lightness
    
    # Convert HSL to RGB
    $c = (1 - [Math]::Abs(2 * $light - 1)) * $sat
    $x = $c * (1 - [Math]::Abs(($hue / 60) % 2 - 1))
    $m = $light - $c / 2
    
    $r = $g = $b = 0
    
    switch ([Math]::Floor($hue / 60)) {
        0 { $r = $c; $g = $x; $b = 0 }
        1 { $r = $x; $g = $c; $b = 0 }
        2 { $r = 0; $g = $c; $b = $x }
        3 { $r = 0; $g = $x; $b = $c }
        4 { $r = $x; $g = 0; $b = $c }
        5 { $r = $c; $g = 0; $b = $x }
    }
    
    $r = [Math]::Round(($r + $m) * 255)
    $g = [Math]::Round(($g + $m) * 255)
    $b = [Math]::Round(($b + $m) * 255)
    
    switch ($Format) {
        "rgb" { return "rgb($r, $g, $b)" }
        "hsl" { return "hsl($hue, $([Math]::Round($sat * 100))%, $([Math]::Round($light * 100))%)" }
        default { return "#{0:X2}{1:X2}{2:X2}" -f $r, $g, $b }
    }
}

function Get-RandomGradient {
    <#
    .SYNOPSIS
    Generate random gradient
    #>
    param(
        [string]$FromPalette = $null,
        [int]$ColorCount = 2,
        [int]$Angle = $null
    )
    
    $colors = @()
    for ($i = 0; $i -lt $ColorCount; $i++) {
        $colors += Get-RandomColor -FromPalette $FromPalette
    }
    
    if ($null -eq $Angle) {
        $Angle = Get-RandomChoice -Items @(0, 45, 90, 135, 180, 225, 270, 315)
    }
    
    return @{
        Colors = $colors
        Angle  = $Angle
        CSS    = "linear-gradient($($Angle)deg, $($colors -join ', '))"
    }
}

function Adjust-ColorBrightness {
    <#
    .SYNOPSIS
    Adjust color brightness
    #>
    param(
        [string]$Color,
        [double]$Factor = 1.2  # 1.0 = no change, >1 = brighter, <1 = darker
    )
    
    # Parse hex color
    $r = [Convert]::ToInt32($Color.Substring(1, 2), 16)
    $g = [Convert]::ToInt32($Color.Substring(3, 2), 16)
    $b = [Convert]::ToInt32($Color.Substring(5, 2), 16)
    
    # Adjust
    $r = [Math]::Min(255, [Math]::Round($r * $Factor))
    $g = [Math]::Min(255, [Math]::Round($g * $Factor))
    $b = [Math]::Min(255, [Math]::Round($b * $Factor))
    
    return "#{0:X2}{1:X2}{2:X2}" -f $r, $g, $b
}

# ============================================================================
# LEVEL 3: GEOMETRIC GENERATION
# ============================================================================

function Get-RandomPoint {
    <#
    .SYNOPSIS
    Generate random point in 2D space
    #>
    param(
        [int]$XMin = 0,
        [int]$XMax = 1000,
        [int]$YMin = 0,
        [int]$YMax = 1000,
        [hashtable]$ExcludeZone = $null  # {X, Y, Width, Height}
    )
    
    do {
        $x = Get-RandomInt -Min $XMin -Max $XMax
        $y = Get-RandomInt -Min $YMin -Max $YMax
        
        if ($ExcludeZone) {
            $inZone = ($x -ge $ExcludeZone.X -and 
                $x -le ($ExcludeZone.X + $ExcludeZone.Width) -and
                $y -ge $ExcludeZone.Y -and 
                $y -le ($ExcludeZone.Y + $ExcludeZone.Height))
            
            if (-not $inZone) { break }
        }
        else {
            break
        }
    } while ($true)
    
    return @{X = $x; Y = $y }
}

function Get-RandomRotation {
    <#
    .SYNOPSIS
    Generate random rotation angle
    #>
    param(
        [string]$Mode = "free",  # free, cardinal (0,90,180,270), diagonal (45,135,225,315)
        [double]$Bias = 0  # Bias towards this angle (0-360)
    )
    
    switch ($Mode) {
        "cardinal" {
            return Get-RandomChoice -Items @(0, 90, 180, 270)
        }
        "diagonal" {
            return Get-RandomChoice -Items @(45, 135, 225, 315)
        }
        default {
            if ($Bias -gt 0) {
                # Return angle biased towards Bias value
                $deviation = Get-RandomFloat -Min -30 -Max 30
                return ($Bias + $deviation) % 360
            }
            return Get-RandomInt -Min 0 -Max 360
        }
    }
}

function Get-RandomSize {
    <#
    .SYNOPSIS
    Generate random size with optional aspect ratio lock
    #>
    param(
        [int]$MinWidth = 50,
        [int]$MaxWidth = 200,
        [int]$MinHeight = $MinWidth,
        [int]$MaxHeight = $MaxWidth,
        [double]$AspectRatio = $null  # If set, locks aspect ratio (e.g., 1.0 for square, 1.77 for 16:9)
    )
    
    $width = Get-RandomInt -Min $MinWidth -Max $MaxWidth
    
    if ($AspectRatio) {
        $height = [Math]::Round($width / $AspectRatio)
    }
    else {
        $height = Get-RandomInt -Min $MinHeight -Max $MaxHeight
    }
    
    return @{Width = $width; Height = $height }
}

# ============================================================================
# LEVEL 4: PATTERN GENERATION
# ============================================================================

function Get-RandomPattern {
    <#
    .SYNOPSIS
    Generate random repeating pattern
    #>
    param(
        [string]$Type = "grid",  # grid, diagonal, hexagon, organic, circuit
        [hashtable]$Bounds = @{Width = 1000; Height = 1000 },
        [int]$Density = 20,
        [double]$Variation = 0.3
    )
    
    $elements = @()
    
    switch ($Type) {
        "grid" {
            $spacing = [Math]::Round($Bounds.Width / $Density)
            
            for ($x = 0; $x -lt $Bounds.Width; $x += $spacing) {
                for ($y = 0; $y -lt $Bounds.Height; $y += $spacing) {
                    $xVar = Get-RandomFloat -Min (-$spacing * $Variation) -Max ($spacing * $Variation)
                    $yVar = Get-RandomFloat -Min (-$spacing * $Variation) -Max ($spacing * $Variation)
                    
                    $elements += @{
                        X    = $x + $xVar
                        Y    = $y + $yVar
                        Type = "point"
                    }
                }
            }
        }
        
        "diagonal" {
            $spacing = [Math]::Round($Bounds.Width / $Density)
            
            for ($offset = - $Bounds.Height; $offset -lt ($Bounds.Width + $Bounds.Height); $offset += $spacing) {
                $elements += @{
                    X1   = $offset
                    Y1   = 0
                    X2   = $offset + $Bounds.Height
                    Y2   = $Bounds.Height
                    Type = "line"
                }
            }
        }
        
        "organic" {
            # Organic blob placement
            for ($i = 0; $i -lt $Density; $i++) {
                $point = Get-RandomPoint -XMax $Bounds.Width -YMax $Bounds.Height
                $size = Get-RandomInt -Min 5 -Max 50
                
                $elements += @{
                    X      = $point.X
                    Y      = $point.Y
                    Radius = $size
                    Type   = "circle"
                }
            }
        }
        
        "circuit" {
            # Tech circuit traces
            $nodeCount = $Density
            $nodes = @()
            
            for ($i = 0; $i -lt $nodeCount; $i++) {
                $nodes += Get-RandomPoint -XMax $Bounds.Width -YMax $Bounds.Height
            }
            
            # Connect nearby nodes
            for ($i = 0; $i -lt $nodes.Count; $i++) {
                $connections = Get-RandomInt -Min 1 -Max 3
                
                for ($c = 0; $c -lt $connections; $c++) {
                    $target = Get-RandomInt -Min 0 -Max ($nodes.Count - 1)
                    if ($target -ne $i) {
                        $elements += @{
                            X1   = $nodes[$i].X
                            Y1   = $nodes[$i].Y
                            X2   = $nodes[$target].X
                            Y2   = $nodes[$target].Y
                            Type = "circuit_trace"
                        }
                    }
                }
            }
        }
    }
    
    return $elements
}

# ============================================================================
# LEVEL 5: GLITCH EFFECTS
# ============================================================================

function Get-RandomGlitch {
    <#
    .SYNOPSIS
    Generate glitch parameters
    #>
    param(
        [string]$Type = "random",  # displacement, chromatic, pixelation, corruption
        [double]$Intensity = 0.5
    )
    
    $glitchTypes = @("displacement", "chromatic", "pixelation", "corruption", "scanline", "rgb_split")
    
    if ($Type -eq "random") {
        $Type = Get-RandomChoice -Items $glitchTypes
    }
    
    $params = @{
        Type      = $Type
        Intensity = $Intensity
    }
    
    switch ($Type) {
        "displacement" {
            $params.OffsetX = Get-RandomInt -Min -20 -Max 20
            $params.OffsetY = Get-RandomInt -Min -10 -Max 10
            $params.BlockHeight = Get-RandomInt -Min 2 -Max 20
        }
        
        "chromatic" {
            $params.RedOffset = Get-RandomInt -Min -5 -Max 5
            $params.GreenOffset = Get-RandomInt -Min -5 -Max 5
            $params.BlueOffset = Get-RandomInt -Min -5 -Max 5
        }
        
        "pixelation" {
            $params.BlockSize = Get-RandomInt -Min 2 -Max 10
            $params.Coverage = Get-RandomFloat -Min 0.1 -Max 0.5
        }
        
        "corruption" {
            $params.CorruptionDensity = Get-RandomFloat -Min 0.01 -Max 0.1
            $params.CorruptionType = Get-RandomChoice -Items @("pixel", "block", "line")
        }
        
        "scanline" {
            $params.LineSpacing = Get-RandomInt -Min 2 -Max 8
            $params.Opacity = Get-RandomFloat -Min 0.1 -Max 0.5
            $params.Jitter = Get-RandomBool -Probability 0.3
        }
        
        "rgb_split" {
            $params.SplitDistance = Get-RandomInt -Min 3 -Max 15
            $params.Angle = Get-RandomInt -Min 0 -Max 360
        }
    }
    
    return $params
}

# ============================================================================
# LEVEL 6: VARIATION SYSTEMS
# ============================================================================

function New-VariationSet {
    <#
    .SYNOPSIS
    Generate multiple variations of same concept
    
    .EXAMPLE
    $variations = New-VariationSet -Count 5 -BaseParams @{
        Color = "#00FFFF"
        Size = 100
    } -VaryParams @("Color", "Size")
    #>
    param(
        [int]$Count = 3,
        [hashtable]$BaseParams = @{},
        [array]$VaryParams = @(),
        [double]$VariationAmount = 0.3
    )
    
    $variations = @()
    
    for ($i = 0; $i -lt $Count; $i++) {
        $variant = $BaseParams.Clone()
        
        foreach ($param in $VaryParams) {
            if ($BaseParams.ContainsKey($param)) {
                $value = $BaseParams[$param]
                
                # Vary based on type
                if ($value -is [int]) {
                    $deviation = [Math]::Round($value * $VariationAmount)
                    $variant[$param] = Get-RandomInt -Min ($value - $deviation) -Max ($value + $deviation)
                }
                elseif ($value -is [double]) {
                    $deviation = $value * $VariationAmount
                    $variant[$param] = Get-RandomFloat -Base $value -Deviation $deviation
                }
                elseif ($value -is [string] -and $value.StartsWith("#")) {
                    # Color variation
                    $variant[$param] = Adjust-ColorBrightness -Color $value -Factor (Get-RandomFloat -Min 0.8 -Max 1.2)
                }
            }
        }
        
        $variations += $variant
    }
    
    return $variations
}

# ============================================================================
# LEVEL 7: GREEBLE GENERATION
# ============================================================================

function Get-RandomGreeble {
    <#
    .SYNOPSIS
    Select random greeble element
    #>
    param(
        [string]$Category = "technical",  # technical, labels, ornamental
        [string]$GreebleDir = "$PSScriptRoot/../assets/greebles"
    )
    
    $categoryPath = Join-Path $GreebleDir $Category
    
    if (Test-Path $categoryPath) {
        $files = Get-ChildItem -Path $categoryPath -Filter "*.svg"
        if ($files.Count -gt 0) {
            return (Get-RandomChoice -Items $files).FullName
        }
    }
    
    # Fallback to procedural greeble
    return Get-ProceduralGreeble -Type $Category
}

function Get-ProceduralGreeble {
    <#
    .SYNOPSIS
    Generate procedural greeble when files not available
    #>
    param(
        [string]$Type = "technical"
    )
    
    $size = Get-RandomInt -Min 10 -Max 30
    $rotation = Get-RandomRotation
    
    $greebleTypes = @{
        technical  = @("screw", "vent", "panel", "rivet")
        labels     = @("barcode", "warning", "serial")
        ornamental = @("circuit", "pattern", "symbol")
    }
    
    $subtype = Get-RandomChoice -Items $greebleTypes[$Type]
    
    return @{
        Type      = $subtype
        Size      = $size
        Rotation  = $rotation
        Generated = $true
    }
}

function Invoke-GreebleSpread {
    <#
    .SYNOPSIS
    Distribute greebles across canvas
    #>
    param(
        [hashtable]$Canvas = @{Width = 1000; Height = 1000 },
        [array]$FocusZones = @(),
        [double]$Density = 0.6,
        [string]$Category = "technical"
    )
    
    $targetCount = [Math]::Round(($Canvas.Width * $Canvas.Height) / 10000 * $Density)
    $placements = @()
    
    for ($i = 0; $i -lt $targetCount; $i++) {
        $point = Get-RandomPoint -XMax $Canvas.Width -YMax $Canvas.Height
        
        # Check if point is in focus zone
        $inFocus = $false
        foreach ($zone in $FocusZones) {
            if ($point.X -ge $zone.X -and $point.X -le ($zone.X + $zone.Width) -and
                $point.Y -ge $zone.Y -and $point.Y -le ($zone.Y + $zone.Height)) {
                $inFocus = $true
                break
            }
        }
        
        if (-not $inFocus) {
            $greeble = Get-RandomGreeble -Category $Category
            $placements += @{
                X        = $point.X
                Y        = $point.Y
                Greeble  = $greeble
                Rotation = Get-RandomRotation
                Scale    = Get-RandomFloat -Min 0.5 -Max 1.5
                Opacity  = Get-RandomFloat -Min 0.3 -Max 0.9
            }
        }
    }
    
    return $placements
}

# ============================================================================
# UTILITIES
# ============================================================================

function Test-ONIRandomness {
    <#
    .SYNOPSIS
    Test randomness distribution
    #>
    param(
        [int]$Iterations = 1000
    )
    
    Write-Host "Testing ONI randomness..." -ForegroundColor Cyan
    
    # Test float distribution
    $floats = 1..$Iterations | ForEach-Object { Get-RandomFloat }
    $avgFloat = ($floats | Measure-Object -Average).Average
    Write-Host "Float average (should be ~0.5): $([Math]::Round($avgFloat, 3))"
    
    # Test bool probability
    $trueCount = (1..$Iterations | ForEach-Object { Get-RandomBool -Probability 0.3 } | Where-Object { $_ }).Count
    $truePercent = $trueCount / $Iterations
    Write-Host "Bool 30% probability result: $([Math]::Round($truePercent * 100, 1))%"
    
    # Test choice distribution
    $choices = 1..$Iterations | ForEach-Object { Get-RandomChoice -Items @("A", "B", "C") }
    $groups = $choices | Group-Object
    Write-Host "Choice distribution:"
    $groups | ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }
}

# ============================================================================
# EXPORT
# ============================================================================

Export-ModuleMember -Function @(
    'New-ONISeed',
    'Set-ONISeed',
    'Get-ONISeed',
    'Get-RandomFloat',
    'Get-RandomInt',
    'Get-RandomBool',
    'Get-RandomChoice',
    'Get-RandomWeighted',
    'Get-RandomColor',
    'Get-RandomGradient',
    'Adjust-ColorBrightness',
    'Get-RandomPoint',
    'Get-RandomRotation',
    'Get-RandomSize',
    'Get-RandomPattern',
    'Get-RandomGlitch',
    'New-VariationSet',
    'Get-RandomGreeble',
    'Get-ProceduralGreeble',
    'Invoke-GreebleSpread',
    'Test-ONIRandomness'
)

# Initialize on module load
New-ONISeed -StylePrefix "GEN" | Out-Null
Write-Verbose "ONI.Gen module loaded. Seed: $(Get-ONISeed)"
