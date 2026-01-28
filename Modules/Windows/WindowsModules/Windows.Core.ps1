# ============================================================================
# Windows.Core.ps1
# Core utilities and logging
# ============================================================================

$ONI = @{}

$ONI.Core = @{
    Version           = "2.0.0"
    LogFile           = "C:\ONI\Windows\oni_operations.log"
    
    Log               = {
        param([string]$Message, [string]$Level = "INFO")
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logEntry = "[$timestamp] [$Level] $Message"
        
        Add-Content -Path $ONI.Core.LogFile -Value $logEntry -ErrorAction SilentlyContinue
        
        $colors = @{
            "INFO"    = "White"
            "SUCCESS" = "Green"
            "WARNING" = "Yellow"
            "ERROR"   = "Red"
        }
        
        $color = $colors[$Level]
        if ($color) {
            Write-Host $logEntry -ForegroundColor $color
        }
        else {
            Write-Host $logEntry
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
            Architecture = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
            Memory_GB    = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            Processors   = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
        }
    }
}

Export-ModuleMember -Variable ONI
