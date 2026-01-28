<#
    .SYNOPSIS
        ONI V24 Module Component.
    .DESCRIPTION
        Part of the ONI Automation Framework.
        Managed by The Jewel Polishing Protocol.
    .AUTHOR
        Antigravity Engine (Google DeepMind)
    .DATE
        2026-01-10
#>
# ============================================================================
# 🚀 ONI EDGE LAUNCHER - Advanced Browser Starter
# Description: Launches Edge with custom profiles, flags, and CDP enabled
# ============================================================================

param(
    [string]$Profile = "Default",
    [int]$CDPPort = 9222,
    [string]$StartURL = "about:blank",
    [switch]$Incognito,
    [switch]$Maximized,
    [switch]$Kiosk,
    [string[]]$Extensions = @(),
    [string]$UserAgent = $null,
    [switch]$DisableGPU,
    [switch]$NoSandbox,
    [string[]]$CustomFlags = @()
)

Write-Host "🚀 ONI EDGE LAUNCHER" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Locate Edge Executable
# ============================================================================
$edgePaths = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

$edgeExe = $null
foreach ($path in $edgePaths) {
    if (Test-Path $path) {
        $edgeExe = $path
        break
    }
}

if (-not $edgeExe) {
    Write-Host "   [FAIL] Microsoft Edge not found" -ForegroundColor Red
    exit 1
}

Write-Host "   [OK] Found Edge: $edgeExe" -ForegroundColor Green

# ============================================================================
# Build Launch Arguments
# ============================================================================
$arguments = @()

# Remote Debugging (Essential for ONI Control)
$arguments += "--remote-debugging-port=$CDPPort"

# Profile
if ($Profile -ne "Default") {
    $arguments += "--profile-directory=`"$Profile`""
}

# Start URL
if ($StartURL -ne "about:blank") {
    $arguments += "`"$StartURL`""
}

# Incognito Mode
if ($Incognito) {
    $arguments += "--inprivate"
}

# Window State
if ($Maximized) {
    $arguments += "--start-maximized"
}

if ($Kiosk) {
    $arguments += "--kiosk"
    $arguments += "--edge-kiosk-type=fullscreen"
}

# User Agent Override
if ($UserAgent) {
    $arguments += "--user-agent=`"$UserAgent`""
}

# Performance Flags
if ($DisableGPU) {
    $arguments += "--disable-gpu"
}

if ($NoSandbox) {
    $arguments += "--no-sandbox"
    Write-Host "   [WARN] Running without sandbox - security risk!" -ForegroundColor Yellow
}

# Extensions
foreach ($ext in $Extensions) {
    $arguments += "--load-extension=`"$ext`""
}

# Custom Flags
$arguments += $CustomFlags

# ============================================================================
# Display Configuration
# ============================================================================
Write-Host ""
Write-Host "   Configuration:" -ForegroundColor White
Write-Host "   ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "   Profile:       $Profile" -ForegroundColor Gray
Write-Host "   CDP Port:      $CDPPort" -ForegroundColor Gray
Write-Host "   Start URL:     $StartURL" -ForegroundColor Gray
Write-Host "   Incognito:     $Incognito" -ForegroundColor Gray
Write-Host "   Maximized:     $Maximized" -ForegroundColor Gray
Write-Host "   Kiosk Mode:    $Kiosk" -ForegroundColor Gray

if ($UserAgent) {
    Write-Host "   User Agent:    $UserAgent" -ForegroundColor Gray
}

if ($Extensions.Count -gt 0) {
    Write-Host "   Extensions:    $($Extensions.Count) loaded" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# Launch Edge
# ============================================================================
Write-Host "   Launching Edge..." -ForegroundColor Yellow

try {
    $process = Start-Process -FilePath $edgeExe -ArgumentList $arguments -PassThru
    
    Write-Host "   ✓ Edge launched (PID: $($process.Id))" -ForegroundColor Green
    
    # Wait for CDP to be ready
    Write-Host "   Waiting for CDP connection..." -ForegroundColor Gray
    
    $maxWait = 30
    $waited = 0
    $cdpReady = $false
    
    while ($waited -lt $maxWait -and -not $cdpReady) {
        Start-Sleep -Seconds 1
        $waited++
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$CDPPort/json/version" -ErrorAction Stop
            $cdpReady = $true
        }
        catch {
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }
    }
    
    Write-Host ""
    
    if ($cdpReady) {
        Write-Host "   ✓ CDP ready at http://localhost:$CDPPort" -ForegroundColor Green
        
        # Get browser version
        try {
            $version = Invoke-RestMethod -Uri "http://localhost:$CDPPort/json/version"
            Write-Host "   Browser: $($version.Browser)" -ForegroundColor Gray
            Write-Host "   Protocol: $($version.'Protocol-Version')" -ForegroundColor Gray
        }
        catch {}
        
        Write-Host ""
        Write-Host "   ═══════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "   ONI Edge Control is now ACTIVE" -ForegroundColor Green
        Write-Host "   ═══════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   Next Steps:" -ForegroundColor White
        Write-Host "   1. Run ONI_Edge_Sentinel.ps1 to monitor" -ForegroundColor Gray
        Write-Host "   2. Use oni_lib_edge.js for automation" -ForegroundColor Gray
        Write-Host "   3. Access DevTools at: http://localhost:$CDPPort" -ForegroundColor Gray
    }
    else {
        Write-Host "   [WARN] CDP did not respond within $maxWait seconds" -ForegroundColor Yellow
        Write-Host "   Edge may still be starting up" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   [FAIL] Could not launch Edge: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Profile Presets
# ============================================================================
Write-Host ""
Write-Host "   Profile Presets:" -ForegroundColor DarkCyan
Write-Host "   ────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "   Development:   .\ONI_Edge_Launcher.ps1 -Profile Dev" -ForegroundColor Gray
Write-Host "   Testing:       .\ONI_Edge_Launcher.ps1 -Profile Test -Incognito" -ForegroundColor Gray
Write-Host "   Automation:    .\ONI_Edge_Launcher.ps1 -Profile Bot -DisableGPU" -ForegroundColor Gray
Write-Host "   Presentation:  .\ONI_Edge_Launcher.ps1 -Kiosk -StartURL 'https://yoursite.com'" -ForegroundColor Gray
Write-Host ""
