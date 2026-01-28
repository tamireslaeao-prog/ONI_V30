# CorelDRAW Autonomous Vectorization Pipeline (Full Protocol)
# Usage: .\corel_full_trace.ps1 -InputPath "c:\path\image.png" -OutputPath "c:\path\out.svg"

param(
    [Parameter(Mandatory=$true)]
    [string]$InputPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Get-CorelApp {
    # Try generic implementation first
    try { return New-Object -ComObject CorelDRAW.Application } catch {}
    try { return New-Object -ComObject CorelDRAW.Application.24 } catch {} # 2022
    try { return New-Object -ComObject CorelDRAW.Application.25 } catch {}
    try { return New-Object -ComObject CorelDRAW.Application.26 } catch {}
    throw "Could not Create CorelDRAW COM Object. Is it installed?"
}

try {
    Write-Host "[PS] connecting to CorelDRAW..."
    $corel = Get-CorelApp
    $corel.Visible = $true
    
    # Wait for startup
    start-sleep -seconds 2
    
    Write-Host "[PS] Creating Document..."
    $doc = $corel.CreateDocument()
    $doc.Unit = 4 # mm
    
    Write-Host "[PS] Importing Image: $InputPath"
    if (-not (Test-Path $InputPath)) {
        throw "Input file not found: $InputPath"
    }
    
    $layer = $doc.ActiveLayer
    $bitmap = $layer.Import($InputPath)
    $bitmap.AlignToPageCenter(0)
    
    # TRACE LOGIC
    # Check if we can trace
    try {
        Write-Host "[PS] Tracing Bitmap (High Quality)..."
        # cdrTraceHighQualityImage = 1, Logo = 2
        $traceSettings = $bitmap.Trace(1) 
        
        # Adjust detail if possible
        # $traceSettings.DetailLevel = 80
        
        $traceSettings.Finish()
        
        # Original bitmap is usually behind or group. 
        # Delete original bitmap? The trace result is usually selected.
        # Let's delete the bitmap explicitly if we can find it.
        $bitmap.Delete()
        
    } catch {
        Write-Host "[WARN] Native Trace failed: $_"
        Write-Host "[WARN] proceeding with raw bitmap export..."
    }
    
    # EXPORT
    if ($OutputPath) {
        Write-Host "[PS] Exporting to: $OutputPath"
        if ($OutputPath -match "\.svg$") {
            $opt = $corel.CreateStruct("ExportFilterOutSVG")
            # Defaults
            $corel.ActiveDocument.Export($OutputPath, 18, 0, $opt) # 18 = SVG filter ID usually
        }
        else {
             $doc.SaveAs($OutputPath)
        }
    }
    
    Write-Host "[SUCCESS] Processing Complete."
    
    # Optional: Keep Open for inspection or Close?
    # $doc.Close() 
    
}
catch {
    Write-Host "[ERROR] PS Automation Failed: $_"
    exit 1
}
