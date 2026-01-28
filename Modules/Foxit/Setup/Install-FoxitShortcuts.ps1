# ONI V23 - Foxit PDF Shortcut Injector
# Target: Foxit PDF Reader (Any Version)
# Injects custom shortcuts via registry modification

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = (Get-Item $ScriptRoot).Parent.FullName
$configPath = Join-Path $BaseDir "Config\foxit_shortcuts.json"

if (-not (Test-Path $configPath)) {
    Write-Host "[!] Config $configPath not found!"
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json

# Find Foxit installation via registry
$foxitPath = $null
$regPaths = @(
    "HKLM:\SOFTWARE\WOW6432Node\Foxit Software\Foxit PDF Reader",
    "HKLM:\SOFTWARE\Foxit Software\Foxit PDF Reader"
)

foreach ($regPath in $regPaths) {
    if (Test-Path $regPath) {
        try {
            $foxitPath = (Get-ItemProperty -Path $regPath -Name "InstallPath" -ErrorAction Stop).InstallPath
            if ($foxitPath) {
                Write-Host "[*] Detected Foxit PDF Reader at: $foxitPath" -ForegroundColor Cyan
                break
            }
        }
        catch {
            continue
        }
    }
}

if (-not $foxitPath) {
    Write-Host "[!] Foxit PDF Reader not found in registry" -ForegroundColor Yellow
    Write-Host "[*] Attempting default path..." -ForegroundColor Gray
    $foxitPath = "${env:ProgramFiles(x86)}\Foxit Software\Foxit PDF Reader"
}

# Foxit uses XML config in AppData
$foxitConfig = "$env:APPDATA\Foxit Software\Foxit PDF Reader"
if (-not (Test-Path $foxitConfig)) {
    New-Item -ItemType Directory -Path $foxitConfig -Force | Out-Null
}

$shortcutsXml = Join-Path $foxitConfig "Shortcuts.xml"

# Backup existing
if (Test-Path $shortcutsXml) {
    $backupFile = "$shortcutsXml.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $shortcutsXml $backupFile -Force
    Write-Host "[*] Backup created: $backupFile" -ForegroundColor Gray
}

# Generate XML
$xmlContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<FoxitShortcuts>
    <Version>1.0</Version>
    <ONI_Custom>true</ONI_Custom>
"@

foreach ($shortcut in $config.shortcuts) {
    $xmlContent += @"

    <Shortcut>
        <Key>$($shortcut.key)</Key>
        <Modifier>$($shortcut.modifier)</Modifier>
        <Command>$($shortcut.command)</Command>
        <Description>$($shortcut.description)</Description>
    </Shortcut>
"@
}

$xmlContent += @"

</FoxitShortcuts>
"@

# Write file
$xmlContent | Out-File -FilePath $shortcutsXml -Encoding UTF8 -Force

Write-Host "[✓] Shortcuts injected successfully!" -ForegroundColor Green
Write-Host "[*] Location: $shortcutsXml" -ForegroundColor Gray
Write-Host ""
Write-Host "[!] Restart Foxit PDF Reader to apply changes" -ForegroundColor Yellow
