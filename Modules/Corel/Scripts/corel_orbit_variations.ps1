# CorelDraw Brand: 5 Orbit Variations
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to CorelDRAW..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    
    $doc = $corel.CreateDocument()
    $doc.ActivePage.SetSize(600, 400)
    $doc.Unit = 1 # mm

    # Function to Draw Orbit Brand
    function Draw-Orbit ($x, $y, $name, $col1_cmyk, $col2_cmyk, $fontName, $isBold, $isItalic, $lineWidth, $bg_cmyk, $isInverse) {
        Write-Host "Drawing Variation: $name"
        
        # Background (Optional)
        if ($bg_cmyk) {
            # Note: CreateRectangle using x, y, w, h logic? API is typically (Left, Top, Right, Bottom)
            # x, y is Top-Left for this function's logic
            $bg = $doc.ActiveLayer.CreateRectangle($x - 40, $y + 40, $x + 40, $y - 40)
            $bg.Outline.SetNoOutline()
            $bg.Fill.UniformColor.CMYKAssign($bg_cmyk[0], $bg_cmyk[1], $bg_cmyk[2], $bg_cmyk[3])
        }

        # Arc 1 (Outer) - Color 1
        $arc1 = $doc.ActiveLayer.CreateEllipse($x - 35, $y - 35, $x + 35, $y + 35, 90, 270, $false)
        $arc1.Outline.Width = $lineWidth
        $arc1.Outline.Color.CMYKAssign($col1_cmyk[0], $col1_cmyk[1], $col1_cmyk[2], $col1_cmyk[3])
        
        # Arc 2 (Inner) - Color 2
        $arc2 = $doc.ActiveLayer.CreateEllipse($x - 20, $y - 20, $x + 20, $y + 20, 270, 90, $false)
        $arc2.Outline.Width = $lineWidth
        $arc2.Outline.Color.CMYKAssign($col2_cmyk[0], $col2_cmyk[1], $col2_cmyk[2], $col2_cmyk[3])
        
        # Text "ONI"
        $t = $doc.ActiveLayer.CreateArtisticText($x, $y, "ONI")
        try {
            $t.Text.Story.Font = $fontName
            $t.Text.Story.Size = 24
            $t.Text.Story.Bold = $isBold
            $t.Text.Story.Italic = $isItalic
        }
        catch { Write-Host "Font Warn: $_" }
        
        # Center Text (Approximation via positioning, actual alginment would need bounding box)
        # Manually adjusting X based on expected width is tricky. 
        # Using Align command
        $t.PositionX = $x - 10 # Rough center offset
        $t.PositionY = $y - 5
        
        if ($isInverse) {
            $t.Fill.UniformColor.CMYKAssign(0, 0, 0, 0) # White
        }
        else {
            $t.Fill.UniformColor.CMYKAssign(0, 0, 0, 100) # Black
        }
    }

    # --- VARIATION 1: THE CORE (Original Refined) ---
    # Cyan (100,0,0,0) & Grey (0,0,0,60)
    Draw-Orbit 100 300 "The Core" @(100, 0, 0, 0) @(0, 0, 0, 60) "Arial" $true $false 2 $null $false

    # --- VARIATION 2: CYBER-NEON (Dark Mode) ---
    # Green (50,0,100,0) & Pink (0,100,0,0) on Black (0,0,0,100)
    Draw-Orbit 250 300 "Cyber-Neon" @(50, 0, 100, 0) @(0, 100, 0, 0) "Courier New" $true $false 1 @(0, 0, 0, 100) $true

    # --- VARIATION 3: CORPORATE TRUST (Blue) ---
    # Navy (100,80,0,20) & Silver (0,0,0,20)
    Draw-Orbit 400 300 "Corporate" @(100, 80, 0, 20) @(0, 0, 0, 20) "Times New Roman" $true $false 3 $null $false

    # --- VARIATION 4: SPEED DEMON (Red) ---
    # Red (0,100,100,0) & Black (0,0,0,100)
    Draw-Orbit 100 150 "Speed" @(0, 100, 100, 0) @(0, 0, 0, 100) "Impact" $false $true 4 $null $false

    # --- VARIATION 5: MINIMALIST (Clean) ---
    # Black (0,0,0,100) & Grey (0,0,0,40) Thin
    Draw-Orbit 250 150 "Minimal" @(0, 0, 0, 100) @(0, 0, 0, 40) "Arial" $false $false 1 $null $false

    Write-Host "SUCCESS: 5 Variations Generated."

}
catch {
    Write-Host "COM Error: $_"
    exit 1
}
