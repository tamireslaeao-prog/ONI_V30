<#
.SYNOPSIS
    ONI Auto-Discovery Tool for Creative Apps.
    Finds the LATEST installed version of Blender and After Effects.

.OUTPUTS
    JSON object with 'Blender' and 'AfterEffects' properties.
#>

$Results = @{
    Blender = $null
    AfterEffects = $null
}

# --- FIND BLENDER ---
$BlenderBase = "C:\Program Files\Blender Foundation"
if (Test-Path $BlenderBase) {
    # Get all "Blender X.X" folders, sort descending (5.0 > 4.0)
    $Versions = Get-ChildItem -Path $BlenderBase -Directory | 
                Where-Object { $_.Name -match "Blender \d+\.\d+" } | 
                Sort-Object Name -Descending

    foreach ($Ver in $Versions) {
        $ExePath = Join-Path $Ver.FullName "blender.exe"
        if (Test-Path $ExePath) {
            $Results.Blender = $ExePath
            break # Found latest
        }
    }
}

# --- FIND AFTER EFFECTS ---
$AdobeBase = "C:\Program Files\Adobe"
if (Test-Path $AdobeBase) {
    # Get "Adobe After Effects 20XX" folders, sort descending
    $Versions = Get-ChildItem -Path $AdobeBase -Directory | 
                Where-Object { $_.Name -match "Adobe After Effects" } | 
                Sort-Object Name -Descending

    foreach ($Ver in $Versions) {
        $ExePath = Join-Path $Ver.FullName "Support Files\AfterFX.exe"
        if (Test-Path $ExePath) {
            $Results.AfterEffects = $ExePath
            break # Found latest
        }
    }
}

# Output as JSON for Python/Agent consumption
$Results | ConvertTo-Json -Compress
