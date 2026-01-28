# CorelDraw Tool Selector (COM/VBA)
# Uses CorelDRAW Object Model to select tools robustly
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to CorelDRAW Application..."
    $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
    
    if (-not $corel) {
        Write-Host "CorelDRAW not running or COM not accessible."
        exit 1
    }

    Write-Host "Current Tool ID: $($corel.ActiveTool)"
    
    # cdrToolBezier = 6
    $BEZIER_TOOL_ID = 6
    
    Write-Host "Setting Active Tool to Bezier ($BEZIER_TOOL_ID)..."
    $corel.ActiveTool = $BEZIER_TOOL_ID
    
    Start-Sleep -Milliseconds 500
    
    if ($corel.ActiveTool -eq $BEZIER_TOOL_ID) {
        Write-Host "SUCCESS: Bezier Tool Selected via COM."
    }
    else {
        Write-Host "WARNING: ActiveTool reports $($corel.ActiveTool) (Expected $BEZIER_TOOL_ID)"
    }

}
catch {
    Write-Host "COM Error: $_"
    # Fallback to creating new object if GetActiveObject fails (though it requires Corel open)
    exit 1
}
