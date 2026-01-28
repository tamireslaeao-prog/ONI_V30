# AutoCAD_Adapter.psm1 - Standard Reliable Version
# Uses Marshal::GetActiveObject for solid connection recovery.

function Connect-AutoCAD {
    $acad = $null
    
    # 1. Try to attach to running instance
    try {
        $acad = [System.Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
        if ($acad) {
            Write-Host "Attached to Running AutoCAD." -ForegroundColor Green
            return $acad
        }
    }
    catch {
        # Not running or access denied
        Write-Verbose "Could not attach to running instance: $($_.Exception.Message)"
    }
    
    # 2. Try to launch new instance
    if (-not $acad) {
        try {
            Write-Host "Launching new AutoCAD instance..." -ForegroundColor Yellow
            $acad = New-Object -ComObject "AutoCAD.Application"
            if ($acad) {
                $acad.Visible = $true
                Write-Host "AutoCAD Launched." -ForegroundColor Green
                return $acad
            }
        }
        catch {
            Write-Error "Failed to connect to AutoCAD. Is it installed?"
        }
    }
    return $null
}


# State Variable for Speed Control
$Script:CurrentRetryDelay = 1.0
$Script:CurrentMaxRetries = 20

function Set-CADAdapterSpeed {
    <#
    .SYNOPSIS
        Sets the speed of the adapter (Normal vs Turbo).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("Normal", "Turbo", "Reflex")]
        [string]$Mode
    )

    switch ($Mode) {
        "Normal" { 
            $Script:CurrentRetryDelay = 1.0
            $Script:CurrentMaxRetries = 20
            Write-Host "[ONI-CAD] Speed: NORMAL (Retry=1s)" -ForegroundColor Gray 
        }
        "Turbo"  { 
            $Script:CurrentRetryDelay = 0.1 
            $Script:CurrentMaxRetries = 50
            Write-Host "[ONI-CAD] Speed: TURBO (Retry=100ms)" -ForegroundColor Yellow 
        }
        "Reflex" { 
            # Aggressive retry for confident actions
            $Script:CurrentRetryDelay = 0.05 
            $Script:CurrentMaxRetries = 100
            Write-Host "[ONI-CAD] Speed: REFLEX (Retry=50ms)" -ForegroundColor Magenta 
        }
    }
}

function Send-Command {
    param(
        [Parameter(Mandatory = $true)]
        [object]$ACAD,
        
        [Parameter(Mandatory = $true)]
        [string]$Command,
        
        [int]$MaxRetries = $Script:CurrentMaxRetries,
        [int]$RetryDelay = $Script:CurrentRetryDelay
    )
    
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        try {
            # Check if busy (State check could be added here if needed)
            $ACAD.Application.ActiveDocument.SendCommand("$Command `r`n")
            return $true
        }
        catch {
            $attempt++
            $err = $_.Exception.Message
            # Common RPC errors: 0x80010001 (CallRejected), 0x800706BE (RPC Failed)
            # Only verbose in Turbo to reduce noise
            if ($Script:CurrentRetryDelay -gt 0.5) { 
                Write-Warning "Busy ($attempt/$MaxRetries): $Command" 
            }
            Start-Sleep -Seconds $RetryDelay
        }
    }
    throw "Failed to send command '$Command' after $MaxRetries retries."
}

Export-ModuleMember -Function Connect-AutoCAD, Send-Command, Set-CADAdapterSpeed

