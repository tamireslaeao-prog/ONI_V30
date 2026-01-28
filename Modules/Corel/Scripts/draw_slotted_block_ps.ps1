# ONI Automation: Slotted Block (Photoshop Isometric via JSX) - v5 Final
# Strategy: PS Calculates Coords (Objects) -> Generates JSX (Correct Property) -> PS Executes

$ErrorActionPreference = "Stop"

# --- CONFIG (Script Scope) ---
$script:Scale = 15.0
$script:OriginX = 1000.0
$script:OriginY = 1200.0

# --- MATH ---
$Rag30 = [Math]::PI / 6
$Rag150 = 5 * [Math]::PI / 6
$script:vx_x = [Math]::Cos($Rag30); $script:vx_y = - ([Math]::Sin($Rag30)) 
$script:vy_x = [Math]::Cos($Rag150); $script:vy_y = - ([Math]::Sin($Rag150))
$script:vz_x = 0; $script:vz_y = -1 

function Get-IsoPoint ($x, $y, $z) {
    $u = $script:OriginX + $script:Scale * ($x * $script:vx_x + $y * $script:vy_x + $z * $script:vz_x)
    $v = $script:OriginY + $script:Scale * ($x * $script:vx_y + $y * $script:vy_y + $z * $script:vz_y)
    return [PSCustomObject]@{ u = $u; v = $v }
}

# Helper for Float Formatting
function Fmt ($val) {
    if ($null -eq $val) { return "0.00" }
    return $val.ToString("0.00", [System.Globalization.CultureInfo]::InvariantCulture)
}

# --- GENERATE JSX CONTENT ---
$jsxInfo = New-Object System.Collections.ArrayList
[void]$jsxInfo.Add("var doc = app.documents.add(2000, 2000, 72, 'Slotted Block Iso', NewDocumentMode.RGB, DocumentFill.WHITE);")
[void]$jsxInfo.Add("var lineSubPaths = new Array();")

function Add-LineToJSX ($p1, $p2) {
    # p1, p2 are Objects .u .v
    $u1 = Fmt $p1.u; $v1 = Fmt $p1.v
    $u2 = Fmt $p2.u; $v2 = Fmt $p2.v
    
    return "
    (function(){
        var spi = new SubPathInfo();
        spi.operation = ShapeOperation.SHAPEXOR;
        spi.closed = false;
        var pts = new Array();
        var p1 = new PathPointInfo(); p1.kind = PointKind.CORNERPOINT; p1.anchor = [$u1, $v1]; p1.leftDirection = p1.anchor; p1.rightDirection = p1.anchor;
        var p2 = new PathPointInfo(); p2.kind = PointKind.CORNERPOINT; p2.anchor = [$u2, $v2]; p2.leftDirection = p2.anchor; p2.rightDirection = p2.anchor;
        pts[0] = p1; pts[1] = p2;
        spi.entireSubPath = pts;
        lineSubPaths.push(spi);
    })();"
}

function Add-PolyToJSX ($ptsArr) {
    # ptsArr is ArrayList or Array of Objects
    $str = "
    (function(){
        var spi = new SubPathInfo();
        spi.operation = ShapeOperation.SHAPEXOR;
        spi.closed = true;
        var pts = new Array();"
    
    $i = 0
    foreach ($pt in $ptsArr) {
        $u = Fmt $pt.u
        $v = Fmt $pt.v
        $str += "
        var p$i = new PathPointInfo(); p$i.kind = PointKind.CORNERPOINT; p$i.anchor = [$u, $v]; p$i.leftDirection = p$i.anchor; p$i.rightDirection = p$i.anchor;
        pts[$i] = p$i;"
        $i++
    }
    
    $str += "
        spi.entireSubPath = pts;
        lineSubPaths.push(spi);
    })();"
    return $str
}

# --- CALCULATE POINTS ---
$FP0 = Get-IsoPoint  0  0  0
$FP1 = Get-IsoPoint 15  0  0
$FP2 = Get-IsoPoint 15  0 10
$FP3 = Get-IsoPoint  0  0 10
$FP4 = Get-IsoPoint  0  0 20
$FP5 = Get-IsoPoint 15  0 20
$FP6 = Get-IsoPoint 15  0 30
$FP7 = Get-IsoPoint 50  0 30
$FP8 = Get-IsoPoint 50  0  0

