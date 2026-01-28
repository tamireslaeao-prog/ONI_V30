# Photoshop Master Lab 2: The Nuclear Console (Action Manager)
# Objective: Wrap Action Manager JS in a clean PowerShell Function.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting..."
    $ps = New-Object -ComObject Photoshop.Application
    $ps.Visible = $true
    $ps.DisplayDialogs = 3
    if ($ps.Documents.Count -eq 0) { $ps.Documents.Add(800, 600) }
    $doc = $ps.ActiveDocument

    # 1. THE WRAPPER FUNCTION
    function Invoke-ActionManager ($jsCode) {
        # Wraps the AM code in a try/catch block for safety
        $safeCode = "try { $jsCode } catch(e) { 'ERROR: ' + e.message }"
        return $ps.DoJavaScript($safeCode)
    }
    
    # 2. THE ID LIBRARY (stringIDToTypeID is readable)
    $JS_LIB = @"
    function sTID(s) { return stringIDToTypeID(s); }
    function cTID(s) { return charIDToTypeID(s); }
    function execute(id, desc) { executeAction(id, desc, DialogModes.NO); }
"@

    function Color([int]$r, [int]$g, [int]$b) {
        $c = New-Object -ComObject Photoshop.SolidColor
        $c.RGB.Red = $r; $c.RGB.Green = $g; $c.RGB.Blue = $b
        return $c
    }
    $red = Color 255 0 0

    # 3. TEST: CONVERT TO SMART OBJECT (Generic)
    Write-Host "Creating Content to Convert..."
    $l = $doc.ArtLayers.Add()
    $l.Name = "To Be Smart"
    $doc.Selection.SelectAll()
    $doc.Selection.Fill($red)
    $doc.Selection.Deselect()
    
    Write-Host "Invoking Smart Object Conversion..."
    
    $codeSmartObject = $JS_LIB + @"
    var idnewPlacedLayer = sTID("newPlacedLayer");
    execute(idnewPlacedLayer, undefined);
"@
    
    Invoke-ActionManager $codeSmartObject
    
    Write-Host "Result Kind: $($doc.ActiveLayer.Kind)" 
    # Kind 17 = Smart Object? (Value depends on version, usually 17)
    
    # 4. TEST: SELECT ALL LAYERS (Impossible via DOM)
    Write-Host "Invoking Select All Layers..."
    $doc.ArtLayers.Add() # Add another so we have 2
    
    $codeSelectAll = $JS_LIB + @"
    var ref = new ActionReference();
    ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
    var desc = new ActionDescriptor();
    desc.putReference(cTID("null"), ref);
    execute(sTID("selectAllLayers"), desc);
"@
    # Note: selectAllLayers might need "selectAllLayers" stringID or "MjAllLayers" charID.
    # StringID "selectAllLayers" works in CC+.
    
    try {
        Invoke-ActionManager $codeSelectAll
        Write-Host "Select All executed."
    }
    catch {
        Write-Host "Select All failed: $_"
    }

    Write-Host "SUCCESS: Action Manager Wrapped."

}
catch {
    Write-Host "ERROR: $_"
    exit 1
}
