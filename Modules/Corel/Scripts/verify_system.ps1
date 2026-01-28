# ONI System Verification - CorelDRAW
param([switch]$Verbose)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    
    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
    public const int MOUSEEVENTF_LEFTUP = 0x04;
}
"@

function Send-Keys {
    param([string]$Keys, [int]$Wait = 100)
    [System.Windows.Forms.SendKeys]::SendWait($Keys)
    Start-Sleep -Milliseconds $Wait
}

function Click-Mouse {
    [Win32]::mouse_event(0x02, 0, 0, 0, 0) # Left Down
    Start-Sleep -Milliseconds 50
    [Win32]::mouse_event(0x04, 0, 0, 0, 0) # Left Up
}

Write-Host "🔍 ONI: Searching for CorelDRAW..." -ForegroundColor Cyan

$corel = Get-Process "CorelDRW" -ErrorAction SilentlyContinue

if (-not $corel) {
    Write-Host "⚠️ CorelDRAW not running. Launching..." -ForegroundColor Yellow
    # Trying standard path:
    $paths = @(
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2024\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2023\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2022\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2021\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2020\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2019\Programs64\CorelDRW.exe"
    )
    
    foreach ($p in $paths) {
        if (Test-Path $p) {
            Start-Process $p
            Write-Host "  Launched: $p"
            Start-Sleep -Seconds 20 # Wait for launch
            break
        }
    }
    
    $corel = Get-Process "CorelDRW" -ErrorAction SilentlyContinue
    if (-not $corel) {
        Write-Error "Could not launch CorelDRAW. Please open it manually."
    }
}

# Focus
Write-Host "⚡ Forcing Focus..."
$handle = $corel.MainWindowHandle
[Win32]::ShowWindow($handle, 9) # Restore
[Win32]::SetForegroundWindow($handle)
Start-Sleep -Seconds 1
[Win32]::SetForegroundWindow($handle) # Double tap

# New Document
Write-Host "📄 Creating Document..." -ForegroundColor White
Send-Keys "^n" # Ctrl+N
Start-Sleep -Seconds 3
Send-Keys "{ENTER}" # Confirm dialog
Start-Sleep -Seconds 3

# Text Tool (F8)
Write-Host "✍️ Selecting Text Tool..." -ForegroundColor White
Send-Keys "{F8}"
Start-Sleep -Seconds 1

# Click in center (approx)
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$x = $screen.Width / 2
$y = $screen.Height / 2
[Win32]::SetCursorPos($x, $y)
Click-Mouse
Start-Sleep -Seconds 1

# Type Message
Write-Host "💬 Typing Message..." -ForegroundColor Green
Send-Keys "ONI"
Start-Sleep -Milliseconds 200
Send-Keys " "
Start-Sleep -Milliseconds 200
Send-Keys "COREL"
Start-Sleep -Milliseconds 200
Send-Keys " "
Start-Sleep -Milliseconds 200
Send-Keys "ONLINE"

Write-Host "✅ Test Complete." -ForegroundColor Green
