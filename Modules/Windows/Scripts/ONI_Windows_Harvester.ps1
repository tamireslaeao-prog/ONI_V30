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
# ONI WINDOWS DEEP HARVESTER v1.0 - Complete System Analyzer
# Description: Deep scan of Windows system state, config, and resources
# ============================================================================

param(
    [string]$OutputFile,
    [switch]$IncludeInstalledApps = $true,
    [switch]$IncludeStartupPrograms = $true,
    [switch]$IncludeDrivers = $true,
    [switch]$IncludeNetworkConfig = $true,
    [switch]$IncludeFirewallRules = $false,  # Can be slow
    [switch]$IncludeEventLogs = $false       # Can be slow
)

if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "system_db.json"
}

Write-Host "[WINDOWS HARVESTER v1.0] Starting deep system scan..." -ForegroundColor Cyan

$harvestData = @{
    harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    system       = @{}
    hardware     = @{}
    software     = @{}
    network      = @{}
    security     = @{}
    performance  = @{}
    statistics   = @{}
}

# ============================================================================
# STEP 1: System Information
# ============================================================================
Write-Host ""
Write-Host "[STEP 1] Harvesting System Information..." -ForegroundColor Yellow

$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem

$harvestData.system = @{
    computer_name      = $env:COMPUTERNAME
    username           = $env:USERNAME
    domain             = $env:USERDOMAIN
    os_name            = $os.Caption
    os_version         = $os.Version
    os_build           = $os.BuildNumber
    os_architecture    = $os.OSArchitecture
    install_date       = $os.InstallDate
    last_boot          = $os.LastBootUpTime
    uptime_hours       = [math]::Round((New-TimeSpan -Start $os.LastBootUpTime -End (Get-Date)).TotalHours, 2)
    system_directory   = $env:SystemRoot
    windows_directory  = $env:windir
    temp_directory     = $env:TEMP
    manufacturer       = $cs.Manufacturer
    model              = $cs.Model
    system_type        = $cs.SystemType
    hypervisor_present = $cs.HypervisorPresent
}

Write-Host "   Computer: $($harvestData.system.computer_name)" -ForegroundColor Green
Write-Host "   OS: $($harvestData.system.os_name)" -ForegroundColor Green
Write-Host "   Build: $($harvestData.system.os_build)" -ForegroundColor Green
Write-Host "   Uptime: $($harvestData.system.uptime_hours) hours" -ForegroundColor Green

# ============================================================================
# STEP 2: Hardware Information
# ============================================================================
Write-Host ""
Write-Host "[STEP 2] Harvesting Hardware Information..." -ForegroundColor Yellow

# CPU
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$harvestData.hardware.cpu = @{
    name                    = $cpu.Name
    manufacturer            = $cpu.Manufacturer
    cores                   = $cpu.NumberOfCores
    logical_processors      = $cpu.NumberOfLogicalProcessors
    max_clock_speed_mhz     = $cpu.MaxClockSpeed
    current_clock_speed_mhz = $cpu.CurrentClockSpeed
    architecture            = $cpu.Architecture
    l2_cache_kb             = $cpu.L2CacheSize
    l3_cache_kb             = $cpu.L3CacheSize
}

Write-Host "   CPU: $($cpu.Name)" -ForegroundColor Gray
Write-Host "      Cores: $($cpu.NumberOfCores) | Threads: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor Gray

# Memory
$totalRAM = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
$freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB / 1024, 2)
$usedRAM = $totalRAM - $freeRAM

$harvestData.hardware.memory = @{
    total_gb     = $totalRAM
    free_gb      = $freeRAM
    used_gb      = $usedRAM
    used_percent = [math]::Round(($usedRAM / $totalRAM) * 100, 2)
}

Write-Host "   RAM: ${usedRAM}GB / ${totalRAM}GB used" -ForegroundColor Gray

# Disks
$disks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
$harvestData.hardware.disks = @()

