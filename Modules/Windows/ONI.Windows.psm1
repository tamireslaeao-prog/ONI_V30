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
# ONI CORE LIBRARY - WINDOWS AUTOMATION
# Version: 1.0 (Total System Control)
# 
# Standardized High-Level Functions for Windows Management & Automation.
# Usage: Import-Module .\oni_lib_windows.ps1
# ============================================================================

$ONI = @{}

# ============================================================================
# MODULE: CORE UTILITIES
# ============================================================================
$ONI.Core = @{
    Version           = "1.0.0"
    LogFile           = "C:\ONI\Windows\oni_operations.log"
    
    Log               = {
        param([string]$Message, [string]$Level = "INFO")
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logEntry = "$timestamp | $Level | $Message"
        
        $color = switch ($Level) {
            "SUCCESS" { "Green" }
            "WARNING" { "Yellow" }
            "ERROR" { "Red" }
            "INFO" { "Gray" }
            default { "White" }
        }
        
        Write-Host $logEntry -ForegroundColor $color
        
        if ($ONI.Core.LogFile) {
            $logEntry | Out-File -FilePath $ONI.Core.LogFile -Append -ErrorAction SilentlyContinue
        }
    }
    
    IsAdmin           = {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    
    RequireAdmin      = {
        if (-not (& $ONI.Core.IsAdmin)) {
            throw "This operation requires Administrator privileges"
        }
    }
    
    GetWindowsVersion = {
        return [System.Environment]::OSVersion.Version
    }
    
    GetSystemInfo     = {
        return @{
            ComputerName = $env:COMPUTERNAME
            UserName     = $env:USERNAME
            OS           = (Get-CimInstance Win32_OperatingSystem).Caption
            Version      = (Get-CimInstance Win32_OperatingSystem).Version
            Build        = (Get-CimInstance Win32_OperatingSystem).BuildNumber
            Architecture = $env:PROCESSOR_ARCHITECTURE
            Memory_GB    = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            Processors   = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
        }
    }
}

# ============================================================================
# MODULE: PROCESS MANAGEMENT
# ============================================================================
$ONI.Process = @{
    List      = {
        param([string]$Name = "*")
        return Get-Process -Name $Name -ErrorAction SilentlyContinue
    }
    
    Kill      = {
        param([string]$Name, [switch]$Force)
        & $ONI.Core.Log "Killing process: $Name"
        
        if ($Force) {
            Stop-Process -Name $Name -Force -ErrorAction SilentlyContinue
        }
        else {
            Stop-Process -Name $Name -ErrorAction SilentlyContinue
        }
    }
    
    Start     = {
        param(
            [string]$Path,
            [string]$Arguments = "",
            [switch]$AsAdmin,
            [switch]$Hidden
        )
        
        $startParams = @{
            FilePath = $Path
        }
        
        if ($Arguments) { $startParams.ArgumentList = $Arguments }
        if ($AsAdmin) { $startParams.Verb = "RunAs" }
        if ($Hidden) { $startParams.WindowStyle = "Hidden" }
        
        & $ONI.Core.Log "Starting process: $Path"
        return Start-Process @startParams -PassThru
    }
    
    GetByPort = {
        param([int]$Port)
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        $processes = @()
        
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                $processes += @{
                    Name  = $process.Name
                    PID   = $process.Id
                    Port  = $Port
                    State = $conn.State
                }
            }
        }
        
        return $processes
    }
    
    Monitor   = {
        param([string]$ProcessName, [int]$Interval = 5)
        
        & $ONI.Core.Log "Monitoring process: $ProcessName (${Interval}s interval)"
        
        while ($true) {
            $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
            
            if ($process) {
                $cpu = [math]::Round($process.CPU, 2)
                $memory_mb = [math]::Round($process.WorkingSet64 / 1MB, 2)
                
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $ProcessName - CPU: ${cpu}s | RAM: ${memory_mb}MB" -ForegroundColor Cyan
            }
            else {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $ProcessName - NOT RUNNING" -ForegroundColor Red
            }
            
            Start-Sleep -Seconds $Interval
        }
    }
}

