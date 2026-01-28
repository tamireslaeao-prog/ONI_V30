$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Export {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);
    [DllImport("user32.dll")]
    public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out IntPtr ProcessId);
    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentThreadId();
}
"@

if (-not ("Win32_Export" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Export (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Export]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Export]::GetCurrentThreadId()
    
    [Win32_Export]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Export]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Export]::SetForegroundWindow($hwnd)
    [Win32_Export]::SwitchToThisWindow($hwnd, $true)
    
    # 1. Open Export Dialog (Ctrl+E)
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("^e")
    Write-Host "Sent Ctrl+E"
    
    # Wait for Dialog (Standard Save As style)
    Start-Sleep -Seconds 2
    
    # 2. Type Filename
    $filePath = "C:\Users\user\Desktop\verify_trace.svg"
    
    # Ensure file doesn't exist to avoid overwrite prompt complexity
    if (Test-Path $filePath) { Remove-Item $filePath -Force }
    
    [System.Windows.Forms.SendKeys]::SendWait($filePath)
    Write-Host "Sent Path"
    Start-Sleep -Milliseconds 500
    
    # 3. Enter (Save)
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter 1"
    
    # 4. Wait for SVG Export Settings Dialog
    Start-Sleep -Seconds 2
    
    # 5. Enter (Confirm Settings)
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter 2 (Settings)"
    
    [Win32_Export]::AttachThreadInput($currentThread, $targetThread, $false)
    Write-Host "Export Sequence Complete."
}
else {
    Write-Error "CorelDRAW process not found!"
}
