$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Action {
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
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentThreadId();
}
"@

if (-not ("Win32_Action" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $shell = New-Object -ComObject Shell.Application
    $shell.MinimizeAll()
    Start-Sleep -Milliseconds 500
    
    $targetThread = [Win32_Action]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Action]::GetCurrentThreadId()
    
    [Win32_Action]::AttachThreadInput($currentThread, $targetThread, $true)
    
    [Win32_Action]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Action]::SetForegroundWindow($hwnd)
    [Win32_Action]::SwitchToThisWindow($hwnd, $true)
    
    # IMMEDIATE INPUT INJECTION: CLICK OK BUTTON at (1286, 831)
    Start-Sleep -Milliseconds 500
    
    $x = 1202
    $y = 831
    # Correction: previous scan showed OK at 1286, but wait...
    # Latest scan: uid_5028d643 (OK) rect: left:1246, top:819, right:1326, bottom:843. Center X: 1286, Center Y: 831.
    $x = 1286
    $y = 831
    
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
    Start-Sleep -Milliseconds 100
    
    # Left Click
    [Win32_Action]::mouse_event(0x02, 0, 0, 0, 0) # LeftDown
    [Win32_Action]::mouse_event(0x04, 0, 0, 0, 0) # LeftUp
    
    Write-Host "Clicked OK at $x, $y"
    
    [Win32_Action]::AttachThreadInput($currentThread, $targetThread, $false)
    Write-Host "Focus Forced and Clicked."
}
else {
    Write-Error "CorelDRAW process not found!"
}
