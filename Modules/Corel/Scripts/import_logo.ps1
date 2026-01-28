$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
public class Win32_Import {
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

if (-not ("Win32_Import" -as [type])) {
    Add-Type -TypeDefinition $code
}

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    Write-Host "Targeting CorelDRAW for Import (PID: $($proc.Id))"
    $hwnd = $proc.MainWindowHandle
    
    $targetThread = [Win32_Import]::GetWindowThreadProcessId($hwnd, [ref][IntPtr]::Zero)
    $currentThread = [Win32_Import]::GetCurrentThreadId()
    
    # Force Focus
    [Win32_Import]::AttachThreadInput($currentThread, $targetThread, $true)
    [Win32_Import]::ShowWindow($hwnd, 3) 
    Start-Sleep -Milliseconds 100
    [Win32_Import]::SetForegroundWindow($hwnd)
    [Win32_Import]::SwitchToThisWindow($hwnd, $true)
    
    # 1. Open Import Dialog (Ctrl+I)
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("^i")
    Write-Host "Sent Ctrl+I"
    
    # Wait for Dialog
    Start-Sleep -Seconds 2
    
    # 2. Type Filename
    $filePath = "C:\Users\user\Desktop\logo_import.png"
    [System.Windows.Forms.SendKeys]::SendWait($filePath)
    Write-Host "Sent Path"
    Start-Sleep -Milliseconds 500
    
    # 3. Enter (to select file)
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter 1"
    Start-Sleep -Milliseconds 1000
    
    # 4. Enter (to place or confirm if second dialog appears)
    # Corel sometimes asks for click to place. Enter usually places at center or 0,0.
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Sent Enter 2"
    
    [Win32_Import]::AttachThreadInput($currentThread, $targetThread, $false)
    Write-Host "Import Sequence Complete."
}
else {
    Write-Error "CorelDRAW process not found!"
}
