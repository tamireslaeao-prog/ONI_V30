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
# ONI PSD DEEP HARVESTER v2.1 - Recursive Layer Analyzer (ExtendScript Safe)
# Description: Uses COM recursion to find all nested layers
# ============================================================================

param(
    [string]$AssetsFolder,
    [string]$OutputFile
)

if ([string]::IsNullOrEmpty($AssetsFolder)) {
    $AssetsFolder = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "Assets"
}
if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent)) "assets_db.json"
}

Write-Host "[DEEP HARVESTER v2.1] Starting recursive scan..." -ForegroundColor Cyan
Write-Host "   Target: $AssetsFolder" -ForegroundColor Gray

# Connect to Photoshop
try {
    $ps = New-Object -ComObject Photoshop.Application
    $ps.Preferences.RulerUnits = 1
    Write-Host "   [OK] Photoshop Connected (v$($ps.Version))" -ForegroundColor Green
}
catch {
    Write-Host "   [FAIL] Photoshop connection failed: $_" -ForegroundColor Red
    exit 1
}

$psdFiles = Get-ChildItem -Path $AssetsFolder -Filter "*.psd"
Write-Host "   Found $($psdFiles.Count) PSD files" -ForegroundColor Yellow

$harvestResults = @()

# Recursive function to traverse layers using COM
function Get-AllLayersRecursive {
    param(
        $Parent,
        [int]$Depth = 0,
        [hashtable]$Results
    )
    
    try {
        # Try LayerSets (groups)
        foreach ($group in $Parent.LayerSets) {
            $Results.groups += @{
                name  = $group.Name
                depth = $Depth
            }
            $Results.allLayers += @{
                name  = $group.Name
                type  = "GROUP"
                depth = $Depth
            }
            Write-Host "      $('  ' * $Depth)[GROUP] $($group.Name)" -ForegroundColor Magenta
            
            # Recurse into group
            Get-AllLayersRecursive -Parent $group -Depth ($Depth + 1) -Results $Results
        }
    }
    catch {}
    
    try {
        # Try ArtLayers (actual layers)
        foreach ($layer in $Parent.ArtLayers) {
            $layerInfo = @{
                name  = $layer.Name
                depth = $Depth
                type  = "LAYER"
            }
            
            # Get layer kind
            try {
                $kindValue = [int]$layer.Kind
                $layerInfo.kindValue = $kindValue
                
                # Check for Smart Object (Kind = 17)
                if ($kindValue -eq 17) {
                    $Results.smartObjects += @{
                        name  = $layer.Name
                        depth = $Depth
                    }
                    Write-Host "      $('  ' * $Depth)[SMART] $($layer.Name)" -ForegroundColor Blue
                    $layerInfo.type = "SMART_OBJECT"
                }
                # Check for Text Layer (Kind = 2)
                elseif ($kindValue -eq 2) {
                    $textContent = ""
                    try {
                        $textContent = $layer.TextItem.Contents
                        if ($textContent.Length -gt 50) {
                            $textContent = $textContent.Substring(0, 50) + "..."
                        }
                    }
                    catch {}
                    
                    $Results.textLayers += @{
                        name    = $layer.Name
                        content = $textContent
                        depth   = $Depth
                    }
                    Write-Host "      $('  ' * $Depth)[TEXT] $($layer.Name): '$textContent'" -ForegroundColor Yellow
                    $layerInfo.type = "TEXT"
                }
                else {
                    Write-Host "      $('  ' * $Depth)[LAYER] $($layer.Name) (kind=$kindValue)" -ForegroundColor Gray
                }
            }
            catch {
                Write-Host "      $('  ' * $Depth)[LAYER] $($layer.Name)" -ForegroundColor Gray
            }
            
            $Results.allLayers += $layerInfo
        }
    }
    catch {}
}

foreach ($psd in $psdFiles) {
    Write-Host ""
    Write-Host "[FILE] $($psd.Name)" -ForegroundColor White
    
    try {
        $doc = $ps.Open($psd.FullName)
        
        # Initialize results hashtable
        $scanResults = @{
            smartObjects = @()
            textLayers   = @()
            groups       = @()
            allLayers    = @()
        }
        
        $docInfo = @{
            filename     = $psd.Name
            path         = $psd.FullName
            width        = $null
            height       = $null
            harvested_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        }
        
        try {
            $docInfo.width = $doc.Width.Value
            $docInfo.height = $doc.Height.Value
        }
        catch {}
        
        Write-Host "   Scanning layers recursively..." -ForegroundColor Gray
        
        # Run recursive scan
        Get-AllLayersRecursive -Parent $doc -Depth 0 -Results $scanResults
        
        $docInfo.smart_objects = $scanResults.smartObjects
        $docInfo.text_layers = $scanResults.textLayers
        $docInfo.layer_groups = $scanResults.groups
        $docInfo.all_layers = $scanResults.allLayers
        $docInfo.total_layers = $scanResults.allLayers.Count
        
        Write-Host "   ---" -ForegroundColor DarkGray
        Write-Host "   Total: $($docInfo.total_layers) items | Smart: $($scanResults.smartObjects.Count) | Text: $($scanResults.textLayers.Count) | Groups: $($scanResults.groups.Count)" -ForegroundColor Green
        
        $doc.Close(2)
        $harvestResults += $docInfo
        
    }
    catch {
        Write-Host "   [ERROR] $($psd.Name): $_" -ForegroundColor Red
    }
}

# Save results
$harvestResults | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "[COMPLETE] Deep harvest finished" -ForegroundColor Cyan
Write-Host "   Output: $OutputFile" -ForegroundColor Gray
Write-Host "   PSDs: $($harvestResults.Count)" -ForegroundColor White

