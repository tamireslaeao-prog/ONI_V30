$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Trace {
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

if (-not ("Win32_Trace" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Trace (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Trace]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Trace]::GetCurrentThreadId()
    
    # 1. Force Focus
    [Win32_Trace]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Trace]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Trace]::SetForegroundWindow($hwnd)
    [Win32_Trace]::SwitchToThisWindow($hwnd, $true)
    
    # 2. Open Bitmaps Menu (Alt+B)
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("%b") # Alt+B
    Write-Host "Sent Alt+B"
    Start-Sleep -Milliseconds 500
    
    # 3. Select 'Rastrear Bitmap' (R)
    # Note: In PT-BR, 'Rastrear Bitmap' usually has 'R' as accelerator.
    [System.Windows.Forms.SendKeys]::SendWait("r")
    Write-Host "Sent R"
    Start-Sleep -Milliseconds 500
    
    # 4. Select 'Logotipo Detalhado' (Likely 'L' or arrow keys)
    # To be safe, we can use Arrow Down multiple times + Enter
    # Menu structure: [Quick Trace, Centerline ->, Outline -> [Line Art, Logo, Detailed Logo...]]
    # It might be in a submenu.
    # Strategy: Try 'l' (Logotipo). If fails, we might need manual verification.
    
    # Let's try 'l' for "Logotipo Detalhado" or "Logotipo".
    [System.Windows.Forms.SendKeys]::SendWait("l")
    Write-Host "Sent L"
    Start-Sleep -Milliseconds 500
    
    # 5. Confirm (Enter) - Just in case it's selected but needs enter
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter (Launch PowerTrace)"
    
    # 6. Wait for PowerTrace Dialog and confirm it.
    # It usually opens a big modal window.
    # We press Enter to accept defaults.
    Start-Sleep -Seconds 3
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter (Confirm PowerTrace)"
    
    [Win32_Trace]::AttachThreadInput($currentThread, $targetThread, $false)
    Write-Host "Trace Sequence Complete."
}
else {
    Write-Error "CorelDRAW process not found!"
}
