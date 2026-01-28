# CorelDRAW Vectorizer V2 - "Neuro-Integration" Mode
# Robust Shortcut Injection Method (Bypassing COM issues)
# Uses WScript.Shell.AppActivate to connect to RUNNING Corel instance

param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $false)][string]$OutputPath
)

$ErrorActionPreference = "Stop"
$wshell = New-Object -ComObject WScript.Shell

function Write-Log($msg) { Write-Host "[ONI-V2] $msg" -ForegroundColor Cyan }

try {
    if (-not (Test-Path $InputPath)) { throw "Input not found: $InputPath" }

    Write-Log "Connecting to CorelDRAW via AppActivate..."
    
    # 1. Focus CorelDRAW (MUST BE ALREADY RUNNING)
    $corelTitles = @("CorelDRAW", "Sem título", "Untitled", "CorelDRW")
    $connected = $false
    
    foreach ($title in $corelTitles) {
        if ($wshell.AppActivate($title)) {
            Write-Log "Connected to: $title"
            $connected = $true
            break
        }
    }
    
    if (-not $connected) {
        throw "CorelDRAW NOT RUNNING. Please open CorelDRAW first!"
    }
    
    Start-Sleep -Seconds 1
    
    # 2. Setup New Doc
    Write-Log "Creating New Doc (Ctrl+N)..."
    $wshell.SendKeys("^n")
    Start-Sleep -Seconds 1
    $wshell.SendKeys("{ENTER}") # Confirm defaults
    Start-Sleep -Seconds 2
    
    # 3. Import Image (Ctrl+I)
    Write-Log "Importing Image..."
    $wshell.SendKeys("^i")
    Start-Sleep -Seconds 1
    
    # Type Path
    $wshell.SendKeys($InputPath)
    Start-Sleep -Seconds 1
    $wshell.SendKeys("{ENTER}")
    Start-Sleep -Seconds 1
    $wshell.SendKeys("{ENTER}") # Place on canvas
    Start-Sleep -Seconds 2
    
    # 4. Trigger PowerTrace (Ctrl+Shift+D - "Neuro" Shortcut mentioned in protocol)
    # NOTE: If this shortcut isn't set, we might need fallback.
    # Protocol says: "Quick Trace (Detailed): Ctrl+Shift+D"
    Write-Log "Tracing (Ctrl+Shift+D)..."
    $wshell.SendKeys("^+d")
    
    Start-Sleep -Seconds 5
    # Confirm Trace Dialog (Enter)
    $wshell.SendKeys("{ENTER}")
    Start-Sleep -Seconds 2
    
    # 5. Delete Original (Delete key) - Assuming original is selected or behind
    # Actually, after trace, usually the group is selected.
    # Let's Skip delete to be safe, or assume Trace deletes original (setting dependent)
    
    # 6. Export (Ctrl+E)
    if ($OutputPath) {
        Write-Log "Exporting (Ctrl+E)..."
        $wshell.SendKeys("^e")
        Start-Sleep -Seconds 1
        $wshell.SendKeys($OutputPath)
        Start-Sleep -Seconds 1
        $wshell.SendKeys("{ENTER}")
        Start-Sleep -Seconds 2
        
        # Confirm Filter Dialog (Enter)
        $wshell.SendKeys("{ENTER}")
        Start-Sleep -Seconds 1
    }
    
    Write-Log "Success."
    
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