# ============================================================================
# MODULE: SERVICE MANAGEMENT
# ============================================================================
$ONI.Service = @{
    List       = {
        param([string]$Name = "*")
        return Get-Service -Name $Name -ErrorAction SilentlyContinue
    }
    
    Start      = {
        param([string]$Name)
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Starting service: $Name"
        Start-Service -Name $Name -ErrorAction Stop
    }
    
    Stop       = {
        param([string]$Name)
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Stopping service: $Name"
        Stop-Service -Name $Name -Force -ErrorAction Stop
    }
    
    Restart    = {
        param([string]$Name)
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Restarting service: $Name"
        Restart-Service -Name $Name -Force -ErrorAction Stop
    }
    
    GetStatus  = {
        param([string]$Name)
        $service = Get-Service -Name $Name -ErrorAction SilentlyContinue
        
        if ($service) {
            return @{
                Name        = $service.Name
                DisplayName = $service.DisplayName
                Status      = $service.Status
                StartType   = $service.StartType
            }
        }
        
        return $null
    }
    
    SetStartup = {
        param(
            [string]$Name,
            [ValidateSet("Automatic", "Manual", "Disabled")]
            [string]$StartType
        )
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Setting $Name startup type to: $StartType"
        Set-Service -Name $Name -StartupType $StartType
    }
}

