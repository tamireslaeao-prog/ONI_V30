# ONI Automation: Test of Fire (Slice Strategy) - v3
# Target: AutoCAD
# Strategy: "Sculpting" (Create Mass -> Slice Corners)

$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "AutoCAD_Adapter.psm1") -Force

if (-not (Connect-AutoCAD)) { Write-Error "AutoCAD not found."; exit 1 }

try {
    Write-Host "Starting Sculpture (Slice)..." -ForegroundColor Cyan

    # 1. New Drawing
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.SendKeys("^n") 
    Start-Sleep -Seconds 2
    $wshell.SendKeys("{ENTER}") 
    Start-Sleep -Seconds 2

    # 2. Reset View to Wireframe
    Clear-CADCommandline
    Send-CADCommand "_UCS" -Delay 100 
    Send-CADCommand "W" -Delay 100 
    Send-CADCommand "_PLAN" -Delay 300
    Send-CADCommand "W" -Delay 300
    Send-CADCommand "_VS" 
    Send-CADCommand "2"    

    # ==========================
    # PHASE 1: MASSING (The Block)
    # ==========================
    # We build the "bounding shapes" before cutting.
    
    # 1. Base Plate Mass (90x60x15)
    Send-CADCommand "_BOX"
    Send-CADCommand "0,0,0"
    Send-CADCommand "90,60,15"

    # 2. Back Wall Mass (90x15x60)
    Send-CADCommand "_BOX"
    Send-CADCommand "0,0,0"
    Send-CADCommand "90,15,60"

    # 3. Left Wall Mass (15x40x45)
    Send-CADCommand "_BOX"
    Send-CADCommand "0,0,0"
    Send-CADCommand "15,40,45"

    # 4. Merge (Union)
    Send-CADCommand "_UNION"
    Send-CADCommand "ALL"
    Send-CADCommand ""

    # ==========================
    # PHASE 2: SCULPTING (Slice)
    # ==========================
    # We cut the excess material using 3 points for each plane.
    # Keep Point: 0,0,0 (Back Left Bottom) is always part of the model.

    # A. Right Slope Slice
    # Cutting Plane: (15,15,60) -> (90,15,60) -> (90,60,30)
    # This removes the top-front-right material.
    Send-CADCommand "_SLICE"
    Send-CADCommand "L"        # Select Last (The Unioned Mass)
    Send-CADCommand ""
    Send-CADCommand "3"        # 3 Points Mode
    Send-CADCommand "15,15,60" # Top Back Left of Slope
    Send-CADCommand "90,15,60" # Top Back Right
    Send-CADCommand "90,60,30" # Bottom Front Right
    Send-CADCommand "0,0,0"    # Point on Desired Side (Keep)

    # B. Left Slope Slice
    # Cutting Plane: (0,15,45) -> (15,15,45) -> (0,40,15)
    Send-CADCommand "_SLICE"
    Send-CADCommand "L"        # Select Last (The Mass)
    Send-CADCommand ""
    Send-CADCommand "3"        
    Send-CADCommand "0,15,45"  # Top Back Left
    Send-CADCommand "15,15,45" # Top Back Right
    Send-CADCommand "0,40,15"  # Bottom Front Left
    Send-CADCommand "0,0,0"    # Keep Side

    # C. Base Chamfer Slice (Front Left)
    # Cutting Plane: (0,40,0) -> (0,40,15) -> (30,60,0)
    # Vertical cut chopping the corner.
    Send-CADCommand "_SLICE"
    Send-CADCommand "L"        
    Send-CADCommand ""
    Send-CADCommand "3" 
    Send-CADCommand "0,40,0"   # Corner Start
    Send-CADCommand "0,40,15"  # Corner Start Top
    Send-CADCommand "30,60,0"  # Corner End
    Send-CADCommand "0,0,0"    # Keep Side

    # ==========================
    # PHASE 3: POCKET (Subtraction)
    # ==========================
    # Create the cutter directly on the face using UCS.
    
    # Switch to Conceptual for better selection later if needed
    Send-CADCommand "_VS"
    Send-CADCommand "C"

    # UCS on Left Slope Face
    # Origin: Top Left (0,15,45)
    # X Axis: Across Width (15,15,45)  -> X goes Right
    # Y Axis: Down Slope (0,40,15)     -> Y goes Down-Front
    Send-CADCommand "_UCS" 
    Send-CADCommand "3" 
    Send-CADCommand "0,15,45"  
    Send-CADCommand "15,15,45" 
    Send-CADCommand "0,40,15"  

    # Draw Pocket Rect
    # 9mm from Top (Y=9)
    # Centered in 15mm Width? Let's assume 3mm margin (15-9=6/2=3).
    # Pocket Size: 15 Long (Y direction), 9 Wide (X direction).
    Send-CADCommand "_RECTANG"
    Send-CADCommand "3,9"      # Start 3mm in, 9mm down
    Send-CADCommand "12,24"    # End 12mm in (3+9), 24mm down (9+15)
    
    # Extrude Cutter (-20 deep)
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"
    Send-CADCommand ""
    Send-CADCommand "-20"
    
    # Reset UCS to World
    Send-CADCommand "_UCS" 
    Send-CADCommand "W"

    # Subtract
    Send-CADCommand "_SUBTRACT"
    # Select Body (Point 5,5,5 is safe inside base corner)
    Send-CADCommand "5,5,5"  
    Send-CADCommand ""
    # Select Cutter (Last object created)
    Send-CADCommand "L"
    Send-CADCommand ""

    # Finish
    Send-CADCommand "_VPOINT"  
    Send-CADCommand "1,-1,1" 
    Send-CADCommand "_CHPROP"
    Send-CADCommand "ALL"
    Send-CADCommand ""
    Send-CADCommand "C" 
    Send-CADCommand "5"        
    Send-CADCommand ""
    Send-CADCommand "_ZOOM"
    Send-CADCommand "E"   

    Write-Host "Sculpture Complete." -ForegroundColor Green

}
catch {
    Write-Error "Execution Failed: $_"
    exit 1
}
