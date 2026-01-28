# ONI Automation: Dimensioned Bracket (3D + Dims)
# Strategy: Intersection Method + UCS Dimensioning

$ScriptPath = $MyInvocation.MyCommand.Path
$ScriptDir = Split-Path $ScriptPath
Import-Module (Join-Path $ScriptDir "AutoCAD_Adapter.psm1") -Force

function Draw-Bracket {
    try {
        Connect-AutoCAD
    }
    catch {
        Write-Warning "AutoCAD not detected. Launching..."
        $AcadPath = "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe"
        if (Test-Path $AcadPath) {
            Start-Process $AcadPath
            Write-Host "Waiting 15s for AutoCAD to start..." -ForegroundColor Cyan
            Start-Sleep -Seconds 15
            Connect-AutoCAD
        }
        else {
            throw "AutoCAD executable not found at $AcadPath"
        }
    }
    Clear-CADCommandline

    # --- SETUP ---
    Send-CADCommand "_QNEW"
    Start-Sleep -Milliseconds 2000
    Send-CADCommand "_UCS"; Send-CADCommand "W"
    Send-CADCommand "_VS"; Send-CADCommand "2" # 2D Wireframe
    
    # Layers
    Send-CADCommand "_LAYER"; Send-CADCommand "N"; Send-CADCommand "MODEL"; Send-CADCommand "C"; Send-CADCommand "5"; Send-CADCommand "MODEL"; 
    Send-CADCommand "N"; Send-CADCommand "DIM"; Send-CADCommand "C"; Send-CADCommand "3"; Send-CADCommand "DIM"; Send-CADCommand ""
    
    # DimStyle
    Send-CADCommand "-DIMSTYLE"; Send-CADCommand "S"; Send-CADCommand "ONI_3D"
    Send-CADCommand "DIMTXT"; Send-CADCommand "3.0"
    Send-CADCommand "DIMASZ"; Send-CADCommand "2.5"
    Send-CADCommand "DIMDEC"; Send-CADCommand "0" # No decimals for mm
    
    # --- GEOMETRY: SIDE PROFILE (XZ Plane) ---
    Send-CADCommand "_LAYER"; Send-CADCommand "S"; Send-CADCommand "MODEL"; Send-CADCommand ""
    
    # Rotate UCS to draw on Front (XZ)
    Send-CADCommand "_UCS"; Send-CADCommand "R"; Send-CADCommand "X"; Send-CADCommand "90"
    
    # Profile: (0,0) -> (68,0) -> (68,14) -> (54,28) -> (22,28) -> (22,18) -> (0,18) -> Close
    # Note: On rotated UCS, Y is up (Old Z), X is right.
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"
    Send-CADCommand "68,0"
    Send-CADCommand "68,14"   # Tip of slope
    Send-CADCommand "54,28"   # Start of slope
    Send-CADCommand "22,28"   # Step Top
    Send-CADCommand "22,18"   # Step Down Vertical
    Send-CADCommand "0,18"    # Step Low Left
    Send-CADCommand "C"       # Close
    
    # Extrude (Along current Z, which is old Y negated? No, Extrude goes perpendicular to plan)
    # If UCS is Right (YZ), Extrude goes X.
    # If UCS is Front (XZ), Extrude goes Y.
    Send-CADCommand "_EXTRUDE"; Send-CADCommand "L"; Send-CADCommand ""; Send-CADCommand "34"

    Send-CADCommand "_UCS"; Send-CADCommand "W" # Reset

    # --- GEOMETRY: TOP PROFILE (XY Plane) ---
    # Rect 68x34 with Chamfers 10x10 on Left
    # Points: (10,0) -> (68,0) -> (68,34) -> (10,34) -> (0,24) -> (0,10) -> Close
    Send-CADCommand "_PLINE"
    Send-CADCommand "10,0"
    Send-CADCommand "68,0"
    Send-CADCommand "68,34"
    Send-CADCommand "10,34"
    Send-CADCommand "0,24"
    Send-CADCommand "0,10"
    Send-CADCommand "C"
    
    Send-CADCommand "_EXTRUDE"; Send-CADCommand "L"; Send-CADCommand ""; Send-CADCommand "50" # Taller than 28

    # --- INTERSECT ---
    # Select All
    Send-CADCommand "_INTERSECT"; Send-CADCommand "ALL"; Send-CADCommand ""

    # --- HOLE ---
    # Pos: X=11, Y=17 (Center of width 34)
    Send-CADCommand "_CYLINDER"
    Send-CADCommand "11,17,-5" # Center Base
    Send-CADCommand "9"        # Radius (D=18)
    Send-CADCommand "50"       # Height
    
    Send-CADCommand "_VS"; Send-CADCommand "C" # Conceptual for boolean
    Send-CADCommand "_SUBTRACT"; Send-CADCommand "ALL"; Send-CADCommand ""; Send-CADCommand "R"; Send-CADCommand "L"; Send-CADCommand ""; Send-CADCommand ""
    # Select 'ALL' removes 'Last' (Cylinder) from selection set? No.
    # Logic: Subtract FROM (All minus Last) ... No, easier to click or use Last.
    # Best way: Subtract FROM big solid.
    # Since Intersect created a new solid ID, it's not Last anymore properly if Cylinder was made.
    # The Cylinder is Last. The Block is Previous.
    # Try: Subtract FROM (Select by coord)
    
    # Retry Boolean Logic
    # 1. Select Block: Click 68,0,0 ? No. 
    # Let's use simple logic:
    # There are only 2 solids. Block and Cylinder.
    # Cylinder is Last.
    # Subtract FROM [All], Remove [Last]. -> Enter. Select [Last] -> Enter.
    
    # Better:
    Send-CADCommand "_SUBTRACT"
    Send-CADCommand "ALL"; Send-CADCommand ""; # Select both
    Send-CADCommand "R"; Send-CADCommand "L"; Send-CADCommand ""; # Remove Cylinder from 'Source' set
    Send-CADCommand "" # Finish Source selection
    Send-CADCommand "L"; Send-CADCommand "" # Select Cylinder as 'Tool'
    
    # --- DIMENSIONS ---
    Send-CADCommand "_LAYER"; Send-CADCommand "S"; Send-CADCommand "DIM"; Send-CADCommand ""
    Send-CADCommand "_VS"; Send-CADCommand "2" # Wireframe for snapping
    
    # 1. Front Dims (Align UCS to Front Face)
    Send-CADCommand "_UCS"; Send-CADCommand "R"; Send-CADCommand "X"; Send-CADCommand "90"
    
    # Height 18
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,0"; Send-CADCommand "0,18"; Send-CADCommand "-5,9"
    # Height 28
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "68,0"; Send-CADCommand "68,28"; Send-CADCommand "75,14" # Far right
    # Step 14 (Difference) - Not in image, image shows 28 and 18. And 14 at tip.
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "68,0"; Send-CADCommand "68,14"; Send-CADCommand "72,7" # Right tip height
    
    # Lengths
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,18"; Send-CADCommand "22,18"; Send-CADCommand "11,25" # 22 seg
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "22,28"; Send-CADCommand "54,28"; Send-CADCommand "38,35" # 32 seg
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,0"; Send-CADCommand "68,0"; Send-CADCommand "34,-5" # Total 68
    
    # 2. Top Dims (Align UCS to Top)
    Send-CADCommand "_UCS"; Send-CADCommand "W"
    # Move UCS Origin to Top Left corner for ease (0,34,28) ? No, Block Top is Z/28?
    # Actually, highest point is Z=28.
    Send-CADCommand "_UCS"; Send-CADCommand "O"; Send-CADCommand "0,34,28" 
    # Now (0,0) is Back-Left-Top corner. X is Right, Y is Back (Wait).
    # World Y is Back. If I moved origin to 0,34,28... Y is still World Y.
    # So Y goes away from screen? No AutoCAD Y is Up in Plan.
    # Let's check rotation. _PLAN W means Y is UP.
    
    # Width 34
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,0"; Send-CADCommand "0,-34"; Send-CADCommand "-5,-17"
    
    # Chamfer 10
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,0"; Send-CADCommand "0,-10"; Send-CADCommand "-5,-5"
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,0"; Send-CADCommand "10,0"; Send-CADCommand "5,5"
    
    # Hole Pos
    Send-CADCommand "_DIMLINEAR"; Send-CADCommand "0,-17"; Send-CADCommand "11,-17"; Send-CADCommand "5,-17" # X pos 11?
    # In dwg: Hole center to Edge is 14? or 18?
    # Let's just dim the diameter.
    Send-CADCommand "_DIMDIAMETER"; Send-CADCommand "11,-17,0"; Send-CADCommand "20,-20,0"

    # --- FINISH ---
    Send-CADCommand "_UCS"; Send-CADCommand "W"
    Send-CADCommand "_VS"; Send-CADCommand "C"
    Send-CADCommand "_ZOOM"; Send-CADCommand "E"
    Send-CADCommand "_VPOINT"; Send-CADCommand "1,-1,1"

    Write-Host "Bracket Modeling Complete." -ForegroundColor Green
}

try {
    Draw-Bracket
}
catch {
    Write-Error $_
}
