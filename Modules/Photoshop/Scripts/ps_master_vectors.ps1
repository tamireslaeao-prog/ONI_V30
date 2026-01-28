# Photoshop Master Lab 3: Vector Perfection (Smooth & Sharp)
# Objective: Robust Bezier Drawing via JSON Payload.
$ErrorActionPreference = "Stop"

try {
    Write-Host "Connecting..."
    $ps = New-Object -ComObject Photoshop.Application
    $ps.Visible = $true
    $ps.DisplayDialogs = 3
    if ($ps.Documents.Count -eq 0) { $ps.Documents.Add(800, 600) }
    $doc = $ps.ActiveDocument

    # 1. THE DRAW-VECTOR FUNCTION (JSON Driven)
    function Draw-VectorPath ($name, $pointsJson) {
        $jsPayload = @"
        var doc = app.activeDocument;
        var jsonPoints = $pointsJson; 
        // JSON format provided by PS variable: [ {k:1, a:[x,y], l:[x,y], r:[x,y]}, ... ]
        
        var lineArray = [];
        for (var i=0; i<jsonPoints.length; i++) {
            var ptData = jsonPoints[i];
            var p = new PathPointInfo();
            p.kind = (ptData.k === 1) ? PointKind.SMOOTHPOINT : PointKind.CORNERPOINT;
            p.anchor = ptData.a;
            p.leftDirection = ptData.l;
            p.rightDirection = ptData.r;
            lineArray.push(p);
        }

        var subPath = new SubPathInfo();
        subPath.operation = ShapeOperation.SHAPEADD;
        subPath.closed = true;
        subPath.entireSubPath = lineArray;

        doc.pathItems.add("$name", [subPath]);
"@
        return $ps.DoJavaScript($jsPayload)
    }

    # 2. DEFINE SHAPES IN JSON
    # Heart: 4 Points.
    # Top(Cleft): Corner. Right: Smooth. Bottom: Corner. Left: Smooth.
    # Smooth points need handles extending out.
    
    $heartJson = @"
[
    {"k":2, "a":[400,250], "l":[420,250], "r":[380,250]}, 
    {"k":1, "a":[550,200], "l":[550,300], "r":[550,100]}, 
    {"k":2, "a":[400,500], "l":[400,500], "r":[400,500]}, 
    {"k":1, "a":[250,200], "l":[250,100], "r":[250,300]}
]
"@
    # Note: JSON coords are [x,y].
    # Re-adjusting logic:
    # P1 (Top Cleft): 400,250. Left Handle goes UP-LEFT (350, 200)? Right Handle UP-RIGHT (450, 200)?
    # Wait, LeftDirection is "Entering" handle? RightDirection is "Exiting"?
    # Actually: "LeftDirection" is the handle for the segment entering the point (or preceding it).
    # "RightDirection" is the handle for the segment leaving the point.
    # Let's try symmetric handles.

    $heartJsonFixed = @"
[
    {"k":2, "a":[400,250], "l":[450,200], "r":[350,200]}, 
    {"k":1, "a":[250,200], "l":[250,250], "r":[250,150]}, 
    {"k":2, "a":[400,500], "l":[400,500], "r":[400,500]}, 
    {"k":1, "a":[550,200], "l":[550,150], "r":[550,250]}
]
"@
    # Checking Order: Top -> Left -> Bottom -> Right (Counter Clockwise usually?)
    # Or Top -> Right?
    # Let's stick to the previous order [Top, Right, Bottom, Left] but fix handles.
    # Top (400,250): Corner. RightOut(350,200)?? No, Right is usually +X? 
    # In PS Scripting, LeftDirection/RightDirection names are tricky.
    # Usually: LeftDirection is the handle associated with the segment "Before" the point.
    # RightDirection is "After".
    # If drawing Top -> Right:
    # Top RightDir -> segment -> Right LeftDir.

    Write-Host "Drawing Vector Heart..."
    Draw-VectorPath "Master Heart" $heartJsonFixed
    
    # Fill it to prove it exists
    $doc.PathItems.Item("Master Heart").MakeSelection(0, $true, 1)
    $l = $doc.ArtLayers.Add()
    $c = New-Object -ComObject Photoshop.SolidColor; $c.RGB.Red = 255
    $doc.Selection.Fill($c)
    $doc.Selection.Deselect()
    
    Write-Host "SUCCESS: Vector Perfection."

}
catch {
    Write-Host "ERROR: $_"
    exit 1
}
