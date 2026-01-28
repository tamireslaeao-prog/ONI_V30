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
# ONI EDGE DEEP HARVESTER v1.0 - Complete Browser State Analyzer
# Description: Extracts profiles, history, bookmarks, extensions
# ============================================================================

param(
    [string]$OutputFile,
    [switch]$IncludeHistory,
    [switch]$IncludeBookmarks,
    [switch]$IncludeExtensions
)

# Default to true if not specified
if (-not $PSBoundParameters.ContainsKey('IncludeHistory')) { $IncludeHistory = $true }
if (-not $PSBoundParameters.ContainsKey('IncludeBookmarks')) { $IncludeBookmarks = $true }
if (-not $PSBoundParameters.ContainsKey('IncludeExtensions')) { $IncludeExtensions = $true }

if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[EDGE HARVESTER v1.0] Starting deep scan..." -ForegroundColor Cyan

$EdgeUserData = "$env:LOCALAPPDATA\Microsoft\Edge\User Data"

if (-not (Test-Path $EdgeUserData)) {
    Write-Host "   [FAIL] Edge User Data folder not found" -ForegroundColor Red
    exit 1
}

Write-Host "   [OK] Found Edge User Data" -ForegroundColor Green

$harvestData = @{
    harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    edge_version = $null
    profiles     = @()
    statistics   = @{}
}

# STEP 1: Detect Edge Version
Write-Host ""
Write-Host "[STEP 1] Detecting Edge Version..." -ForegroundColor Yellow

try {
    $edgeExe = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (-not (Test-Path $edgeExe)) {
        $edgeExe = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    }
    if (Test-Path $edgeExe) {
        $version = (Get-Item $edgeExe).VersionInfo.ProductVersion
        $harvestData.edge_version = $version
        Write-Host "   Version: $version" -ForegroundColor Green
    }
}
catch {
    Write-Host "   [WARN] Could not detect version" -ForegroundColor Yellow
}

# STEP 2: Discover Profiles
Write-Host ""
Write-Host "[STEP 2] Discovering Profiles..." -ForegroundColor Yellow

$profileFolders = Get-ChildItem -Path $EdgeUserData -Directory | Where-Object {
    $_.Name -match '^(Default|Profile \d+)$'
}

$totalBookmarks = 0
$totalExtensions = 0

