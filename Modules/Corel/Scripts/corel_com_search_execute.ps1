# CorelDraw COM Command Search & Execute
# Attempts to find "Bezier" command dynamically and execute it.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to CorelDRAW Application..."
    $corel = $null
    
    # Try GetActiveObject first
    try {
        $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
        Write-Host "Connected to running instance."
    }
    catch {
        Write-Host "GetActiveObject failed. Trying New-Object..."
        $corel = New-Object -ComObject CorelDRAW.Application
        $corel.Visible = $true
    }
    
    if (-not $corel) {
        throw "Could not obtain CorelDRAW Application object."
    }

    Write-Host "Application: $($corel.Name) v$($corel.Version)"
    
    # Search for command
    Write-Host "Searching for Bezier command..."
    # Note: Accessing .Commands can be slow, iterating carefully
    # Use FindCommand equivalent logic
    
    # Try to find specific command by English name 'Bezier Tool' or 'Draw Bezier'
    # We can try to use the method the user suggested if we can pass the ID?
    # but we don't have the ID. So let's try to map the user's intent.
    
    # Alternative 1: ActiveTool property (which we tried and failed, but maybe due to connection)
    # Alternative 2: CommandBars
    
    $found = $false
    
    # Let's try to set ActiveTool again with the robust connection
    # cdrToolBezier = 6
    Write-Host "Attempting ActiveTool = 6..."
    try {
        $corel.ActiveTool = 6
        Start-Sleep -Seconds 1
        if ($corel.ActiveTool -eq 6) {
            Write-Host "SUCCESS: Selected via ActiveTool property."
            $found = $true
        }
    }
    catch {
        Write-Host "ActiveTool set failed: $_"
    }

    if (-not $found) {
        Write-Host "Searching CommandBars for 'Bezier'..."
        # This is expensive, might take time.
        # Shortcuts: 
        # 'BezierTool' is a common internal name.
    }
    
}
catch {
    Write-Host "CRITICAL ERROR: $_"
}
