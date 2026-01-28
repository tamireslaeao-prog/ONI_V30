<#
.SYNOPSIS
    ONI V23 - MASTER SHORTCUTS INSTALLER (SIMPLE)
    Wrapper simples para instaladores individuais.
#>

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
# ScriptDir = Modules/Core/Setup
$ModulesRoot = (Get-Item $ScriptDir).Parent.Parent.FullName

function Run-Installer {
    param($Module, $Script, $Name, $IsPython = $false)
    $path = Join-Path $ModulesRoot "$Module\Setup\$Script"
    
    if (Test-Path $path) {
        Write-Host "Instalando $Name..." -ForegroundColor Cyan
        if ($IsPython) {
            python $path
        }
        else {
            powershell -ExecutionPolicy Bypass -File $path
        }
    }
    else {
        Write-Host "Installer nao encontrado: $Module/$Script" -ForegroundColor DarkGray
    }
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ONI V24 - MASTER INSTALLER (MODULAR)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# CorelDRAW
Run-Installer -Module "Corel" -Script "Install-CorelShortcuts.ps1" -Name "CorelDRAW"

# Photoshop
Run-Installer -Module "Photoshop" -Script "Install-PSShortcuts.ps1" -Name "Photoshop"

# After Effects
Run-Installer -Module "AfterEffects" -Script "Install-AEShortcuts.ps1" -Name "After Effects"

# Illustrator
Run-Installer -Module "Illustrator" -Script "Install-AIShortcuts.ps1" -Name "Illustrator"

# Foxit
Run-Installer -Module "Foxit" -Script "Install-FoxitShortcuts.ps1" -Name "Foxit PDF"

# Blender (Python)
Run-Installer -Module "Blender" -Script "Install-BlenderShortcuts.py" -Name "Blender" -IsPython $true

Write-Host ""
Write-Host "Concluido." -ForegroundColor Green
