# Photoshop ONI V8 Signatures: Pixel Perfect (Fixed V2)
# Fix: Strict Typing and Void Output to prevent op_Addition errors.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to Photoshop..."
    $ps = New-Object -ComObject Photoshop.Application
    $ps.Visible = $true
    $ps.DisplayDialogs = 3 

    # Create Document (1920x1080, 72dpi)
    $doc = $ps.Documents.Add(1920, 1080, 72, "ONI_V8_Signatures", 2, 1)

    # --- COLOR HELPERS ---
    function Get-Color ([int]$r, [int]$g, [int]$b) {
        $color = New-Object -ComObject Photoshop.SolidColor
        $color.RGB.Red = $r
        $color.RGB.Green = $g
        $color.RGB.Blue = $b
        return $color
    }
    
    $black = Get-Color 0 0 0
    $white = Get-Color 255 255 255
    $red = Get-Color 255 0 0
    $cyan = Get-Color 0 255 255
    $green = Get-Color 0 255 0
    $grey = Get-Color 128 128 128

    # --- TEXT HELPER ---
    function Draw-Text ([int]$x, [int]$y, [string]$text, [int]$size, [string]$font, $color, [int]$tracking = 0) {
        $layer = $doc.ArtLayers.Add()
        $layer.Kind = 2 # psTextLayer
        $ti = $layer.TextItem
        $ti.Contents = $text
        $ti.Position = @($x, $y)
        $ti.Size = $size
        try { $ti.Font = $font } catch {} 
        $ti.Color = $color
        try { $ti.Tracking = $tracking } catch {}
        return $layer
    }

    # --- RECT HELPER (Simplified Selection Fill) ---
    function Draw-Rect ([int]$x, [int]$y, [int]$w, [int]$h, $color) {
        # Select takes Array of Arrays (Points)
        $region = @(
            @($x, $y),
            @($x + $w, $y),
            @($x + $w, $y + $h),
            @($x, $y + $h),
            @($x, $y)
        )
        $doc.Selection.Select($region)
        $layer = $doc.ArtLayers.Add()
        $doc.Selection.Fill($color)
        $doc.Selection.Deselect()
    }
    
    # --- LABEL HELPER ---
    function Draw-Label ([int]$x, [int]$y, [string]$text) {
        [void](Draw-Text $x ($y + 150) $text 18 "ArialMT" $grey)
    }

    # ==========================================
    # 1. MODERN STACK
    # ==========================================
    $x = 350; $y = 300
    Write-Host "1. Modern Stack..."
    Draw-Label $x $y "1. MODERN STACK"
    
    [void](Draw-Text ($x - 60) $y "ONI" 72 "Arial-BoldMT" $black)
    [void](Draw-Text ($x - 60) ($y + 25) "SYSTEMS" 18 "ArialMT" $black 300)
    
    # ==========================================
    # 2. THE ACCENT
    # ==========================================
    $x = 960; $y = 300
    Write-Host "2. The Accent..."
    Draw-Label $x $y "2. THE ACCENT"
    
    [void](Draw-Text ($x - 60) $y "oni" 80 "TimesNewRomanPS-BoldMT" $black)
    Draw-Rect ($x + 45) ($y - 15) 15 15 $red

    # ==========================================
    # 3. THE FRAME 
    # ==========================================
    $x = 1570; $y = 300
    Write-Host "3. The Frame..."
    Draw-Label $x $y "3. THE FRAME"
    
    [void](Draw-Text ($x - 40) ($y - 10) "ONI" 48 "Arial-BoldMT" $black)
    
    # Draw Frame
    $bx = $x - 80; $by = $y - 60; $bw = 160; $bh = 80
    $region = @(
        @($bx, $by),
        @($bx + $bw, $by),
        @($bx + $bw, $by + $bh),
        @($bx, $by + $bh),
        @($bx, $by)
    )
    $doc.Selection.Select($region)
    $layer = $doc.ArtLayers.Add()
    # Stroke: Color, Width, Location(2=Inside)
    $doc.Selection.Stroke($black, 3, 2)
    $doc.Selection.Deselect()

    # ==========================================
    # 4. SIDE-BAR TECH
    # ==========================================
    $x = 350; $y = 800
    Write-Host "4. Side-Bar..."
    Draw-Label $x $y "4. SIDE-BAR"
    
    Draw-Rect ($x - 80) ($y - 70) 20 80 $cyan
    [void](Draw-Text ($x - 50) ($y - 20) "ONI" 60 "Arial-BoldMT" $black)
    [void](Draw-Text ($x + 30) ($y + 5) "V17" 24 "ArialMT" $grey)

    # ==========================================
    # 5. THE GHOST
    # ==========================================
    $x = 960; $y = 800
    Write-Host "5. The Ghost..."
    Draw-Label $x $y "5. THE GHOST"
    
    $ghost = Draw-Text ($x - 50) ($y + 20) "O" 120 "TimesNewRomanPS-BoldMT" $grey
    $ghost.Opacity = 20
    
    [void](Draw-Text ($x - 40) $y "ONI" 48 "Arial-BoldMT" $black)

    # ==========================================
    # 6. THE TERMINAL
    # ==========================================
    $x = 1570; $y = 800
    Write-Host "6. The Terminal..."
    Draw-Label $x $y "6. THE TERMINAL"
    
    Draw-Rect ($x - 120) ($y - 50) 240 70 $black
    [void](Draw-Text ($x - 100) ($y - 10) "> ONI_CORE" 36 "CourierNewPS-BoldMT" $green)
    
    Write-Host "SUCCESS: 6 Photoshop Signatures Generated."

}
catch {
    Write-Host "Error: $_"
    exit 1
}
