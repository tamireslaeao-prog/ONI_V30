$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Center {
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

if (-not ("Win32_Center" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Center (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Center]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Center]::GetCurrentThreadId()
    
    # Force Focus
    [Win32_Center]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Center]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Center]::SetForegroundWindow($hwnd)
    [Win32_Center]::SwitchToThisWindow($hwnd, $true)
    
    # Send P (Center)
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("p")
    Write-Host "Sent P"
    
    # Send F4 (Zoom to Fit) just in case
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{F4}")
    Write-Host "Sent F4"
    
    [Win32_Center]::AttachThreadInput($currentThread, $targetThread, $false)
}
else {
    Write-Error "CorelDRAW process not found!"
}
