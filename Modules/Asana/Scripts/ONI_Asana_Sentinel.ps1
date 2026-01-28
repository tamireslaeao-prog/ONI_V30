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
# 👁️ ONI ASANA SENTINEL - REAL-TIME MONITOR
# Description: Watches Asana workspace for changes and auto-updates index
# ============================================================================

param(
    [string]$AsanaToken = $env:ASANA_TOKEN,
    [string]$WorkspaceGid = "",
    [string]$IndexFile,
    [string]$LogFile,
    [int]$PollInterval = 60  # Seconds between checks
)

if ([string]::IsNullOrEmpty($IndexFile)) {
    $IndexFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}
if ([string]::IsNullOrEmpty($LogFile)) {
    $LogFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "sentinel_log.txt"
}

if ([string]::IsNullOrEmpty($AsanaToken)) {
    Write-Host "   [FAIL] ASANA_TOKEN not set" -ForegroundColor Red
    exit 1
}

$BaseURL = "https://app.asana.com/api/1.0"
$Headers = @{
    "Authorization" = "Bearer $AsanaToken"
    "Content-Type"  = "application/json"
}

# Ensure directories exist
$logDir = Split-Path $LogFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

Write-Host "👁️ ONI ASANA SENTINEL ACTIVATED" -ForegroundColor Cyan
Write-Host "   Workspace: $WorkspaceGid" -ForegroundColor Gray
Write-Host "   Index:     $IndexFile" -ForegroundColor Gray
Write-Host "   Log:       $LogFile" -ForegroundColor Gray
Write-Host "   Interval:  $PollInterval seconds" -ForegroundColor Gray

# Helper: API Call
function Invoke-AsanaAPI {
    param([string]$Endpoint)
    try {
        $response = Invoke-RestMethod -Uri "$BaseURL$Endpoint" -Headers $Headers -Method Get
        return $response.data
    }
    catch {
        return $null
    }
}

