$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " CORELDRAW TRACE HELPER (MANUAL ASSIST)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will attempt to trigger 'Trace Bitmap' for you."
Write-Host "1. Ensure CorelDRAW is open and the Logo is SELECTED."
Write-Host "2. We will send 'Alt+B' (Bitmaps) -> 'R' (Trace) -> 'L' (Detailed)."
Write-Host ""
Write-Host "Press ENTER to execute..." -ForegroundColor Yellow
Read-Host

$proc = Get-Process | Where-Object { $_.ProcessName -like "CorelDRW*" } | Select-Object -First 1

if ($proc) {
    $hwnd = $proc.MainWindowHandle
    
    # Simple Focus
    [System.Windows.Forms.SendKeys]::SendWait("%{TAB}") # Alt+Tab toggle attempt or just rely on user being active?
    # Better: Use the robust focus we know works, but keep it simple here.
    # We assume user might be looking at it.
    
    # Try the Keys
    Write-Host "Sending Keys in 3 seconds..."
    Start-Sleep -Seconds 3
    
    [System.Windows.Forms.SendKeys]::SendWait("%b")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("r")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("l")
    
    Write-Host "Done. If dialog appears, press Enter manually."
}
else {
    Write-Error "CorelDRAW process not found!"
}
