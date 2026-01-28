# After Effects Adapter Module for ONI (Golden Standard)
# Version: 1.0
# Protocol: Robust Slow-Type

function Connect-AfterEffects {
    <#
    .SYNOPSIS
        Finds and focuses After Effects.
    #>
    [CmdletBinding()]
    param()

    Write-Host "[ONI-AE] Searching for 'AfterFX' process..." -ForegroundColor Cyan
    $wshell = New-Object -ComObject WScript.Shell
    
    $proc = Get-Process AfterFX -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Error "[ONI-AE] Process 'AfterFX' not found."
        return $false
    }
    
    $title = $proc.MainWindowTitle
    if ([string]::IsNullOrWhiteSpace($title)) {
         if (-not $wshell.AppActivate("Adobe After Effects")) {
             return $false
         }
    } else {
        if (-not $wshell.AppActivate($title)) {
            $wshell.AppActivate("Adobe After Effects")
        }
    }

    Write-Host "[ONI-AE] Connected to After Effects." -ForegroundColor Green
    Start-Sleep -Milliseconds 500
    return $true
}

function Clear-AEState {
    <#
    .SYNOPSIS
        Resets state (Esc).
    #>
    [CmdletBinding()]
    param()

    $wshell = New-Object -ComObject WScript.Shell
    Write-Host "[ONI-AE] Clearing State..." -ForegroundColor Gray
    
    # Esc x 3 to close dialogs or selections
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 200
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 200
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 500
    
    # Click on empty space? Hard blind.
    # F2 deselect all?
    # Shift+F2 is deselect all layers.
    $wshell.SendKeys("+{F2}") 
    Start-Sleep -Milliseconds 200
}



# State Variable for Speed Control
$Script:CurrentInputDelay = 300
$Script:CachedWShell = $null

function Get-GenericWShell {
    if ($null -eq $Script:CachedWShell) {
        $Script:CachedWShell = New-Object -ComObject WScript.Shell
    }
    return $Script:CachedWShell
}

function Set-AEAdapterSpeed {
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
        "Normal" { $Script:CurrentInputDelay = 300; Write-Host "[ONI-AE] Speed: NORMAL (300ms)" -ForegroundColor Gray }
        "Turbo"  { $Script:CurrentInputDelay = 50;  Write-Host "[ONI-AE] Speed: TURBO (50ms)" -ForegroundColor Yellow }
        "Reflex" { $Script:CurrentInputDelay = 10;  Write-Host "[ONI-AE] Speed: REFLEX (10ms)" -ForegroundColor Magenta }
    }
}

function Send-AEShortcut {
    [CmdletBinding()]
    param([string]$Keys, [int]$Delay=$Script:CurrentInputDelay)
    
    $wshell = Get-GenericWShell
    Write-Host "[ONI-AE] > Keys: $Keys (Delay: ${Delay}ms)" -NoNewline
    $wshell.SendKeys($Keys)
    Write-Host " [SENT]"
    Start-Sleep -Milliseconds $Delay
}

function Send-AEInput {
    [CmdletBinding()]
    param([string]$Text, [int]$Delay=$Script:CurrentInputDelay, [switch]$Enter)
    
    $wshell = Get-GenericWShell
    Write-Host "[ONI-AE] > Type: $Text (Delay: ${Delay}ms)" -NoNewline
    $wshell.SendKeys($Text)
    
    if ($Enter) {
        $wshell.SendKeys("{ENTER}")
        Write-Host " [ENTER]"
    } else {
        Write-Host ""
    }
    Start-Sleep -Milliseconds $Delay
}

Export-ModuleMember -Function Connect-AfterEffects, Clear-AEState, Send-AEShortcut, Send-AEInput, Set-AEAdapterSpeed