[void]$jsxInfo.Add((Add-LineToJSX $FP0 $FP1))
[void]$jsxInfo.Add((Add-LineToJSX $FP1 $FP2))
[void]$jsxInfo.Add((Add-LineToJSX $FP2 $FP3))
[void]$jsxInfo.Add((Add-LineToJSX $FP3 $FP0))
[void]$jsxInfo.Add((Add-LineToJSX $FP4 $FP5))
[void]$jsxInfo.Add((Add-LineToJSX $FP5 $FP6))
[void]$jsxInfo.Add((Add-LineToJSX $FP6 $FP4))
[void]$jsxInfo.Add((Add-LineToJSX $FP6 $FP7))
[void]$jsxInfo.Add((Add-LineToJSX $FP7 $FP8))
[void]$jsxInfo.Add((Add-LineToJSX $FP8 $FP1))

$D = 15
$TopRight = Get-IsoPoint 50 0 30; $TopRightB = Get-IsoPoint 50 $D 30
$BotRight = Get-IsoPoint 50 0 0; $BotRightB = Get-IsoPoint 50 $D 0
$TopLeftI = Get-IsoPoint 15 0 30; $TopLeftIB = Get-IsoPoint 15 $D 30
$TopLeftO = Get-IsoPoint 0 0 30; $TopLeftOB = Get-IsoPoint 0 $D 30

[void]$jsxInfo.Add((Add-LineToJSX $TopRight $TopRightB))
[void]$jsxInfo.Add((Add-LineToJSX $BotRight $BotRightB))
[void]$jsxInfo.Add((Add-LineToJSX $TopLeftI $TopLeftIB))
[void]$jsxInfo.Add((Add-LineToJSX $FP6 $TopLeftO))
[void]$jsxInfo.Add((Add-LineToJSX $TopLeftO $TopLeftOB))

[void]$jsxInfo.Add((Add-LineToJSX $TopRightB $TopLeftIB))
[void]$jsxInfo.Add((Add-LineToJSX $TopRightB $BotRightB))
[void]$jsxInfo.Add((Add-LineToJSX $TopLeftOB $TopLeftIB))

$ShelfBot = Get-IsoPoint 15 0 10; $ShelfBotB = Get-IsoPoint 15 $D 10
$ShelfTop = Get-IsoPoint 15 0 20; $ShelfTopB = Get-IsoPoint 15 $D 20

[void]$jsxInfo.Add((Add-LineToJSX $ShelfBot $ShelfBotB))
[void]$jsxInfo.Add((Add-LineToJSX $ShelfTop $ShelfTopB))
[void]$jsxInfo.Add((Add-LineToJSX $ShelfBotB $ShelfTopB))

$HolePts = New-Object System.Collections.ArrayList
for ($ang = 0; $ang -le 360; $ang += 10) {
    $rad = $ang * [Math]::PI / 180.0
    $cx = 30.0 + 5.0 * [Math]::Cos($rad)
    $cz = 15.0 + 5.0 * [Math]::Sin($rad)
    [void]$HolePts.Add((Get-IsoPoint $cx 0.0 $cz))
}
[void]$jsxInfo.Add((Add-PolyToJSX $HolePts))

# --- FINALIZE JSX ---
[void]$jsxInfo.Add("
try {
    var myPathItem = doc.pathItems.add('WireframeIso', lineSubPaths);
    doc.selection.deselect();
    app.foregroundColor.rgb.red = 0;
    app.foregroundColor.rgb.green = 0;
    app.foregroundColor.rgb.blue = 0;
    myPathItem.strokePath(ToolType.PENCIL, false);
} catch(e) {
    alert(e + ' Line ' + e.line);
}")

$jsxPath = Join-Path $PSScriptRoot "slotted_iso.jsx"
$jsxText = $jsxInfo -join "`n"
$jsxText | Out-File -FilePath $jsxPath -Encoding ASCII

# --- EXECUTE ---
Write-Host "Executing JSX... [$jsxPath]" -ForegroundColor Cyan
$ps = New-Object -ComObject Photoshop.Application
$ps.DoJavaScriptFile($jsxPath)
Write-Host "Photoshop Drawing Complete." -ForegroundColor Green
