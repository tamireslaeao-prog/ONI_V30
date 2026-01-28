
# ONI Corel Hotfix - Force Resize
# Attaches to ACTIVE Corel instance and resizes selection.

try {
    # Try to grab active instance
    try {
        $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
    }
    catch {
        Write-Host "Could not find active Corel instance. Trying New-Object..."
        $corel = New-Object -ComObject CorelDRAW.Application
    }
    
    $doc = $corel.ActiveDocument
    if ($null -eq $doc) {
        Write-Error "No active document found!"
        exit
    }
    
    Write-Host "Connected to: $($doc.Name)"
    
    # Get Selection
    $sel = $doc.ActiveSelection
    if ($sel.Shapes.Count -eq 0) {
        Write-Host "Nothing selected. Selecting ALL shapes on active page..."
        # Avoid selecting the GRID if it's locked/on another layer?
        # Let's try selecting MOLD_DXF layer content specifically if possible
        # Or just everything.
        $sel = $doc.ActivePage.Shapes.All()
    }
    
    if ($sel.Shapes.Count -gt 0) {
        # Group to treat as one unit
        $grp = $sel.Group()
        
        # Dimensions from User Request (A3 fit)
        # Real height ~420mm (Unit Height)
        # Width ~175mm
        Write-Host "Resizing to 175x420mm..."
        $grp.SetSize(175, 420)
        
        # Center on Page
        $grp.CenterX = 148.5
        $grp.CenterY = 210.0
        
        Write-Host "SUCCESS: Scaled and Centered."
    }
    else {
        Write-Warning "Page is empty?"
    }
    
}
catch {
    Write-Error "Hotfix Failed: $_"
}
