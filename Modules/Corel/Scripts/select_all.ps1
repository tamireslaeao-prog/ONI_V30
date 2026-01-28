$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Select {
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

if (-not ("Win32_Select" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Selection (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Select]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Select]::GetCurrentThreadId()
    
    [Win32_Select]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Select]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Select]::SetForegroundWindow($hwnd)
    [Win32_Select]::SwitchToThisWindow($hwnd, $true)
    
    # Send Ctrl+A
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Write-Host "Sent Ctrl+A"
    
    [Win32_Select]::AttachThreadInput($currentThread, $targetThread, $false)
}
else {
    Write-Error "CorelDRAW process not found!"
}
