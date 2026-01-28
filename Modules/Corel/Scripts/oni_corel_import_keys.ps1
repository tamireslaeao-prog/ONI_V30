
param(
    [Parameter(Mandatory = $true)][string]$FilePath
)

$wshell = New-Object -ComObject WScript.Shell

# Focus Corel
if ($wshell.AppActivate("CorelDRAW")) {
    Write-Host "Focused CorelDRAW."
    Start-Sleep -Seconds 1
    
    # Ctrl+I (Import)
    $wshell.SendKeys("^i")
    Start-Sleep -Seconds 2
    
    # Type Path
    $wshell.SendKeys($FilePath)
    Start-Sleep -Seconds 1
    
    # Enter (Select File)
    $wshell.SendKeys("{ENTER}")
    Start-Sleep -Seconds 2
    
    # Enter (Place at default pos/center)
    # Sometimes Corel asks for position cursor. Enter usually places at 0,0 or center.
    $wshell.SendKeys("{ENTER}")
    Start-Sleep -Seconds 1
    
    # Enter again (Just in case of filter dialog) - but we use SVG which usually has one
    $wshell.SendKeys("{ENTER}")
    
    Write-Host "Keystrokes sent."
}
else {
    Write-Host "CorelDRAW not found."
    exit 1
}
