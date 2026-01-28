# CorelDraw Drawing Moves Only
# Assumes Tool is ALREADY SELECTED
$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
Add-Type -AssemblyName System.Windows.Forms

function Click-At ($x, $y, $isNode) {
    [User32]::SetCursorPos($x, $y)
    Start-Sleep -Milliseconds 100
    [User32]::mouse_event(0x02, 0, 0, 0, 0) # Left Down
    Start-Sleep -Milliseconds 50
    [User32]::mouse_event(0x04, 0, 0, 0, 0) # Left Up
    Start-Sleep -Milliseconds 200 # Wait for node
}

function Drag-At ($startX, $startY, $endX, $endY) {
    [User32]::SetCursorPos($startX, $startY)
    Start-Sleep -Milliseconds 100
    [User32]::mouse_event(0x02, 0, 0, 0, 0) # Left Down
    Start-Sleep -Milliseconds 100
    # Drag
    [User32]::SetCursorPos($endX, $endY)
    Start-Sleep -Milliseconds 100
    [User32]::mouse_event(0x04, 0, 0, 0, 0) # Left Up
    Start-Sleep -Milliseconds 200
}

# Focus Corel
$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1
if ($proc) {
    $hwnd = $proc.MainWindowHandle
    [User32]::SetForegroundWindow($hwnd)
    Start-Sleep -Seconds 1
}

# Resolution & Center
$res = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$cx = $res.Width / 2
$cy = $res.Height / 2

Write-Host "Starting Apple Draw Routine..."

# 0. COM AUTOMATION ACTION: Select Bezier Tool (Robust)
Write-Host "Selecting Bezier Tool via COM (ActiveTool=6)..."
try {
    # Try New-Object force connection as proven in testing
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    $corel.ActiveTool = 6 # cdrToolBezier
    Start-Sleep -Seconds 1
    if ($corel.ActiveTool -eq 6) {
        Write-Host "COM Selection Confirmed."
    }
    else {
        Write-Host "WARNING: COM Selection might have failed. ActiveTool: $($corel.ActiveTool)"
    }
}
catch {
    Write-Host "COM Selection Error: $_"
}
Start-Sleep -Seconds 1

# 1. Top Center (Start)
Click-At $cx ($cy - 200) $true

# 2. Right Shoulder (Curve)
Drag-At ($cx + 150) ($cy - 180) ($cx + 200) ($cy - 250)

# 3. Right Side (Curve down)
Drag-At ($cx + 180) ($cy + 50) ($cx + 250) ($cy)

# 4. Bottom Center (Base indentation)
Click-At $cx ($cy + 180) $true

# 5. Left Side (Curve Up)
Drag-At ($cx - 180) ($cy + 50) ($cx - 250) ($cy)

# 6. Left Shoulder
Drag-At ($cx - 150) ($cy - 180) ($cx - 200) ($cy - 250)

# 7. Close Shape
Click-At $cx ($cy - 200) $true

Write-Host "Drawing Complete!"
