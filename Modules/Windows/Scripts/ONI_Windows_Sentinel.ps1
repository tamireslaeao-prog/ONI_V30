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
# 👁️ ONI WINDOWS SENTINEL - REAL-TIME SYSTEM MONITOR
# Description: Monitors system health, processes, network, security alerts
# ============================================================================

param(
    [string]$LogFile = "",
    [int]$PollInterval = 5,  # Seconds between checks
    [int]$CPUThreshold = 90,
    [int]$MemoryThreshold = 85,
    [int]$DiskThreshold = 90,
    [switch]$MonitorProcesses = $true,
    [switch]$MonitorNetwork = $true,
    [switch]$MonitorSecurity = $true
)

if ([string]::IsNullOrEmpty($LogFile)) {
    $LogFile = Join-Path $PSScriptRoot "..\logs\sentinel_log.txt"
}
$LogFile = [System.IO.Path]::GetFullPath($LogFile)

Write-Host "👁️ ONI WINDOWS SENTINEL ACTIVATED" -ForegroundColor Cyan
Write-Host "   Log File:        $LogFile" -ForegroundColor Gray
Write-Host "   Poll Interval:   ${PollInterval}s" -ForegroundColor Gray
Write-Host "   CPU Alert:       ${CPUThreshold}%" -ForegroundColor Gray
Write-Host "   Memory Alert:    ${MemoryThreshold}%" -ForegroundColor Gray
Write-Host "   Disk Alert:      ${DiskThreshold}%" -ForegroundColor Gray
Write-Host ""