foreach ($disk in $disks) {
    $diskInfo = @{
        drive_letter = $disk.DeviceID
        volume_name  = $disk.VolumeName
        file_system  = $disk.FileSystem
        total_gb     = [math]::Round($disk.Size / 1GB, 2)
        free_gb      = [math]::Round($disk.FreeSpace / 1GB, 2)
        used_gb      = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 2)
        free_percent = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 2)
    }
    
    $harvestData.hardware.disks += $diskInfo
    Write-Host "   DISK $($disk.DeviceID): $($diskInfo.free_gb)GB free ($($diskInfo.free_percent)%)" -ForegroundColor Gray
}

# Graphics Cards
$gpus = Get-CimInstance Win32_VideoController
$harvestData.hardware.graphics = @()

foreach ($gpu in $gpus) {
    $harvestData.hardware.graphics += @{
        name               = $gpu.Name
        driver_version     = $gpu.DriverVersion
        video_memory_mb    = [math]::Round($gpu.AdapterRAM / 1MB, 2)
        current_resolution = "$($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution)"
        refresh_rate       = $gpu.CurrentRefreshRate
    }
    
    Write-Host "   GPU: $($gpu.Name)" -ForegroundColor Gray
}

# ============================================================================
# STEP 3: Installed Software
# ============================================================================
Write-Host ""
Write-Host "[STEP 3] Harvesting Installed Applications..." -ForegroundColor Yellow

if ($IncludeInstalledApps) {
    $regPaths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    
    $installedApps = @()
    
    foreach ($path in $regPaths) {
        $apps = Get-ItemProperty $path -ErrorAction SilentlyContinue | 
        Where-Object { $_.DisplayName } |
        Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation
        
        $installedApps += $apps
    }
    
    $harvestData.software.installed_applications = $installedApps | ForEach-Object {
        @{
            name             = $_.DisplayName
            version          = $_.DisplayVersion
            publisher        = $_.Publisher
            install_date     = $_.InstallDate
            install_location = $_.InstallLocation
        }
    } | Sort-Object name -Unique
    
    Write-Host "   Found $($harvestData.software.installed_applications.Count) applications" -ForegroundColor Green
    
    # Show top 10
    $harvestData.software.installed_applications | Select-Object -First 10 | ForEach-Object {
        Write-Host "      [APP] $($_.name)" -ForegroundColor Gray
    }
    
    if ($harvestData.software.installed_applications.Count -gt 10) {
        Write-Host "      ... and $($harvestData.software.installed_applications.Count - 10) more" -ForegroundColor DarkGray
    }
}

# ============================================================================
# STEP 4: Startup Programs
# ============================================================================
Write-Host ""
Write-Host "[STEP 4] Harvesting Startup Programs..." -ForegroundColor Yellow

if ($IncludeStartupPrograms) {
    $startupLocations = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
    )
    
    $startupPrograms = @()
    
    foreach ($location in $startupLocations) {
        if (Test-Path $location) {
            $items = Get-ItemProperty $location -ErrorAction SilentlyContinue
            
            $items.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                $startupPrograms += @{
                    name     = $_.Name
                    command  = $_.Value
                    location = $location
                }
            }
        }
    }
    
    # Add Startup folder items
    $startupFolders = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    
    foreach ($folder in $startupFolders) {
        if (Test-Path $folder) {
            Get-ChildItem $folder -File | ForEach-Object {
                $startupPrograms += @{
                    name     = $_.Name
                    command  = $_.FullName
                    location = $folder
                }
            }
        }
    }
    
    $harvestData.software.startup_programs = $startupPrograms
    
    Write-Host "   Found $($startupPrograms.Count) startup items" -ForegroundColor Green
    
    $startupPrograms | Select-Object -First 5 | ForEach-Object {
        Write-Host "      [STARTUP] $($_.name)" -ForegroundColor Cyan
    }
}

# ============================================================================
# STEP 5: Running Processes & Services
# ============================================================================
Write-Host ""
Write-Host "[STEP 5] Harvesting Processes & Services..." -ForegroundColor Yellow

# Top processes by CPU
$topProcesses = Get-Process | 
Where-Object { $_.CPU -gt 0 } |
Sort-Object CPU -Descending |
Select-Object -First 20

