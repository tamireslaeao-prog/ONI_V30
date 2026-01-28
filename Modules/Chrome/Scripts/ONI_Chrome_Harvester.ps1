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
# ONI CHROME HARVESTER - Browser Data Analyzer
# Version: 1.0
# Description: Extracts bookmarks, history, extensions from Chrome profile
# ============================================================================

param(
    [string]$ChromeProfilePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default",
    [string]$OutputFile
)

if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[CHROME HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Profile: $ChromeProfilePath" -ForegroundColor Gray

$harvestResult = @{
    harvested_at      = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    profile_path      = $ChromeProfilePath
    bookmarks         = @()
    bookmarks_folders = @()
    extensions        = @()
    top_sites         = @()
    search_engines    = @()
}

# ============================================================================
# BOOKMARKS
# ============================================================================
$bookmarksFile = Join-Path $ChromeProfilePath "Bookmarks"
if (Test-Path $bookmarksFile) {
    Write-Host "   [BOOKMARKS] Reading..." -ForegroundColor Blue
    
    try {
        $bookmarksJson = Get-Content $bookmarksFile -Raw | ConvertFrom-Json
        
        # Recursive function to extract bookmarks
        function Get-BookmarksRecursive {
            param($node, $folder = "")
            
            $results = @{bookmarks = @(); folders = @() }
            
            if ($node.type -eq "folder") {
                $currentFolder = if ($folder) { "$folder/$($node.name)" } else { $node.name }
                $results.folders += $currentFolder
                
                foreach ($child in $node.children) {
                    $childResults = Get-BookmarksRecursive -node $child -folder $currentFolder
                    $results.bookmarks += $childResults.bookmarks
                    $results.folders += $childResults.folders
                }
            }
            elseif ($node.type -eq "url") {
                $results.bookmarks += @{
                    name   = $node.name
                    url    = $node.url
                    folder = $folder
                    added  = $node.date_added
                }
            }
            
            return $results
        }
        
        # Process bookmark bar and other folders
        foreach ($rootName in @("bookmark_bar", "other", "synced")) {
            $root = $bookmarksJson.roots.$rootName
            if ($root) {
                $extracted = Get-BookmarksRecursive -node $root
                $harvestResult.bookmarks += $extracted.bookmarks
                $harvestResult.bookmarks_folders += $extracted.folders
            }
        }
        
        Write-Host "      Found $($harvestResult.bookmarks.Count) bookmarks in $($harvestResult.bookmarks_folders.Count) folders" -ForegroundColor Green
        
    }
    catch {
        Write-Host "      [WARN] Could not parse bookmarks: $_" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   [BOOKMARKS] File not found" -ForegroundColor DarkYellow
}

# ============================================================================
# EXTENSIONS
# ============================================================================
$extensionsPath = Join-Path $ChromeProfilePath "Extensions"
if (Test-Path $extensionsPath) {
    Write-Host "   [EXTENSIONS] Scanning..." -ForegroundColor Blue
    
    try {
        $extFolders = Get-ChildItem -Path $extensionsPath -Directory
        
        foreach ($extFolder in $extFolders) {
            # Get latest version folder
            $versionFolders = Get-ChildItem -Path $extFolder.FullName -Directory | Sort-Object Name -Descending
            if ($versionFolders.Count -gt 0) {
                $latestVersion = $versionFolders[0]
                $manifestPath = Join-Path $latestVersion.FullName "manifest.json"
                
                if (Test-Path $manifestPath) {
                    try {
                        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
                        $harvestResult.extensions += @{
                            id          = $extFolder.Name
                            name        = $manifest.name
                            version     = $manifest.version
                            description = $manifest.description
                        }
                        Write-Host "      [EXT] $($manifest.name)" -ForegroundColor Magenta
                    }
                    catch {}
                }
            }
        }
        
        Write-Host "      Found $($harvestResult.extensions.Count) extensions" -ForegroundColor Green
        
    }
    catch {
        Write-Host "      [WARN] Could not scan extensions: $_" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   [EXTENSIONS] Folder not found" -ForegroundColor DarkYellow
}

# ============================================================================
# TOP SITES
# ============================================================================
$topSitesFile = Join-Path $ChromeProfilePath "Top Sites"
if (Test-Path $topSitesFile) {
    Write-Host "   [TOP SITES] Chrome stores this in SQLite - skipping direct read" -ForegroundColor DarkGray
    # Reading SQLite requires additional tooling, marking as available
    $harvestResult.top_sites = @{status = "AVAILABLE_IN_SQLITE"; path = $topSitesFile }
}

# ============================================================================
# PREFERENCES (Search Engines, etc.)
# ============================================================================
$prefsFile = Join-Path $ChromeProfilePath "Preferences"
if (Test-Path $prefsFile) {
    Write-Host "   [PREFERENCES] Reading..." -ForegroundColor Blue
    
    try {
        $prefs = Get-Content $prefsFile -Raw | ConvertFrom-Json
        
        # Default search engine
        if ($prefs.default_search_provider_data) {
            $harvestResult.search_engines += @{
                name    = "Default"
                keyword = $prefs.default_search_provider_data.keyword
            }
        }
        
        Write-Host "      Preferences extracted" -ForegroundColor Green
        
    }
    catch {
        Write-Host "      [WARN] Could not parse preferences: $_" -ForegroundColor Yellow
    }
}

# ============================================================================
# SAVE RESULTS
# ============================================================================
$harvestResult | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Chrome harvest finished" -ForegroundColor Cyan
Write-Host "   Bookmarks: $($harvestResult.bookmarks.Count)" -ForegroundColor White
Write-Host "   Extensions: $($harvestResult.extensions.Count)" -ForegroundColor White
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

