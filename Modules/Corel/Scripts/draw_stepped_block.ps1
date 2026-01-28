# AutoCAD Automation - Stepped Block (Use Existing Doc)
# Date: 2026-01-08

# --- 1. Attach to EXISTING AutoCAD ---
$acad = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$doc = $acad.ActiveDocument

# Helper
function Send-Cmd($cmd) {
    $doc.SendCommand("$cmd`n")
}

# --- 2. Setup Layers ---
Send-Cmd "_UCS" ; Send-Cmd "W"
Send-Cmd "-LAYER" ; Send-Cmd "N" ; Send-Cmd "VISIBLE" ; Send-Cmd "C" ; Send-Cmd "7" ; Send-Cmd "VISIBLE" ; Send-Cmd ""
Send-Cmd "-LAYER" ; Send-Cmd "N" ; Send-Cmd "HIDDEN" ; Send-Cmd "C" ; Send-Cmd "3" ; Send-Cmd "HIDDEN" ; Send-Cmd "L" ; Send-Cmd "HIDDEN" ; Send-Cmd "HIDDEN" ; Send-Cmd ""
Send-Cmd "-LAYER" ; Send-Cmd "N" ; Send-Cmd "DIM" ; Send-Cmd "C" ; Send-Cmd "2" ; Send-Cmd "DIM" ; Send-Cmd ""
Send-Cmd "-LINETYPE" ; Send-Cmd "L" ; Send-Cmd "HIDDEN" ; Send-Cmd "" ; Send-Cmd ""
Send-Cmd "DIMTXT" ; Send-Cmd "2.5"; Send-Cmd "DIMASZ" ; Send-Cmd "2.5"; Send-Cmd "DIMDEC" ; Send-Cmd "0"

# --- 3. Parameters ---
$W1 = 32; $W2 = 10; $W3 = 13; $W4 = 38
$TotalW = $W1 + $W2 + $W3 + $W4 # 93
$D = 38; $H1 = 15; $H2 = 24
$TopBlockW = 12; $TopBlockD = 16
$TopBlockX1 = ($W1 - $TopBlockW) / 2; $TopBlockX2 = $TopBlockX1 + $TopBlockW
$PocketW = 12; $PocketD = 13

# --- 4. FRONT VIEW ---
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "VISIBLE" ; Send-Cmd ""

# Left Block (32x24 with Top 12x9)
Send-Cmd "_RECTANG" ; Send-Cmd "0,0" ; Send-Cmd "$W1,$H1"
Send-Cmd "_RECTANG" ; Send-Cmd "$TopBlockX1,$H1" ; Send-Cmd "$TopBlockX2,$H2"

# Right Base (61x15)
Send-Cmd "_RECTANG" ; Send-Cmd "$W1,0" ; Send-Cmd "$TotalW,$H1"

# Pocket Hidden
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "HIDDEN" ; Send-Cmd ""
Send-Cmd "_LINE" ; Send-Cmd "$($TotalW - $PocketW),0" ; Send-Cmd "$($TotalW - $PocketW),$H1" ; Send-Cmd ""
Send-Cmd "_LINE" ; Send-Cmd "$($W1 + $W2),0" ; Send-Cmd "$($W1 + $W2),$H1" ; Send-Cmd ""

# --- 5. TOP VIEW ---
$TopY = -60
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "VISIBLE" ; Send-Cmd ""
Send-Cmd "_RECTANG" ; Send-Cmd "0,$TopY" ; Send-Cmd "$W1,$($TopY - $D)"
Send-Cmd "_RECTANG" ; Send-Cmd "$W1,$TopY" ; Send-Cmd "$TotalW,$($TopY - $D)"

# Top Block
$TBY1 = $TopY - (($D - $TopBlockD) / 2)
$TBY2 = $TBY1 - $TopBlockD
Send-Cmd "_RECTANG" ; Send-Cmd "$TopBlockX1,$TBY1" ; Send-Cmd "$TopBlockX2,$TBY2"

# Pocket
Send-Cmd "_RECTANG" ; Send-Cmd "$($TotalW - $PocketW),$TopY" ; Send-Cmd "$TotalW,$($TopY - $PocketD)"

# Hidden
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "HIDDEN" ; Send-Cmd ""
Send-Cmd "_LINE" ; Send-Cmd "$($W1 + $W2),$TopY" ; Send-Cmd "$($W1 + $W2),$($TopY - $D)" ; Send-Cmd ""
Send-Cmd "_LINE" ; Send-Cmd "$($W1 + $W2 + $W3),$TopY" ; Send-Cmd "$($W1 + $W2 + $W3),$($TopY - $D)" ; Send-Cmd ""

# --- 6. SIDE VIEW ---
$SideX = 110
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "VISIBLE" ; Send-Cmd ""
Send-Cmd "_RECTANG" ; Send-Cmd "$SideX,0" ; Send-Cmd "$($SideX + $D),$H1"
$SBSY1 = (38 - 16) / 2
$SBSY2 = $SBSY1 + 16
Send-Cmd "_RECTANG" ; Send-Cmd "$($SideX + $SBSY1),$H1" ; Send-Cmd "$($SideX + $SBSY2),$H2"
Send-Cmd "_LINE" ; Send-Cmd "$($SideX + $PocketD),0" ; Send-Cmd "$($SideX + $PocketD),$H1" ; Send-Cmd ""

# --- 7. DIMS ---
Send-Cmd "-LAYER" ; Send-Cmd "S" ; Send-Cmd "DIM" ; Send-Cmd ""
Send-Cmd "_DIMLINEAR" ; Send-Cmd "0,0" ; Send-Cmd "$W1,0" ; Send-Cmd "16,-10"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "$W1,0" ; Send-Cmd "$($W1+$W2),0" ; Send-Cmd "37,-10"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "$($W1+$W2),0" ; Send-Cmd "$($W1+$W2+$W3),0" ; Send-Cmd "48,-10"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "$($W1+$W2+$W3),0" ; Send-Cmd "$TotalW,0" ; Send-Cmd "74,-10"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "0,0" ; Send-Cmd "0,$H1" ; Send-Cmd "-10,7"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "0,0" ; Send-Cmd "0,$H2" ; Send-Cmd "-10,12"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "$TopBlockX1,$H2" ; Send-Cmd "$TopBlockX2,$H2" ; Send-Cmd "16,30"
Send-Cmd "_DIMLINEAR" ; Send-Cmd "0,$TopY" ; Send-Cmd "0,$($TopY - $D)" ; Send-Cmd "-10,$($TopY - 19)"

Send-Cmd "_ZOOM" ; Send-Cmd "E"
Write-Host "DONE - Stepped Block 3 Views."
