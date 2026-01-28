<#
.SYNOPSIS
    ONI AutoCAD Adapter - PowerShell Wrapper for Python Bridge
    
.DESCRIPTION
    PowerShell module that wraps the Python COM Bridge for simple AutoCAD automation.
    Can be used standalone or in combination with Python scripts.
    
.VERSION
    1.0.0
    
.DATE
    2026-01-14
    
.AUTHOR
    ONI Team
#>

# ============================================================================
# MODULE: CONNECTION
# ============================================================================

function Connect-AutoCAD {
    <#
    .SYNOPSIS
        Connect to AutoCAD via COM
    #>
    [CmdletBinding()]
    param(
        [switch]$CreateNewDoc
    )
    
    try {
        # Try to get existing instance
        $script:acad = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
        Write-Host "[OK] Connected to existing AutoCAD" -ForegroundColor Green
    }
    catch {
        # Create new instance
        $script:acad = New-Object -ComObject AutoCAD.Application
        $script:acad.Visible = $true
        Write-Host "[OK] Started new AutoCAD instance" -ForegroundColor Green
    }
    
    # Get or create document
    if ($script:acad.Documents.Count -eq 0) {
        if ($CreateNewDoc) {
            $script:doc = $script:acad.Documents.Add()
            Write-Host "[OK] Created new document" -ForegroundColor Green
        }
        else {
            throw "No document open"
        }
    }
    else {
        $script:doc = $script:acad.ActiveDocument
    }
    
    $script:modelSpace = $script:doc.ModelSpace
    return $true
}

function Disconnect-AutoCAD {
    <#
    .SYNOPSIS
        Safely disconnect from AutoCAD
    #>
    $script:modelSpace = $null
    $script:doc = $null
    $script:acad = $null
    [System.GC]::Collect()
    Write-Host "[OK] Disconnected from AutoCAD" -ForegroundColor Green
}

function Get-AutoCADInfo {
    <#
    .SYNOPSIS
        Get AutoCAD version and document info
    #>
    if (-not $script:acad) {
        return @{ Error = "Not connected" }
    }
    
    return @{
        Version = $script:acad.Version
        Document = $script:doc.Name
        Path = $script:doc.Path
        Saved = $script:doc.Saved
    }
}

# ============================================================================
# MODULE: DRAWING
# ============================================================================

function New-CADLine {
    <#
    .SYNOPSIS
        Draw a line from point to point
    .EXAMPLE
        New-CADLine -X1 0 -Y1 0 -X2 100 -Y2 100
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][double]$X1,
        [Parameter(Mandatory)][double]$Y1,
        [Parameter(Mandatory)][double]$X2,
        [Parameter(Mandatory)][double]$Y2,
        [double]$Z1 = 0,
        [double]$Z2 = 0
    )
    
    $startPoint = @($X1, $Y1, $Z1)
    $endPoint = @($X2, $Y2, $Z2)
    
    $line = $script:modelSpace.AddLine($startPoint, $endPoint)
    return $line
}

function New-CADCircle {
    <#
    .SYNOPSIS
        Draw a circle
    .EXAMPLE
        New-CADCircle -CenterX 50 -CenterY 50 -Radius 25
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][double]$CenterX,
        [Parameter(Mandatory)][double]$CenterY,
        [Parameter(Mandatory)][double]$Radius,
        [double]$CenterZ = 0
    )
    
    $center = @($CenterX, $CenterY, $CenterZ)
    $circle = $script:modelSpace.AddCircle($center, $Radius)
    return $circle
}

function New-CADRectangle {
    <#
    .SYNOPSIS
        Draw a rectangle using polyline
    .EXAMPLE
        New-CADRectangle -X 0 -Y 0 -Width 100 -Height 50
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][double]$X,
        [Parameter(Mandatory)][double]$Y,
        [Parameter(Mandatory)][double]$Width,
        [Parameter(Mandatory)][double]$Height
    )
    
    $points = @(
        $X, $Y,
        $X + $Width, $Y,
        $X + $Width, $Y + $Height,
        $X, $Y + $Height
    )
    
    $pline = $script:modelSpace.AddLightWeightPolyline($points)
    $pline.Closed = $true
    return $pline
}

