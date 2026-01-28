# ONI_AutoCAD_ActiveX.psm1 - The Proven Version
# Confirmed by Diagnostic: Must use .NET Double[] explicit arrays.

# Constants
New-Variable -Name acUnion -Value 0 -Option Constant -Force
New-Variable -Name acIntersection -Value 1 -Option Constant -Force
New-Variable -Name acSubtraction -Value 2 -Option Constant -Force
New-Variable -Name acAllViewports -Value 1 -Option Constant -Force

function Connect-Acad {
    $acad = $null
    try {
        $acad = [System.Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
        Write-Host "Connected to running AutoCAD." -ForegroundColor Green
    }
    catch {
        Write-Warning "Could not attach. Launching..."
        try {
            $acad = New-Object -ComObject "AutoCAD.Application"
            $acad.Visible = $true
        }
        catch { return $null }
    }
    
    if ($acad) {
        try {
            if ($acad.Documents.Count -eq 0) { $acad.Documents.Add() }
        }
        catch { }
    }
    return $acad
}

function Create-Point([double]$x, [double]$y, [double]$z) {
    # CRITICAL: Must be strict .NET Double Array.
    # PowerShell Arrays (@()) fail the COM marshaller for AddBox.
    $pt = New-Object "Double[]" 3
    $pt[0] = $x; $pt[1] = $y; $pt[2] = $z
    return $pt
}

function New-AcadBox {
    param($Acad, [double]$X, [double]$Y, [double]$Z, [double]$Len, [double]$Width, [double]$Height)
    Write-Host "DEBUG: Box Origin($X,$Y,$Z) Dim($Len,$Width,$Height)" -ForegroundColor DarkGray
    $pt = Create-Point $X $Y $Z
    return $Acad.ActiveDocument.ModelSpace.AddBox($pt, $Len, $Width, $Height)
}

function New-AcadCylinder {
    param($Acad, [double]$X, [double]$Y, [double]$Z, [double]$Radius, [double]$Height)
    Write-Host "DEBUG: Cyl Center($X,$Y,$Z) Rad($Radius) H($Height)" -ForegroundColor DarkGray
    $pt = Create-Point $X $Y $Z
    return $Acad.ActiveDocument.ModelSpace.AddCylinder($pt, $Radius, $Height)
}

function Invoke-AcadBoolean {
    param($Target, $Tool, $OpStr)
    $op = 0
    switch ($OpStr) {
        "UNION" { $op = 0 }
        "INTERSECT" { $op = 1 }
        "SUBTRACT" { $op = 2 }
    }
    Write-Host "DEBUG: Boolean $OpStr" -ForegroundColor DarkGray
    $Target.Boolean($op, $Tool)
}

function Set-ViewIso {
    param($Acad)
    $vp = $Acad.ActiveDocument.ActiveViewport
    $pt = Create-Point 1 -1 1
    $vp.Direction = $pt
    $Acad.ActiveDocument.ActiveViewport = $vp
    $Acad.ActiveDocument.Regen(1) 
    $Acad.Application.ZoomExtents()
}

Export-ModuleMember -Function Connect-Acad, New-AcadBox, New-AcadCylinder, Invoke-AcadBoolean, Set-ViewIso
