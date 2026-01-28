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
# ONI ASANA DEEP HARVESTER v1.0 - Complete Workspace Analyzer
# Description: Scans entire Asana workspace and creates comprehensive index
# ============================================================================

param(
    [string]$AsanaToken = $env:ASANA_TOKEN,
    [string]$WorkspaceGid = "",
    [string]$OutputFile
)

if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[ASANA HARVESTER v1.0] Starting deep scan..." -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($AsanaToken)) {
    Write-Host "   [FAIL] ASANA_TOKEN not set. Use: `$env:ASANA_TOKEN = 'your_token'" -ForegroundColor Red
    exit 1
}

$BaseURL = "https://app.asana.com/api/1.0"
$Headers = @{
    "Authorization" = "Bearer $AsanaToken"
    "Content-Type"  = "application/json"
}

# Helper: Safe API Call
function Invoke-AsanaAPI {
    param([string]$Endpoint)
    try {
        $response = Invoke-RestMethod -Uri "$BaseURL$Endpoint" -Headers $Headers -Method Get
        return $response.data
    }
    catch {
        Write-Host "   [ERROR] API Call Failed: $Endpoint - $_" -ForegroundColor Red
        return $null
    }
}

# ============================================================================
# STEP 1: Get Workspace Info
# ============================================================================
Write-Host ""
Write-Host "[STEP 1] Fetching Workspace..." -ForegroundColor Yellow

$workspaces = Invoke-AsanaAPI -Endpoint "/workspaces"

if ($null -eq $workspaces) {
    Write-Host "   [FAIL] Could not fetch workspaces" -ForegroundColor Red
    exit 1
}

# If no workspace specified, use first one
if ([string]::IsNullOrEmpty($WorkspaceGid)) {
    $workspace = $workspaces[0]
    $WorkspaceGid = $workspace.gid
    Write-Host "   Using: $($workspace.name) (GID: $WorkspaceGid)" -ForegroundColor Green
}
else {
    $workspace = $workspaces | Where-Object { $_.gid -eq $WorkspaceGid }
    Write-Host "   Target: $($workspace.name)" -ForegroundColor Green
}

$harvestData = @{
    workspace     = @{
        gid             = $workspace.gid
        name            = $workspace.name
        is_organization = $workspace.is_organization
    }
    harvested_at  = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    projects      = @()
    users         = @()
    teams         = @()
    tags          = @()
    custom_fields = @()
    statistics    = @{}
}

# ============================================================================
# STEP 2: Harvest Users
# ============================================================================
Write-Host ""
Write-Host "[STEP 2] Harvesting Users..." -ForegroundColor Yellow

$users = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/users"

if ($users) {
    foreach ($user in $users) {
        $harvestData.users += @{
            gid   = $user.gid
            name  = $user.name
            email = $user.email
        }
        Write-Host "   [USER] $($user.name)" -ForegroundColor Gray
    }
    Write-Host "   Total Users: $($users.Count)" -ForegroundColor Green
}

# ============================================================================
# STEP 3: Harvest Teams
# ============================================================================
Write-Host ""
Write-Host "[STEP 3] Harvesting Teams..." -ForegroundColor Yellow

if ($workspace.is_organization) {
    $teams = Invoke-AsanaAPI -Endpoint "/organizations/$WorkspaceGid/teams"
    
    if ($teams) {
        foreach ($team in $teams) {
            $harvestData.teams += @{
                gid  = $team.gid
                name = $team.name
            }
            Write-Host "   [TEAM] $($team.name)" -ForegroundColor Cyan
        }
        Write-Host "   Total Teams: $($teams.Count)" -ForegroundColor Green
    }
}
else {
    Write-Host "   (Workspace is not an organization - skipping teams)" -ForegroundColor Gray
}

# ============================================================================
# STEP 4: Harvest Tags
# ============================================================================
Write-Host ""
Write-Host "[STEP 4] Harvesting Tags..." -ForegroundColor Yellow

$tags = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/tags"

if ($tags) {
    foreach ($tag in $tags) {
        $harvestData.tags += @{
            gid   = $tag.gid
            name  = $tag.name
            color = $tag.color
        }
        Write-Host "   [TAG] $($tag.name) ($($tag.color))" -ForegroundColor Magenta
    }
    Write-Host "   Total Tags: $($tags.Count)" -ForegroundColor Green
}

# ============================================================================
# STEP 5: Harvest Custom Fields
# ============================================================================
Write-Host ""
Write-Host "[STEP 5] Harvesting Custom Fields..." -ForegroundColor Yellow

$customFields = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/custom_fields"

if ($customFields) {
    foreach ($field in $customFields) {
        $fieldData = @{
            gid  = $field.gid
            name = $field.name
            type = $field.resource_subtype
        }
        
        if ($field.enum_options) {
            $fieldData.options = $field.enum_options | ForEach-Object { $_.name }
        }
        
        $harvestData.custom_fields += $fieldData
        Write-Host "   [FIELD] $($field.name) (Type: $($field.resource_subtype))" -ForegroundColor Blue
    }
    Write-Host "   Total Custom Fields: $($customFields.Count)" -ForegroundColor Green
}

# ============================================================================
# STEP 6: Harvest Projects (DEEP SCAN)
# ============================================================================
Write-Host ""
Write-Host "[STEP 6] Harvesting Projects (Deep Scan)..." -ForegroundColor Yellow

$projects = Invoke-AsanaAPI -Endpoint "/workspaces/$WorkspaceGid/projects"

