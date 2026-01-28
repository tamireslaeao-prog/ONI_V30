# ONI AutoCAD Automation - 3D Block (User Task)
# Dimensions Strategy: Total=35.4. 
# Left=13.4, Slot=10, Right=12. Depth=16. 
# Heights: Left=10(f)-20(b), Right=13, Slot Depth=9.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$ScriptDir\AutoCAD_Adapter.psm1" -Force

if (-not (Connect-AutoCAD)) { 
    Write-Error "AutoCAD not found. Please open AutoCAD first."
    exit 
}

# --- NEW DOCUMENT (If stuck on Start Screen) ---
Write-Host "Creating New Document..."
$wshell = New-Object -ComObject WScript.Shell
$wshell.SendKeys("^n") # Ctrl+N
Start-Sleep -Seconds 2
$wshell.SendKeys("{ENTER}") # Confirm Template
Start-Sleep -Seconds 5

Clear-CADCommandline

# --- SETUP ---
Send-CADCommand "_UCS" 300 -NoEnter
Send-CADCommand "_World" 
Send-CADCommand "_OSMODE"
Send-CADCommand "0" # Disable OSNAP for script precision
Send-CADCommand "_VSUALSTYLES" 300 -NoEnter # Visual Style
Send-CADCommand "_Conceptual"

# --- LEFT BLOCK (Trapezoidal 20->10) ---
# Width 21 x Depth 16 x Height 20
Send-CADCommand "_BOX"
Send-CADCommand "0,0,0"
Send-CADCommand "21,16,20"

# Slice to create slope (Left=20 -> Right=10)
# Plane Points: (0,0,20), (0,16,20), (21,0,10)
Send-CADCommand "_SLICE"
Send-CADCommand "_LAST"
Send-CADCommand "" # Confirm selection
Send-CADCommand "3" # 3 Points mode
Send-CADCommand "0,0,20" # Top Left Front
Send-CADCommand "0,16,20" # Top Left Back
Send-CADCommand "21,0,10" # Top Right Front (Target)
Send-CADCommand "0,0,0" # Keep point on bottom side

# --- MIDDLE BRIDGE (Slot Bottom) ---
# Box 10 x 16 x 4 (Height = 13 - 9)
# Position: X=21
Send-CADCommand "_BOX"
Send-CADCommand "21,0,0"
Send-CADCommand "31,16,4"

# --- RIGHT BLOCK ---
# Box 12 x 16 x 13
# Position: X=31
Send-CADCommand "_BOX"
Send-CADCommand "31,0,0"
Send-CADCommand "43,16,13"

# --- UNION ALL ---
Send-CADCommand "_UNION"
Send-CADCommand "_ALL"
Send-CADCommand ""

# --- VIEW ---
Send-CADCommand "_VPOINT"
Send-CADCommand "1,-1,1"
Send-CADCommand "_ZOOM"
Send-CADCommand "_EXTENTS"

# --- DIMENSIONS (Basic) ---
Send-CADCommand "_LAYER" 300 -NoEnter
Send-CADCommand "_Make"
Send-CADCommand "COTAS"
Send-CADCommand "_Color"
Send-CADCommand "Red"
Send-CADCommand "" # Exit Layer
Send-CADCommand ""

# Total X
Send-CADCommand "_DIMLINEAR"
Send-CADCommand "0,0,0"
Send-CADCommand "43,0,0"
Send-CADCommand "21.5,-5,0"

# Depth
Send-CADCommand "_DIMLINEAR"
Send-CADCommand "43,0,0"
Send-CADCommand "43,16,0"
Send-CADCommand "48,8,0"

# Height Right
Send-CADCommand "_DIMLINEAR"
Send-CADCommand "43,0,0"
Send-CADCommand "43,0,13"
Send-CADCommand "48,0,6.5"

# Slot Depth (Approx)
Send-CADCommand "_DIMLINEAR"
Send-CADCommand "31,0,13"
Send-CADCommand "31,0,4"
Send-CADCommand "35,0,8"


Write-Host "Done."
