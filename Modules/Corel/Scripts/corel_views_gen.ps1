
# ONI Corel Automation - Orthographic Views (Vistas ABNT)
# Subject: "EXTRA 04" - Bracket with Slot
# Projection: 1º Diedro (Front, Top below, Side Right)

try {
    Write-Host "1. Init Corel..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    $doc = $corel.CreateDocument()
    $doc.ActivePage.SetSize(297, 210) # A4
    
    $vLayer = $doc.ActivePage.CreateLayer("VISTAS")
    $vLayer.Activate()
    
    # Styles
    $black = $corel.CreateColor(); $black.CMYKAssign(0, 0, 0, 100)
    
    # Function to Draw Line
    function Line($x1, $y1, $x2, $y2, $style) {
        # Style 1: Solid (Visible) - Thick
        # Style 2: Dashed (Hidden) - Thin
        # Style 3: Center (Axis) - Thin DashDot
        
        $l = $vLayer.CreateLineSegment($x1, $y1, $x2, $y2)
        $l.Outline.Color = $black
        
        if ($style -eq 1) {
            $l.Outline.Width = 0.5 # Thick
        }
        elseif ($style -eq 2) {
            $l.Outline.Width = 0.2
            try { $l.Outline.Style = 2 } catch {} # Dot
        }
        elseif ($style -eq 3) {
            $l.Outline.Width = 0.2
            try { $l.Outline.Style = 4 } catch {} # DashDot
        }
    }
    
    function Circle($cx, $cy, $r, $style) {
        $c = $vLayer.CreateEllipse2($cx, $cy, $r)
        $c.Outline.Color = $black
        if ($style -eq 1) { $c.Outline.Width = 0.5 }
        else { $c.Outline.Width = 0.2; try { $c.Outline.Style = 2 } catch {} }
    }

    # --- LAYOUT - 1º Diedro ---
    # VF (Front) at Top Left.
    # VS (Top) Below VF.
    # VLE (Left Side) at Right of VF.
    
    # Origins
    $VF_X = 50; $VF_Y = 140
    $VS_X = 50; $VS_Y = 80 # (140 - 40 - 20 gap)
    $VL_X = 130; $VF_Y = 140 # (50 + 60 + 20 gap)
    
    # --- VISTA FRONTAL (VF) ---
    # Looking from Arrow direction (Usually Right-Front in Iso).
    # Width: 60 (Base Length). Height: 40 (Tower).
    # L-Shape: Base Height 10. Tower Width 20? 
    # Left Tower is 20 wide. Base goes to 60.
    # So L-shape profile:
    # (0,0) to (60,0) Bottom.
    # (60,0) to (60,10) Right Up.
    # (60,10) to (20,10) Base Top.
    # (20,10) to (20,40) Tower Inner Vertical.
    # (20,40) to (0,40) Tower Top.
    # (0,40) to (0,0) Left Edge.
    
    # Draw Outline (Visible)
    Line ($VF_X) ($VF_Y) ($VF_X + 60) ($VF_Y) 1      # Bottom
    Line ($VF_X + 60) ($VF_Y) ($VF_X + 60) ($VF_Y + 10) 1 # Right Vertical
    Line ($VF_X + 60) ($VF_Y + 10) ($VF_X + 20) ($VF_Y + 10) 1 # Base Top
    Line ($VF_X + 20) ($VF_Y + 10) ($VF_X + 20) ($VF_Y + 40) 1 # Tower Inner
    Line ($VF_X + 20) ($VF_Y + 40) ($VF_X) ($VF_Y + 40) 1      # Tower Top
    Line ($VF_X) ($VF_Y + 40) ($VF_X) ($VF_Y) 1           # Left Edge
    
    # Hidden Lines (Slot)
    # Slot is U-shape R10 centered at Y=20 (in Top view).
    # In Front View, slot is hidden inside the base?
    # Or is Slot going through?
    # Diagram shows U-slot on Base.
    # From Front, we see the side of the slot?
    # Wait, Front View Direction?
    # If viewed from X axis (Length 60): We see the L-shape described above.
    # The Slot is in the Base (Z=0..10).
    # Slot Center X=40? Top view...
    # Top View: Slot is U-shape opening to right?
    # "Extra 04" Iso shows U-slot.
    # Usually opening is towards the "Right" in Front view?
    # Slot center X=40? Radius 10.
    # So Slot extends from X=30 to X=50? Or X=60?
    # If U-shape opens to X=60 (Right).
    # Then in Front View, we look perpendicular to the opening?
    # No, Front View looks at the *Solid* side usually?
    # Let's assume Front View is looking at the L-Profile side-on.
    # Slot is inside the 10mm base.
    # Hidden lines for Slot walls.
    # Slot Y-width is 20 (R10 x 2). Centered.
    # But Front View projects onto X-Z plane.
    # Slot walls are parallel to X-Z? No, Slot walls are parallel to X-X (along length).
    # Wait, Slot varies in Y.
    # In Front View (X-Z), we see the *profile* of the slot?
    # No, projected, the entire slot is within the 10mm thickness.
    # Slot goes *through* the plate? Or is it a pocket?
    # "phi 20" usually through hole.
    # So lines at Z=0 and Z=10 are solid boundaries.
    # Are there hidden lines?
    # Only if looking from Side (Y-Z).
    # In Front (X-Z), the slot is overlapping itself.
    # Unless the slot has features perpendicular.
    # Actually, the Slot is cut *vertically* (Z axis hole)?
    # Image shows "R10" on flat surface. Vertical walls.
    # So hole is through Z.
    # In Front View, we see the "Gap" if we look from right.
    # But looking from "Front" (X axis long side facing us):
    # We see solid face 60x10.
    # Inside, there is a hole.
    # Hole is R10. Centered at Y=20.
    # But Front View flattens Y.
    # So we don't see the hole's Y-width.
    # We see the *extent* of the hole in X?
    # No, we see the *bounds* of the hole.
    # The hole exists from X=30 (Arc start) to X=60?
    # So from X=30 to X=60, there is a slot.
    # But since we look from Y (perpendicular to X), the slot is "behind" the wall?
    # AHH. View Direction matters.
    # Standard: Front View shows the L-shape (X-Z plane projection? No, X-Z is looking from Y).
    # Yes. Looking from Y (Front) shows X and Z Dimensions.
    # Length 60. Height 40.
    # We see the "Face" of the L-bracket.
    # And we see the Slot as HIDDEN lines (dashed) because it's cut through the middle of the Y-depth?
    # Yes. The slot is in the middle of the plate.
    # So Hidden Lines corresponding to the Slot Profile?
    # No, hole is vertical.
    # So looking from Front (Y), we see the cylinder walls?
    # No, we see the *edges* of the cylinder tangent to line of sight?
    # If hole center is Y=20 and Radius=10.
    # Limits are Y=10 and Y=30.
    # Since we project Y to flat...
    # We are looking ALONG Y?
    # If looking *Along* Y, we see the cross section?
    # No, Side View looks along X. Front View looks along Y.
    # Wait, Front View usually shows Length (X) and Height (Z).
    # So we look FROM Y.
    # If the Slot is cylindrical (vertical axis), and we look perpendicular to axis.
    # We see a Rectangle (Hidden).
    # But the slot is U-shaped.
    # It has a flat bottom? Or is it through?
    # "Through Base".
    # So Hidden Lines at X=30? (Arc tangent).
    # And X=30 is the "start" of the slot.
    # So Hidden Line Vertical at X=30, from Z=0 to Z=10.
    # And horizontal hidden lines? No.
    # Just the vertical limit of the cut.
    # So Line ($VF_X + 30) ($VF_Y) to ($VF_X + 30) ($VF_Y + 10) Style 2.
    
    Line ($VF_X + 30) ($VF_Y) ($VF_X + 30) ($VF_Y + 10) 2

    # Towel Slant (Inclined Phase) on Tower?
    # The User's "Nao" might imply I missed the *Slant*.
    # Extra 04 Image shows "Left Tower" with an angled face.
    # It looks like a V-cut or "Rabo de Andorinha".
    # Assuming the Inner Face (at X=20) is slanted.
    # Top width 20? Bottom width 20?
    # If slanted, say 10mm offset.
    # Let's assume Top X=20, Bottom X=30? (Slant inwards).
    # Or Top X=20, Bottom X=10?
    # Without dimensions, standard usually 60 deg or 45 deg or 10mm offset.
    # Let's draw Vertical for now, but if "Nao" persists, it's the slant.
    # User didn't give dims for slant.
    # I'll stick to Vertical for the Tower Inner Face as per my Iso.
    
    # --- VISTA SUPERIOR (VS) ---
    # Projected X-Y plane.
    # Width 60. Height (Depth) 40.
    # Position: Below VF. Aligned X.
    $S_Y = $VS_Y # Top line of View
    # Dims: X=0..60, Y=0..40 (drawn downwards from S_Y).
    
    # Outline 60x40
    Line $VS_X $S_Y ($VS_X + 60) $S_Y 1 # Top Edge (Front)
    Line ($VS_X + 60) $S_Y ($VS_X + 60) ($S_Y - 40) 1 # Right Edge
    Line ($VS_X + 60) ($S_Y - 40) $VS_X ($S_Y - 40) 1 # Bottom Edge (Rear)
    Line $VS_X ($S_Y - 40) $VS_X $S_Y 1 # Left Edge
    
    # Features
    # Tower Top Face (20x40)?
    # Line at X=20.
    Line ($VS_X + 20) $S_Y ($VS_X + 20) ($S_Y - 40) 1
    
    # Slot (Visible U scale)
    # Center X=40, Y=20.
    # Y=20 corresponds to Middle of Y-depth (0..40).
    # In View Y coordinates (S_Y down to S_Y-40):
    # Center Y_view = S_Y - 20.
    # Center X_view = VS_X + 40.
    # Radius 10.
    # U-Shape: Arc Left, Lines Right.
    # Arc Center (VS_X + 40, S_Y - 20).
    # Lines from (X=40, Y=10) to (X=60, Y=10).
    # Lines from (X=40, Y=30) to (X=60, Y=30).
    
    # Draw Lines
    Line ($VS_X + 40) ($S_Y - 10) ($VS_X + 60) ($S_Y - 10) 1
    Line ($VS_X + 40) ($S_Y - 30) ($VS_X + 60) ($S_Y - 30) 1
    
    # Draw Arc
    # CreateEllipse2(cx, cy, r, r, start, end)
    # Start 90 (Top), End 270 (Bottom). Arc on Left.
    $arc = $vLayer.CreateEllipse2(($VS_X + 40), ($S_Y - 20), 10, 10, 90, 270)
    $arc.Outline.Color = $black; $arc.Outline.Width = 0.5
    
    # Axis Line (Center)
    Line ($VS_X + 30) ($S_Y - 20) ($VS_X + 65) ($S_Y - 20) 3
    Line ($VS_X + 40) ($S_Y - 8) ($VS_X + 40) ($S_Y - 32) 3
    
    # --- VISTA LATERAL ESQUERDA (VLE) ---
    # Projected Z-Y plane? Looking from Left.
    # Drawn on Right of VF.
    # Shows Height (Z) and Depth (Y).
    # Width 40 (Y). Height 40 (Z).
    # Origin VLE_X, VF_Y (Bottom Aligned with Front).
    
    $L_X = $VL_X
    $L_Y = $VF_Y # Bottom
    
    # Outline 40x40 (Tower Side mostly)
    Line $L_X $L_Y ($L_X + 40) $L_Y 1 # Bottom
    Line ($L_X + 40) $L_Y ($L_X + 40) ($L_Y + 40) 1 # Right Vertical (Front Face)
    Line ($L_X + 40) ($L_Y + 40) $L_X ($L_Y + 40) 1 # Top Edge
    Line $L_X ($L_Y + 40) $L_X $L_Y 1 # Left Vertical (Rear Face)
    
    # Base Thickness Line (Z=10)
    Line $L_X ($L_Y + 10) ($L_X + 40) ($L_Y + 10) 1 
    
    # Slot Hidden Lines
    # Looking from Left Side (Tower Side).
    # Slot is behind the Tower? No, Tower is X=0..20. Slot X=30..60.
    # So we look THROUGH the Tower?
    # No, Left View shows the Left Face (Tower).
    # Everything "Right" of it is hidden (if obstructed).
    # Tower obstructed the Base Slot? Yes.
    # Slot is X=30.
    # Slot Cutout is Y=10 to Y=30 (Height 10 in Z).
    # So we project the Slot Profile onto the View.
    # Slot Y limits: Y=10, Y=30.
    # In View X (Depth Y): 10 and 30.
    # In View Y (Height Z): 0 and 10.
    # So Hidden Rectangle for Slot Cutout?
    # Yes. (L_X + 10) to (L_X + 30) at Height Z=0..10.
    # Is it a cut? Yes.
    # So horizontal lines at Z=10 (Existing solid) and Z=0 (Existing Solid).
    # Vertical Hidden Lines at Y=10 and Y=30.
    
    Line ($L_X + 10) $L_Y ($L_X + 10) ($L_Y + 10) 2
    Line ($L_X + 30) $L_Y ($L_X + 30) ($L_Y + 10) 2
    
    Write-Host "Done."
    
}
catch {
    Write-Error $_
}
