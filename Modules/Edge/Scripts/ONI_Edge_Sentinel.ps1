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
# 👁️ ONI EDGE SENTINEL - REAL-TIME BROWSER MONITOR
# Description: Watches Edge browser for tab changes, downloads, network activity
# ============================================================================

param(
    [int]$CDPPort = 9222,
    [string]$LogFile = "C:\ONI\Edge\sentinel_log.txt",
    [string]$IndexFile = "C:\ONI\Edge\browser_db.json",
    [int]$PollInterval = 2  # Seconds between checks
)

Write-Host "👁️ ONI EDGE SENTINEL ACTIVATED" -ForegroundColor Cyan
Write-Host "   CDP Port:   $CDPPort" -ForegroundColor Gray
Write-Host "   Log File:   $LogFile" -ForegroundColor Gray
Write-Host "   Interval:   $PollInterval seconds" -ForegroundColor Gray

# Ensure directories exist
$logDir = Split-Path $LogFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# ============================================================================
# Helper: Log Event
# ============================================================================
function Write-SentinelLog {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Type | $Message"
    $logEntry | Out-File -FilePath $LogFile -Append
    
    $color = switch ($Type) {
        "NEW"       { "Green" }
        "CLOSE"     { "Yellow" }
        "NAVIGATE"  { "Cyan" }
        "DOWNLOAD"  { "Magenta" }
        "ERROR"     { "Red" }
        default     { "Gray" }
    }
    
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# ============================================================================
# Helper: Check if Edge is running with CDP
# ============================================================================
function Test-EdgeCDP {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:$CDPPort/json/version" -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# ============================================================================
# Helper: Get CDP Tabs
# ============================================================================
function Get-EdgeTabs {
    try {
        $tabs = Invoke-RestMethod -Uri "http://localhost:$CDPPort/json" -ErrorAction Stop
        return $tabs | Where-Object { $_.type -eq "page" }
    }
    catch {
        return @()
    }
}

# ============================================================================
# Check CDP Connection
# ============================================================================
Write-Host ""
if (-not (Test-EdgeCDP)) {
    Write-Host "   [WARN] Edge CDP not available" -ForegroundColor Yellow
    Write-Host "   Launch Edge with: msedge.exe --remote-debugging-port=$CDPPort" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Waiting for Edge to start..." -ForegroundColor Gray
    
    # Wait for Edge to start
    while (-not (Test-EdgeCDP)) {
        Start-Sleep -Seconds 2
        Write-Host "." -NoNewline -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "   ✓ Edge CDP connected!" -ForegroundColor Green
}
else {
    Write-Host "   ✓ Edge CDP connected" -ForegroundColor Green
}

Write-SentinelLog "Sentinel started - monitoring Edge browser"

# ============================================================================
# Initialize State Tracking
# ============================================================================
$lastKnownTabs = @{}
$downloadMonitor = @{}
$sessionStats = @{
    tabs_opened = 0
    tabs_closed = 0
    navigations = 0
    downloads = 0
    start_time = Get-Date
}

# Load initial tabs
$currentTabs = Get-EdgeTabs
foreach ($tab in $currentTabs) {
    $lastKnownTabs[$tab.id] = @{
        title = $tab.title
        url = $tab.url
        last_seen = Get-Date
    }
}

Write-Host ""
Write-Host "   Currently tracking $($lastKnownTabs.Count) tabs" -ForegroundColor Gray
Write-Host "   (Press Ctrl+C to stop monitoring)" -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# Main Monitoring Loop
# ============================================================================
try {
    while ($true) {
        # Check CDP connection
        if (-not (Test-EdgeCDP)) {
            Write-SentinelLog "Edge CDP connection lost" "ERROR"
            Write-Host "   Waiting for Edge to restart..." -ForegroundColor Yellow
            
            while (-not (Test-EdgeCDP)) {
                Start-Sleep -Seconds 2
            }
            
            Write-SentinelLog "Edge CDP connection restored" "INFO"
        }
        
        # ====================================================================
        # MONITOR TABS
        # ====================================================================
        $currentTabs = Get-EdgeTabs
        $currentTabIds = $currentTabs | ForEach-Object { $_.id }
        
        # Detect NEW TABS
        foreach ($tab in $currentTabs) {
            if (-not $lastKnownTabs.ContainsKey($tab.id)) {
                Write-SentinelLog "🆕 NEW TAB: $($tab.title)" "NEW"
                Write-SentinelLog "   URL: $($tab.url)" "INFO"
                
                $lastKnownTabs[$tab.id] = @{
                    title = $tab.title
                    url = $tab.url
                    last_seen = Get-Date
                }
                
                $sessionStats.tabs_opened++
            }
            # Detect NAVIGATION (URL changed)
            elseif ($lastKnownTabs[$tab.id].url -ne $tab.url) {
                Write-SentinelLog "🔄 NAVIGATION: $($tab.title)" "NAVIGATE"
                Write-SentinelLog "   From: $($lastKnownTabs[$tab.id].url)" "INFO"
                Write-SentinelLog "   To:   $($tab.url)" "INFO"
                
                $lastKnownTabs[$tab.id].url = $tab.url
                $lastKnownTabs[$tab.id].title = $tab.title
                $lastKnownTabs[$tab.id].last_seen = Get-Date
                
                $sessionStats.navigations++
            }
            # Update last seen
            else {
                $lastKnownTabs[$tab.id].last_seen = Get-Date
            }
        }
        
        # Detect CLOSED TABS
        $closedTabs = $lastKnownTabs.Keys | Where-Object { $_ -notin $currentTabIds }
        foreach ($tabId in $closedTabs) {
            $closedTab = $lastKnownTabs[$tabId]
            Write-SentinelLog "❌ TAB CLOSED: $($closedTab.title)" "CLOSE"
            
            $lastKnownTabs.Remove($tabId)
            $sessionStats.tabs_closed++
        }
        
        # ====================================================================
        # MONITOR DOWNLOADS (Check Downloads folder)
        # ====================================================================
        $downloadsPath = [Environment]::GetFolderPath("UserProfile") + "\Downloads"
        
        if (Test-Path $downloadsPath) {
            $recentDownloads = Get-ChildItem $downloadsPath -File | 
                Where-Object { $_.LastWriteTime -gt (Get-Date).AddSeconds(-($PollInterval + 1)) } |
                Sort-Object LastWriteTime -Descending
            
            foreach ($file in $recentDownloads) {
                $fileKey = "$($file.Name)_$($file.Length)"
                
                if (-not $downloadMonitor.ContainsKey($fileKey)) {
                    Write-SentinelLog "📥 DOWNLOAD COMPLETED: $($file.Name)" "DOWNLOAD"
                    Write-SentinelLog "   Size: $([math]::Round($file.Length / 1MB, 2)) MB" "INFO"
                    Write-SentinelLog "   Path: $($file.FullName)" "INFO"
                    
                    $downloadMonitor[$fileKey] = $file.LastWriteTime
                    $sessionStats.downloads++
                }
            }
        }
        
        # ====================================================================
        # PERIODIC STATISTICS
        # ====================================================================
        $elapsed = (Get-Date) - $sessionStats.start_time
        
        if ($elapsed.TotalMinutes -gt 0 -and $elapsed.TotalSeconds % 300 -lt $PollInterval) {
            Write-Host ""
            Write-Host "   ═══ SESSION STATISTICS ═══" -ForegroundColor White
            Write-Host "   Runtime:      $([math]::Floor($elapsed.TotalMinutes)) minutes" -ForegroundColor Gray
            Write-Host "   Tabs Opened:  $($sessionStats.tabs_opened)" -ForegroundColor Gray
            Write-Host "   Tabs Closed:  $($sessionStats.tabs_closed)" -ForegroundColor Gray
            Write-Host "   Navigations:  $($sessionStats.navigations)" -ForegroundColor Gray
            Write-Host "   Downloads:    $($sessionStats.downloads)" -ForegroundColor Gray
            Write-Host "   Active Tabs:  $($lastKnownTabs.Count)" -ForegroundColor Gray
            Write-Host ""
        }
        
        # Wait before next check
        Start-Sleep -Seconds $PollInterval
    }
}
catch {
    Write-Host ""
    Write-SentinelLog "Sentinel error: $_" "ERROR"
}
finally {
    Write-Host ""
    Write-SentinelLog "Sentinel shutting down" "INFO"
    
    # Final Statistics
    $elapsed = (Get-Date) - $sessionStats.start_time
    
    Write-Host ""
    Write-Host "   ═══ FINAL SESSION REPORT ═══" -ForegroundColor Cyan
    Write-Host "   Total Runtime:    $([math]::Floor($elapsed.TotalMinutes)) minutes" -ForegroundColor White
    Write-Host "   Tabs Opened:      $($sessionStats.tabs_opened)" -ForegroundColor White
    Write-Host "   Tabs Closed:      $($sessionStats.tabs_closed)" -ForegroundColor White
    Write-Host "   Total Navigations: $($sessionStats.navigations)" -ForegroundColor White
    Write-Host "   Total Downloads:  $($sessionStats.downloads)" -ForegroundColor White
    Write-Host ""
    
    # Update index file
    if (Test-Path $IndexFile) {
        try {
            $index = Get-Content $IndexFile -Raw | ConvertFrom-Json
            
            # Add session report
            if (-not $index.session_history) {
                $index | Add-Member -NotePropertyName "session_history" -NotePropertyValue @()
            }
            
            $sessionReport = @{
                start_time = $sessionStats.start_time.ToString("yyyy-MM-dd HH:mm:ss")
                end_time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                duration_minutes = [math]::Floor($elapsed.TotalMinutes)
                tabs_opened = $sessionStats.tabs_opened
                tabs_closed = $sessionStats.tabs_closed
                navigations = $sessionStats.navigations
                downloads = $sessionStats.downloads
            }
            
            $index.session_history += $sessionReport
            
            $index | ConvertTo-Json -Depth 10 | Set-Content $IndexFile -Encoding UTF8
            Write-Host "   ✓ Session saved to index" -ForegroundColor Green
        }
        catch {
            Write-Host "   [WARN] Could not update index: $_" -ForegroundColor Yellow
        }
    }
}
