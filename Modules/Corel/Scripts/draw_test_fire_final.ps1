# ONI Automation: Test of Fire (Component Assembly / Lego) - Repaired v2
# Target: AutoCAD
# Fix: Corrected Send-CADCommand usage (One command per call).

$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "AutoCAD_Adapter.psm1") -Force

if (-not (Connect-AutoCAD)) { Write-Error "AutoCAD not found."; exit 1 }

try {
    Write-Host "Starting Lego Assembly (Repair v2)..." -ForegroundColor Cyan

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

    # ==========================
    # COMPONENT 1: BASE PLATE
    # ==========================
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"
    Send-CADCommand "90,0"
    Send-CADCommand "90,60"
    Send-CADCommand "30,60"
    Send-CADCommand "0,40"
    Send-CADCommand "C"
    
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"
    Send-CADCommand ""
    Send-CADCommand "15"       

    # ==========================
    # COMPONENT 2: RIGHT WING
    # ==========================
    Send-CADCommand "_UCS"
    Send-CADCommand "3"
    Send-CADCommand "90,0,0"   # Origin 
    Send-CADCommand "90,60,0"  # X 
    Send-CADCommand "90,0,60"  # Y 
    
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"      
    Send-CADCommand "0,60"     
    Send-CADCommand "15,60"    
    Send-CADCommand "60,30"    
    Send-CADCommand "60,0"     
    Send-CADCommand "C"
    
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"
    Send-CADCommand ""
    Send-CADCommand "-75"    
    
    Send-CADCommand "_UCS" 
    Send-CADCommand "W"

    # ==========================
    # COMPONENT 3: LEFT WING
    # ==========================
    Send-CADCommand "_UCS"
    Send-CADCommand "3"
    Send-CADCommand "0,0,0"    
    Send-CADCommand "0,60,0"   
    Send-CADCommand "0,0,60"   
    
    Send-CADCommand "_PLINE"
    Send-CADCommand "0,0"      
    Send-CADCommand "0,45"     
    Send-CADCommand "15,45"    
    Send-CADCommand "40,15"    
    Send-CADCommand "40,0"     
    Send-CADCommand "C"
    
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"
    Send-CADCommand ""
    Send-CADCommand "15"      

    Send-CADCommand "_UCS" 
    Send-CADCommand "W"

    # ==========================
    # ASSEMBLY (Union)
    # ==========================
    Send-CADCommand "_UNION"
    Send-CADCommand "ALL"
    Send-CADCommand ""

    # ==========================
    # POCKET (Subtraction)
    # ==========================
    Send-CADCommand "_VS" 
    Send-CADCommand "C"     
    
    Send-CADCommand "_UCS" 
    Send-CADCommand "3" 
    Send-CADCommand "0,15,45"  # Orig
    Send-CADCommand "0,40,15"  # X 
    Send-CADCommand "15,15,45" # Y 
    
    Send-CADCommand "_RECTANG"
    Send-CADCommand "9,3"
    Send-CADCommand "24,12"
    
    Send-CADCommand "_EXTRUDE"
    Send-CADCommand "L"
    Send-CADCommand ""
    Send-CADCommand "-20"
    
    Send-CADCommand "_UCS" 
    Send-CADCommand "W"
    
    Send-CADCommand "_SUBTRACT"
    Send-CADCommand "5,5,5"  
    Send-CADCommand ""
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

    Write-Host "Lego Assembly Complete." -ForegroundColor Green

}
catch {
    Write-Error "Execution Failed: $_"
    exit 1
}