$harvestData.software.top_processes = $topProcesses | ForEach-Object {
    @{
        name        = $_.Name
        pid         = $_.Id
        cpu_seconds = [math]::Round($_.CPU, 2)
        memory_mb   = [math]::Round($_.WorkingSet64 / 1MB, 2)
        threads     = $_.Threads.Count
        handles     = $_.HandleCount
    }
}

Write-Host "   Top 5 processes by CPU:" -ForegroundColor Green
$topProcesses | Select-Object -First 5 | ForEach-Object {
    Write-Host "      [PROC] $($_.Name): $([math]::Round($_.CPU, 2))s CPU | $([math]::Round($_.WorkingSet64 / 1MB, 2))MB RAM" -ForegroundColor Gray
}

# Running services
$services = Get-Service | Where-Object { $_.Status -eq "Running" }
$harvestData.software.running_services = $services | ForEach-Object {
    @{
        name         = $_.Name
        display_name = $_.DisplayName
        status       = $_.Status.ToString()
        start_type   = $_.StartType.ToString()
    }
}

Write-Host "   Running services: $($services.Count)" -ForegroundColor Green

# ============================================================================
# STEP 6: Network Configuration
# ============================================================================
Write-Host ""
Write-Host "[STEP 6] Harvesting Network Configuration..." -ForegroundColor Yellow

if ($IncludeNetworkConfig) {
    # Network adapters
    $adapters = Get-NetAdapter
    $harvestData.network.adapters = $adapters | ForEach-Object {
        @{
            name        = $_.Name
            description = $_.InterfaceDescription
            status      = $_.Status
            link_speed  = $_.LinkSpeed
            mac_address = $_.MacAddress
        }
    }
    
    Write-Host "   Network adapters: $($adapters.Count)" -ForegroundColor Green
    
    # IP Configuration
    $ipConfigs = Get-NetIPConfiguration
    $harvestData.network.ip_configuration = $ipConfigs | ForEach-Object {
        @{
            interface       = $_.InterfaceAlias
            ipv4_address    = ($_.IPv4Address | Select-Object -First 1).IPAddress
            ipv6_address    = ($_.IPv6Address | Select-Object -First 1).IPAddress
            default_gateway = ($_.IPv4DefaultGateway | Select-Object -First 1).NextHop
            dns_servers     = $_.DNSServer.ServerAddresses
        }
    }
    
    # Open ports
    $openPorts = Get-NetTCPConnection | 
    Where-Object { $_.State -eq "Listen" } |
    Select-Object LocalAddress, LocalPort, State |
    Sort-Object LocalPort
    
    $harvestData.network.open_ports = $openPorts | ForEach-Object {
        @{
            address = $_.LocalAddress
            port    = $_.LocalPort
            state   = $_.State
        }
    }
    
    Write-Host "   Open ports: $($openPorts.Count)" -ForegroundColor Green
    
    # Public IP
    try {
        $publicIP = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5).Trim()
        $harvestData.network.public_ip = $publicIP
        Write-Host "   Public IP: $publicIP" -ForegroundColor Green
    }
    catch {
        $harvestData.network.public_ip = "Unknown"
    }
}

# ============================================================================
# STEP 7: Drivers
# ============================================================================
Write-Host ""
Write-Host "[STEP 7] Harvesting Device Drivers..." -ForegroundColor Yellow

if ($IncludeDrivers) {
    $drivers = Get-WindowsDriver -Online -All
    $harvestData.hardware.drivers = $drivers | ForEach-Object {
        @{
            driver             = $_.Driver
            original_file_name = $_.OriginalFileName
            provider_name      = $_.ProviderName
            class_name         = $_.ClassName
            driver_version     = $_.Version
            date               = $_.Date
        }
    } | Select-Object -First 100  # Limit to 100 most recent
    
    Write-Host "   Drivers cataloged: $($drivers.Count) (showing first 100)" -ForegroundColor Green
}

# ============================================================================
# STEP 8: Security & Firewall
# ============================================================================
Write-Host ""
Write-Host "[STEP 8] Harvesting Security Configuration..." -ForegroundColor Yellow

