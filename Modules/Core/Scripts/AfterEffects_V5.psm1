# ONI V5 - After Effects PowerShell Adapter
# Generates "Smart Payloads" using ONI_AE_Library.jsx
# Save as: C:\Users\user\Desktop\ONI V19\app\core\AfterEffects_V5.psm1

$Global:AEBuffer = ""

function New-AEBuffer {
    $Global:AEBuffer = "// ONI V5 Auto-Generated Script`n"
    $Global:AEBuffer += "try {`n"
}

function Add-AEOperation {
    param([string]$ScriptLine)
    $Global:AEBuffer += "    " + $ScriptLine + "`n"
}

function New-AEProject {
    New-AEBuffer
    Add-AEOperation "AE.createProject();"
}

function New-AEComp {
    param(
        [string]$Name = "ONI_Comp",
        [int]$Width = 1920, 
        [int]$Height = 1080, 
        [int]$Duration = 10
    )
    # Define a variable for the comp in JS scope
    Add-AEOperation "var activeComp = AE.createComp('$Name', $Width, $Height, $Duration);"
}

function Add-AEText {
    param(
        [string]$Content,
        [int]$Size = 100,
        [string]$Color = "[1, 1, 1]",
        [string]$VarName = "txtLayer"
    )
    # Add text and assign to a JS variable for further chaining
    Add-AEOperation "var $VarName = AE.addText(activeComp, '$Content', $Size, $Color);"
}

function Add-AESolid {
    param(
        [string]$Name = "Background",
        [string]$Color = "[0, 0, 0]",
        [string]$VarName = "solidLayer"
    )
    Add-AEOperation "var $VarName = AE.addSolid(activeComp, $Color, '$Name');"
    Add-AEOperation "$VarName.moveToEnd();" # Typically solids are backgrounds
}

function Add-AEEffect {
    param(
        [string]$LayerVar = "txtLayer",
        [string]$EffectName
    )
    Add-AEOperation "AE.addEffect($LayerVar, '$EffectName');"
}

function Add-AEAnimation {
    param(
        [string]$LayerVar = "txtLayer",
        [string]$Property = "Opacity",
        [string]$Keys = "[[0, 0], [1, 100]]" # Time, Value pairs
    )
    Add-AEOperation "AE.animate($LayerVar, '$Property', $Keys);"
}

function Add-AEShapeLayer {
    param(
        [string]$Name = "Shape Layer",
        [string]$VarName = "shapeLayer"
    )
    Add-AEOperation "var $VarName = AE.addShape(activeComp, '$Name');"
}

function Set-AEExpression {
    param(
        [string]$LayerVar = "shapeLayer",
        [string]$Property = "Position",
        [string]$Expression
    )
    # Escape newlines for JS string
    # Flatten expression to single line for robust injection
    $CleanExpr = $Expression -replace "`r`n", " " -replace "`n", " " -replace "'", "\'"
    Add-AEOperation "AE.setExpression($LayerVar, '$Property', '$CleanExpr');"
}

function Invoke-AEExecution {
    param([switch]$Wait)
    
    $Global:AEBuffer += "} catch(e) { alert('ONI ERROR: ' + e.toString()); }`n"
    
    # 1. Read the Library
    $LibPath = "C:\Users\user\Desktop\ONI V19\app\lib\ae\ONI_AE_Library.jsx"
    if (!(Test-Path $LibPath)) { Throw "ONI_AE_Library.jsx not found at $LibPath" }
    $LibContent = Get-Content $LibPath -Raw

    # 2. Combine Library + Payload
    $FinalScript = $LibContent + "`n`n" + $Global:AEBuffer
    
    # 3. Save to Temp
    $TempJSX = "$env:TEMP\ONI_AE_Payload_V5.jsx"
    $FinalScript | Out-File -Encoding UTF8 $TempJSX

    # 4. Launch AE Processor
    # Robust Discovery (From ONI V4)
    Write-Host "Locating AfterFX..." -ForegroundColor Yellow
    $AEPath = Get-ChildItem "C:\Program Files\Adobe" -Recurse -Filter "AfterFX.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    
    if (-not $AEPath) {
        Write-Error "AfterFX.exe not found in C:\Program Files\Adobe"
        return
    }

    Write-Host "🚀 Launching After Effects V5 Payload..." -ForegroundColor Cyan
    Write-Host "Target: $AEPath" -ForegroundColor Gray
    Start-Process -FilePath $AEPath -ArgumentList "-r `"$TempJSX`"" -Wait:$Wait
}

Export-ModuleMember -Function *
