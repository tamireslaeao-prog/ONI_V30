# Photoshop Adapter Module for ONI (Golden Standard)
# Version: 1.0
# Protocol: Robust Slow-Type


# C# P/Invoke for Absolute Focus Power
$FocusCode = @'
    using System;
    using System.Runtime.InteropServices;
    public class FocusHelper {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    }
'@
Add-Type -TypeDefinition $FocusCode -ErrorAction SilentlyContinue

function Connect-Photoshop {
    <#
    .SYNOPSIS
        Finds and forces focus on Photoshop using Win32 API.
    #>
    [CmdletBinding()]
    param()

    Write-Host "[ONI-PS] Searching for 'Photoshop' process..." -ForegroundColor Cyan
    
    $proc = Get-Process Photoshop -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Error "[ONI-PS] Process 'Photoshop' not found."
        return $false
    }
    
    $hwnd = $proc.MainWindowHandle
    if ($hwnd -eq [IntPtr]::Zero) {
        # Fallback for some versions where MainWindowHandle is hidden
        $wshell = New-Object -ComObject WScript.Shell
        if ($wshell.AppActivate("Photoshop")) {
            return $true
        }
    } else {
        # The Nuclear Option: Win32 API
        [FocusHelper]::ShowWindow($hwnd, 9) # SW_RESTORE
        Start-Sleep -Milliseconds 200
        [FocusHelper]::SetForegroundWindow($hwnd)
        Start-Sleep -Milliseconds 200
        
        # Double Tap with WShell just in case
        $wshell = New-Object -ComObject WScript.Shell
        $wshell.AppActivate($proc.Id)
    }

    Write-Host "[ONI-PS] Connected to Photoshop (PID: $($proc.Id))." -ForegroundColor Green
    Start-Sleep -Milliseconds 500
    return $true
}


function Clear-PhotoshopState {
    <#
    .SYNOPSIS
        Resets state (Esc).
    #>
    [CmdletBinding()]
    param()

    $wshell = New-Object -ComObject WScript.Shell
    Write-Host "[ONI-PS] Clearing State..." -ForegroundColor Gray
    
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 200
    $wshell.SendKeys("{ESC}")
    Start-Sleep -Milliseconds 500
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

function Set-PSAdapterSpeed {
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
        "Normal" { $Script:CurrentInputDelay = 300; Write-Host "[ONI-PS] Speed: NORMAL (300ms)" -ForegroundColor Gray }
        "Turbo"  { $Script:CurrentInputDelay = 50;  Write-Host "[ONI-PS] Speed: TURBO (50ms)" -ForegroundColor Yellow }
        "Reflex" { $Script:CurrentInputDelay = 10;  Write-Host "[ONI-PS] Speed: REFLEX (10ms)" -ForegroundColor Magenta }
    }
}

function Send-PSShortcut {
    [CmdletBinding()]
    param([string]$Keys, [int]$Delay=$Script:CurrentInputDelay)
    
    $wshell = Get-GenericWShell
    Write-Host "[ONI-PS] > Keys: $Keys (Delay: ${Delay}ms)" -NoNewline
    $wshell.SendKeys($Keys)
    Write-Host " [SENT]"
    Start-Sleep -Milliseconds $Delay
}

function Send-PSInput {
    [CmdletBinding()]
    param([string]$Text, [int]$Delay=$Script:CurrentInputDelay, [switch]$Enter)
    
    $wshell = Get-GenericWShell
    Write-Host "[ONI-PS] > Type: $Text (Delay: ${Delay}ms)" -NoNewline
    $wshell.SendKeys($Text)
    
    if ($Enter) {
        $wshell.SendKeys("{ENTER}")
        Write-Host " [ENTER]"
    } else {
        Write-Host ""
    }
    Start-Sleep -Milliseconds $Delay
}


function New-PSDocument {
    <#
    .SYNOPSIS
        Creates a new document using COM (Bypasses UI dialogs).
    #>
    [CmdletBinding()]
    param(
        [int]$Width = 1920,
        [int]$Height = 1080
    )
    
    try {
        $app = New-Object -ComObject Photoshop.Application
        $doc = $app.Documents.Add($Width, $Height, 72, "ONI Canvas", 2, 1, 1) # RGB, White, Square
        Write-Host "[ONI-PS] Document Created via COM ($Width x $Height)" -ForegroundColor Green
        return $true
    } catch {

        Write-Error "[ONI-PS] COM Creation Failed: $_"
        return $false
    }
}

function New-PSTextLayer {
    <#
    .SYNOPSIS
        Creates a text layer using COM.
    #>
    [CmdletBinding()]
    param(
        [string]$Text = "ONI V22",
        [int]$Size = 100
    )
    
    try {
        $app = New-Object -ComObject Photoshop.Application
        $doc = $app.ActiveDocument
        $layer = $doc.ArtLayers.Add()
        $layer.Kind = 2 # psTextLayer
        $textItem = $layer.TextItem
        $textItem.Contents = $Text
        $textItem.Size = $Size
        $textItem.Justification = 1 # Center
        # Position in center (approx)
        $textItem.Position = @(960, 540) 
        
        Write-Host "[ONI-PS] Text Injected: $Text" -ForegroundColor Cyan
        return $true
    } catch {
        Write-Error "[ONI-PS] Text Injection Failed: $_"
        return $false
    }
}

Export-ModuleMember -Function Connect-Photoshop, Clear-PhotoshopState, Send-PSShortcut, Send-PSInput, Set-PSAdapterSpeed, New-PSDocument, New-PSTextLayer