# Windows Defender status
try {
    $defender = Get-MpComputerStatus
    $harvestData.security.windows_defender = @{
        antivirus_enabled   = $defender.AntivirusEnabled
        realtime_protection = $defender.RealTimeProtectionEnabled
        behavior_monitor    = $defender.BehaviorMonitorEnabled
        signature_updated   = $defender.AntivirusSignatureLastUpdated
    }
    
    Write-Host "   Windows Defender: $(if ($defender.RealTimeProtectionEnabled) { 'Enabled' } else { 'Disabled' })" -ForegroundColor $(if ($defender.RealTimeProtectionEnabled) { 'Green' } else { 'Red' })
}
catch {
    $harvestData.security.windows_defender = "Not available"
}

# Firewall status
$firewallProfiles = Get-NetFirewallProfile
$harvestData.security.firewall = $firewallProfiles | ForEach-Object {
    @{
        profile          = $_.Name
        enabled          = $_.Enabled
        default_inbound  = $_.DefaultInboundAction
        default_outbound = $_.DefaultOutboundAction
    }
}

Write-Host "   Firewall profiles:" -ForegroundColor Green
$firewallProfiles | ForEach-Object {
    Write-Host "      $($_.Name): $(if ($_.Enabled) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Gray
}

# ============================================================================
# STEP 9: Performance Metrics
# ============================================================================
Write-Host ""
Write-Host "[STEP 9] Collecting Performance Metrics..." -ForegroundColor Yellow

$harvestData.performance = @{
    cpu           = $harvestData.hardware.cpu
    memory        = $harvestData.hardware.memory
    disks         = $harvestData.hardware.disks
    top_processes = $harvestData.software.top_processes | Select-Object -First 10
}

# ============================================================================
# STEP 10: Statistics
# ============================================================================
Write-Host ""
Write-Host "[STEP 10] Calculating Statistics..." -ForegroundColor Yellow

$harvestData.statistics = @{
    installed_applications = $harvestData.software.installed_applications.Count
    startup_programs       = $harvestData.software.startup_programs.Count
    running_processes      = (Get-Process).Count
    running_services       = $harvestData.software.running_services.Count
    network_adapters       = $harvestData.network.adapters.Count
    open_ports             = $harvestData.network.open_ports.Count
    total_disk_space_gb    = ($harvestData.hardware.disks | Measure-Object -Property total_gb -Sum).Sum
    total_free_space_gb    = ($harvestData.hardware.disks | Measure-Object -Property free_gb -Sum).Sum
}

Write-Host "   Statistics:" -ForegroundColor White
Write-Host "      Applications: $($harvestData.statistics.installed_applications)" -ForegroundColor Gray
Write-Host "      Startup Items: $($harvestData.statistics.startup_programs)" -ForegroundColor Gray
Write-Host "      Running Processes: $($harvestData.statistics.running_processes)" -ForegroundColor Gray
Write-Host "      Running Services: $($harvestData.statistics.running_services)" -ForegroundColor Gray
Write-Host "      Open Ports: $($harvestData.statistics.open_ports)" -ForegroundColor Gray

# ============================================================================
# STEP 11: Save to JSON
# ============================================================================
Write-Host ""
Write-Host "[STEP 11] Saving to Database..." -ForegroundColor Yellow

$outputDir = Split-Path $OutputFile -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$harvestData | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

$fileSizeMB = [math]::Round((Get-Item $OutputFile).Length / 1MB, 2)
Write-Host "   ✓ Saved to: $OutputFile ($fileSizeMB MB)" -ForegroundColor Green

# ============================================================================
# COMPLETE
# ============================================================================
Write-Host ""
Write-Host "[COMPLETE] Windows harvest finished" -ForegroundColor Cyan
Write-Host "   Computer: $($harvestData.system.computer_name)" -ForegroundColor White
Write-Host "   OS: $($harvestData.system.os_name)" -ForegroundColor White
Write-Host "   Applications: $($harvestData.statistics.installed_applications)" -ForegroundColor White
Write-Host "   Processes: $($harvestData.statistics.running_processes)" -ForegroundColor White
Write-Host "   Output: $OutputFile" -ForegroundColor Gray