function New-CADPolyline {
    <#
    .SYNOPSIS
        Draw a polyline from array of points
    .EXAMPLE
        New-CADPolyline -Points @(0,0, 100,0, 100,100, 0,100) -Closed
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][double[]]$Points,
        [switch]$Closed
    )
    
    $pline = $script:modelSpace.AddLightWeightPolyline($Points)
    
    if ($Closed) {
        $pline.Closed = $true
    }
    
    return $pline
}

# ============================================================================
# MODULE: TEXT
# ============================================================================

function New-CADText {
    <#
    .SYNOPSIS
        Add single-line text
    .EXAMPLE
        New-CADText -Text "Hello" -X 10 -Y 10 -Height 5
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][double]$X,
        [Parameter(Mandatory)][double]$Y,
        [double]$Height = 2.5,
        [double]$Rotation = 0,
        [double]$Z = 0
    )
    
    $insertion = @($X, $Y, $Z)
    $textObj = $script:modelSpace.AddText($Text, $insertion, $Height)
    
    if ($Rotation -ne 0) {
        $textObj.Rotation = [Math]::PI * $Rotation / 180
    }
    
    return $textObj
}

# ============================================================================
# MODULE: LAYERS
# ============================================================================

function New-CADLayer {
    <#
    .SYNOPSIS
        Create a new layer
    .EXAMPLE
        New-CADLayer -Name "Cuts" -Color 1
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name,
        [int]$Color = 7
    )
    
    try {
        $layer = $script:doc.Layers.Add($Name)
        $layer.Color = $Color
        Write-Host "[OK] Created layer: $Name" -ForegroundColor Green
        return $layer
    }
    catch {
        Write-Warning "Failed to create layer: $_"
        return $null
    }
}

function Set-CADLayer {
    <#
    .SYNOPSIS
        Set current layer
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name
    )
    
    $script:doc.ActiveLayer = $script:doc.Layers.Item($Name)
}

# ============================================================================
# MODULE: FILE OPERATIONS
# ============================================================================

function Save-CADDrawing {
    <#
    .SYNOPSIS
        Save drawing
    .EXAMPLE
        Save-CADDrawing -Path "C:\output\drawing.dwg"
    #>
    [CmdletBinding()]
    param(
        [string]$Path
    )
    
    if ($Path) {
        $script:doc.SaveAs($Path)
        Write-Host "[OK] Saved: $Path" -ForegroundColor Green
    }
    else {
        $script:doc.Save()
        Write-Host "[OK] Document saved" -ForegroundColor Green
    }
}

function Close-CADDrawing {
    <#
    .SYNOPSIS
        Close current drawing
    #>
    [CmdletBinding()]
    param(
        [switch]$Save
    )
    
    if ($Save) {
        $script:doc.Close($true)
    }
    else {
        $script:doc.Close($false)
    }
    
    $script:doc = $null
    $script:modelSpace = $null
}

# ============================================================================
# MODULE: UTILITIES
# ============================================================================

function Invoke-CADCommand {
    <#
    .SYNOPSIS
        Send command to AutoCAD command line
    .EXAMPLE
        Invoke-CADCommand "ZOOM E "
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Command
    )
    
    $script:doc.SendCommand("$Command`n")
}

function Invoke-CADZoomExtents {
    <#
    .SYNOPSIS
        Zoom to show all objects
    #>
    Invoke-CADCommand "ZOOM E "
}

function Invoke-CADRegen {
    <#
    .SYNOPSIS
        Regenerate drawing
    #>
    Invoke-CADCommand "REGEN "
}

# ============================================================================
# EXPORTS
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-AutoCAD',
    'Disconnect-AutoCAD',
    'Get-AutoCADInfo',
    'New-CADLine',
    'New-CADCircle',
    'New-CADRectangle',
    'New-CADPolyline',
    'New-CADText',
    'New-CADLayer',
    'Set-CADLayer',
    'Save-CADDrawing',
    'Close-CADDrawing',
    'Invoke-CADCommand',
    'Invoke-CADZoomExtents',
    'Invoke-CADRegen'
)
