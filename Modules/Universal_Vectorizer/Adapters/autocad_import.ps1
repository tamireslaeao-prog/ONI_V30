
<#
.SYNOPSIS
    Imports a Universal SVG into AutoCAD.
.DESCRIPTION
    Uses COM to send the IMPORTSVG command to the active AutoCAD session.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$SvgPath
)

$ErrorActionPreference = 'Stop'

try {
    # 1. Connect to AutoCAD
    $acad = $null
    
    # Try generic ProgID
    try {
        $acad = [System.Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
    }
    catch {
        # Try version specific if needed
        Write-Error "Could not connect to AutoCAD. Is it running?"
        exit 1
    }

    $doc = $acad.ActiveDocument
    
    Write-Host "Connected to AutoCAD. Importing $SvgPath..."
    
    # 2. Send Command
    # AutoCAD's COM 'SendCommand' is the most reliable way to invoke commands like IMPORTSVG
    # Syntax: IMPORTSVG <Enter> <Path> <Enter> <Options...>
    # Note: Path must not have spaces or be quoted properly.
    
    # 'filedia' must be 0 for command line file input usually
    $doc.SendCommand("(setvar ""FILEDIA"" 0) ")
    
    # We use a LISP expression to import if possible, or just keystrokes via SendCommand
    # -IMPORTSVG is the command line version
    
    $cmd = "-IMPORTSVG `"$SvgPath`" 0,0 1 0 " # Path, Insertion Point, Scale, Rotation
    $doc.SendCommand($cmd)
    
    # Restore FILEDIA
    $doc.SendCommand("(setvar ""FILEDIA"" 1) ")
    
    Write-Host "✅ Command Sent."

}
catch {
    Write-Error "AutoCAD Adapter Error: $_"
    exit 1
}