foreach ($profileFolder in $profileFolders) {
    Write-Host ""
    Write-Host "   [PROFILE] $($profileFolder.Name)" -ForegroundColor White
    
    $profileData = @{
        name       = $profileFolder.Name
        path       = $profileFolder.FullName
        bookmarks  = @()
        extensions = @()
        statistics = @{}
    }
    
    # Get Profile Name from Preferences
    $prefsFile = Join-Path $profileFolder.FullName "Preferences"
    if (Test-Path $prefsFile) {
        try {
            $prefs = Get-Content $prefsFile -Raw | ConvertFrom-Json
            if ($prefs.profile) {
                $profileData.display_name = $prefs.profile.name
            }
            Write-Host "      Display Name: $($profileData.display_name)" -ForegroundColor Gray
        }
        catch {}
    }
    
    # BOOKMARKS
    if ($IncludeBookmarks) {
        $bookmarksFile = Join-Path $profileFolder.FullName "Bookmarks"
        if (Test-Path $bookmarksFile) {
            try {
                $bookmarksJson = Get-Content $bookmarksFile -Raw | ConvertFrom-Json
                
                function Get-BookmarksRecursive {
                    param($node, $folder = "")
                    $results = @()
                    if ($node.children) {
                        foreach ($item in $node.children) {
                            if ($item.type -eq "url") {
                                $results += @{
                                    name   = $item.name
                                    url    = $item.url
                                    folder = $folder
                                }
                            }
                            elseif ($item.type -eq "folder") {
                                $results += Get-BookmarksRecursive -node $item -folder "$folder/$($item.name)"
                            }
                        }
                    }
                    return $results
                }
                
                $profileData.bookmarks = @(Get-BookmarksRecursive -node $bookmarksJson.roots.bookmark_bar -folder "Bookmark Bar")
                $profileData.bookmarks += @(Get-BookmarksRecursive -node $bookmarksJson.roots.other -folder "Other")
                
                $totalBookmarks += $profileData.bookmarks.Count
                Write-Host "      Bookmarks: $($profileData.bookmarks.Count)" -ForegroundColor Green
            }
            catch {
                Write-Host "      [ERROR] Bookmarks: $_" -ForegroundColor Red
            }
        }
    }
    
    # EXTENSIONS
    if ($IncludeExtensions) {
        $extensionsPath = Join-Path $profileFolder.FullName "Extensions"
        if (Test-Path $extensionsPath) {
            $extensions = Get-ChildItem $extensionsPath -Directory
            foreach ($ext in $extensions) {
                $versionFolder = Get-ChildItem $ext.FullName -Directory | Sort-Object Name -Descending | Select-Object -First 1
                if ($versionFolder) {
                    $manifestFile = Join-Path $versionFolder.FullName "manifest.json"
                    if (Test-Path $manifestFile) {
                        try {
                            $manifest = Get-Content $manifestFile -Raw | ConvertFrom-Json
                            $profileData.extensions += @{
                                id      = $ext.Name
                                name    = $manifest.name
                                version = $manifest.version
                            }
                            Write-Host "      [EXT] $($manifest.name)" -ForegroundColor Blue
                        }
                        catch {}
                    }
                }
            }
            $totalExtensions += $profileData.extensions.Count
            Write-Host "      Extensions: $($profileData.extensions.Count)" -ForegroundColor Green
        }
    }
    
    $profileData.statistics = @{
        total_bookmarks  = $profileData.bookmarks.Count
        total_extensions = $profileData.extensions.Count
    }
    
    $harvestData.profiles += $profileData
}

# STEP 3: Global Statistics
Write-Host ""
Write-Host "[STEP 3] Statistics..." -ForegroundColor Yellow

$harvestData.statistics = @{
    total_profiles   = $harvestData.profiles.Count
    total_bookmarks  = $totalBookmarks
    total_extensions = $totalExtensions
}

Write-Host "   Profiles: $($harvestData.statistics.total_profiles)" -ForegroundColor Gray
Write-Host "   Bookmarks: $totalBookmarks" -ForegroundColor Gray
Write-Host "   Extensions: $totalExtensions" -ForegroundColor Gray

# STEP 4: Check CDP for open tabs
Write-Host ""
Write-Host "[STEP 4] Checking CDP..." -ForegroundColor Yellow

try {
    $cdpResponse = Invoke-RestMethod -Uri "http://localhost:9222/json" -ErrorAction Stop -TimeoutSec 2
    $openTabs = @($cdpResponse | Where-Object { $_.type -eq "page" } | ForEach-Object {
            @{ title = $_.title; url = $_.url; id = $_.id }
        })
    $harvestData.open_tabs = $openTabs
    $harvestData.statistics.open_tabs = $openTabs.Count
    Write-Host "   Open Tabs: $($openTabs.Count)" -ForegroundColor Green
}
catch {
    Write-Host "   [INFO] CDP not available" -ForegroundColor Yellow
    $harvestData.open_tabs = @()
    $harvestData.statistics.open_tabs = 0
}

# STEP 5: Save
Write-Host ""
Write-Host "[STEP 5] Saving..." -ForegroundColor Yellow

$harvestData | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host "   Saved to: $OutputFile" -ForegroundColor Green

Write-Host ""
Write-Host "[COMPLETE] Edge harvest finished" -ForegroundColor Cyan
Write-Host "   Profiles: $($harvestData.statistics.total_profiles)" -ForegroundColor White
Write-Host "   Bookmarks: $($harvestData.statistics.total_bookmarks)" -ForegroundColor White
Write-Host "   Extensions: $($harvestData.statistics.total_extensions)" -ForegroundColor White
