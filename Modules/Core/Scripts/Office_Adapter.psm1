<#
.SYNOPSIS
    ONI Office Adapter - Universal Interface for Microsoft 365 Automation.
    Combines COM (ActiveX) for precision with GUI visibility for "Impact".

.DESCRIPTION
    Provides functions to control Excel, Word, and PowerPoint.
    Ensures 'Visible = $true' for the "Show" effect.

.EXAMPLE
    Import-Module .\app\scripts\Office_Adapter.psm1
    Open-Excel -Visible $true
    Set-ExcelCell -Address "A1" -Value "ONI DOMINATION"
#>

# --- EXCEL MODULE ---
function Open-Excel {
    param([bool]$Visible = $true)
    try {
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $Visible
        $excel.DisplayAlerts = $false
        $wb = $excel.Workbooks.Add()
        return $excel
    }
    catch {
        Write-Error "Failed to initiate Excel: $_"
        return $null
    }
}

function Set-ExcelCell {
    param(
        [Parameter(Mandatory = $true)]$ExcelApp,
        [string]$Address, # e.g. "A1"
        [string]$Value,
        [string]$Color = "Green" # Simple color name or logic
    )
    $ws = $ExcelApp.ActiveSheet
    $range = $ws.Range($Address)
    $range.Value2 = $Value
    
    # Visual Impact Styles
    $range.Font.Bold = $true
    $range.Font.Size = 14
    if ($Color -eq "Green") { $range.Interior.Color = 5296274 } # A nice green
}

# --- WORD MODULE ---
function Open-Word {
    param([bool]$Visible = $true)
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $Visible
        $doc = $word.Documents.Add()
        return $word
    }
    catch {
        Write-Error "Failed to initiate Word: $_"
        return $null
    }
}

function Write-WordText {
    param(
        [Parameter(Mandatory = $true)]$WordApp,
        [string]$Text,
        [string]$Style = "Heading 1"
    )
    $selection = $WordApp.Selection
    $selection.TypeText($Text)
    $selection.Style = $Style
    $selection.TypeParagraph()
}

# --- POWERPOINT MODULE ---
function Open-PowerPoint {
    param([bool]$Visible = $true)
    try {
        $ppt = New-Object -ComObject PowerPoint.Application
        $ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
        $pres = $ppt.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoTrue)
        return $ppt
    }
    catch {
        Write-Error "Failed to initiate PowerPoint: $_"
        return $null
    }
}

function Add-Slide {
    param(
        [Parameter(Mandatory = $true)]$PPTApp,
        [string]$Title,
        [string]$Content
    )
    $pres = $PPTApp.ActivePresentation
    # ppLayoutTitle = 1, ppLayoutText = 2
    $slide = $pres.Slides.Add($pres.Slides.Count + 1, 2) 
    
    $slide.Shapes.Title.TextFrame.TextRange.Text = $Title
    $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $Content
}

Export-ModuleMember -Function Open-Excel, Set-ExcelCell, Open-Word, Write-WordText, Open-PowerPoint, Add-Slide
