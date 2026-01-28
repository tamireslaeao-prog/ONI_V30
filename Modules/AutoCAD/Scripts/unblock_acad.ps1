
$wshell = New-Object -ComObject WScript.Shell
if ($wshell.AppActivate("Autodesk AutoCAD")) {
    Write-Host "Focusing AutoCAD..."
    Start-Sleep -Seconds 1
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 500
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 500
    $wshell.SendKeys("{ENTER}")
    Write-Host "Keys sent."
}
else {
    Write-Host "Could not find AutoCAD window."
}
