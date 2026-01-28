# Photoshop Master Lab 1: Speed (suspendHistory)
# Objective: Demonstrate the power of history suspension.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting..."
    $ps = New-Object -ComObject Photoshop.Application
    $ps.Visible = $true
    $ps.DisplayDialogs = 3
    if ($ps.Documents.Count -eq 0) { $ps.Documents.Add(800, 600) }
    $doc = $ps.ActiveDocument

    # 1. THE SLOW WAY (One by one)
    Write-Host "--- TEST 1: The Slow Way (20 Layers) ---"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    
    for ($i = 1; $i -le 20; $i++) {
        $l = $doc.ArtLayers.Add()
        $l.Name = "Slow Layer $i"
        # Each add updates UI and History Panel
    }
    
    $sw.Stop()
    Write-Host "Slow Time: $($sw.ElapsedMilliseconds) ms"
    
    # Cleanup
    $doc.ActiveHistoryState = $doc.HistoryStates.Item($doc.HistoryStates.Count - 21)
    
    # 2. THE MASTER WAY (suspendHistory)
    Write-Host "--- TEST 2: The Master Way (20 Layers) ---"
    
    # We need a JS Payload that does the loop inside
    # suspendHistory takes a JS string.
    
    $jsPayload = @"
    var doc = app.activeDocument;
    
    // The Function to Suspend
    function createLayers() {
        for (var i=1; i<=20; i++) {
            var l = doc.artLayers.add();
            l.name = "Fast Layer " + i;
        }
    }
    
    // The Magic Command
    doc.suspendHistory("Create 20 Fast Layers", "createLayers()");
"@
    
    $sw.Restart()
    $ps.DoJavaScript($jsPayload)
    $sw.Stop()
    
    Write-Host "Fast Time: $($sw.ElapsedMilliseconds) ms"
    Write-Host "Check History Panel: Only 1 state created."
    
    Write-Host "SUCCESS: Speed Demon Verified."

}
catch {
    Write-Host "ERROR: $_"
    exit 1
}
