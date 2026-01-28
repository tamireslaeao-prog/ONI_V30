$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Context {
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

if (-not ("Win32_Context" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Context Trace (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Context]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Context]::GetCurrentThreadId()
    
    [Win32_Context]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Context]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Context]::SetForegroundWindow($hwnd)
    [Win32_Context]::SwitchToThisWindow($hwnd, $true)
    
    # 1. Move to Center (964, 565)
    $x = 964
    $y = 565
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
    Start-Sleep -Milliseconds 500
    
    # 2. Right Click
    # MOUSEEVENTF_RIGHTDOWN = 0x0008
    # MOUSEEVENTF_RIGHTUP = 0x0010
    [Win32_Context]::mouse_event(0x0008, 0, 0, 0, 0)
    [Win32_Context]::mouse_event(0x0010, 0, 0, 0, 0)
    Write-Host "Right Clicked at $x, $y"
    Start-Sleep -Seconds 1
    
    # 3. Brief visual pause for menu to appear
    # Send 'r' for Rastrear
    [System.Windows.Forms.SendKeys]::SendWait("r")
    Write-Host "Sent R"
    Start-Sleep -Milliseconds 500
    
    # 4. Send 'l' for Logotipo Detalhado (if submenu opens)
    [System.Windows.Forms.SendKeys]::SendWait("l")
    Write-Host "Sent L"
    Start-Sleep -Milliseconds 500
    
    # 5. Confirm
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter"
    
    # 6. Confirm PowerTrace Dialog (if opened)
    Start-Sleep -Seconds 3
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter 2"

    [Win32_Context]::AttachThreadInput($currentThread, $targetThread, $false)
}
else {
    Write-Error "CorelDRAW process not found!"
}
