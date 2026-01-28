
# ONI SHOWTIME: CYBERPUNK GENESIS (PROFESSIONAL)
# Launches JSX via COM - 100% Reliable

param()

# Cinematic Logging
function Log-Cinematic {
    param([string]$Msg, [string]$Color="Cyan")
    Write-Host "[ ONI CORE ] $Msg" -ForegroundColor $Color
}

Clear-Host
Write-Host ""
Log-Cinematic "========================================" "DarkGray"
Log-Cinematic "    ONI SHOWTIME: CYBERPUNK GENESIS    " "Magenta"
Log-Cinematic "========================================" "DarkGray"
Write-Host ""

Start-Sleep -Milliseconds 500

Log-Cinematic "CONNECTING TO PHOTOSHOP NEURAL INTERFACE..." "Yellow"
Start-Sleep -Milliseconds 300

try {
    $app = New-Object -ComObject Photoshop.Application
    Log-Cinematic "CONNECTION ESTABLISHED." "Green"
} catch {
    Log-Cinematic "FAILED TO CONNECT. Is Photoshop running?" "Red"
    exit 1
}

Start-Sleep -Milliseconds 500

Log-Cinematic "LOADING GENESIS PAYLOAD..." "Cyan"
$jsxPath = "C:\Users\user\Desktop\ONIV24\app\scripts\demos\demo_genesis.jsx"

if (-not (Test-Path $jsxPath)) {
    Log-Cinematic "PAYLOAD NOT FOUND: $jsxPath" "Red"
    exit 1
}

Log-Cinematic "INJECTING GENESIS PROTOCOL..." "Magenta"
Start-Sleep -Milliseconds 300

try {
    $app.DoJavaScriptFile($jsxPath)
    Log-Cinematic "INJECTION COMPLETE." "Green"
} catch {
    Log-Cinematic "INJECTION FAILED: $_" "Red"
    exit 1
}

Write-Host ""
Log-Cinematic "========================================" "DarkGray"
Log-Cinematic "        SHOWTIME EXECUTION COMPLETE    " "Green"
Log-Cinematic "========================================" "DarkGray"
Write-Host ""
