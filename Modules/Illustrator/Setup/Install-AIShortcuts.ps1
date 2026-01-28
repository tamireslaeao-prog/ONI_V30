# ONI V23 - Illustrator Shortcut Injector
# Target: Adobe Illustrator (Any Version)
# Injects ONI_Neural.kys profile with Power AI Shortcuts.

$ErrorActionPreference = "Stop"

# Auto-detect Illustrator version
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = (Get-Item $ScriptRoot).Parent.FullName
$configPath = Join-Path $BaseDir "Config\ai_shortcuts.json"

if (-not (Test-Path $configPath)) {
    Write-Host "[!] Config $configPath not found!"
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json
$profileName = $config.profile_name

# Find Illustrator Presets Path (auto-detect version)
$AdobePresets = "$env:APPDATA\Adobe"
$AIVersions = Get-ChildItem -Path $AdobePresets -Directory -ErrorAction SilentlyContinue | 
Where-Object { $_.Name -match "Illustrator" } | 
Sort-Object Name -Descending

if ($AIVersions.Count -gt 0) {
    $aiSettingsPath = Join-Path $AIVersions[0].FullName "Presets\en_US\Keyboard Shortcuts"
    Write-Host "[*] Detected: $($AIVersions[0].Name)" -ForegroundColor Cyan
}
else {
    # Fallback
    $aiSettingsPath = "$env:APPDATA\Adobe\Illustrator\Presets\en_US\Keyboard Shortcuts"
    Write-Host "[!] No Illustrator detected, using fallback path" -ForegroundColor Yellow
}

if (-not (Test-Path $aiSettingsPath)) {
    Write-Host "[*] Creating Illustrator Shortcuts directory..."
    New-Item -ItemType Directory -Path $aiSettingsPath -Force
}

$targetFile = Join-Path $aiSettingsPath "$profileName.kys"

# Backup existing
if (Test-Path $targetFile) {
    $backupFile = "$targetFile.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $targetFile $backupFile -Force
    Write-Host "[*] Backup created: $backupFile" -ForegroundColor Gray
}

# Generate .kys content from JSON config
$kysContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<shortcuts>
    <version>1.0</version>
    <name>$profileName</name>
"@

foreach ($shortcut in $config.shortcuts) {
    $kysContent += @"

    <shortcut>
        <key>$($shortcut.key)</key>
        <modifier>$($shortcut.modifier)</modifier>
        <command>$($shortcut.command)</command>
        <description>$($shortcut.description)</description>
    </shortcut>
"@
}

$kysContent += @"

</shortcuts>
"@

# Write file
$kysContent | Out-File -FilePath $targetFile -Encoding UTF8 -Force

Write-Host "[✓] Shortcuts injected successfully!" -ForegroundColor Green
Write-Host "[*] Profile: $profileName" -ForegroundColor Cyan
Write-Host "[*] Location: $targetFile" -ForegroundColor Gray
Write-Host ""
Write-Host "[!] To activate:" -ForegroundColor Yellow
Write-Host "    1. Open Illustrator" -ForegroundColor White
Write-Host "    2. Edit > Keyboard Shortcuts" -ForegroundColor White
Write-Host "    3. Set: $profileName" -ForegroundColor White