# Ensure log directory exists
$logDir = Split-Path $LogFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# ============================================================================
# Helper: Log Event
# ============================================================================
function Write-SentinelLog {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Type | $Message"
    $logEntry | Out-File -FilePath $LogFile -Append -ErrorAction SilentlyContinue
    
    $color = switch ($Type) {
        "ALERT"    { "Red" }
        "WARNING"  { "Yellow" }
        "SUCCESS"  { "Green" }
        "INFO"     { "Cyan" }
        default    { "Gray" }
    }
    
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# ============================================================================
# Initialize State Tracking
# ============================================================================
$lastKnownProcesses = @{}
$lastKnownConnections = @{}
$alertHistory = @{}
$sessionStats = @{
    alerts_triggered = 0
    processes_started = 0
    processes_ended = 0
    network_connections = 0
    start_time = Get-Date
}

Write-SentinelLog "Sentinel started - monitoring Windows system"

# Load initial process state
Get-Process | ForEach-Object {
    $lastKnownProcesses[$_.Id] = @{
        Name = $_.Name
        CPU = $_.CPU
        Memory = $_.WorkingSet64
    }
}

Write-Host "   Currently tracking $($lastKnownProcesses.Count) processes" -ForegroundColor Gray
Write-Host "   (Press Ctrl+C to stop monitoring)" -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# Main Monitoring Loop
# ============================================================================
try {
    while ($true) {
        $alertsThisCycle = 0
        
        # ====================================================================
        # MONITOR CPU
        # ====================================================================
        $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
        $cpuLoad = $cpu.LoadPercentage
        
        if ($cpuLoad -ge $CPUThreshold) {
            if (-not $alertHistory.ContainsKey("CPU_$cpuLoad")) {
                Write-SentinelLog "⚠️ ALERT: CPU usage at ${cpuLoad}% (threshold: ${CPUThreshold}%)" "ALERT"
                $alertHistory["CPU_$cpuLoad"] = Get-Date
                $sessionStats.alerts_triggered++
                $alertsThisCycle++
                
                # Find top CPU consumer
                $topProcess = Get-Process | Sort-Object CPU -Descending | Select-Object -First 1
                Write-SentinelLog "   Top process: $($topProcess.Name) - $([math]::Round($topProcess.CPU, 2))s" "WARNING"
            }
        }
        
        # ====================================================================
        # MONITOR MEMORY
        # ====================================================================
        $os = Get-CimInstance Win32_OperatingSystem
        $totalRAM = $os.TotalVisibleMemorySize / 1MB
        $freeRAM = $os.FreePhysicalMemory / 1MB / 1024
        $usedRAM = $totalRAM - $freeRAM
        $memoryPercent = [math]::Round(($usedRAM / $totalRAM) * 100, 2)
        
        if ($memoryPercent -ge $MemoryThreshold) {
            $alertKey = "MEM_$([math]::Floor($memoryPercent))"
            if (-not $alertHistory.ContainsKey($alertKey)) {
                Write-SentinelLog "⚠️ ALERT: Memory usage at ${memoryPercent}% (threshold: ${MemoryThreshold}%)" "ALERT"
                $alertHistory[$alertKey] = Get-Date
                $sessionStats.alerts_triggered++
                $alertsThisCycle++
                
                # Find top memory consumer
                $topProcess = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 1
                $memMB = [math]::Round($topProcess.WorkingSet64 / 1MB, 2)
                Write-SentinelLog "   Top process: $($topProcess.Name) - ${memMB}MB" "WARNING"
            }
        }
        
        # ====================================================================
        # MONITOR DISK SPACE
        # ====================================================================
        $disks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        
        foreach ($disk in $disks) {
            $freePercent = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 2)
            $usedPercent = 100 - $freePercent
            
            if ($usedPercent -ge $DiskThreshold) {
                $alertKey = "DISK_$($disk.DeviceID)_$([math]::Floor($usedPercent))"
                if (-not $alertHistory.ContainsKey($alertKey)) {
                    $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
                    Write-SentinelLog "⚠️ ALERT: Disk $($disk.DeviceID) at ${usedPercent}% full (${freeGB}GB free)" "ALERT"
                    $alertHistory[$alertKey] = Get-Date
                    $sessionStats.alerts_triggered++
                    $alertsThisCycle++
                }
            }
        }
        
        # ====================================================================
        # MONITOR PROCESSES
        # ====================================================================
        if ($MonitorProcesses) {
            $currentProcesses = @{}
            Get-Process | ForEach-Object {
                $currentProcesses[$_.Id] = @{
                    Name = $_.Name
                    CPU = $_.CPU
                    Memory = $_.WorkingSet64
                }
            }
            
            # Detect NEW PROCESSES
            foreach ($pid in $currentProcesses.Keys) {
                if (-not $lastKnownProcesses.ContainsKey($pid)) {
                    $proc = $currentProcesses[$pid]
                    Write-SentinelLog "🆕 NEW PROCESS: $($proc.Name) (PID: $pid)" "INFO"
                    $sessionStats.processes_started++
                }
            }
            
            # Detect ENDED PROCESSES
            foreach ($pid in $lastKnownProcesses.Keys) {
                if (-not $currentProcesses.ContainsKey($pid)) {
                    $proc = $lastKnownProcesses[$pid]
                    Write-SentinelLog "❌ PROCESS ENDED: $($proc.Name) (PID: $pid)" "INFO"
                    $sessionStats.processes_ended++
                }
            }
            
            $lastKnownProcesses = $currentProcesses
        }
        
        # ====================================================================
        # MONITOR NETWORK
        # ====================================================================
        if ($MonitorNetwork) {
            $currentConnections = @{}
            $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue
            
            foreach ($conn in $connections) {
                $key = "$($conn.LocalAddress):$($conn.LocalPort)-$($conn.RemoteAddress):$($conn.RemotePort)"
                $currentConnections[$key] = @{
                    Process = (Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue).Name
                    State = $conn.State
                }
                
                # Detect NEW CONNECTIONS
                if (-not $lastKnownConnections.ContainsKey($key)) {
                    $proc = $currentConnections[$key].Process
                    Write-SentinelLog "🔗 NEW CONNECTION: $proc -> $($conn.RemoteAddress):$($conn.RemotePort)" "INFO"
                    $sessionStats.network_connections++
                }
            }
            
            $lastKnownConnections = $currentConnections
        }
        
        # ====================================================================
        # MONITOR SECURITY EVENTS
        # ====================================================================
        if ($MonitorSecurity) {
            # Check Windows Defender status changes
            try {
                $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
                
                if (-not $defender.RealTimeProtectionEnabled) {
                    if (-not $alertHistory.ContainsKey("DEFENDER_OFF")) {
                        Write-SentinelLog "⚠️ SECURITY ALERT: Windows Defender Real-Time Protection is DISABLED" "ALERT"
                        $alertHistory["DEFENDER_OFF"] = Get-Date
                        $sessionStats.alerts_triggered++
                        $alertsThisCycle++
                    }
                } else {
                    $alertHistory.Remove("DEFENDER_OFF")
                }
            } catch {}
            
            # Check firewall status
            $firewallProfiles = Get-NetFirewallProfile
            foreach ($profile in $firewallProfiles) {
                if (-not $profile.Enabled) {
                    $alertKey = "FIREWALL_OFF_$($profile.Name)"
                    if (-not $alertHistory.ContainsKey($alertKey)) {
                        Write-SentinelLog "⚠️ SECURITY ALERT: Firewall $($profile.Name) profile is DISABLED" "ALERT"
                        $alertHistory[$alertKey] = Get-Date
                        $sessionStats.alerts_triggered++
                        $alertsThisCycle++
                    }
                } else {
                    $alertHistory.Remove("FIREWALL_OFF_$($profile.Name)")
                }
            }
        }
        
        # ====================================================================
        # PERIODIC STATUS UPDATE
        # ====================================================================
        $elapsed = (Get-Date) - $sessionStats.start_time
        
        if ($elapsed.TotalSeconds % 60 -lt $PollInterval -and $elapsed.TotalSeconds -gt 30) {
            Write-Host ""
            Write-Host "   ═══ STATUS UPDATE ═══" -ForegroundColor White
            Write-Host "   Runtime:          $([math]::Floor($elapsed.TotalMinutes)) minutes" -ForegroundColor Gray
            Write-Host "   CPU:              ${cpuLoad}%" -ForegroundColor $(if ($cpuLoad -ge $CPUThreshold) { "Red" } else { "Green" })
            Write-Host "   Memory:           ${memoryPercent}%" -ForegroundColor $(if ($memoryPercent -ge $MemoryThreshold) { "Red" } else { "Green" })
            Write-Host "   Active Processes: $($lastKnownProcesses.Count)" -ForegroundColor Gray
            Write-Host "   Alerts Triggered: $($sessionStats.alerts_triggered)" -ForegroundColor $(if ($sessionStats.alerts_triggered -gt 0) { "Yellow" } else { "Green" })
            Write-Host ""
        }
        
        # Clean old alert history (older than 5 minutes)
        $oldAlerts = $alertHistory.Keys | Where-Object {
            ((Get-Date) - $alertHistory[$_]).TotalMinutes -gt 5
        }
        foreach ($key in $oldAlerts) {
            $alertHistory.Remove($key)
        }
        
        # Wait before next check
        if ($alertsThisCycle -eq 0) {
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }
        
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
    
    # Final Report
    $elapsed = (Get-Date) - $sessionStats.start_time
    
    Write-Host ""
    Write-Host "   ═══ FINAL SESSION REPORT ═══" -ForegroundColor Cyan
    Write-Host "   Total Runtime:       $([math]::Floor($elapsed.TotalMinutes)) minutes" -ForegroundColor White
    Write-Host "   Alerts Triggered:    $($sessionStats.alerts_triggered)" -ForegroundColor White
    Write-Host "   Processes Started:   $($sessionStats.processes_started)" -ForegroundColor White
    Write-Host "   Processes Ended:     $($sessionStats.processes_ended)" -ForegroundColor White
    Write-Host "   Network Connections: $($sessionStats.network_connections)" -ForegroundColor White
    Write-Host ""
}
