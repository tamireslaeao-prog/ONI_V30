# ONI Automation: Slotted Block (Bloco com Fenda)
# Target: AutoCAD
# Strategy: Profile Extrusion (Front Plane)

$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "AutoCAD_Adapter.psm1") -Force

if (-not (Connect-AutoCAD)) { Write-Error "AutoCAD not found."; exit 1 }

try {
    Write-Host "Starting Slotted Block..." -ForegroundColor Cyan

    # 1. New Drawing
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.SendKeys("^n") 
    Start-Sleep -Seconds 2
    $wshell.SendKeys("{ENTER}") 
    Start-Sleep -Seconds 2

    # 2. Reset View
    Clear-CADCommandline
    Send-CADCommand "_UCS" 
    Send-CADCommand "W"
    Send-CADCommand "_PLAN" 
    Send-CADCommand "W" 
    Send-CADCommand "_VS" 
    Send-CADCommand "2"    

    # 3. Set UCS to Front (XZ Plane)
    # Origin 0,0,0. X along World X. Y along World Z.
    Send-CADCommand "_UCS"
    Send-CADCommand "3"
    Send-CADCommand "0,0,0"   
    Send-CADCommand "100,0,0" 
    Send-CADCommand "0,0,100" 
    
    # 4. Draw Main Profile (Polyline)
    # Coords relative to new UCS (X=X, Y=Z)
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"      # Bottom Left
    Send-CADCommand "50,0"     # Bottom Right
    Send-CADCommand "50,30"    # Top Right
    Send-CADCommand "0,30"     # Top Left
    Send-CADCommand "0,20"     # Slot Top Start
    Send-CADCommand "15,20"    # Slot Corner Inner Top
    Send-CADCommand "15,10"    # Slot Corner Inner Bottom
    Send-CADCommand "0,10"     # Slot Bottom Start
    Send-CADCommand "C"        # Close
    
    # 5. Draw Hole Circle
    # Center X=30 (50-20), Y=15 (Height)
    Send-CADCommand "_CIRCLE"
    Send-CADCommand "30,15"
    Send-CADCommand "5"        # Radius 5 (D10)
    
    # 6. Region & Subtract
    Send-CADCommand "_REGION"
    Send-CADCommand "ALL"
    Send-CADCommand ""
    
    Send-CADCommand "_SUBTRACT"
    # Select Main Profile (Point on solid part)
    # Safe point: 45, 10
    Send-CADCommand "45,10"
    Send-CADCommand ""
    # Select Hole (Center)
    Send-CADCommand "30,15"
    Send-CADCommand ""
    
    # 7. Extrude
    # Depth 15mm
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"        # Last (Region)
    Send-CADCommand ""
    Send-CADCommand "15"       
    
    # 8. Finish
    Send-CADCommand "_UCS" 
    Send-CADCommand "W"
    
    Send-CADCommand "_VPOINT"  
    Send-CADCommand "1,-1,1" 
    Send-CADCommand "_CHPROP"
    Send-CADCommand "ALL"
    Send-CADCommand ""
    Send-CADCommand "C" 
    Send-CADCommand "5"        
    Send-CADCommand ""
    Send-CADCommand "_VS" 
    Send-CADCommand "C"   
    Send-CADCommand "_ZOOM"
    Send-CADCommand "E"   

    Write-Host "Slotted Block Complete." -ForegroundColor Green

}
catch {
    Write-Error "Execution Failed: $_"
    exit 1
}
