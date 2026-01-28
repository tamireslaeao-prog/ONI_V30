
<#
.SYNOPSIS
    Imports a Universal SVG into CorelDRAW.
.DESCRIPTION
    Connects to the active CorelDRAW instance and imports the specified SVG file into the active layer.
.PARAMETER SvgPath
    The full path to the SVG file.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$SvgPath
)

$ErrorActionPreference = 'Stop'

try {
    # 1. Connect to CorelDRAW
    $corel = $null
    $progIds = @('CorelDRAW.Application.26', 'CorelDRAW.Application', 'CorelDRAW.Application.25')
    
    foreach ($progId in $progIds) {
        try {
            $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
            Write-Host "Connected to $progId"
            break
        }
        catch {}
    }

    if (-not $corel) {
        Write-Error "Could not connect to CorelDRAW. Is it running?"
        exit 1
    }

    # 2. Get/Create Document
    if (-not $corel.ActiveDocument) {
        $corel.CreateDocument()
    }
    $doc = $corel.ActiveDocument

    # 3. Import SVG
    # cdrSVG = 10 (Filter ID for SVG usually, checking import filters can be tricky)
    # Using Import() method which auto-detects by extension usually works best or explicit filter.
    # structImportOptions / Filter ID:
    # Corel's Import method: Layer.Import(FileName, Filter, Options)
    
    Write-Host "Importing $SvgPath..."
    
    # 0 = cdrAutoSense
    $doc.ActiveLayer.Import($SvgPath, 0)
    
    Write-Host "✅ Import Successful."

}
catch {
    Write-Error "Fusion Error: $_"
    exit 1
}