# ============================================================================
# MODULE: FILE SYSTEM OPERATIONS
# ============================================================================
$ONI.FileSystem = @{
    Search         = {
        param(
            [string]$Path,
            [string]$Pattern = "*",
            [switch]$Recurse,
            [switch]$FilesOnly,
            [switch]$FoldersOnly
        )
        
        $params = @{
            Path        = $Path
            Filter      = $Pattern
            ErrorAction = "SilentlyContinue"
        }
        
        if ($Recurse) { $params.Recurse = $true }
        if ($FilesOnly) { $params.File = $true }
        if ($FoldersOnly) { $params.Directory = $true }
        
        return Get-ChildItem @params
    }
    
    Copy           = {
        param(
            [string]$Source,
            [string]$Destination,
            [switch]$Force,
            [switch]$Recurse
        )
        
        & $ONI.Core.Log "Copying: $Source -> $Destination"
        
        $params = @{
            Path        = $Source
            Destination = $Destination
            ErrorAction = "Stop"
        }
        
        if ($Force) { $params.Force = $true }
        if ($Recurse) { $params.Recurse = $true }
        
        Copy-Item @params
    }
    
    Delete         = {
        param(
            [string]$Path,
            [switch]$Force,
            [switch]$Recurse
        )
        
        & $ONI.Core.Log "Deleting: $Path" "WARNING"
        
        $params = @{
            Path        = $Path
            ErrorAction = "Stop"
        }
        
        if ($Force) { $params.Force = $true }
        if ($Recurse) { $params.Recurse = $true }
        
        Remove-Item @params
    }
    
    GetSize        = {
        param([string]$Path)
        
        if (Test-Path $Path -PathType Container) {
            $size = (Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum
        }
        else {
            $size = (Get-Item $Path -ErrorAction SilentlyContinue).Length
        }
        
        return @{
            Bytes = $size
            KB    = [math]::Round($size / 1KB, 2)
            MB    = [math]::Round($size / 1MB, 2)
            GB    = [math]::Round($size / 1GB, 2)
        }
    }
    
    FindDuplicates = {
        param([string]$Path)
        
        & $ONI.Core.Log "Searching for duplicates in: $Path"
        
        $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
        $hashes = @{}
        $duplicates = @()
        
        foreach ($file in $files) {
            $hash = (Get-FileHash -Path $file.FullName -Algorithm MD5).Hash
            
            if ($hashes.ContainsKey($hash)) {
                $duplicates += @{
                    Original  = $hashes[$hash]
                    Duplicate = $file.FullName
                    Size      = $file.Length
                }
            }
            else {
                $hashes[$hash] = $file.FullName
            }
        }
        
        return $duplicates
    }
    
    CleanTemp      = {
        & $ONI.Core.Log "Cleaning temporary files"
        
        $tempPaths = @(
            $env:TEMP,
            "C:\Windows\Temp",
            "C:\Windows\Prefetch"
        )
        
        $totalCleaned = 0
        
        foreach ($path in $tempPaths) {
            if (Test-Path $path) {
                $before = (& $ONI.FileSystem.GetSize $path).MB
                
                Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue | 
                Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
                
                $after = (& $ONI.FileSystem.GetSize $path).MB
                $cleaned = $before - $after
                $totalCleaned += $cleaned
                
                & $ONI.Core.Log "Cleaned $path`: $($cleaned)MB" "SUCCESS"
            }
        }
        
        return @{
            TotalCleanedMB = [math]::Round($totalCleaned, 2)
        }
    }
}

# ============================================================================
# MODULE: REGISTRY OPERATIONS
# ============================================================================
$ONI.Registry = @{
    Get    = {
        param([string]$Path, [string]$Name)
        
        try {
            return Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop | 
            Select-Object -ExpandProperty $Name
        }
        catch {
            return $null
        }
    }
    
    Set    = {
        param(
            [string]$Path,
            [string]$Name,
            $Value,
            [string]$Type = "String"
        )
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Setting registry: $Path\$Name = $Value"
        
        if (-not (Test-Path $Path)) {
            New-Item -Path $Path -Force | Out-Null
        }
        
        Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type $Type
    }
    
    Delete = {
        param([string]$Path, [string]$Name)
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Deleting registry: $Path\$Name" "WARNING"
        
        Remove-ItemProperty -Path $Path -Name $Name -ErrorAction SilentlyContinue
    }
    
    Export = {
        param([string]$Path, [string]$OutputFile)
        
        & $ONI.Core.Log "Exporting registry: $Path -> $OutputFile"
        reg export $Path $OutputFile /y
    }
    
    Import = {
        param([string]$File)
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Importing registry: $File"
        reg import $File
    }
}

# ============================================================================
# MODULE: NETWORK OPERATIONS
# ============================================================================
$ONI.Network = @{
    GetAdapters  = {
        return Get-NetAdapter | Select-Object Name, Status, LinkSpeed, MacAddress
    }
    
    GetIPConfig  = {
        return Get-NetIPConfiguration
    }
    
    Ping         = {
        param([string]$Target, [int]$Count = 4)
        
        return Test-Connection -ComputerName $Target -Count $Count -ErrorAction SilentlyContinue
    }
    
    GetOpenPorts = {
        return Get-NetTCPConnection | 
        Where-Object { $_.State -eq "Listen" } |
        Select-Object LocalAddress, LocalPort, State |
        Sort-Object LocalPort
    }
    
    FlushDNS     = {
        & $ONI.Core.Log "Flushing DNS cache"
        Clear-DnsClientCache
        ipconfig /flushdns | Out-Null
    }
    
    RenewIP      = {
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Renewing IP address"
        ipconfig /release | Out-Null
        ipconfig /renew | Out-Null
    }
    
    GetPublicIP  = {
        try {
            return (Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
        }
        catch {
            return $null
        }
    }
    
    TestPort     = {
        param([string]$Target, [int]$Port, [int]$Timeout = 1000)
        
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $connect = $tcp.BeginConnect($Target, $Port, $null, $null)
            $wait = $connect.AsyncWaitHandle.WaitOne($Timeout, $false)
            
            if ($wait) {
                $tcp.EndConnect($connect)
                $tcp.Close()
                return $true
            }
            else {
                $tcp.Close()
                return $false
            }
        }
        catch {
            return $false
        }
    }
}

# ============================================================================
# MODULE: SYSTEM PERFORMANCE
# ============================================================================
$ONI.Performance = @{
    GetCPU          = {
        $cpu = Get-CimInstance Win32_Processor
        return @{
            Name              = $cpu.Name
            Cores             = $cpu.NumberOfCores
            LogicalProcessors = $cpu.NumberOfLogicalProcessors
            CurrentClockSpeed = $cpu.CurrentClockSpeed
            MaxClockSpeed     = $cpu.MaxClockSpeed
            LoadPercentage    = $cpu.LoadPercentage
        }
    }
    
    GetMemory       = {
        $os = Get-CimInstance Win32_OperatingSystem
        $total = $os.TotalVisibleMemorySize / 1MB
        $free = $os.FreePhysicalMemory / 1MB
        $used = $total - $free
        
        return @{
            Total_GB    = [math]::Round($total, 2)
            Used_GB     = [math]::Round($used, 2)
            Free_GB     = [math]::Round($free, 2)
            UsedPercent = [math]::Round(($used / $total) * 100, 2)
        }
    }
    
    GetDisk         = {
        $disks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        
        return $disks | ForEach-Object {
            @{
                Drive       = $_.DeviceID
                Total_GB    = [math]::Round($_.Size / 1GB, 2)
                Used_GB     = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 2)
                Free_GB     = [math]::Round($_.FreeSpace / 1GB, 2)
                FreePercent = [math]::Round(($_.FreeSpace / $_.Size) * 100, 2)
            }
        }
    }
    
    GetTopProcesses = {
        param([int]$Count = 10, [string]$SortBy = "CPU")
        
        $processes = Get-Process | Where-Object { $_.CPU -gt 0 }
        
        if ($SortBy -eq "CPU") {
            $processes = $processes | Sort-Object CPU -Descending
        }
        else {
            $processes = $processes | Sort-Object WorkingSet64 -Descending
        }
        
        return $processes | Select-Object -First $Count | ForEach-Object {
            @{
                Name      = $_.Name
                PID       = $_.Id
                CPU       = [math]::Round($_.CPU, 2)
                Memory_MB = [math]::Round($_.WorkingSet64 / 1MB, 2)
            }
        }
    }
    
    Monitor         = {
        param([int]$Interval = 2, [int]$Duration = 60)
        
        & $ONI.Core.Log "Monitoring system performance for ${Duration}s"
        
        $endTime = (Get-Date).AddSeconds($Duration)
        
        while ((Get-Date) -lt $endTime) {
            Clear-Host
            Write-Host "═══ ONI SYSTEM MONITOR ═══" -ForegroundColor Cyan
            Write-Host ""
            
            $cpu = & $ONI.Performance.GetCPU
            $mem = & $ONI.Performance.GetMemory
            $disk = & $ONI.Performance.GetDisk
            
            Write-Host "CPU: $($cpu.LoadPercentage)%" -ForegroundColor $(if ($cpu.LoadPercentage -gt 80) { "Red" } else { "Green" })
            Write-Host "RAM: $($mem.Used_GB)GB / $($mem.Total_GB)GB ($($mem.UsedPercent)%)" -ForegroundColor $(if ($mem.UsedPercent -gt 80) { "Red" } else { "Green" })
            
            foreach ($d in $disk) {
                Write-Host "DISK $($d.Drive): $($d.Free_GB)GB free ($($d.FreePercent)%)" -ForegroundColor $(if ($d.FreePercent -lt 20) { "Red" } else { "Green" })
            }
            
            Write-Host ""
            Write-Host "Top Processes:" -ForegroundColor Yellow
            $top = & $ONI.Performance.GetTopProcesses -Count 5
            $top | ForEach-Object {
                Write-Host "  $($_.Name): $($_.CPU)s CPU | $($_.Memory_MB)MB RAM" -ForegroundColor Gray
            }
            
            Start-Sleep -Seconds $Interval
        }
    }
}

