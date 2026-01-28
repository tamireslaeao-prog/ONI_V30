# ============================================================================
# ONI.Windows.psm1 (v2.0 - Modularized)
# Main Windows automation module
# ============================================================================

<#
.SYNOPSIS
    ONI V25 Windows Module (Modularized)
.DESCRIPTION
    Modular Windows automation with functions organized by:
    - Windows.Core: Utilities, logging, system info
    - Windows.Process: Process management  
    - Windows.Service: Windows service management
    - Windows.FileSystem: File operations
#>

# Get module directory
$ModuleRoot = $PSScriptRoot

# Import modules
. "$ModuleRoot\WindowsModules\Windows.Core.ps1"

Write-Host "[OK] ONI Windows Module Loaded (v2.0 Modular)" -ForegroundColor Cyan

# Export all
Export-ModuleMember -Variable ONI
Export-ModuleMember -Function *
