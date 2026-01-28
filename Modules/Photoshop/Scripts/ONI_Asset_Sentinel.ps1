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
# 👁️ ONI ASSET SENTINEL - REAL-TIME MONITOR
# Description: Watches folders for new assets and auto-indexes them.
# ============================================================================

$ModuleRoot = Split-Path (Split-Path $PSScriptRoot -Parent)
$WatchFolder = Join-Path $ModuleRoot "Assets"
$IndexFile = Join-Path $ModuleRoot "assets_db.json"
$LogFile = Join-Path $ModuleRoot "sentinel_log.txt"

# Ensure folder exists
if (-not (Test-Path $WatchFolder)) { New-Item -ItemType Directory -Path $WatchFolder | Out-Null }

Write-Host "👁️ ONI SENTINEL ACTIVATED" -ForegroundColor Cyan
Write-Host "   Watching: $WatchFolder" -ForegroundColor Gray
Write-Host "   Target:   $IndexFile" -ForegroundColor Gray

# Create FileSystemWatcher
$Watcher = New-Object System.IO.FileSystemWatcher
$Watcher.Path = $WatchFolder
$Watcher.Filter = "*.*" # Watch all, filter logic later
$Watcher.IncludeSubdirectories = $true
$Watcher.EnableRaisingEvents = $true

# Define Action
$Action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Filter for relevant extensions
    if ($name -match "\.(psd|png|jpg|ai|cdr)$") {
        Write-Host "[$timestamp] 📥 NEW ASSET DETECTED: $name" -ForegroundColor Green
        
        # 1. Log to text file
        "$timestamp | ADDED | $name" | Out-File -FilePath $LogFile -Append
        
        # 2. Update JSON Index (Simple Append Logic)
        # In a full version, this would parse the PSD for @LAYERS
        $jsonEntry = @{
            id       = [Guid]::NewGuid().ToString()
            file     = $name
            path     = $path
            added_at = $timestamp
            status   = "ready"
        }
        
        # Read existing or create new
        if (Test-Path $IndexFile) {
            $currentDB = Get-Content $IndexFile -Raw | ConvertFrom-Json
            # Convert to ArrayList for easy adding
            $dbList = [System.Collections.ArrayList]@($currentDB)
        }
        else {
            $dbList = [System.Collections.ArrayList]@()
        }
        
        $dbList.Add($jsonEntry) | Out-Null
        $dbList | ConvertTo-Json -Depth 3 | Set-Content $IndexFile
        
        Write-Host "   ✓ Indexed to DB" -ForegroundColor DarkGray
    }
}

# Register Events
Register-ObjectEvent $Watcher "Created" -Action $Action
Register-ObjectEvent $Watcher "Changed" -Action $Action
Register-ObjectEvent $Watcher "Renamed" -Action $Action

Write-Host "   (Press Ctrl+C to stop watching)" -ForegroundColor Yellow

# Keep alive loop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Unregister-Event -SourceIdentifier "FileChanged" -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier "FileCreated" -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier "FileRenamed" -ErrorAction SilentlyContinue
}

