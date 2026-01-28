# CorelDraw Launch Script (COM Enhanced)
$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
}
"@
Add-Type -AssemblyName System.Windows.Forms

function Log-Info {
    param([string]$msg)
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

function Log-Error {
    param([string]$msg)
    Write-Host "[ERROR] $msg" -ForegroundColor Red
}

# 1. Try COM Automation (Preferred Method)
Log-Info "Attempting COM Connection..."
try {
    $corel = New-Object -ComObject CorelDRAW.Application
    if ($corel) {
        Log-Info "COM Object created successfully."
        $corel.Visible = $true
        
        # Check for active document
        if ($corel.Documents.Count -eq 0) {
            Log-Info "No active document. Creating new..."
            $doc = $corel.CreateDocument()
            $doc.Activate()
        } else {
            Log-Info "Document already open: $($corel.ActiveDocument.Name)"
            $corel.ActiveDocument.Activate()
        }
        
        # Force window to foreground
        $hwnd = $corel.AppWindow.Handle
        [User32]::ShowWindow($hwnd, 3) # Maximize
        [User32]::SetForegroundWindow($hwnd)
        
        Log-Info "CorelDRAW Ready via COM."
        exit 0
    }
} catch {
    Log-Info "COM Connection failed/unavailable. Falling back to Process Launch."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
}

# 2. Fallback: Process Launch
Log-Info "Starting Legacy Launch Protocol..."

$running = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($running) {
    Log-Info "Process found: $($running.Id)"
    $hwnd = $running.MainWindowHandle
    if ($hwnd -ne 0) {
        [User32]::ShowWindow($hwnd, 3) # Maximize
        [User32]::SetForegroundWindow($hwnd)
    }
} else {
    Log-Info "Process not found. Searching executable..."
    
    # Smart Path Search
    $paths = @(
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2024\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite 2025\Programs64\CorelDRW.exe",
        "C:\Program Files\Corel\CorelDRAW Graphics Suite\Programs64\CorelDRW.exe"
    )
    
    $exePath = $null
    foreach ($p in $paths) {
        if (Test-Path $p) {
            $exePath = $p
            break
        }
    }
    
    if (-not $exePath) {
        Log-Info "Using Get-StartApps fallback..."
        Start-Process "powershell" -ArgumentList "start shell:AppsFolder\$(Get-StartApps 'CorelDRAW' | Select -First 1 -ExpandProperty AppID)"
    } else {
        Log-Info "Launching: $exePath"
        Start-Process $exePath
    }
    
    # Wait for Startup
    Log-Info "Waiting 20s for startup..."
    Start-Sleep -Seconds 20
}

# 3. Post-Launch interactions (Legacy Blind Input)
# Only run if we couldn't use COM
$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1
if ($proc) {
    $hwnd = $proc.MainWindowHandle
    [User32]::SetForegroundWindow($hwnd)
    Start-Sleep -Seconds 1
    
    # Send Ctrl+N blindly just in case
    Log-Info "Sending blind Ctrl+N..."
    [System.Windows.Forms.SendKeys]::SendWait("^n")
    Start-Sleep -Seconds 1
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
}

Log-Info "Legacy Startup Complete."
