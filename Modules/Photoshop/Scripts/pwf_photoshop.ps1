<#
.SYNOPSIS
    PWF (Principle Write-First) Launcher for Photoshop.
    Ensures file exists before opening app.

.DESCRIPTION
    1. Checks if target file exists.
    2. If not, creates a dummy file (valid PSD header if possible, or just empty).
    3. Launches Photoshop with the file.
    4. Waits for Window Title to match.

.PARAMETER Path
    Absolute path to the target .psd file.

.EXAMPLE
    .\pwf_photoshop.ps1 -Path "C:\Caminho\Para\ProjectX.psd"
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [int]$WaitSeconds = 15
)

# 1. Validation
if (-not $Path.EndsWith(".psd")) {
    Write-Warning "PWF: Target should be a .psd file. Proceeding anyway."
}

# 2. PWF: Create if missing
if (-not (Test-Path $Path)) {
    Write-Host "PWF: File '$Path' not found. Creating blank template..."
    
    # Create directory if needed
    $parent = Split-Path $Path
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    # Create empty file (Photoshop will complain if 0 bytes, but it's better than nothing)
    # Ideally we would copy a template, but for now New-Item is the protocol
    New-Item -Path $Path -ItemType File -Force | Out-Null
    Write-Host "PWF: Created blank file."
} else {
    Write-Host "PWF: File exists. Opening..."
}

# 3. Launch
$psCmd = "Start-Process 'photoshop' -ArgumentList '$Path'"
Write-Host "PWF: Executing -> $psCmd"
Invoke-Expression $psCmd

# 4. Verify
Write-Host "PWF: Waiting for Photoshop focus..."
Start-Sleep -s 5

$psProcess = Get-Process | Where-Object {$_.MainWindowTitle -match "Photoshop"} | Select-Object -First 1

if ($psProcess) {
    Write-Host "PWF: SUCCESS. Photoshop is running with Title: $($psProcess.MainWindowTitle)"
} else {
    Write-Warning "PWF: Photoshop started but window not detected yet. Please check manually."
}
<#
.SYNOPSIS
    PWF (Principle Write-First) Launcher for Photoshop.
    Ensures file exists before opening app.

.DESCRIPTION
    1. Checks if target file exists.
    2. If not, creates a dummy file (valid PSD header if possible, or just empty).
    3. Launches Photoshop with the file.
    4. Waits for Window Title to match.

.PARAMETER Path
    Absolute path to the target .psd file.

.EXAMPLE
    .\pwf_photoshop.ps1 -Path "C:\Caminho\Para\ProjectX.psd"
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [int]$WaitSeconds = 15
)

# 1. Validation
if (-not $Path.EndsWith(".psd")) {
    Write-Warning "PWF: Target should be a .psd file. Proceeding anyway."
}

# 2. PWF: Create if missing
if (-not (Test-Path $Path)) {
    Write-Host "PWF: File '$Path' not found. Creating blank template..."
    
    # Create directory if needed
    $parent = Split-Path $Path
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    # Create empty file (Photoshop will complain if 0 bytes, but it's better than nothing)
    # Ideally we would copy a template, but for now New-Item is the protocol
    New-Item -Path $Path -ItemType File -Force | Out-Null
    Write-Host "PWF: Created blank file."
} else {
    Write-Host "PWF: File exists. Opening..."
}

# 3. Launch
$psCmd = "Start-Process 'photoshop' -ArgumentList '$Path'"
Write-Host "PWF: Executing -> $psCmd"
Invoke-Expression $psCmd

# 4. Verify
Write-Host "PWF: Waiting for Photoshop focus..."
Start-Sleep -s 5

$psProcess = Get-Process | Where-Object {$_.MainWindowTitle -match "Photoshop"} | Select-Object -First 1

if ($psProcess) {
    Write-Host "PWF: SUCCESS. Photoshop is running with Title: $($psProcess.MainWindowTitle)"
} else {
    Write-Warning "PWF: Photoshop started but window not detected yet. Please check manually."
}
