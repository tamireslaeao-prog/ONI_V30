<#
    .SYNOPSIS
        ONI V24 Module Component.
    .DESCRIPTION
        Part of the ONI Automation Framework.
        Managed by The Jewel Polishing Protocol.
    .AUTHOR
        Antigravity Engine (Google DeepMind)
    .DATE
        2026-01-10
#>
# ============================================================================
# ONI BLENDER HARVESTER - 3D Asset Analyzer
# Version: 1.0
# Description: Uses Blender Python to extract objects, materials, armatures
# ============================================================================

param(
    [string]$AssetsFolder,
    [string]$OutputFile,
    [string]$BlenderPath = "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
)

if ([string]::IsNullOrEmpty($AssetsFolder)) {
    $AssetsFolder = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
}
if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[BLENDER HARVESTER] Starting..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Check Blender exists
if (-not (Test-Path $BlenderPath)) {
    # Try common paths
    $altPaths = @(
        "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        "C:\Program Files\Blender Foundation\Blender\blender.exe"
    )
    foreach ($path in $altPaths) {
        if (Test-Path $path) {
            $BlenderPath = $path
            break
        }
    }
}

$blendFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.blend" -ErrorAction SilentlyContinue
$fbxFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.fbx" -ErrorAction SilentlyContinue
$gltfFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.gltf" -ErrorAction SilentlyContinue
$glbFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.glb" -ErrorAction SilentlyContinue

$allFiles = @($blendFiles) + @($fbxFiles) + @($gltfFiles) + @($glbFiles)
Write-Host "   Found $($allFiles.Count) 3D files" -ForegroundColor Yellow

if ($allFiles.Count -eq 0) {
    @() | ConvertTo-Json | Set-Content $OutputFile -Encoding UTF8
    Write-Host "   No 3D files to process" -ForegroundColor DarkYellow
    exit 0
}

$harvestResults = @()

foreach ($file in $allFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor White
    
    # Basic metadata (full scan requires Blender running)
    $docInfo = @{
        filename     = $file.Name
        path         = $file.FullName
        format       = $file.Extension.ToUpper().Replace(".", "")
        harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        file_size_mb = [math]::Round($file.Length / 1MB, 2)
        status       = "INDEXED"
        objects      = @()
        materials    = @()
        armatures    = @()
        animations   = @()
    }
    
    # For BLEND files, we can try headless Blender scan
    if ($file.Extension -eq ".blend" -and (Test-Path $BlenderPath)) {
        Write-Host "   [SCAN] Attempting Blender headless scan..." -ForegroundColor Gray
        
        # Create temp Python script
        $pyScript = @"
import bpy
import json
import sys

result = {
    'objects': [],
    'materials': [],
    'armatures': [],
    'animations': []
}

for obj in bpy.data.objects:
    result['objects'].append({
        'name': obj.name,
        'type': obj.type
    })

for mat in bpy.data.materials:
    result['materials'].append({
        'name': mat.name
    })

for arm in bpy.data.armatures:
    result['armatures'].append({
        'name': arm.name,
        'bones': len(arm.bones)
    })

for action in bpy.data.actions:
    result['animations'].append({
        'name': action.name,
        'frames': action.frame_range[1] - action.frame_range[0]
    })

print('###JSON_START###')
print(json.dumps(result))
print('###JSON_END###')
"@
        $tempPy = [System.IO.Path]::GetTempFileName() + ".py"
        $pyScript | Set-Content $tempPy -Encoding UTF8
        
        try {
            $output = & $BlenderPath --background $file.FullName --python $tempPy 2>&1
            $jsonMatch = $output -join "`n" | Select-String -Pattern '###JSON_START###(.*)###JSON_END###' -AllMatches
            if ($jsonMatch) {
                $jsonStr = $jsonMatch.Matches[0].Groups[1].Value.Trim()
                $parsed = $jsonStr | ConvertFrom-Json
                $docInfo.objects = $parsed.objects
                $docInfo.materials = $parsed.materials
                $docInfo.armatures = $parsed.armatures
                $docInfo.animations = $parsed.animations
                $docInfo.status = "SCANNED"
                
                Write-Host "   Objects: $($parsed.objects.Count) | Materials: $($parsed.materials.Count) | Armatures: $($parsed.armatures.Count)" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "   [WARN] Blender scan failed: $_" -ForegroundColor DarkYellow
        }
        
        Remove-Item $tempPy -ErrorAction SilentlyContinue
    }
    else {
        Write-Host "   [INFO] Metadata indexed - full scan requires Blender" -ForegroundColor Yellow
    }
    
    $harvestResults += $docInfo
}

$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Blender harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray

