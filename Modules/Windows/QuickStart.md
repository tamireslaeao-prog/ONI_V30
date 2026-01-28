# 🪟 ONI WINDOWS CONTROL SYSTEM
> **Version:** 1.0  
> **Status:** PRODUCTION READY

---

## 🌟 OVERVIEW
Complete automation framework for Windows 10/11 with real-time system monitoring, performance optimization, security hardening, and bulk automation capabilities.

**Key Difference:** Unlike other ONI systems, Windows doesn't need a "Harvester" because system state is queried in real-time via native APIs. Focus is on **control and automation**, not state cataloging.

---

## 📂 SYSTEM ARCHITECTURE

```
C:\ONI\Windows\
├── oni_lib_windows.ps1          # Core PowerShell Library
├── ONI_Windows_Sentinel.ps1     # Real-time system monitor
├── ONI_Windows_Automator.ps1    # Bulk automation engine
├── oni_operations.log           # Operation log
├── sentinel_log.txt             # Monitoring log
└── Tasks\
    ├── cleanup_tasks.json
    ├── security_tasks.json
    └── custom_tasks.json
```

---

## 🚀 QUICK START

### 1. Import ONI Library

```powershell
Import-Module .\oni_lib_windows.ps1
```

### 2. Verify System Access

```powershell
# Check system info
$info = & $ONI.Core.GetSystemInfo
$info

# Check if running as admin
$isAdmin = & $ONI.Core.IsAdmin
Write-Host "Admin: $isAdmin"
```

### 3. Start Real-Time Monitor

```powershell
.\ONI_Windows_Sentinel.ps1 -PollInterval 5 -CPUThreshold 90
```

### 4. Run Automation Templates

```powershell
.\ONI_Windows_Automator.ps1 -Interactive
```

---

## 💻 CORE LIBRARY USAGE

### System Information

```powershell
# Get complete system info
$info = & $ONI.Core.GetSystemInfo

# Result:
# ComputerName    : DESKTOP-ABC123
# UserName        : John
# OS              : Microsoft Windows 11 Pro
# Version         : 10.0.22621
# Build           : 22621
# Architecture    : AMD64
# Memory_GB       : 16
# Processors      : 8
```

### Process Management

```powershell
# List all processes
$processes = & $ONI.Process.List

# Kill specific process
& $ONI.Process.Kill "chrome" -Force

# Start process
& $ONI.Process.Start "notepad.exe"

# Start as admin
& $ONI.Process.Start "powershell.exe" -AsAdmin

# Find process using port
$procs = & $ONI.Process.GetByPort 8080
$procs | Format-Table

# Monitor process in real-time
& $ONI.Process.Monitor "code" -Interval 3
```

### Service Management

```powershell
# List all services
$services = & $ONI.Service.List

# Get service status
$status = & $ONI.Service.GetStatus "wuauserv"

# Start service
& $ONI.Service.Start "wuauserv"

# Stop service
& $ONI.Service.Stop "wuauserv"

# Restart service
& $ONI.Service.Restart "wuauserv"

# Set startup type
& $ONI.Service.SetStartup "wuauserv" "Automatic"
```

### File System Operations

```powershell
# Search files
$files = & $ONI.FileSystem.Search "C:\Projects" "*.ps1" -Recurse

# Copy files
& $ONI.FileSystem.Copy "C:\Source\file.txt" "D:\Backup\" -Force

# Delete files
& $ONI.FileSystem.Delete "C:\Temp\old.txt" -Force

# Get folder size
$size = & $ONI.FileSystem.GetSize "C:\Users\John\Documents"
Write-Host "Size: $($size.GB) GB"

# Find duplicates
$duplicates = & $ONI.FileSystem.FindDuplicates "C:\Downloads"
$duplicates | ForEach-Object {
    Write-Host "Original: $($_.Original)"
    Write-Host "Duplicate: $($_.Duplicate)"
    Write-Host "Size: $($_.Size) bytes"
    Write-Host ""
}

# Clean temp files
$result = & $ONI.FileSystem.CleanTemp
Write-Host "Cleaned: $($result.TotalCleanedMB) MB"
```

### Registry Operations

```powershell
# Read registry value
$value = & $ONI.Registry.Get "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion" "ProgramFilesDir"

# Write registry value
& $ONI.Registry.Set "HKCU:\Software\MyApp" "Version" "1.0.0" "String"

# Delete registry value
& $ONI.Registry.Delete "HKCU:\Software\OldApp" "Setting"

# Export registry key
& $ONI.Registry.Export "HKCU:\Software\MyApp" "C:\Backup\myapp.reg"

# Import registry file
& $ONI.Registry.Import "C:\Backup\myapp.reg"
```

### Network Operations

```powershell
# Get network adapters
$adapters = & $ONI.Network.GetAdapters

# Get IP configuration
$ipConfig = & $ONI.Network.GetIPConfig

# Ping host
$result = & $ONI.Network.Ping "google.com" 4

# Get open ports
$ports = & $ONI.Network.GetOpenPorts

# Flush DNS
& $ONI.Network.FlushDNS

# Renew IP (requires admin)
& $ONI.Network.RenewIP

# Get public IP
$publicIP = & $ONI.Network.GetPublicIP
Write-Host "Your IP: $publicIP"

# Test if port is open
$open = & $ONI.Network.TestPort "google.com" 443
Write-Host "Port 443 open: $open"
```

### Performance Monitoring

```powershell
# Get CPU info
$cpu = & $ONI.Performance.GetCPU

# Get memory info
$mem = & $ONI.Performance.GetMemory
Write-Host "RAM: $($mem.Used_GB)GB / $($mem.Total_GB)GB ($($mem.UsedPercent)%)"

# Get disk info
$disks = & $ONI.Performance.GetDisk
$disks | Format-Table

# Get top processes
$top = & $ONI.Performance.GetTopProcesses -Count 10 -SortBy "CPU"

# Real-time system monitor
& $ONI.Performance.Monitor -Interval 2 -Duration 60
```

### Scheduled Tasks

```powershell
# Create daily task
& $ONI.Task.Create "DailyBackup" "C:\Scripts\backup.ps1" -Trigger "Daily" -Time "02:00"

# Create startup task
& $ONI.Task.Create "MonitorStartup" "C:\Scripts\monitor.ps1" -Trigger "Startup"

# List tasks
$tasks = & $ONI.Task.List

# Run task manually
& $ONI.Task.Run "DailyBackup"

# Delete task
& $ONI.Task.Delete "OldTask"
```

### Windows Features

```powershell
# List all features
$features = & $ONI.Features.List

# Enable feature
& $ONI.Features.Enable "TelnetClient"

# Disable feature
& $ONI.Features.Disable "Internet-Explorer-Optional-amd64"
```

---

## 👁️ REAL-TIME SENTINEL

### Start Monitoring

```powershell
# Basic monitoring
.\ONI_Windows_Sentinel.ps1

# Custom thresholds
.\ONI_Windows_Sentinel.ps1 -CPUThreshold 85 -MemoryThreshold 80 -DiskThreshold 95

# Selective monitoring
.\ONI_Windows_Sentinel.ps1 -MonitorProcesses -MonitorNetwork
```

### What It Monitors

**System Resources:**
- 🔥 CPU usage alerts
- 💾 Memory usage alerts
- 💿 Disk space alerts

**Process Activity:**
- ✨ New processes started
- ❌ Processes terminated
- 📊 Resource-intensive processes

**Network Activity:**
- 🔗 New network connections
- 📡 Connection states
- 🌐 Remote addresses

**Security Events:**
- 🛡️ Windows Defender status
- 🔥 Firewall status changes
- ⚠️ Security alerts

### Alert Examples

```
[2026-01-05 14:32:15] ⚠️ ALERT: CPU usage at 92% (threshold: 90%)
[2026-01-05 14:32:15]    Top process: chrome.exe - 145.23s

[2026-01-05 14:35:42] 🆕 NEW PROCESS: code.exe (PID: 12345)

[2026-01-05 14:40:18] 🔗 NEW CONNECTION: chrome.exe -> 142.250.185.46:443

[2026-01-05 14:45:00] ⚠️ SECURITY ALERT: Windows Defender Real-Time Protection is DISABLED
```

---

## 🤖 AUTOMATION TEMPLATES

### Interactive Mode

```powershell
.\ONI_Windows_Automator.ps1 -Interactive

# Available Templates:
#   1. System Cleanup
#   2. Security Hardening
#   3. Performance Boost
#   4. Development Setup
#   5. Backup Manager
#   6. Network Diagnostics
#   7. Process Killer
#   8. Service Manager
#   9. Schedule Tasks
#   10. System Report
```

### Template Details

#### 1. System Cleanup
```powershell
# What it does:
- Cleans temp files
- Empties Recycle Bin
- Clears DNS cache
- Runs Disk Cleanup
- Defragments drives (HDD only)

# Typical savings: 2-10 GB
```

#### 2. Security Hardening
```powershell
# What it does:
- Enables Windows Defender
- Enables Firewall (all profiles)
- Disables SMBv1
- Enables UAC
- Configures Windows Update
- Updates Defender signatures

# Requires: Administrator
```

#### 3. Performance Boost
```powershell
# What it does:
- Disables unnecessary services
- Disables visual effects
- Sets High Performance power plan
- Disables Windows animations
- Disables Cortana
- Optimizes paging file
- Clears prefetch

# Requires: Administrator
# Warning: Restart required
```

#### 6. Network Diagnostics
```powershell
# What it does:
- Tests internet connectivity
- Gets public IP
- Tests DNS resolution
- Checks network adapters
- Scans open ports
- Tests common ports
- Runs traceroute
- Checks network speed

# Output: Comprehensive network report
```

#### 10. System Report
```powershell
# What it does:
- Generates HTML report with:
  • System overview
  • CPU & Memory stats
  • Disk space analysis
  • Top processes
  • Formatted dashboard

# Automatically opens in browser
```

---

## 🎯 REAL-WORLD USE CASES

### 1. Automated System Maintenance

```powershell
# Create scheduled task for weekly cleanup
& $ONI.Task.Create "WeeklyMaintenance" "C:\ONI\Windows\ONI_Windows_Automator.ps1" -Trigger "Weekly" -Time "03:00"

# Script executes:
# - System cleanup
# - Disk optimization
# - Temp file removal
# - Recycle Bin empty
```

### 2. Development Environment Setup

```powershell
# Install development tools
& $ONI.Features.Enable "Microsoft-Windows-Subsystem-Linux"
& $ONI.Features.Enable "VirtualMachinePlatform"

# Configure services
& $ONI.Service.Start "Docker"
& $ONI.Service.SetStartup "Docker" "Automatic"

# Setup development folders
New-Item "C:\Dev\Projects" -ItemType Directory -Force
New-Item "C:\Dev\Tools" -ItemType Directory -Force
```

### 3. Security Audit Script

```powershell
# Check security posture
$defender = Get-MpComputerStatus
$firewall = Get-NetFirewallProfile

$securityReport = @{
    DefenderEnabled = $defender.RealTimeProtectionEnabled
    FirewallEnabled = ($firewall | Where-Object { -not $_.Enabled }).Count -eq 0
    UpdatesPending = (Get-WindowsUpdate -ErrorAction SilentlyContinue).Count
}

if (-not $securityReport.DefenderEnabled) {
    Write-Host "⚠️ CRITICAL: Defender is disabled!" -ForegroundColor Red
}
```

### 4. Performance Monitoring Dashboard

```powershell
# Real-time dashboard
while ($true) {
    Clear-Host
    
    $cpu = & $ONI.Performance.GetCPU
    $mem = & $ONI.Performance.GetMemory
    $top = & $ONI.Performance.GetTopProcesses -Count 5
    
    Write-Host "═══ SYSTEM DASHBOARD ═══" -ForegroundColor Cyan
    Write-Host "CPU: $($cpu.LoadPercentage)%" -ForegroundColor $(if ($cpu.LoadPercentage -gt 80) { "Red" } else { "Green" })
    Write-Host "RAM: $($mem.UsedPercent)%" -ForegroundColor $(if ($mem.UsedPercent -gt 80) { "Red" } else { "Green" })
    Write-Host ""
    Write-Host "Top Processes:" -ForegroundColor Yellow
    $top | Format-Table Name, CPU, Memory_MB -AutoSize
    
    Start-Sleep -Seconds 2
}
```

### 5. Network Monitoring Script

```powershell
# Monitor specific ports
$portsToMonitor = @(80, 443, 3389, 8080)

while ($true) {
    foreach ($port in $portsToMonitor) {
        $processes = & $ONI.Process.GetByPort $port
        
        if ($processes) {
            Write-Host "[ACTIVE] Port $port : $($processes[0].Name)" -ForegroundColor Green
        } else {
            Write-Host "[CLOSED] Port $port" -ForegroundColor Gray
        }
    }
    
    Start-Sleep -Seconds 10
}
```

### 6. Automated Backup System

```powershell
# Backup critical directories
$backupPaths = @(
    "$env:USERPROFILE\Documents",
    "$env:USERPROFILE\Desktop",
    "C:\Projects"
)

$backupDestination = "D:\Backups\$(Get-Date -Format 'yyyy-MM-dd')"
New-Item $backupDestination -ItemType Directory -Force

foreach ($path in $backupPaths) {
    if (Test-Path $path) {
        $folderName = Split-Path $path -Leaf
        & $ONI.FileSystem.Copy $path "$backupDestination\$folderName" -Recurse -Force
        Write-Host "✓ Backed up: $path" -ForegroundColor Green
    }
}
```

---

## ⚡ ADVANCED FEATURES

### Batch Process Management

```powershell
# Kill multiple processes at once
$processesToKill = @("chrome", "firefox", "msedge", "spotify")

foreach ($proc in $processesToKill) {
    & $ONI.Process.Kill $proc -Force
}
```

### Service Batch Operations

```powershell
# Stop multiple services
$servicesToStop = @("Spooler", "WSearch", "SysMain")

foreach ($svc in $servicesToStop) {
    & $ONI.Service.Stop $svc
}
```

### Custom Automation Pipeline

```powershell
# Create custom automation workflow
function Invoke-CustomWorkflow {
    # Step 1: Cleanup
    & $ONI.FileSystem.CleanTemp
    
    # Step 2: Stop unnecessary processes
    & $ONI.Process.Kill "spotify"
    
    # Step 3: Restart critical services
    & $ONI.Service.Restart "Spooler"
    
    # Step 4: Network flush
    & $ONI.Network.FlushDNS
    
    # Step 5: Generate report
    $report = @{
        Timestamp = Get-Date
        CPU = (& $ONI.Performance.GetCPU).LoadPercentage
        Memory = (& $ONI.Performance.GetMemory).UsedPercent
    }
    
    $report | ConvertTo-Json | Out-File "C:\ONI\Windows\workflow_log.json" -Append
}

# Schedule it
& $ONI.Task.Create "CustomWorkflow" "C:\Scripts\workflow.ps1" -Trigger "Daily" -Time "08:00"
```

---

## 🛡️ SECURITY & PERMISSIONS

### Administrator Requirements

Some operations require elevated privileges:
- Service management
- Registry modifications (HKLM)
- Windows Features
- Network configuration
- Security settings

### Check and Request Admin

```powershell
# Check if admin
if (-not (& $ONI.Core.IsAdmin)) {
    Write-Host "This operation requires Administrator privileges" -ForegroundColor Red
    
    # Restart as admin
    Start-Process PowerShell -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
    exit
}
```

---

## 🚨 TROUBLESHOOTING

### "Access Denied" Errors
```
Solution: Run PowerShell as Administrator
Fix: Right-click PowerShell → Run as Administrator
```

### "Execution Policy" Error
```
Solution: Enable script execution
Fix: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Sentinel Not Starting
```
Solution: Check log file permissions
Fix: New-Item "C:\ONI\Windows" -ItemType Directory -Force
```

### Library Import Fails
```
Solution: Ensure oni_lib_windows.ps1 is in same directory
Fix: Import-Module .\oni_lib_windows.ps1 -Force
```

---

## 📚 ADDITIONAL RESOURCES

- **PowerShell Docs:** https://docs.microsoft.com/powershell
- **WMI/CIM Classes:** https://docs.microsoft.com/windows/win32/wmisdk
- **ONI Support:** (Your internal channel)

---

## 🎉 READY TO USE!

```powershell
# 1. Import library
Import-Module .\oni_lib_windows.ps1

# 2. Start monitoring
Start-Process PowerShell -ArgumentList "-File .\ONI_Windows_Sentinel.ps1"

# 3. Run automation
.\ONI_Windows_Automator.ps1 -Interactive

# 4. Check logs
Get-Content C:\ONI\Windows\sentinel_log.txt -Tail 20
```

**System Status:** ✅ OPERATIONAL  
**Version:** 1.0  
**Platform:** Windows 10/11  
**Last Updated:** January 2026