$totalTasks = 0
$totalSections = 0

if ($projects) {
    foreach ($project in $projects) {
        Write-Host ""
        Write-Host "   [PROJECT] $($project.name)" -ForegroundColor White
        
        $projectData = @{
            gid        = $project.gid
            name       = $project.name
            color      = $project.color
            layout     = $project.layout
            public     = $project.public
            archived   = $project.archived
            owner      = @{}
            members    = @()
            sections   = @()
            tasks      = @()
            statistics = @{}
        }
        
        # Get detailed project info
        $projectDetails = Invoke-AsanaAPI -Endpoint "/projects/$($project.gid)"
        
        if ($projectDetails) {
            if ($projectDetails.owner) {
                $projectData.owner = @{
                    gid  = $projectDetails.owner.gid
                    name = $projectDetails.owner.name
                }
            }
            
            # Get Sections
            $sections = Invoke-AsanaAPI -Endpoint "/projects/$($project.gid)/sections"
            if ($sections) {
                foreach ($section in $sections) {
                    $projectData.sections += @{
                        gid  = $section.gid
                        name = $section.name
                    }
                    Write-Host "      [SECTION] $($section.name)" -ForegroundColor DarkCyan
                }
                $totalSections += $sections.Count
            }
            
            # Get Tasks (Summary only to avoid huge data)
            $tasks = Invoke-AsanaAPI -Endpoint "/projects/$($project.gid)/tasks?opt_fields=name,completed,assignee,due_on"
            
            if ($tasks) {
                $completedCount = 0
                
                foreach ($task in $tasks) {
                    $taskData = @{
                        gid       = $task.gid
                        name      = $task.name
                        completed = $task.completed
                        due_on    = $task.due_on
                    }
                    
                    if ($task.assignee) {
                        $taskData.assignee = @{
                            gid  = $task.assignee.gid
                            name = $task.assignee.name
                        }
                    }
                    
                    if ($task.completed) { $completedCount++ }
                    
                    $projectData.tasks += $taskData
                    
                    # Show first 5 tasks only
                    if ($projectData.tasks.Count -le 5) {
                        $status = if ($task.completed) { "✓" } else { "○" }
                        Write-Host "      [$status] $($task.name)" -ForegroundColor Gray
                    }
                }
                
                if ($tasks.Count -gt 5) {
                    Write-Host "      ... and $($tasks.Count - 5) more tasks" -ForegroundColor DarkGray
                }
                
                $totalTasks += $tasks.Count
                
                # Calculate statistics
                $projectData.statistics = @{
                    total_tasks      = $tasks.Count
                    completed_tasks  = $completedCount
                    incomplete_tasks = $tasks.Count - $completedCount
                    completion_rate  = if ($tasks.Count -gt 0) {
                        [math]::Round(($completedCount / $tasks.Count) * 100, 2)
                    }
                    else { 0 }
                }
                
                Write-Host "      ---" -ForegroundColor DarkGray
                Write-Host "      Stats: $($tasks.Count) tasks | $completedCount completed | $($projectData.statistics.completion_rate)% done" -ForegroundColor Green
            }
        }
        
        $harvestData.projects += $projectData
    }
    
    Write-Host ""
    Write-Host "   Total Projects: $($projects.Count)" -ForegroundColor Green
}

# ============================================================================
# STEP 7: Calculate Global Statistics
# ============================================================================
Write-Host ""
Write-Host "[STEP 7] Calculating Statistics..." -ForegroundColor Yellow

$harvestData.statistics = @{
    total_projects      = $harvestData.projects.Count
    total_users         = $harvestData.users.Count
    total_teams         = $harvestData.teams.Count
    total_tags          = $harvestData.tags.Count
    total_custom_fields = $harvestData.custom_fields.Count
    total_tasks         = $totalTasks
    total_sections      = $totalSections
    archived_projects   = ($harvestData.projects | Where-Object { $_.archived }).Count
    active_projects     = ($harvestData.projects | Where-Object { -not $_.archived }).Count
}

Write-Host "   Global Statistics:" -ForegroundColor White
Write-Host "      Projects: $($harvestData.statistics.total_projects) (Active: $($harvestData.statistics.active_projects))" -ForegroundColor Gray
Write-Host "      Tasks: $totalTasks" -ForegroundColor Gray
Write-Host "      Users: $($harvestData.statistics.total_users)" -ForegroundColor Gray
Write-Host "      Teams: $($harvestData.statistics.total_teams)" -ForegroundColor Gray
Write-Host "      Tags: $($harvestData.statistics.total_tags)" -ForegroundColor Gray

# ============================================================================
# STEP 8: Save to JSON
# ============================================================================
Write-Host ""
Write-Host "[STEP 8] Saving to Database..." -ForegroundColor Yellow

$outputDir = Split-Path $OutputFile -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$harvestData | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host "   ✓ Saved to: $OutputFile" -ForegroundColor Green

# ============================================================================
# COMPLETE
# ============================================================================
Write-Host ""
Write-Host "[COMPLETE] Asana harvest finished" -ForegroundColor Cyan
Write-Host "   Workspace: $($workspace.name)" -ForegroundColor White
Write-Host "   Projects: $($harvestData.statistics.total_projects)" -ForegroundColor White
Write-Host "   Tasks: $totalTasks" -ForegroundColor White
Write-Host "   Output: $OutputFile" -ForegroundColor Gray
