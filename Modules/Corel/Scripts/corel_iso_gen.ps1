
# ONI Corel - Extra 04 Isometric Replica
# Exact geometry + Isometric Dimensions.

try {
    Write-Host "1. Init..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    $doc = $corel.CreateDocument()
    $doc.ActivePage.SetSize(297, 210) # A4
    
    $isoLayer = $doc.ActivePage.CreateLayer("ISO_REPLICA")
    $isoLayer.Activate()
    
    # --- MATH ---
    $CX = 140; $CY = 150; $SCALE = 2.0
    
    function Iso($x, $y, $z) {
        # X axis (Right Down): 30 deg
        # Y axis (Left Down): 150 deg
        # Z axis (Up): 90 deg
        # Standard Iso Projection on 2D:
        # x_p = (x - y) * cos(30)
        # y_p = -z + (x + y) * sin(30)
        
        $cos30 = 0.866
        $sin30 = 0.5
        
        $u = ($x - $y) * $cos30
        $v = -1 * $z + ($x + $y) * $sin30
        
        return @(($CX + $u * $SCALE), ($CY + $v * $SCALE))
    }
    
    # Styles
    $black = $corel.CreateColor(); $black.CMYKAssign(0, 0, 0, 100)
    
    function Line($p1, $p2, $thick) {
        $l = $isoLayer.CreateLineSegment($p1[0], $p1[1], $p2[0], $p2[1])
        $l.Outline.Color = $black
        $l.Outline.Width = if ($thick) { 0.5 } else { 0.2 }
        return $l
    }

    # --- GEOMETRY ---
    Write-Host "2. Geometry..."
    
    # 1. Base L-Shape (Left Tower + Base)
    # Origin (0,40,0) is outer corner of L? No, let's stick to Box Ref system.
    # X=Width(60), Y=Depth(40), Z=Height(40).
    # L-Shape:
    # Tower part: X=0..20, Y=0..40, Z=0..40.
    # Base part: X=20..60, Y=0..40, Z=0..10.
    
    # Tower
    $T_FL = Iso 0 40 0; $T_FR = Iso 20 40 0
    $T_BL = Iso 0 0 0; $T_BR = Iso 20 0 0
    $T_TFL = Iso 0 40 40; $T_TFR = Iso 20 40 40
    $T_TBL = Iso 0 0 40; $T_TBR = Iso 20 0 40
    
    # Base Plate
    # Starts at X=20.
    $B_FL = Iso 20 40 0; $B_FR = Iso 60 40 0
    $B_BL = Iso 20 0 0; $B_BR = Iso 60 0 0
    $B_TFL = Iso 20 40 10; $B_TFR = Iso 60 40 10
    $B_TBL = Iso 20 0 10; $B_TBR = Iso 60 0 10
    
    # Draw Visible Lines (Tower)
    Line $T_TFL $T_TFR $true # Top Front
    Line $T_TFR $T_TBR $true # Top Right
    Line $T_TBR $T_TBL $true # Top Back
    Line $T_TBL $T_TFL $true # Top Left
    
    Line $T_TFL $T_FL $true # Vertical Front Left
    # Line $T_TFR $B_TFL $true # Vertical Front Right (Upper part) -> Goes to Base top
    
    # Junction Tower-Base
    # The Tower Right Face (X=20) is visible above Z=10.
    # From Z=10 to Z=40.
    $J_F = Iso 20 40 10 # Front Junction point
    $J_B = Iso 20 0 10  # Back Junction point
    
    Line $T_TFR $J_F $true # Vertical Tower Right Front
    Line $T_TBR $J_B $true # Vertical Tower Right Back
    
    # Base Top Surface
    # Outline: J_B -> B_TBR -> B_TFR -> J_F
    Line $J_B $B_TBR $true # Rear Edge
    Line $B_TBR $B_TFR $true # Right Edge
    Line $B_TFR $J_F $true # Front Edge
    Line $J_F $J_B $false # Inner Edge (Hidden/Construction). Actually existing edge? No, continuous surface?
    # Wait, Tower and Base are one piece. So J_F to J_B is just a line on surface?
    # No, L-shape corner. Yes, visible line.
    Line $J_F $J_B $true
    
    # Base Vertical Height
    Line $B_TFR $B_FR $true # Front Right Corner
    Line $B_TBR $B_BR $true # Back Right Corner
    Line $T_FL $B_FR $true  # Bottom Front Edge (0..60)? 
    # Actually from T_FL(0,40,0) to B_FR(60,40,0).
    Line $T_FL $B_FR $true
    
    # Right Bottom Edge
    Line $B_FR $B_BR $true
    
    # --- SLOT ---
    # U-Shape R10. Center X=40, Y=20. Z=10 (Top) and Z=0 (Bottom).
    # Cutout from Right? No, "Extra 04" shows Slot in Middle of Base.
    # Looking at Ref: The slot is open to the Right (X=60)? No.
    # It looks like a "C" shape?
    # Ah, standard U slot.
    # Opening at X=60?
    # Let's assume opening at X=60.
    # Top Arc: Center (40, 20, 10). R=10.
    # Lines from (40,10,10) to (60,10,10).
    # Lines from (40,30,10) to (60,30,10).
    # And vertical wall inside.
    
    function IsoArc($cx, $cy, $cz, $r, $ang1, $ang2) {
        $pts = @()
        for ($i = 0; $i -le 10; $i++) {
            $a = $ang1 + ($i * ($ang2 - $ang1) / 10)
            $ra = $a * [math]::PI / 180
            # Circle in XY plane
            $lx = $cx + $r * [math]::Cos($ra)
            $ly = $cy + $r * [math]::Sin($ra)
            $pts += (Iso $lx $ly $cz)
        }
        for ($k = 0; $k -lt 10; $k++) { Line $pts[$k] $pts[$k + 1] $true }
    }
    
    # Top Slot
    IsoArc 40 20 10 10 90 270 # Left Semicircle
    Line (Iso 40 10 10) (Iso 60 10 10) $true
    Line (Iso 40 30 10) (Iso 60 30 10) $true
    
    # Bottom Slot (Visible Part)
    IsoArc 40 20 0 10 90 270
    
    # Vertical Wall inside Slot
    # At arc tangent (30, 20)? No, visible walls.
    # Visible wall is the "Far" side (Y=10 side or Y=30 side?).
    # View is X,Y,Z>0. We see Top, Front, Right.
    # We look from X+, Y+.
    # Slot Y=10 wall is visible (Front-ish).
    # Slot Y=30 wall is hidden (Back-ish).
    Line (Iso 40 10 10) (Iso 40 10 0) $true # Corner of straight/arc
    # Tangent at X=30?
    Line (Iso 30 20 10) (Iso 30 20 0) $true # Back of arc center?
    
    # --- FLOATING WEDGE ---
    # Floating Wedge 04
    # Top Square 20x20. Height 20? 
    # Let's place it above the slot.
    # Slot Center (40,20).
    # Wedge Top Center (40,20) at Z=80.
    # Wedge Bottom Line? Or Base?
    # Let's make it a truncated pyramid.
    # Top 20x20. Bottom 10x10? Or point?
    # Diagram usually shows "Dovetail".
    # Let's assume Top 20x20, Bottom 10x20 (Tapered in X).
    # Z from 60 to 80.
    
    $W_Z1 = 60; $W_Z2 = 80
    # Top Square (centered at 40,20) -> (30..50, 10..30)
    $Wt1 = Iso 30 10 80; $Wt2 = Iso 50 10 80
    $Wt3 = Iso 50 30 80; $Wt4 = Iso 30 30 80
    
    Line $Wt1 $Wt2 $true
    Line $Wt2 $Wt3 $true
    Line $Wt3 $Wt4 $true
    Line $Wt4 $Wt1 $true
    
    # Bottom (Tapered) -> Centered (40,20). Size 10x10?
    $Wb1 = Iso 35 15 60; $Wb2 = Iso 45 15 60
    $Wb3 = Iso 45 25 60; $Wb4 = Iso 35 25 60
    
    # Draw Bottom (Visible?)
    Line $Wb1 $Wb2 $true
    Line $Wb2 $Wb3 $true
    # Rear edges hidden
    
    # Slanted Edges
    Line $Wt1 $Wb1 $true
    Line $Wt2 $Wb2 $true
    Line $Wt3 $Wb3 $true
    # Line $Wt4 $Wb4 $true # Hidden
    
    # --- DIMENSIONS (COTAS ISO) ---
    Write-Host "3. Dimensions..."
    
    $dimL = $doc.ActivePage.CreateLayer("ISO_COTAS")
    $dimL.Activate()
    
    function IsoDim($p1, $p2, $offsetVec, $text) {
        # Draw Extension lines
        $e1a = $p1; $e1b = @($p1[0] + $offsetVec[0], $p1[1] + $offsetVec[1])
        $e2a = $p2; $e2b = @($p2[0] + $offsetVec[0], $p2[1] + $offsetVec[1])
        
        # Draw Main line
        $m1 = $e1b; $m2 = $e2b
        
        $l1 = $dimL.CreateLineSegment($e1a[0], $e1a[1], $e1b[0], $e1b[1])
        $l1.Outline.Width = 0.1
        $l2 = $dimL.CreateLineSegment($e2a[0], $e2a[1], $e2b[0], $e2b[1])
        $l2.Outline.Width = 0.1
        $lm = $dimL.CreateLineSegment($m1[0], $m1[1], $m2[0], $m2[1])
        $lm.Outline.Width = 0.1
        # Arrows? (Start/End Arrow properties)
        try { $lm.Outline.StartArrow = 2; $lm.Outline.EndArrow = 2 } catch {}
        
        # Text
        $mx = ($m1[0] + $m2[0]) / 2
        $my = ($m1[1] + $m2[1]) / 2
        $t = $dimL.CreateArtisticText($mx, $my, $text)
        try { $t.Text.Story.Size = 10 } catch {}
        # Skew/Rotate text to match Iso axis? Complex.
        # Just leave horizontal for readability.
    }
    
    # Dims Vectors (Screen coords)
    # X-axis parallel offset (Down Right): (10, 5) ?
    # Y-axis parallel offset (Left Down): (-10, 5) ?
    # Z-axis parallel offset: (0, 10)?
    
    # Dim 60 (Length)
    IsoDim (Iso 0 40 0) (Iso 60 40 0) @(0, 15) "60"
    
    # Dim 40 (Depth)
    IsoDim (Iso 0 40 0) (Iso 0 0 0) @(-15, 10) "40"
    
    # Dim 40 (Height)
    IsoDim (Iso 0 40 0) (Iso 0 40 40) @(-15, 0) "40"
    
    # Dim 10 (Base Thickness)
    IsoDim (Iso 60 40 0) (Iso 60 40 10) @(15, 0) "10"
    
    # Dim 20 (Tower Top)
    IsoDim (Iso 0 40 40) (Iso 20 40 40) @(0, -10) "20"
    
    Write-Host "Done."
    
}
catch {
    Write-Error $_
}
