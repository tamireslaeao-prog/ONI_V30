# ONI Automation: Draw Blue 3D Part (Solid Hole Fix) - v6
# Target: AutoCAD
# Fix: Enable Visual Style 'Conceptual' BEFORE Subtraction to allow volume picking.

$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "AutoCAD_Adapter.psm1") -Force

if (-not (Connect-AutoCAD)) { Write-Error "AutoCAD not found."; exit 1 }

try {
    Write-Host "Starting Drawing (Visual Selection Fix)..." -ForegroundColor Cyan

    # 1. New Drawing
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.SendKeys("^n") 
    Start-Sleep -Seconds 2
    $wshell.SendKeys("{ENTER}") 
    Start-Sleep -Seconds 2

    # 2. Reset View
    Clear-CADCommandline
    Send-CADCommand "_UCS" -Delay 100 
    Send-CADCommand "W" -Delay 100 
    Send-CADCommand "_PLAN" -Delay 300
    Send-CADCommand "W" -Delay 300
    Send-CADCommand "_VS" 
    Send-CADCommand "2"    # 2D Wireframe for fast drawing

    # 3. Precise Polyline
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"
    
    # Right Side
    Send-CADCommand "25,0"
    Send-CADCommand "A" 
    Send-CADCommand "35,10"
    Send-CADCommand "L" 
    Send-CADCommand "35,25"
    Send-CADCommand "15,25"
    Send-CADCommand "15,45"
    
    # Top
    Send-CADCommand "-15,45"
    
    # Left Side
    Send-CADCommand "-15,25"
    Send-CADCommand "-35,25"
    Send-CADCommand "-35,10"
    Send-CADCommand "A" 
    Send-CADCommand "-25,0"
    Send-CADCommand "L" 
    Send-CADCommand "C" 

    # 4. Extrude BODY to 30
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"        
    Send-CADCommand ""
    Send-CADCommand "30"

    # 5. Cutter (Circle)
    Send-CADCommand "_CIRCLE"
    Send-CADCommand "0,15,0"   
    Send-CADCommand "D" 
    Send-CADCommand "20"       

    # 6. Extrude Cutter
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"        
    Send-CADCommand ""
    Send-CADCommand "60"

    # 7. Move Cutter (Z-15)
    Send-CADCommand "_MOVE"
    Send-CADCommand "L"        
    Send-CADCommand ""
    Send-CADCommand "0,0,0"    
    Send-CADCommand "0,0,-15"  

    # === CRITICAL FIX: VISUAL SELECTION ===
    # Switch to Isometric + Conceptual NOW so we can pick volumes
    Send-CADCommand "_VPOINT"
    Send-CADCommand "1,-1,1"
    Send-CADCommand "_VS" 
    Send-CADCommand "C"   # Conceptual
    
    # Wait for visual switch
    Start-Sleep -Seconds 1

    # 8. Subtract
    Send-CADCommand "_SUBTRACT"
    
    # 8a. Select KEEP (The Body)
    # Pick Point on Top Surface of Right Wing (Z=30)
    # X=25, Y=15 is safely on the wing (Wing is X 15..35, Y 10..25)
    Send-CADCommand "25,15,30" 
    Send-CADCommand ""         
    
    # 8b. Select REMOVE (The Cutter)
    # Pick Point on Top Face of Cutter (Z=45)
    # Center 0,15. 
    Send-CADCommand "0,15,45" 
    Send-CADCommand ""         

    # 9. Finish
    # Color Blue
    Send-CADCommand "_CHPROP"
    Send-CADCommand "ALL"
    Send-CADCommand ""
    Send-CADCommand "C" 
    Send-CADCommand "5"        
    Send-CADCommand ""

    Send-CADCommand "_ZOOM"
    Send-CADCommand "E"        

    Write-Host "Solid Hole Fix Complete." -ForegroundColor Green

}
catch {
    Write-Error "Execution Failed: $_"
    exit 1
}
