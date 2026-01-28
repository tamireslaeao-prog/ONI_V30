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
# ONI CHROME WEB SCRAPER - Data Extraction Toolkit
# Version: 1.0
# Description: Automated web scraping with visual verification
# ============================================================================

param(
    [string]$Url,
    [string]$Selector,
    [string]$Action = "extract",
    [string]$OutputFile,
    [int]$WaitSeconds = 3
)

$ONI_API = "http://localhost:8000"

function Invoke-ONI {
    param([string]$Endpoint, [string]$Method = "Get")
    
    try {
        $response = Invoke-RestMethod -Uri "$ONI_API$Endpoint" -Method $Method -TimeoutSec 60
        return $response
    }
    catch {
        Write-Host "[ERROR] ONI API failed: $_" -ForegroundColor Red
        return $null
    }
}

function Wait-ForPage {
    param([int]$Seconds)
    Write-Host "   Waiting $Seconds seconds for page load..." -ForegroundColor Gray
    Start-Sleep -Seconds $Seconds
}

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

Write-Host "[WEB SCRAPER] Starting..." -ForegroundColor Cyan

if (-not $Url) {
    Write-Host "Usage: ONI_Chrome_Scraper.ps1 -Url <url> [-Action extract|click|type] [-Selector <css>]" -ForegroundColor Yellow
    exit 0
}

# Step 1: Focus Chrome
Write-Host "[1/5] Focusing Chrome..." -ForegroundColor Blue
Invoke-ONI -Endpoint "/api/focus?title=Chrome"
Start-Sleep -Milliseconds 500

# Step 2: Navigate to URL
Write-Host "[2/5] Navigating to: $Url" -ForegroundColor Blue
Invoke-ONI -Endpoint "/api/keys?keys=ctrl,l"
Start-Sleep -Milliseconds 300
Invoke-ONI -Endpoint "/api/type?text=$([uri]::EscapeDataString($Url))"
Start-Sleep -Milliseconds 200
Invoke-ONI -Endpoint "/api/keys?keys=enter"

Wait-ForPage -Seconds $WaitSeconds

# Step 3: Visual Scan
Write-Host "[3/5] Scanning page with Hybrid Vision..." -ForegroundColor Blue
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$scan = Invoke-ONI -Endpoint "/api/hybrid-vision/web?nocache=$timestamp"

if (-not $scan) {
    Write-Host "[ERROR] Could not scan page" -ForegroundColor Red
    exit 1
}

Write-Host "   Title: $($scan.window_title)" -ForegroundColor White
Write-Host "   Elements detected: $($scan.elements.Count)" -ForegroundColor White

# Step 4: Extract/Act based on action
Write-Host "[4/5] Executing action: $Action" -ForegroundColor Blue

switch ($Action) {
    "extract" {
        # Extract all text and structure
        $extractedData = @{
            url             = $Url
            title           = $scan.window_title
            timestamp       = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            elements        = $scan.elements
            ocr_text        = $scan.ocr_text
            annotated_image = $scan.annotated_path
        }
        
        if (-not $OutputFile) {
            $AssetsDir = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
            if (-not (Test-Path $AssetsDir)) { New-Item -ItemType Directory -Path $AssetsDir | Out-Null }
            $OutputFile = Join-Path $AssetsDir "extracted_$timestamp.json"
        }
        
        $extractedData | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8
        Write-Host "   Data extracted to: $OutputFile" -ForegroundColor Green
    }
    
    "click" {
        if (-not $Selector) {
            Write-Host "[ERROR] -Selector required for click action" -ForegroundColor Red
            exit 1
        }
        
        # Find element by text match in OCR
        $targetElement = $scan.elements | Where-Object { $_.text -match $Selector } | Select-Object -First 1
        
        if ($targetElement) {
            $x = $targetElement.rect.x + ($targetElement.rect.width / 2)
            $y = $targetElement.rect.y + ($targetElement.rect.height / 2)
            Write-Host "   Clicking at ($x, $y) - '$($targetElement.text)'" -ForegroundColor Yellow
            Invoke-ONI -Endpoint "/api/click?x=$x&y=$y"
        }
        else {
            Write-Host "[WARN] Element matching '$Selector' not found" -ForegroundColor Yellow
        }
    }
    
    "type" {
        if (-not $Selector) {
            Write-Host "[ERROR] -Selector (text to type) required" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "   Typing: $Selector" -ForegroundColor Yellow
        Invoke-ONI -Endpoint "/api/type?text=$([uri]::EscapeDataString($Selector))"
    }
}

# Step 5: Final verification
Write-Host "[5/5] Verification scan..." -ForegroundColor Blue
$finalScan = Invoke-ONI -Endpoint "/api/hybrid-vision/web?nocache=final_$timestamp"

if ($finalScan) {
    Write-Host "   Final state captured" -ForegroundColor Green
}

Write-Host ""
Write-Host "[COMPLETE] Web scraping finished" -ForegroundColor Cyan

