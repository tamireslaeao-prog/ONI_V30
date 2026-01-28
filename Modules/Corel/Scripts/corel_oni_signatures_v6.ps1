# CorelDraw ONI V6 Signatures: "The Big Canvas Fix" (Fixed Color Creation)
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to CorelDRAW..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    
    # 0. Start Fresh
    $doc = $corel.CreateDocument()
    
    # 1. FIX THE CANVAS (A4 Landscape)
    $doc.ActivePage.SetSize(297, 210)
    $doc.Unit = 1 # mm
    Write-Host "Canvas Set to 297x210mm"

    # Function Helper: Create Label
    function Draw-Label ($x, $y, $text) {
        $l = $doc.ActiveLayer.CreateArtisticText($x, $y + 40, $text)
        $l.Text.Story.Size = 10
        # Use simple fill 50% grey
        $l.Fill.UniformColor.CMYKAssign(0, 0, 0, 50)
    }

    # --- CONCEPT 1: THE MONOLITH (Top Left) ---
    Write-Host "1. Monolith..."
    $x = 50; $y = 150
    Draw-Label $x $y "1. MONOLITH"
    
    # Black Box
    $rect = $doc.ActiveLayer.CreateRectangle($x - 30, $y + 15, $x + 30, $y - 15)
    $rect.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
    
    # White Text
    $t1 = $doc.ActiveLayer.CreateArtisticText($x - 22, $y - 5, "ONI")
    $t1.Text.Story.Font = "Impact"
    $t1.Text.Story.Size = 36
    $t1.Fill.UniformColor.CMYKAssign(0, 0, 0, 0) # White
    $t1.OrderToFront()

    # --- CONCEPT 2: THE CIRCUIT (Top Center) ---
    Write-Host "2. Circuit..."
    $x = 148; $y = 150
    Draw-Label $x $y "2. CIRCUIT"
    
    $t2 = $doc.ActiveLayer.CreateArtisticText($x - 15, $y - 5, "ONI")
    $t2.Text.Story.Font = "Courier New"
    $t2.Text.Story.Size = 24
    
    # Fix: Correct Color Creation
    $nodeColor = New-Object -ComObject CorelDRAW.Color
    $nodeColor.CMYKAssign(100, 0, 0, 0) # Cyan
    
    foreach ($offX in @(-25, 25)) {
        foreach ($offY in @(-15, 15)) {
            $n = $doc.ActiveLayer.CreateEllipse($x + $offX - 1, $y + $offY - 1, $x + $offX + 1, $y + $offY + 1)
            $n.Fill.UniformColor = $nodeColor
            $n.Outline.SetNoOutline()
            
            # Line to text center approx ($x, $y)
            $l = $doc.ActiveLayer.CreateLineSegment($x + $offX, $y + $offY, $x, $y)
            $l.Outline.Width = 0.2
            $l.Outline.Color = $nodeColor
            $l.OrderToBack()
        }
    }

    # --- CONCEPT 3: THE ECLIPSE (Top Right) ---
    Write-Host "3. Eclipse..."
    $x = 247; $y = 150
    Draw-Label $x $y "3. ECLIPSE"
    
    # Circle
    $c3 = $doc.ActiveLayer.CreateEllipse($x - 20, $y - 20, $x + 20, $y + 20)
    $c3.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
    $c3.Outline.SetNoOutline()
    
    # Text Overlapping
    $t3 = $doc.ActiveLayer.CreateArtisticText($x - 5, $y - 5, "ONI")
    $t3.Text.Story.Font = "Arial Black"
    $t3.Text.Story.Size = 24
    $t3.Fill.UniformColor.CMYKAssign(0, 0, 0, 0) # White
    $t3.OrderToFront()
    
    # --- CONCEPT 4: THE BLUEPRINT (Bottom Left) ---
    Write-Host "4. Blueprint..."
    $x = 50; $y = 70
    Draw-Label $x $y "4. BLUEPRINT"
    
    $t4 = $doc.ActiveLayer.CreateArtisticText($x - 15, $y - 5, "ONI")
    $t4.Text.Story.Font = "Consolas"
    $t4.Text.Story.Size = 24
    $t4.Fill.UniformColor.CMYKAssign(100, 50, 0, 0) # Blueprint Blue
    
    # Dimension Lines
    $topL = $doc.ActiveLayer.CreateLineSegment($x - 20, $y + 10, $x + 20, $y + 10)
    $topL.Outline.Width = 0.1
    $topL.Outline.Color.CMYKAssign(100, 50, 0, 0)
    try {
        $topL.Outline.EndArrow = 1 
        $topL.Outline.StartArrow = 1
    }
    catch {}

    # --- CONCEPT 5: THE GLITCH (Bottom Center) ---
    Write-Host "5. Glitch..."
    $x = 148; $y = 70
    Draw-Label $x $y "5. GLITCH"
    
    # Cyan Offset
    $t5a = $doc.ActiveLayer.CreateArtisticText($x - 16, $y - 4, "ONI")
    $t5a.Text.Story.Font = "Arial Black"
    $t5a.Text.Story.Size = 24
    $t5a.Fill.UniformColor.CMYKAssign(100, 0, 0, 0)
    try { $t5a.Transparency.ApplyUniformTransparency(50) } catch {}
    
    # Magenta Offset
    $t5b = $doc.ActiveLayer.CreateArtisticText($x - 14, $y - 6, "ONI")
    $t5b.Text.Story.Font = "Arial Black"
    $t5b.Text.Story.Size = 24
    $t5b.Fill.UniformColor.CMYKAssign(0, 100, 0, 0)
    try { $t5b.Transparency.ApplyUniformTransparency(50) } catch {}
    
    # Black Main
    $t5c = $doc.ActiveLayer.CreateArtisticText($x - 15, $y - 5, "ONI")
    $t5c.Text.Story.Font = "Arial Black"
    $t5c.Text.Story.Size = 24
    $t5c.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
    $t5c.OrderToFront()

    # --- CONCEPT 6: THE STAMP (Bottom Right) ---
    Write-Host "6. Stamp..."
    $x = 247; $y = 70
    Draw-Label $x $y "6. STAMP"
    
    # Polygon (6 sides)
    $poly = $doc.ActiveLayer.CreatePolygon($x, $y, $x + 25, $y + 25, 6)
    $poly.Outline.Width = 1.0
    $poly.Outline.Color.CMYKAssign(0, 0, 0, 100)
    $poly.Fill.UniformColor.CMYKAssign(0, 0, 0, 10) # Light Grey
    
    $t6 = $doc.ActiveLayer.CreateArtisticText($x, $y, "ONI")
    # Center text in polygon?
    # Manual approximation for now
    $t6.PositionX = $x - 10
    $t6.PositionY = $y - 5
    
    $t6.Text.Story.Font = "Times New Roman"
    $t6.Text.Story.Size = 20
    $t6.Text.Story.Bold = $true

    # --- FINAL ZOOM FIX ---
    Write-Host "Zooming to Fit..."
    $doc.ActiveWindow.ActiveView.ToFitAllObjects()

    Write-Host "SUCCESS: 6 Signatures Generated."

}
catch {
    Write-Host "COM Error: $_"
    exit 1
}
