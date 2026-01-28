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
# ONI CHROME CONTROLLER - Web Automation Master
# Version: 1.0
# Description: Controls Chrome for web automation, navigation, data collection
# ============================================================================

param(
    [string]$Action,
    [string]$Url,
    [string]$Profile = "ONI_Automation",
    [switch]$Incognito,
    [switch]$Headless
)

$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$ONI_API = "http://localhost:8000"
$ProfilesDir = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Profiles"

# Ensure profiles directory exists
if (-not (Test-Path $ProfilesDir)) {
    New-Item -ItemType Directory -Path $ProfilesDir | Out-Null
}

function Show-Usage {
    Write-Host "ONI Chrome Controller" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  -Action open -Url <url>     Open URL in Chrome"
    Write-Host "  -Action search -Url <query> Search Google for query"
    Write-Host "  -Action screenshot          Capture current page"
    Write-Host "  -Action focus               Focus Chrome window"
    Write-Host "  -Action close               Close Chrome"
    Write-Host "  -Action new-tab             Open new tab"
    Write-Host "  -Action collect             Collect page data via ONI Vision"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Profile <name>     Use specific Chrome profile (default: ONI_Automation)"
    Write-Host "  -Incognito          Open in incognito mode"
    Write-Host "  -Headless           Run headless (no UI)"
}

function Start-Chrome {
    param([string]$TargetUrl, [bool]$UseIncognito, [bool]$UseHeadless)
    
    $args = @()
    
    # Use dedicated profile for automation
    $profilePath = Join-Path $ProfilesDir $Profile
    $args += "--user-data-dir=`"$profilePath`""
    
    if ($UseIncognito) {
        $args += "--incognito"
    }
    
    if ($UseHeadless) {
        $args += "--headless=new"
    }
    
    # Automation-friendly flags
    $args += "--disable-popup-blocking"
    $args += "--disable-infobars"
    $args += "--disable-extensions-except="
    $args += "--start-maximized"
    
    if ($TargetUrl) {
        $args += "`"$TargetUrl`""
    }
    
    $argString = $args -join " "
    Write-Host "[CHROME] Starting with args: $argString" -ForegroundColor Gray
    
    Start-Process -FilePath $ChromePath -ArgumentList $argString
    Start-Sleep -Seconds 2
}

function Invoke-ONI {
    param([string]$Endpoint)
    
    try {
        $response = Invoke-RestMethod -Uri "$ONI_API$Endpoint" -Method Get -TimeoutSec 30
        return $response
    }
    catch {
        Write-Host "[ERROR] ONI API call failed: $_" -ForegroundColor Red
        return $null
    }
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

switch ($Action) {
    "open" {
        if (-not $Url) {
            Write-Host "[ERROR] -Url required for 'open' action" -ForegroundColor Red
            exit 1
        }
        Write-Host "[CHROME] Opening: $Url" -ForegroundColor Cyan
        Start-Chrome -TargetUrl $Url -UseIncognito $Incognito -UseHeadless $Headless
        Write-Host "[OK] Chrome started" -ForegroundColor Green
    }
    
    "search" {
        if (-not $Url) {
            Write-Host "[ERROR] -Url (search query) required" -ForegroundColor Red
            exit 1
        }
        $searchUrl = "https://www.google.com/search?q=" + [uri]::EscapeDataString($Url)
        Write-Host "[CHROME] Searching: $Url" -ForegroundColor Cyan
        Start-Chrome -TargetUrl $searchUrl -UseIncognito $Incognito -UseHeadless $Headless
        Write-Host "[OK] Search initiated" -ForegroundColor Green
    }
    
    "focus" {
        Write-Host "[CHROME] Focusing window..." -ForegroundColor Cyan
        $result = Invoke-ONI -Endpoint "/api/focus?title=Chrome"
        if ($result) {
            Write-Host "[OK] Chrome focused" -ForegroundColor Green
        }
    }
    
    "screenshot" {
        Write-Host "[CHROME] Capturing screenshot..." -ForegroundColor Cyan
        $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
        $AssetsDir = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
        if (-not (Test-Path $AssetsDir)) { New-Item -ItemType Directory -Path $AssetsDir | Out-Null }
        $outputPath = Join-Path $AssetsDir "screenshot_$timestamp.png"
        
        # Use ONI hybrid vision
        $result = Invoke-ONI -Endpoint "/api/hybrid-vision/web?nocache=$timestamp"
        if ($result -and $result.annotated_path) {
            Copy-Item $result.annotated_path $outputPath
            Write-Host "[OK] Screenshot saved: $outputPath" -ForegroundColor Green
        }
        else {
            Write-Host "[WARN] Could not capture - ensure ONI server is running" -ForegroundColor Yellow
        }
    }
    
    "new-tab" {
        Write-Host "[CHROME] Opening new tab..." -ForegroundColor Cyan
        Invoke-ONI -Endpoint "/api/keys?keys=ctrl,t"
        Start-Sleep -Milliseconds 500
        Write-Host "[OK] New tab opened" -ForegroundColor Green
    }
    
    "close" {
        Write-Host "[CHROME] Closing..." -ForegroundColor Cyan
        Get-Process -Name "chrome" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Host "[OK] Chrome closed" -ForegroundColor Green
    }
    
    "collect" {
        Write-Host "[CHROME] Collecting page data via ONI Vision..." -ForegroundColor Cyan
        
        # Get hybrid vision scan
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        $result = Invoke-ONI -Endpoint "/api/hybrid-vision/web?nocache=$timestamp"
        
        if ($result) {
            $AssetsDir = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
            if (-not (Test-Path $AssetsDir)) { New-Item -ItemType Directory -Path $AssetsDir | Out-Null }
            $collectOutput = Join-Path $AssetsDir "collected_$timestamp.json"
            $result | ConvertTo-Json -Depth 10 | Set-Content $collectOutput -Encoding UTF8
            Write-Host "[OK] Page data collected: $collectOutput" -ForegroundColor Green
            
            # Show summary
            if ($result.window_title) {
                Write-Host "   Title: $($result.window_title)" -ForegroundColor White
            }
            if ($result.elements) {
                Write-Host "   Elements: $($result.elements.Count)" -ForegroundColor White
            }
        }
        else {
            Write-Host "[WARN] Could not collect - ensure Chrome is open and ONI server running" -ForegroundColor Yellow
        }
    }
    
    default {
        Show-Usage
    }
}

