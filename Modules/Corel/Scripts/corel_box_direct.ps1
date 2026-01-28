
# ONI Corel Automation - Direct Draw (Native) v6
# Fixes: Manual Dimensions (Lines + Text) for robustness.
# Dimensions: Millimeters.

try {
    Write-Host "1. Initializing CorelDRAW..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    
    $doc = $corel.CreateDocument()
    $doc.Unit = 4 # Millimeters
    $doc.ActivePage.SetSize(297, 420)
    $doc.ActivePage.Orientation = 1 
    
    # --- GRID ---
    Write-Host "2. Creating Grid..."
    $gridLayer = $doc.ActivePage.CreateLayer("GRID_BACKGROUND")
    $gray = $corel.CreateColor()
    $gray.CMYKAssign(0, 0, 0, 20)
    
    for ($x = 0; $x -le 300; $x += 10) { 
        $l = $gridLayer.CreateLineSegment($x, 0, $x, 420)
        $l.Outline.Color = $gray; $l.Outline.Width = 0.1
    }
    for ($y = 0; $y -le 430; $y += 10) { 
        $l = $gridLayer.CreateLineSegment(0, $y, 297, $y)
        $l.Outline.Color = $gray; $l.Outline.Width = 0.1
    }
    $gridLayer.Editable = $false
    
    # --- MOLD ---
    Write-Host "3. Drawing Mold..."
    $moldLayer = $doc.ActivePage.CreateLayer("MOLD_CORTE_VINCO")
    $moldLayer.Activate()
    
    # Vars
    $X0 = 0; $X1 = 95
    $Y0 = 0; $Y1 = 85; $Y2 = 205; $Y3 = 295; $Y4 = 415
    $R = 50
    
    # helper
    function Set-Cut($s) {
        $s.Outline.Color.CMYKAssign(0, 100, 100, 0) # RED
        $s.Outline.Width = 0.2
    }
    
    function Set-Fold($s) {
        $s.Outline.Color.CMYKAssign(0, 0, 0, 100) # BLACK
        try { $s.Outline.Style = 2 } catch { } 
        $s.Outline.Width = 0.2
    }

    Write-Host "   - Outline"
    Set-Cut ($moldLayer.CreateLineSegment($X0, $Y0, $X1, $Y0))
    Set-Cut ($moldLayer.CreateLineSegment($X1, $Y0, $X1, $Y3))
    Set-Cut ($moldLayer.CreateLineSegment($X1, $Y3, $X1, $Y4))
    Set-Cut ($moldLayer.CreateLineSegment($X1, $Y4, $X0 + $R, $Y4))
    Set-Cut ($moldLayer.CreateLineSegment($X0, $Y4 - $R, $X0, $Y2))
    
    Write-Host "   - Arc"
    $cx = $X0 + $R
    $cy = $Y4 - $R
    Set-Cut ($moldLayer.CreateEllipse2($cx, $cy, $R, $R, 90, 180))
    
    Write-Host "   - Flap"
    Set-Cut ($moldLayer.CreateLineSegment($X0, $Y2, $X0 - 80, $Y2 - 5))
    Set-Cut ($moldLayer.CreateLineSegment($X0 - 80, $Y2 - 5, $X0 - 80, $Y1 + 5))
    Set-Cut ($moldLayer.CreateLineSegment($X0 - 80, $Y1 + 5, $X0, $Y1))
    
    Set-Cut ($moldLayer.CreateLineSegment($X0, $Y1, $X0, $Y0))
    
    Write-Host "   - Holes"
    Set-Cut ($moldLayer.CreateEllipse2($X0 + 30, $Y4 - 30, 2.5))
    Set-Cut ($moldLayer.CreateEllipse2($X1 / 2, 20, 2.5))
    
    Write-Host "   - Folds"
    Set-Fold ($moldLayer.CreateLineSegment($X0, $Y1, $X1, $Y1))
    Set-Fold ($moldLayer.CreateLineSegment($X0, $Y2, $X1, $Y2))
    Set-Fold ($moldLayer.CreateLineSegment($X0, $Y3, $X1, $Y3))
    Set-Fold ($moldLayer.CreateLineSegment($X0, $Y1, $X0, $Y2))
    
    # --- COTAS (DIMENSIONS) - MANUAL VECTORS ---
    Write-Host "5. Dimensions (Manual)..."
    $dimLayer = $doc.ActivePage.CreateLayer("COTAS")
    $dimLayer.Activate()
    $green = $corel.CreateColor(); $green.CMYKAssign(100, 0, 100, 0)

    function Add-FakeDimV($x, $y1, $y2, $texContent) {
        $off = 10
        # Main Line
        $l = $dimLayer.CreateLineSegment($x + $off, $y1, $x + $off, $y2)
        $l.Outline.Color = $green; $l.Outline.Width = 0.1
        
        # Ticks (Leaders)
        $t1 = $dimLayer.CreateLineSegment($x, $y1, $x + $off + 2, $y1)
        $t1.Outline.Color = $green; $t1.Outline.Width = 0.1
        $t2 = $dimLayer.CreateLineSegment($x, $y2, $x + $off + 2, $y2)
        $t2.Outline.Color = $green; $t2.Outline.Width = 0.1
        
        # Text
        $midY = ($y1 + $y2) / 2
        # Text at X+12
        $txt = $dimLayer.CreateArtisticText($x + $off + 2, $midY, $texContent)
        $txt.Fill.UniformColor = $green
        try { $txt.Text.Story.Size = 12 } catch { } 
        $txt.RotationAngle = 90
    }
    
    function Add-FakeDimH($y, $x1, $x2, $texContent) {
        $off = -10 # Below
        # Main Line
        $l = $dimLayer.CreateLineSegment($x1, $y + $off, $x2, $y + $off)
        $l.Outline.Color = $green; $l.Outline.Width = 0.1
        
        # Ticks
        $t1 = $dimLayer.CreateLineSegment($x1, $y, $x1, $y + $off - 2)
        $t1.Outline.Color = $green; $t1.Outline.Width = 0.1
        $t2 = $dimLayer.CreateLineSegment($x2, $y, $x2, $y + $off - 2)
        $t2.Outline.Color = $green; $t2.Outline.Width = 0.1
        
        # Text
        $midX = ($x1 + $x2) / 2
        $txt = $dimLayer.CreateArtisticText($midX - 10, $y + $off - 5, $texContent)
        $txt.Fill.UniformColor = $green
        try { $txt.Text.Story.Size = 12 } catch { }
    }

    # Right Side Dims
    Add-FakeDimV $X1 $Y0 $Y1 "85"
    Add-FakeDimV $X1 $Y1 $Y2 "120"
    Add-FakeDimV $X1 $Y2 $Y3 "90"
    Add-FakeDimV $X1 $Y3 $Y4 "120"

    # Bottom
    Add-FakeDimH $Y0 $X0 $X1 "95"
    
    # Flap (Left Side? )
    Add-FakeDimH ($Y1 - 20) ($X0 - 80) $X0 "80"
    
    # R50
    $txt = $dimLayer.CreateArtisticText($X0 + 10, $Y4 - 20, "R50")
    $txt.Fill.UniformColor = $green
    try { $txt.Text.Story.Size = 12 } catch { }
    
    # Group & Center
    Write-Host "4. Centering..."
    $toGroup = $corel.CreateShapeRange()
    $toGroup.AddRange($moldLayer.Shapes.All())
    $toGroup.AddRange($dimLayer.Shapes.All())
    
    if ($toGroup.Count -gt 0) {
        $grp = $toGroup.Group()
        $grp.CenterX = 148.5
        $grp.CenterY = 210.0
    }
    
    Write-Host "Done. Success."
    
}
catch {
    Write-Error "Error: $_"
}
