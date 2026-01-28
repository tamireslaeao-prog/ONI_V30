# ONI Automation: Slotted Block (CorelDRAW Isometric)
# Target: CorelDRAW 2024 (via COM)
# Strategy: 2.5D Construction (Isometric Math)

$ErrorActionPreference = "Stop"

# --- CONFIG ---
# Scale Factor (mm to Corel units approx, or just draw 1:1 in mm)
# Corel uses inches internally often, but we can set units.
# Simple way: Calculate values and multiply by a scale for visibility.
$Scale = 2.0  # Double size for better visibility
$OriginX = 100.0
$OriginY = 100.0

# --- ISOMETRIC MATH ---
# X Axis (Right-Up): 30 deg
# Y Axis (Left-Up): 150 deg  (Depth)
# Z Axis (Up): 90 deg
$Rag30 = [Math]::PI / 6
$Rag150 = 5 * [Math]::PI / 6
$Rag90 = [Math]::PI / 2

# Vectors per unit
$vx_x = [Math]::Cos($Rag30)
$vx_y = [Math]::Sin($Rag30)

$vy_x = [Math]::Cos($Rag150)
$vy_y = [Math]::Sin($Rag150)

$vz_x = 0
$vz_y = 1

function Get-IsoPoint ($x, $y, $z) {
    # Returns [u, v] screen coords relative to Origin
    # x goes along X vector, y along Y vector, z along Z vector
    # In the drawing conventions:
    # Length (50) is along "Right" axis (our X).
    # Depth (15) is along "Left" axis (our Y).
    # Height (30) is along "Up" axis (our Z).
    
    $u = $OriginX + $Scale * ($x * $vx_x + $y * $vy_x + $z * $vz_x)
    $v = $OriginY + $Scale * ($x * $vx_y + $y * $vy_y + $z * $vz_y)
    return @($u, $v)
}

