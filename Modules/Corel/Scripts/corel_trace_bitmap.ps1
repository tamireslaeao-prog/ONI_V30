# CorelDraw COM PowerTrace Automation
# Traces the selected bitmap using the "Logo" preset.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting to CorelDRAW Application..."
    $corel = New-Object -ComObject CorelDRAW.Application
    $corel.Visible = $true
    
    if ($corel.ActiveSelection.Shapes.Count -eq 0) {
        Write-Host "No selection. Searching Active Layer for Bitmap..."
        $found = $false
        foreach ($s in $corel.ActiveLayer.Shapes) {
            # cdrBitmapShape = 5
            if ($s.Type -eq 5) {
                Write-Host "Found Bitmap. Selecting..."
                $s.CreateSelection()
                $found = $true
                break
            }
        }
        
        if (-not $found) {
            Write-Host "ERROR: No Bitmap found on Active Layer."
            exit 1
        }
    }
    
    $shape = $corel.ActiveSelection.Shapes.Item(1)
    Write-Host "Selected Shape Type: $($shape.Type)"
    
    # cdrBitmapShape = 5
    if ($shape.Type -eq 5) {
        Write-Host "Bitmap detected. Starting PowerTrace (Logo Preset)..."
        
        # cdrTraceLogo = 2
        $traceSettings = $shape.Bitmap.Trace(2)
        
        # Adjust settings if needed (Optional)
        # $traceSettings.DetailLevel = 80
        # $traceSettings.Smoothing = 50
        
        Write-Host "Executing Trace..."
        $traceSettings.Finish()
        
        Write-Host "SUCCESS: Vectorization Complete."
        
    }
    else {
        Write-Host "ERROR: Selected object is not a Bitmap. (Type: $($shape.Type))"
    }

}
catch {
    Write-Host "COM Error: $_"
    exit 1
}
