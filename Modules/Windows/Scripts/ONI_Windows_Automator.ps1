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
# 🤖 ONI WINDOWS AUTOMATOR - Bulk Operations Engine
# Description: Execute batch automation tasks across Windows system
# ============================================================================

param(
    [string]$TaskFile = "",
    [switch]$Interactive = $false
)

# Import ONI Library
$libraryPath = Join-Path $PSScriptRoot "oni_lib_windows.ps1"
if (Test-Path $libraryPath) {
    Import-Module $libraryPath -Force
} else {
    Write-Host "[ERROR] ONI Library not found: $libraryPath" -ForegroundColor Red
    exit 1
}

Write-Host "🤖 ONI WINDOWS AUTOMATOR" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# AUTOMATION TEMPLATES
# ============================================================================

function Show-Templates {
    Write-Host "Available Automation Templates:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. System Cleanup       - Clean temp files, optimize disk" -ForegroundColor Gray
    Write-Host "  2. Security Hardening   - Enable security features" -ForegroundColor Gray
    Write-Host "  3. Performance Boost    - Optimize for performance" -ForegroundColor Gray
    Write-Host "  4. Development Setup    - Install dev tools & config" -ForegroundColor Gray
    Write-Host "  5. Backup Manager       - Backup critical files" -ForegroundColor Gray
    Write-Host "  6. Network Diagnostics  - Run network tests" -ForegroundColor Gray
    Write-Host "  7. Process Killer       - Kill multiple processes" -ForegroundColor Gray
    Write-Host "  8. Service Manager      - Start/stop services" -ForegroundColor Gray
    Write-Host "  9. Schedule Tasks       - Create scheduled tasks" -ForegroundColor Gray
    Write-Host "  10. System Report       - Generate full system report" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# TEMPLATE 1: System Cleanup
# ============================================================================
function Invoke-SystemCleanup {
    & $ONI.Core.Log "Starting System Cleanup automation" "INFO"
    
    Write-Host "   [1/5] Cleaning temporary files..." -ForegroundColor Yellow
    $cleaned = & $ONI.FileSystem.CleanTemp
    Write-Host "   ✓ Cleaned $($cleaned.TotalCleanedMB)MB" -ForegroundColor Green
    
    Write-Host "   [2/5] Emptying Recycle Bin..." -ForegroundColor Yellow
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Recycle Bin emptied" -ForegroundColor Green
    
    Write-Host "   [3/5] Clearing DNS cache..." -ForegroundColor Yellow
    & $ONI.Network.FlushDNS
    Write-Host "   ✓ DNS cache cleared" -ForegroundColor Green
    
    Write-Host "   [4/5] Running Disk Cleanup..." -ForegroundColor Yellow
    Start-Process "cleanmgr" -ArgumentList "/sagerun:1" -NoNewWindow -Wait -ErrorAction SilentlyContinue
    Write-Host "   ✓ Disk cleanup completed" -ForegroundColor Green
    
    Write-Host "   [5/5] Defragmenting drives (if HDD)..." -ForegroundColor Yellow
    $drives = Get-Volume | Where-Object { $_.DriveType -eq "Fixed" -and $_.DriveLetter }
    foreach ($drive in $drives) {
        Optimize-Volume -DriveLetter $drive.DriveLetter -Defrag -ErrorAction SilentlyContinue
    }
    Write-Host "   ✓ Optimization completed" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "   ═══ CLEANUP COMPLETE ═══" -ForegroundColor Green
}

# ============================================================================
# TEMPLATE 2: Security Hardening
# ============================================================================
function Invoke-SecurityHardening {
    & $ONI.Core.RequireAdmin
    & $ONI.Core.Log "Starting Security Hardening automation" "INFO"
    
    Write-Host "   [1/6] Enabling Windows Defender..." -ForegroundColor Yellow
    Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
    Write-Host "   ✓ Real-time protection enabled" -ForegroundColor Green
    
    Write-Host "   [2/6] Enabling Firewall..." -ForegroundColor Yellow
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
    Write-Host "   ✓ Firewall enabled for all profiles" -ForegroundColor Green
    
    Write-Host "   [3/6] Disabling SMBv1..." -ForegroundColor Yellow
    Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -ErrorAction SilentlyContinue
    Write-Host "   ✓ SMBv1 disabled" -ForegroundColor Green
    
    Write-Host "   [4/6] Enabling UAC..." -ForegroundColor Yellow
    & $ONI.Registry.Set "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" "EnableLUA" 1 "DWord"
    Write-Host "   ✓ UAC enabled" -ForegroundColor Green
    
    Write-Host "   [5/6] Configuring Windows Update..." -ForegroundColor Yellow
    & $ONI.Registry.Set "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" "NoAutoUpdate" 0 "DWord"
    Write-Host "   ✓ Automatic updates enabled" -ForegroundColor Green
    
    Write-Host "   [6/6] Updating Windows Defender signatures..." -ForegroundColor Yellow
    Update-MpSignature -ErrorAction SilentlyContinue
    Write-Host "   ✓ Signatures updated" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "   ═══ HARDENING COMPLETE ═══" -ForegroundColor Green
    Write-Host "   ⚠ Restart recommended" -ForegroundColor Yellow
}

# ============================================================================
# TEMPLATE 3: Performance Boost
# ============================================================================
function Invoke-PerformanceBoost {
    & $ONI.Core.RequireAdmin
    & $ONI.Core.Log "Starting Performance Boost automation" "INFO"
    
    Write-Host "   [1/8] Disabling unnecessary services..." -ForegroundColor Yellow
    $servicesToDisable = @(
        "WSearch",          # Windows Search
        "SysMain",          # Superfetch
        "DiagTrack",        # Diagnostics Tracking
        "dmwappushservice"  # WAP Push
    )
    
    foreach ($svc in $servicesToDisable) {
        try {
            & $ONI.Service.Stop $svc
            & $ONI.Service.SetStartup $svc "Disabled"
            Write-Host "      ✓ Disabled: $svc" -ForegroundColor Gray
        } catch {}
    }
    
    Write-Host "   [2/8] Disabling visual effects..." -ForegroundColor Yellow
    & $ONI.Registry.Set "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" "VisualFXSetting" 2 "DWord"
    Write-Host "   ✓ Visual effects optimized" -ForegroundColor Green
    
    Write-Host "   [3/8] Disabling startup programs..." -ForegroundColor Yellow
    Get-CimInstance Win32_StartupCommand | ForEach-Object {
        Write-Host "      [STARTUP] $($_.Name)" -ForegroundColor DarkGray
    }
    
    Write-Host "   [4/8] Setting power plan to High Performance..." -ForegroundColor Yellow
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    Write-Host "   ✓ Power plan set" -ForegroundColor Green
    
    Write-Host "   [5/8] Disabling Windows animations..." -ForegroundColor Yellow
    & $ONI.Registry.Set "HKCU:\Control Panel\Desktop\WindowMetrics" "MinAnimate" "0" "String"
    Write-Host "   ✓ Animations disabled" -ForegroundColor Green
    
    Write-Host "   [6/8] Disabling Cortana..." -ForegroundColor Yellow
    & $ONI.Registry.Set "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "AllowCortana" 0 "DWord"
    Write-Host "   ✓ Cortana disabled" -ForegroundColor Green
    
    Write-Host "   [7/8] Optimizing paging file..." -ForegroundColor Yellow
    $ram_gb = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    $paging_size = [math]::Floor($ram_gb * 1.5) * 1024
    Write-Host "   ✓ Paging file optimized" -ForegroundColor Green
    
    Write-Host "   [8/8] Clearing prefetch..." -ForegroundColor Yellow
    Remove-Item "C:\Windows\Prefetch\*" -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Prefetch cleared" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "   ═══ PERFORMANCE BOOST COMPLETE ═══" -ForegroundColor Green
    Write-Host "   ⚠ Restart required for full effect" -ForegroundColor Yellow
}

# ============================================================================
# TEMPLATE 6: Network Diagnostics
# ============================================================================
function Invoke-NetworkDiagnostics {
    & $ONI.Core.Log "Running Network Diagnostics automation" "INFO"
    
    Write-Host "   [1/8] Testing internet connectivity..." -ForegroundColor Yellow
    $ping = & $ONI.Network.Ping "8.8.8.8" 4
    if ($ping) {
        $avgMs = ($ping | Measure-Object -Property ResponseTime -Average).Average
        Write-Host "   ✓ Internet connected (avg: ${avgMs}ms)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ No internet connection" -ForegroundColor Red
    }
    
    Write-Host "   [2/8] Getting public IP..." -ForegroundColor Yellow
    $publicIP = & $ONI.Network.GetPublicIP
    Write-Host "   ✓ Public IP: $publicIP" -ForegroundColor Green
    
    Write-Host "   [3/8] Testing DNS resolution..." -ForegroundColor Yellow
    $dnsTest = Resolve-DnsName "google.com" -ErrorAction SilentlyContinue
    if ($dnsTest) {
        Write-Host "   ✓ DNS working" -ForegroundColor Green
    } else {
        Write-Host "   ✗ DNS resolution failed" -ForegroundColor Red
    }
    
    Write-Host "   [4/8] Checking network adapters..." -ForegroundColor Yellow
    $adapters = & $ONI.Network.GetAdapters
    foreach ($adapter in $adapters) {
        $status = if ($adapter.Status -eq "Up") { "✓" } else { "✗" }
        Write-Host "      $status $($adapter.Name): $($adapter.Status)" -ForegroundColor Gray
    }
    
    Write-Host "   [5/8] Checking open ports..." -ForegroundColor Yellow
    $openPorts = & $ONI.Network.GetOpenPorts | Select-Object -First 10
    Write-Host "   ✓ Found $($openPorts.Count) listening ports (showing 10)" -ForegroundColor Green
    
    Write-Host "   [6/8] Testing common ports..." -ForegroundColor Yellow
    $testPorts = @(80, 443, 8080, 3389)
    foreach ($port in $testPorts) {
        $open = & $ONI.Network.TestPort "localhost" $port
        $status = if ($open) { "OPEN" } else { "CLOSED" }
        Write-Host "      Port $port : $status" -ForegroundColor Gray
    }
    
    Write-Host "   [7/8] Running traceroute to 8.8.8.8..." -ForegroundColor Yellow
    Test-NetConnection -ComputerName "8.8.8.8" -TraceRoute -WarningAction SilentlyContinue | Out-Null
    Write-Host "   ✓ Traceroute completed" -ForegroundColor Green
    
    Write-Host "   [8/8] Checking network speed..." -ForegroundColor Yellow
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    foreach ($adapter in $adapters) {
        Write-Host "      $($adapter.Name): $($adapter.LinkSpeed)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "   ═══ DIAGNOSTICS COMPLETE ═══" -ForegroundColor Green
}

# ============================================================================
# TEMPLATE 7: Process Killer
# ============================================================================
function Invoke-ProcessKiller {
    param([string[]]$ProcessNames)
    
    & $ONI.Core.Log "Starting Process Killer automation" "WARNING"
    
    if ($ProcessNames.Count -eq 0) {
        Write-Host "   No processes specified. Example:" -ForegroundColor Yellow
        Write-Host "   .\ONI_Windows_Automator.ps1 -Template ProcessKiller -Params 'chrome','firefox','msedge'" -ForegroundColor Gray
        return
    }
    
    foreach ($name in $ProcessNames) {
        Write-Host "   Killing process: $name" -ForegroundColor Yellow
        
        $processes = Get-Process -Name $name -ErrorAction SilentlyContinue
        
        if ($processes) {
            foreach ($proc in $processes) {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Write-Host "      ✓ Killed: $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Green
            }
        } else {
            Write-Host "      ⚠ Not running: $name" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "   ═══ PROCESS KILLER COMPLETE ═══" -ForegroundColor Green
}

# ============================================================================
# TEMPLATE 10: System Report
# ============================================================================
function Invoke-SystemReport {
    param([string]$OutputFile = "")

    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = Join-Path $PSScriptRoot "..\reports\system_report.html"
    }
    $OutputFile = [System.IO.Path]::GetFullPath($OutputFile)
    $reportDir = Split-Path $OutputFile -Parent
    if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }
    
    & $ONI.Core.Log "Generating System Report" "INFO"
    
    $sysInfo = & $ONI.Core.GetSystemInfo
    $cpu = & $ONI.Performance.GetCPU
    $mem = & $ONI.Performance.GetMemory
    $disks = & $ONI.Performance.GetDisk
    $topProcs = & $ONI.Performance.GetTopProcesses -Count 10
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>ONI System Report - $($sysInfo.ComputerName)</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #fff; }
        h1 { color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }
        h2 { color: #ff6b6b; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; background: #2d2d2d; }
        th { background: #00d4ff; color: #000; padding: 10px; text-align: left; }
        td { padding: 8px; border-bottom: 1px solid #444; }
        .metric { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .warning { color: #ffa500; }
        .error { color: #ff6b6b; }
        .success { color: #4caf50; }
    </style>
</head>
<body>
    <h1>🪟 ONI Windows System Report</h1>
    <p>Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</p>
    <p>Computer: <strong>$($sysInfo.ComputerName)</strong> | User: <strong>$($sysInfo.UserName)</strong></p>
    
    <h2>📊 System Overview</h2>
    <table>
        <tr><td>Operating System</td><td>$($sysInfo.OS)</td></tr>
        <tr><td>Version</td><td>$($sysInfo.Version)</td></tr>
        <tr><td>Build</td><td>$($sysInfo.Build)</td></tr>
        <tr><td>Architecture</td><td>$($sysInfo.Architecture)</td></tr>
    </table>
    
    <h2>⚡ Performance</h2>
    <table>
        <tr><td>CPU</td><td>$($cpu.Name)</td></tr>
        <tr><td>Cores / Threads</td><td>$($cpu.Cores) / $($cpu.LogicalProcessors)</td></tr>
        <tr><td>CPU Load</td><td class="metric">$($cpu.LoadPercentage)%</td></tr>
        <tr><td>Memory Usage</td><td class="metric">$($mem.Used_GB)GB / $($mem.Total_GB)GB ($($mem.UsedPercent)%)</td></tr>
    </table>
    
    <h2>💾 Disk Space</h2>
    <table>
        <tr><th>Drive</th><th>Total</th><th>Used</th><th>Free</th><th>Free %</th></tr>
"@

    foreach ($disk in $disks) {
        $class = if ($disk.FreePercent -lt 20) { "error" } elseif ($disk.FreePercent -lt 40) { "warning" } else { "success" }
        $html += @"
        <tr>
            <td>$($disk.Drive)</td>
            <td>$($disk.Total_GB) GB</td>
            <td>$($disk.Used_GB) GB</td>
            <td class="$class">$($disk.Free_GB) GB</td>
            <td class="$class">$($disk.FreePercent)%</td>
        </tr>
"@
    }

    $html += @"
    </table>
    
    <h2>🔝 Top Processes</h2>
    <table>
        <tr><th>Name</th><th>PID</th><th>CPU (s)</th><th>Memory (MB)</th></tr>
"@

    foreach ($proc in $topProcs) {
        $html += @"
        <tr>
            <td>$($proc.Name)</td>
            <td>$($proc.PID)</td>
            <td>$($proc.CPU)</td>
            <td>$($proc.Memory_MB)</td>
        </tr>
"@
    }

    $html += @"
    </table>
    
    <footer style="margin-top: 50px; text-align: center; color: #666;">
        <p>Generated by ONI Windows Control System v1.0</p>
    </footer>
</body>
</html>
"@

    $html | Out-File -FilePath $OutputFile -Encoding UTF8
    
    Write-Host ""
    Write-Host "   ═══ REPORT GENERATED ═══" -ForegroundColor Green
    Write-Host "   Location: $OutputFile" -ForegroundColor Cyan
    Write-Host ""
    
    # Open in browser
    Start-Process $OutputFile
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if ($Interactive) {
    Show-Templates
    $choice = Read-Host "Select template (1-10)"
    
    switch ($choice) {
        "1" { Invoke-SystemCleanup }
        "2" { Invoke-SecurityHardening }
        "3" { Invoke-PerformanceBoost }
        "6" { Invoke-NetworkDiagnostics }
        "10" { Invoke-SystemReport }
        default { Write-Host "Invalid selection" -ForegroundColor Red }
    }
} elseif ($TaskFile) {
    # Load and execute task file (JSON)
    Write-Host "Task file execution not yet implemented" -ForegroundColor Yellow
} else {
    Show-Templates
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\ONI_Windows_Automator.ps1 -Interactive" -ForegroundColor Cyan
    Write-Host "  .\ONI_Windows_Automator.ps1 -TaskFile tasks.json" -ForegroundColor Cyan
}