# ============================================================================
# MODULE: SCHEDULED TASKS
# ============================================================================
$ONI.Task = @{
    Create = {
        param(
            [string]$Name,
            [string]$ScriptPath,
            [string]$Trigger = "Daily",
            [string]$Time = "09:00"
        )
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Creating scheduled task: $Name"
        
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$ScriptPath`""
        
        if ($Trigger -eq "Daily") {
            $trigger = New-ScheduledTaskTrigger -Daily -At $Time
        }
        elseif ($Trigger -eq "Startup") {
            $trigger = New-ScheduledTaskTrigger -AtStartup
        }
        elseif ($Trigger -eq "Logon") {
            $trigger = New-ScheduledTaskTrigger -AtLogOn
        }
        
        Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Force
    }
    
    Delete = {
        param([string]$Name)
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Deleting scheduled task: $Name"
        Unregister-ScheduledTask -TaskName $Name -Confirm:$false
    }
    
    List   = {
        return Get-ScheduledTask | Select-Object TaskName, State, LastRunTime, NextRunTime
    }
    
    Run    = {
        param([string]$Name)
        & $ONI.Core.Log "Running scheduled task: $Name"
        Start-ScheduledTask -TaskName $Name
    }
}

# ============================================================================
# MODULE: WINDOWS FEATURES
# ============================================================================
$ONI.Features = @{
    List    = {
        return Get-WindowsOptionalFeature -Online | 
        Select-Object FeatureName, State |
        Sort-Object FeatureName
    }
    
    Enable  = {
        param([string]$Name)
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Enabling Windows feature: $Name"
        Enable-WindowsOptionalFeature -Online -FeatureName $Name -NoRestart
    }
    
    Disable = {
        param([string]$Name)
        
        & $ONI.Core.RequireAdmin
        & $ONI.Core.Log "Disabling Windows feature: $Name"
        Disable-WindowsOptionalFeature -Online -FeatureName $Name -NoRestart
    }
}

# ============================================================================
# EXPORT MODULE
# ============================================================================
Export-ModuleMember -Variable ONI
