# ============================================================================
# ONI.Word.Automation.psm1
# Main module that imports all sub-modules
# Version: 2.0 (Modularized)
# ============================================================================

<#
.SYNOPSIS
Complete automation system for Microsoft Word document generation

.DESCRIPTION
Modular Word automation with functions organized by:
- Word.Connection: COM connection management
- Word.Document: Document operations
- Word.Content: Content creation
- Word.Tables: Table operations
- Word.Images: Image handling

.EXAMPLE
Import-Module .\ONI.Word.Automation.psm1
$word = Connect-Word
$doc = New-WordDocument -Word $word
Add-WordText -Document $doc -Text "Hello World"
#>

# Get module directory
$ModuleRoot = $PSScriptRoot

# Import sub-modules
. "$ModuleRoot\WordAutomation\Word.Connection.ps1"
. "$ModuleRoot\WordAutomation\Word.Document.ps1"
. "$ModuleRoot\WordAutomation\Word.Content.ps1"

Write-Host "[OK] ONI Word Automation Module Loaded (v2.0 Modular)" -ForegroundColor Cyan

# Export all functions
Export-ModuleMember -Function *