# Helper: Log Event
function Write-SentinelLog {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Type | $Message"
    $logEntry | Out-File -FilePath $LogFile -Append
    
    $color = switch ($Type) {
        "NEW" { "Green" }
        "UPDATE" { "Yellow" }
        "DELETE" { "Red" }
        "ERROR" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# Get initial workspace
$workspaces = Invoke-AsanaAPI -Endpoint "/workspaces"
if ([string]::IsNullOrEmpty($WorkspaceGid)) {
    $WorkspaceGid = $workspaces[0].gid
}

# Initialize tracking state
$lastKnownState = @{
    projects = @{}
    tasks    = @{}
    users    = @{}
    tags     = @{}
}

# Load existing index if available
if (Test-Path $IndexFile) {
    try {
        $existingIndex = Get-Content $IndexFile -Raw | ConvertFrom-Json
        
        # Build initial state from index
        foreach ($project in $existingIndex.projects) {
            $lastKnownState.projects[$project.gid] = $project
            foreach ($task in $project.tasks) {
                $lastKnownState.tasks[$task.gid] = $task
            }
        }
        
        foreach ($user in $existingIndex.users) {
            $lastKnownState.users[$user.gid] = $user
        }
        
        foreach ($tag in $existingIndex.tags) {
            $lastKnownState.tags[$tag.gid] = $tag
        }
        
        Write-SentinelLog "Loaded existing index: $($lastKnownState.projects.Count) projects tracked"
    }
    catch {
        Write-SentinelLog "Could not load existing index, starting fresh" "ERROR"
    }
}

Write-Host ""
Write-Host "   (Press Ctrl+C to stop monitoring)" -ForegroundColor Yellow
Write-Host ""

# Main monitoring loop
try {
    while ($true) {
        $changesDetected = $false
        
        # ============================================================================
        # MONITOR PROJECTS
        # ============================================================================
        $currentProjects = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/projects"
        
        if ($currentProjects) {
            foreach ($project in $currentProjects) {
                $projectGid = $project.gid
                
                # NEW PROJECT
                if (-not $lastKnownState.projects.ContainsKey($projectGid)) {
                    Write-SentinelLog "🆕 NEW PROJECT: $($project.name)" "NEW"
                    $lastKnownState.projects[$projectGid] = $project
                    $changesDetected = $true
                }
                # UPDATED PROJECT
                else {
                    $oldProject = $lastKnownState.projects[$projectGid]
                    if ($oldProject.name -ne $project.name -or 
                        $oldProject.archived -ne $project.archived) {
                        Write-SentinelLog "📝 UPDATED PROJECT: $($project.name)" "UPDATE"
                        $lastKnownState.projects[$projectGid] = $project
                        $changesDetected = $true
                    }
                }
            }
            
            # DELETED PROJECTS
            $currentGids = $currentProjects | ForEach-Object { $_.gid }
            $deletedProjects = $lastKnownState.projects.Keys | Where-Object { $_ -notin $currentGids }
            
            foreach ($deletedGid in $deletedProjects) {
                $deletedName = $lastKnownState.projects[$deletedGid].name
                Write-SentinelLog "🗑️ DELETED PROJECT: $deletedName" "DELETE"
                $lastKnownState.projects.Remove($deletedGid)
                $changesDetected = $true
            }
        }
        
        # ============================================================================
        # MONITOR RECENT TASKS (Last 100 modified)
        # ============================================================================
        $recentTasks = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/tasks?modified_since=$(Get-Date).AddHours(-1).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')&limit=100"
        
        if ($recentTasks) {
            foreach ($task in $recentTasks) {
                $taskGid = $task.gid
                
                # NEW TASK
                if (-not $lastKnownState.tasks.ContainsKey($taskGid)) {
                    Write-SentinelLog "✨ NEW TASK: $($task.name)" "NEW"
                    $lastKnownState.tasks[$taskGid] = $task
                    $changesDetected = $true
                }
                # UPDATED TASK
                else {
                    $oldTask = $lastKnownState.tasks[$taskGid]
                    if ($oldTask.completed -ne $task.completed) {
                        $status = if ($task.completed) { "COMPLETED" } else { "REOPENED" }
                        Write-SentinelLog "✓ TASK $status: $($task.name)" "UPDATE"
                        $lastKnownState.tasks[$taskGid] = $task
                        $changesDetected = $true
                    }
                }
            }
        }
        
        # ============================================================================
        # MONITOR USERS
        # ============================================================================
        $currentUsers = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/users"
        
        if ($currentUsers) {
            foreach ($user in $currentUsers) {
                if (-not $lastKnownState.users.ContainsKey($user.gid)) {
                    Write-SentinelLog "👤 NEW USER: $($user.name)" "NEW"
                    $lastKnownState.users[$user.gid] = $user
                    $changesDetected = $true
                }
            }
        }
        
        # ============================================================================
        # MONITOR TAGS
        # ============================================================================
        $currentTags = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/tags"
        
        if ($currentTags) {
            foreach ($tag in $currentTags) {
                if (-not $lastKnownState.tags.ContainsKey($tag.gid)) {
                    Write-SentinelLog "🏷️ NEW TAG: $($tag.name)" "NEW"
                    $lastKnownState.tags[$tag.gid] = $tag
                    $changesDetected = $true
                }
            }
        }
        
        # ============================================================================
        # UPDATE INDEX IF CHANGES DETECTED
        # ============================================================================
        if ($changesDetected) {
            Write-SentinelLog "💾 Changes detected, updating index..." "INFO"
            
            # Rebuild index structure
            $updatedIndex = @{
                workspace           = @{
                    gid = $WorkspaceGid
                }
                updated_at          = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
                projects            = @($lastKnownState.projects.Values)
                users               = @($lastKnownState.users.Values)
                tags                = @($lastKnownState.tags.Values)
                total_tracked_tasks = $lastKnownState.tasks.Count
            }
            
            try {
                $updatedIndex | ConvertTo-Json -Depth 10 | Set-Content $IndexFile -Encoding UTF8
                Write-SentinelLog "✓ Index updated successfully" "INFO"
            }
            catch {
                Write-SentinelLog "Failed to update index: $_" "ERROR"
            }
        }
        else {
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }
        
        # Wait before next poll
        Start-Sleep -Seconds $PollInterval
    }
}
finally {
    Write-Host ""
    Write-SentinelLog "Sentinel shutting down" "INFO"
}