try {
    Write-Host "Connecting to CorelDRAW..." -ForegroundColor Cyan
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    $doc = $corel.CreateDocument()
    $doc.Unit = 4 # mm
    $layer = $doc.ActiveLayer

    # --- GEOMETRY DEFINITION ---
    # Slotted Block:
    # 0 < x < 50
    # 0 < y < 15
    # 0 < z < 30
    
    # Vertices (Front Face, y=0)
    # The slot is at the X=0 end? Or X=50 end?
    # Drawing shows slot at left. So near X=0.
    # Slot fingers: 15mm long.
    
    # Front Profile Points (y=0)
    # P_F_1: (0,0,0) - Bot Left
    # P_F_2: (15,0,0) - Bot Slot Inner
    # P_F_3: (15,0,10) - Shelf Bot
    # P_F_4: (0,0,10) - Slot Inner Bot (Wait, slot is cut FROM left)
    # Re-reading image geometry:
    # The left side has a "C" profile.
    # So at X=15, the face becomes full height.
    # Points loop:
    # (0,0,0) -> (15,0,0) -> (15,0,10) [Corner] -> (0,0,10) [Slot Bot]
    # Then there is empty space from Z=10 to Z=20.
    # Then (0,0,20) [Slot Top] -> (15,0,20) [Corner] -> (15,0,30) [Top] -> (0,0,30) [Top Left]
    # And the main body continues to X=50.
    # Actually, diagram says "15" length legs.
    # So X goes 0..15 (legs) then 15..50 (body).
    
    # Let's list points for Front Face (y=0)
    $P00 = Get-IsoPoint  0  0  0
    $P01 = Get-IsoPoint 15  0  0
    $P02 = Get-IsoPoint 50  0  0
    $P03 = Get-IsoPoint 50  0 30
    $P04 = Get-IsoPoint 15  0 30
    $P05 = Get-IsoPoint  0  0 30
    $P06 = Get-IsoPoint  0  0 20
    $P07 = Get-IsoPoint 15  0 20
    $P08 = Get-IsoPoint 15  0 10
    $P09 = Get-IsoPoint  0  0 10

    # Draw Front Face
    $l1 = $layer.CreateLineSegment($P00[0], $P00[1], $P01[0], $P01[1])
    $l2 = $layer.CreateLineSegment($P01[0], $P01[1], $P02[0], $P02[1])
    $l3 = $layer.CreateLineSegment($P02[0], $P02[1], $P03[0], $P03[1])
    $l4 = $layer.CreateLineSegment($P03[0], $P03[1], $P04[0], $P04[1])
    $l5 = $layer.CreateLineSegment($P04[0], $P04[1], $P05[0], $P05[1])
    $l6 = $layer.CreateLineSegment($P05[0], $P05[1], $P06[0], $P06[1])
    $l7 = $layer.CreateLineSegment($P06[0], $P06[1], $P07[0], $P07[1])
    $l8 = $layer.CreateLineSegment($P07[0], $P07[1], $P08[0], $P08[1])
    $l9 = $layer.CreateLineSegment($P08[0], $P08[1], $P09[0], $P09[1])
    $l10 = $layer.CreateLineSegment($P09[0], $P09[1], $P00[0], $P00[1])

    # Visible Depth Lines (y=15)
    # We project points back by Depth vector.
    # Visible corners usually: Top, Right, Side.
    # Top-Right-Back: (50, 15, 30)
    # Top-Left-Back: (0, 15, 30)
    # Bot-Right-Back: (50, 15, 0)
    
    $D = 15
    $P_TR = Get-IsoPoint 50 0 30
    $P_TR_Back = Get-IsoPoint 50 $D 30
    $l_d1 = $layer.CreateLineSegment($P_TR[0], $P_TR[1], $P_TR_Back[0], $P_TR_Back[1])
    
    $P_TL = Get-IsoPoint 0 0 30
    $P_TL_Back = Get-IsoPoint 0 $D 30
    $l_d2 = $layer.CreateLineSegment($P_TL[0], $P_TL[1], $P_TL_Back[0], $P_TL_Back[1])
    
    $P_BR = Get-IsoPoint 50 0 0
    $P_BR_Back = Get-IsoPoint 50 $D 0
    $l_d3 = $layer.CreateLineSegment($P_BR[0], $P_BR[1], $P_BR_Back[0], $P_BR_Back[1])
    
    # Connecting Back Face (Partial)
    # Back Top Edge
    $l_b1 = $layer.CreateLineSegment($P_TR_Back[0], $P_TR_Back[1], $P_TL_Back[0], $P_TL_Back[1])
    # Back Right Edge
    $l_b2 = $layer.CreateLineSegment($P_TR_Back[0], $P_TR_Back[1], $P_BR_Back[0], $P_BR_Back[1])

    # Slot Depth Lines
    # Top Shelf of Bot Leg (15, 0, 10) -> (15, 15, 10)
    $P_ShelfBot = Get-IsoPoint 15 0 10
    $P_ShelfBot_Back = Get-IsoPoint 15 $D 10
    $l_s1 = $layer.CreateLineSegment($P_ShelfBot[0], $P_ShelfBot[1], $P_ShelfBot_Back[0], $P_ShelfBot_Back[1])
    
    # Bot Shelf of Top Leg (15, 0, 20) -> (15, 15, 20)
    $P_ShelfTop = Get-IsoPoint 15 0 20
    $P_ShelfTop_Back = Get-IsoPoint 15 $D 20
    $l_s2 = $layer.CreateLineSegment($P_ShelfTop[0], $P_ShelfTop[1], $P_ShelfTop_Back[0], $P_ShelfTop_Back[1])
    
    # Inner Vertical of Slot? (15, 0, 10)to(15,0,20) is drawn.
    # The back vertical (15, 15, 10) to (15, 15, 20) is hidden? 
    # Or visible through slot?
    # View is Front-Right-Top. Slot is Left.
    # So we see into the slot? No, Slot is on Left. 
    # Left face is mostly hidden, except the thickness edges.
    
    # Actually, if we view from Front-Right, the Left face logic means:
    # X=0 faces away from us (to the back-left).
    # So we see the Front Face (XZ) and Right Face (YZ) and Top Face (XY).
    # Slot is at X=0. We see the start of the slot on the Front face.
    # We see the "thickness" of the slot going back?
    # Yes, lines going from P09, P08, P07, P06 back to Y=15.
    # P09 (0,0,10) goes to (0,15,10). Visible? No, hidden by leg.
    # P08 (15,0,10) goes to (15,15,10). Visible. (Drawn as l_s1)
    # P07 (15,0,20) goes to (15,15,20). Visible. (Drawn as l_s2)
    # P06 (0,0,20) goes to (0,15,20). Visible? No.
    
    # Is vertical line at x=15, y=15 visible?
    # (15,15,10) to (15,15,20). Yes, that's the back wall of the slot.
    $l_s3 = $layer.CreateLineSegment($P_ShelfBot_Back[0], $P_ShelfBot_Back[1], $P_ShelfTop_Back[0], $P_ShelfTop_Back[1])

    # --- HOLE (Isocircle) ---
    # Center: X=30, Y=0 (Front Face), Z=15.
    # Radius 5 (D=10).
    $HC = Get-IsoPoint 30 0 15
    
    # Corel DrawEllipse(Left, Top, Right, Bottom) is for bounding box. Not good for rotation.
    # Use CreateEllipse(CenterX, CenterY, Radius1, Radius2, Rotation...) ?
    # Actually `CreateEllipse` takes bounding box.
    # `CreateEllipse2(CenterX, CenterY, Radius1, Radius2)`
    
    # Iso Circle Math:
    # Major Axis Radius: R
    # Minor Axis Radius: R * 0.577 (approx tan 30 or similar)
    # Valid for true isometric.
    # Actually, for 30deg projection:
    # Major Axis is same as true radius? No, 1.22 something.
    # Standard Corel logic: Draw circle, then transform scale vertical 57.7%, then rotate 30 deg?
    # Let's try: Radius 5.
    # Draw Circle R=5.
    # Scale vertical by 0.58.
    # Rotate 60 degrees (for Front/Right face orientation).
    
    # Front Face (XZ) Isocircle:
    # Axis alignment: 60 degrees.
    
    $circle = $layer.CreateEllipse2($HC[0], $HC[1], 5 * $Scale, 5 * $Scale)
    # Squash to make ellipse
    $circle.Stretch(0.5774) # Squash height? 
    # Stretch affects relative to shape center. 
    # Wait, Stretch takes (sx, sy).
    # If we stretch y by 0.577, we get flat ellipse.
    # Then rotate.
    $circle.Stretch(1.0, 0.5774)
    $circle.Rotate(60) # Or -60. Front face usually 60. Note Corel angles.
    
    if ($circle) {
        $circle.Outline.Color.RGBAssign(0, 0, 255)
    }

    # Select All for visibility (Optional)
    # $doc.ActiveLayer.Shapes.All().CreateSelection()
    
    Write-Host "Corel Drawing Complete." -ForegroundColor Green
    
}
catch {
    Write-Error "Corel Execution Failed: $_"
    exit 1
}
