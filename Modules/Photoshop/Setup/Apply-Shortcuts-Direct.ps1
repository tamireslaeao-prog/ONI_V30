$ErrorActionPreference = "Stop"

# Configuration
$ConfigPath = "C:\Users\user\Desktop\ONI_V27\Modules\Photoshop\Config\ps_shortcuts.json"
$ProfileName = "ONI_Neural"

# Helper Functions
function Convert-KeyToPhotoshopFormat {
    param([string]$Keys)
    $parts = $Keys -split "\+"
    $result = @{ Ctrl = $false; Shift = $false; Alt = $false; Key = "" }
    foreach ($part in $parts) {
        $p = $part.Trim()
        switch -Regex ($p) {
            "^Ctrl$" { $result.Ctrl = $true }
            "^Shift$" { $result.Shift = $true }
            "^Alt$" { $result.Alt = $true }
            default { $result.Key = $p }
        }
    }
    return $result
}

function Get-VirtualKeyCode {
    param([string]$Key)
    $keyMap = @{
        "A" = 65; "B" = 66; "C" = 67; "D" = 68; "E" = 69
        "F" = 70; "G" = 71; "H" = 72; "I" = 73; "J" = 74
        "K" = 75; "L" = 76; "M" = 77; "N" = 78; "O" = 79
        "P" = 80; "Q" = 81; "R" = 82; "S" = 83; "T" = 84
        "U" = 85; "V" = 86; "W" = 87; "X" = 88; "Y" = 89; "Z" = 90
        "0" = 48; "1" = 49; "2" = 50; "3" = 51; "4" = 52
        "5" = 53; "6" = 54; "7" = 55; "8" = 56; "9" = 57
        "F1" = 112; "F2" = 113; "F3" = 114; "F4" = 115
        "F5" = 116; "F6" = 117; "F7" = 118; "F8" = 119
        "F9" = 120; "F10" = 121; "F11" = 122; "F12" = 123
        "Enter" = 13; "Escape" = 27; "Space" = 32
        "Tab" = 9; "Backspace" = 8; "Delete" = 46
    }
    if ($keyMap.ContainsKey($Key)) { return $keyMap[$Key] }
    return 0
}

# Main Logic
$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$appData = [Environment]::GetFolderPath("ApplicationData")
$adobeRoot = Join-Path $appData "Adobe"
$psDirs = Get-ChildItem $adobeRoot -Directory | Where-Object { $_.Name -match "^Adobe Photoshop" }

if ($psDirs.Count -eq 0) { Write-Error "No Photoshop installation found."; exit 1 }

foreach ($dir in $psDirs) {
    $shortcutsDir = Join-Path $dir.FullName "Presets\Keyboard Shortcuts"
    if (-not (Test-Path $shortcutsDir)) { New-Item -ItemType Directory -Path $shortcutsDir -Force | Out-Null }
    
    $outputPath = Join-Path $shortcutsDir "${ProfileName}.kys"
    
    $xml = @"
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>$ProfileName</key>
    <dict>
"@

    foreach ($shortcut in $config.shortcuts) {
        $keyData = Convert-KeyToPhotoshopFormat -Keys $shortcut.keys
        $vk = Get-VirtualKeyCode -Key $keyData.Key
        $modifiers = 0
        if ($keyData.Shift) { $modifiers += 1 }
        if ($keyData.Ctrl) { $modifiers += 2 }
        if ($keyData.Alt) { $modifiers += 4 }
        
        $id = $shortcut.id
        $xml += @"

        <key>$id</key>
        <dict>
            <key>key</key>
            <integer>$vk</integer>
            <key>modifiers</key>
            <integer>$modifiers</integer>
        </dict>
"@
    }

    $xml += @"

    </dict>
</dict>
</plist>
"@

    $xml | Out-File -FilePath $outputPath -Encoding UTF8 -Force
    Write-Host "Installed .kys to: $outputPath" -ForegroundColor Green
}
