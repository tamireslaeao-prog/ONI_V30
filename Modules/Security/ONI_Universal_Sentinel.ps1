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
# 👁️ ONI UNIVERSAL SENTINEL - GLOBAL ASSET MONITOR
# Version: 2.0 (Multi-Module Support)
# Description: Watches ALL module asset folders simultaneously.
# ============================================================================

$ModulesRoot = $PSScriptRoot
$GlobalLog = Join-Path $ModulesRoot "global_sentinel_log.txt"

# Define Modules to Watch
$Targets = @("Photoshop", "Illustrator", "Excel", "AfterEffects", "Blender", "Corel", "Word", "Chrome")

Write-Host "👁️ ONI UNIVERSAL SENTINEL ACTIVATED" -ForegroundColor Cyan
Write-Host "   Root: $ModulesRoot" -ForegroundColor Gray
Write-Host "----------------------------------------"

# List to hold watchers to prevent garbage collection
$Watchers = @()

foreach ($Module in $Targets) {
    $AssetPath = Join-Path $ModulesRoot "$Module\Assets"
    
    # Create if missing (Self-Healing)
    if (-not (Test-Path $AssetPath)) { 
        New-Item -ItemType Directory -Path $AssetPath | Out-Null 
        Write-Host "   [+] Created missing folder: $Module\Assets" -ForegroundColor DarkGray
    }

    # Setup Watcher
    $Watcher = New-Object System.IO.FileSystemWatcher
    $Watcher.Path = $AssetPath
    $Watcher.Filter = "*.*"
    $Watcher.IncludeSubdirectories = $true
    $Watcher.EnableRaisingEvents = $true

    # Define Event
    $Action = {
        $path = $Event.SourceEventArgs.FullPath
        $name = $Event.SourceEventArgs.Name
        $contextModule = $Event.MessageData # Pass Module Name context custom
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        Write-Host "[$timestamp] 📥 $contextModule DETECTED: $name" -ForegroundColor Green
        
        # Log to Global File
        "$timestamp | $contextModule | $name" | Out-File -FilePath $GlobalLog -Append

        # Update Local DB (Simple JSON Append)
        $LocalDB = Join-Path (Split-Path (Split-Path $path)) "assets_db.json"
        
        $jsonEntry = @{
            id       = [Guid]::NewGuid().ToString()
            file     = $name
            path     = $path
            added_at = $timestamp
            module   = $contextModule
        }

        # Thread-safe-ish file write
        try {
            if (Test-Path $LocalDB) {
                $current = Get-Content $LocalDB -Raw -ErrorAction SilentlyContinue | ConvertFrom-Json
                $list = [System.Collections.ArrayList]@($current)
            }
            else {
                $list = [System.Collections.ArrayList]@()
            }
            $list.Add($jsonEntry) | Out-Null
            $list | ConvertTo-Json -Depth 3 | Set-Content $LocalDB -Force
            Write-Host "      ✓ Indexed in $contextModule DB" -ForegroundColor DarkGray
        }
        catch {
            Write-Host "      X Error writing DB: $_" -ForegroundColor Red
        }
    }

    # Register Event with Module Name as MessageData
    Register-ObjectEvent $Watcher "Created" -Action $Action -MessageData $Module | Out-Null
    
    # Store watcher reference
    $Watchers += $Watcher
    Write-Host "   ✓ Watching: $Module" -ForegroundColor Green
}

Write-Host "----------------------------------------"
Write-Host "   (Press Ctrl+C to stop watching)" -ForegroundColor Yellow

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Unregister-Event -SourceIdentifier "FileCreated" -ErrorAction SilentlyContinue
}

