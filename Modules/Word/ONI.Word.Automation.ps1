# ============================================================================
# ONI.Word.Automation.ps1
# Version: 1.0
# Description: Complete document automation system for Microsoft Word
# ============================================================================

<#
.SYNOPSIS
Complete automation system for Microsoft Word document generation

.DESCRIPTION
This module provides functions to:
- Generate corporate documents from templates
- Apply professional styles automatically
- Batch process reports and certificates
- Create tables, charts, and data visualizations
- Export to multiple formats (PDF, HTML, DOCX)

.EXAMPLE
$word = Connect-Word
New-CorporateReport -Word $word -Title "Q4 Financial Report" -Style "modern_corporate"
#>

# ============================================================================
# WORD CONNECTION MANAGEMENT
# ============================================================================

function Connect-Word {
    <#
    .SYNOPSIS
    Establishes COM connection to Microsoft Word
    
    .EXAMPLE
    $word = Connect-Word
    #>
    
    try {
        # Try to connect to existing instance
        $word = [Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
        Write-Host "[OK] Connected to existing Word instance" -ForegroundColor Green
    }
    catch {
        # Create new instance
        try {
            $word = New-Object -ComObject Word.Application
            $word.Visible = $true
            Write-Host "[OK] Created new Word instance" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to Word. Ensure Microsoft Word is installed."
            return $null
        }
    }
    
    return $word
}

function Disconnect-Word {
    <#
    .SYNOPSIS
    Releases COM connection and optionally closes Word
    #>
    param(
        $Word,
        [switch]$Close
    )
    
    if ($Word) {
        if ($Close) {
            $Word.Quit()
            Write-Host "[OK] Word closed" -ForegroundColor Green
        }
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Word) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Host "[OK] Disconnected from Word" -ForegroundColor Green
    }
}

# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

function New-WordDocument {
    <#
    .SYNOPSIS
    Creates new Word document
    
    .EXAMPLE
    New-WordDocument -Word $word -Template "Normal"
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [string]$Template = "",
        [switch]$Visible = $true
    )
    
    $doc = $Word.Documents.Add($Template)
    $Word.Visible = $Visible
    
    Write-Host "[OK] Document created" -ForegroundColor Green
    
    return $doc
}

function Open-WordDocument {
    <#
    .SYNOPSIS
    Opens existing Word document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [Parameter(Mandatory = $true)]
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Document not found: $Path"
        return $null
    }
    
    $doc = $Word.Documents.Open($Path)
    Write-Host "[OK] Document opened: $Path" -ForegroundColor Green
    
    return $doc
}

function Save-WordDocument {
    <#
    .SYNOPSIS
    Saves Word document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [string]$Path,
        [string]$Format = "docx" # docx, pdf, html, txt
    )
    
    # Format constants
    $formats = @{
        "docx" = 16  # wdFormatXMLDocument
        "pdf"  = 17  # wdFormatPDF
        "html" = 8   # wdFormatHTML
        "txt"  = 2   # wdFormatText
        "rtf"  = 6   # wdFormatRTF
    }
    
    if ($Path) {
        $formatCode = $formats[$Format.ToLower()]
        if ($formatCode) {
            $Document.SaveAs([ref]$Path, [ref]$formatCode)
        }
        else {
            $Document.SaveAs([ref]$Path)
        }
        Write-Host "[OK] Document saved: $Path" -ForegroundColor Green
    }
    else {
        $Document.Save()
        Write-Host "[OK] Document saved" -ForegroundColor Green
    }
}

# ============================================================================
# CONTENT CREATION
# ============================================================================

function Add-WordText {
    <#
    .SYNOPSIS
    Adds text to document
    
    .EXAMPLE
    Add-WordText -Document $doc -Text "Hello World" -Style "Title"
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [string]$Style = "Normal",
        [string]$FontName = "",
        [int]$FontSize = 0,
        [string]$FontColor = "",
        [switch]$Bold,
        [switch]$Italic,
        [string]$Alignment = "Left" # Left, Center, Right, Justify
    )
    
    $selection = $Document.Application.Selection
    
    # Apply style if specified
    if ($Style) {
        try {
            $selection.Style = $Document.Styles[$Style]
        }
        catch {
            Write-Warning "Style '$Style' not found, using Normal"
        }
    }
    
    # Apply formatting
    if ($FontName) {
        $selection.Font.Name = $FontName
    }
    if ($FontSize -gt 0) {
        $selection.Font.Size = $FontSize
    }
    if ($Bold) {
        $selection.Font.Bold = 1
    }
    if ($Italic) {
        $selection.Font.Italic = 1
    }
    if ($FontColor) {
        $rgb = ConvertFrom-HexColor -HexColor $FontColor
        $selection.Font.Color = $rgb.R + ($rgb.G * 256) + ($rgb.B * 65536)
    }
    
    # Set alignment
    $alignments = @{
        "Left"    = 0     # wdAlignParagraphLeft
        "Center"  = 1   # wdAlignParagraphCenter
        "Right"   = 2    # wdAlignParagraphRight
        "Justify" = 3  # wdAlignParagraphJustify
    }
    if ($alignments.ContainsKey($Alignment)) {
        $selection.ParagraphFormat.Alignment = $alignments[$Alignment]
    }
    
    # Type text
    $selection.TypeText($Text)
    $selection.TypeParagraph()
}

function Add-WordHeading {
    <#
    .SYNOPSIS
    Adds heading to document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [int]$Level = 1 # 1-9
    )
    
    $styleName = "Heading $Level"
    Add-WordText -Document $Document -Text $Text -Style $styleName
}

function Add-WordParagraph {
    <#
    .SYNOPSIS
    Adds paragraph with formatting
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [double]$SpaceBefore = 0,
        [double]$SpaceAfter = 0,
        [double]$LineSpacing = 1.0,
        [string]$Alignment = "Left"
    )
    
    $selection = $Document.Application.Selection
    
    # Set spacing
    if ($SpaceBefore -gt 0) {
        $selection.ParagraphFormat.SpaceBefore = $SpaceBefore
    }
    if ($SpaceAfter -gt 0) {
        $selection.ParagraphFormat.SpaceAfter = $SpaceAfter
    }
    
    # Set line spacing
    $selection.ParagraphFormat.LineSpacingRule = 0 # wdLineSpaceMultiple
    $selection.ParagraphFormat.LineSpacing = $LineSpacing * 12
    
    Add-WordText -Document $Document -Text $Text -Alignment $Alignment
}

# ============================================================================
# TABLE OPERATIONS
# ============================================================================

function Add-WordTable {
    <#
    .SYNOPSIS
    Creates table in document
    
    .EXAMPLE
    $data = @(
        @("Name", "Age", "City"),
        @("John", "30", "NYC"),
        @("Jane", "25", "LA")
    )
    Add-WordTable -Document $doc -Data $data -Style "Grid Table 4 - Accent 1"
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [array]$Data,
        
        [string]$Style = "Grid Table 4 - Accent 1",
        [switch]$HeaderRow,
        [switch]$AutoFit
    )
    
    $rows = $Data.Count
    $cols = $Data[0].Count
    
    $range = $Document.Application.Selection.Range
    $table = $Document.Tables.Add($range, $rows, $cols)
    
    # Apply style
    if ($Style) {
        try {
            $table.Style = $Style
        }
        catch {
            Write-Warning "Table style '$Style' not found"
        }
    }
    
    # Fill data
    for ($i = 0; $i -lt $rows; $i++) {
        for ($j = 0; $j -lt $cols; $j++) {
            $table.Cell($i + 1, $j + 1).Range.Text = $Data[$i][$j]
        }
    }
    
    # Format header row
    if ($HeaderRow) {
        $table.Rows.Item(1).HeadingFormat = -1
        $table.Rows.Item(1).Range.Font.Bold = 1
    }
    
    # Auto fit
    if ($AutoFit) {
        $table.AutoFitBehavior(1) # wdAutoFitContent
    }
    
    $Document.Application.Selection.EndKey(6) # wdStory
    $Document.Application.Selection.TypeParagraph()
    
    Write-Host "[OK] Table created ($rows x $cols)" -ForegroundColor Green
    
    return $table
}

function Add-WordTableFromCSV {
    <#
    .SYNOPSIS
    Creates table from CSV file
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$CSVPath,
        
        [string]$Style = "Grid Table 4 - Accent 1"
    )
    
    if (-not (Test-Path $CSVPath)) {
        Write-Error "CSV file not found: $CSVPath"
        return
    }
    
    $csvData = Import-Csv -Path $CSVPath
    
    # Convert to array
    $headers = $csvData[0].PSObject.Properties.Name
    $data = @(, $headers)
    
    foreach ($row in $csvData) {
        $rowData = @()
        foreach ($header in $headers) {
            $rowData += $row.$header
        }
        $data += , $rowData
    }
    
    Add-WordTable -Document $Document -Data $data -Style $Style -HeaderRow
}

# ============================================================================
# IMAGE OPERATIONS
# ============================================================================

function Add-WordImage {
    <#
    .SYNOPSIS
    Inserts image into document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$ImagePath,
        
        [double]$Width = 0,
        [double]$Height = 0,
        [string]$Alignment = "Center"
    )
    
    if (-not (Test-Path $ImagePath)) {
        Write-Error "Image not found: $ImagePath"
        return
    }
    
    $selection = $Document.Application.Selection
    $shape = $selection.InlineShapes.AddPicture($ImagePath)
    
    # Resize if specified
    if ($Width -gt 0) {
        $shape.Width = $Width
    }
    if ($Height -gt 0) {
        $shape.Height = $Height
    }
    
    # Alignment
    $alignments = @{
        "Left"   = 0
        "Center" = 1
        "Right"  = 2
    }
    if ($alignments.ContainsKey($Alignment)) {
        $selection.ParagraphFormat.Alignment = $alignments[$Alignment]
    }
    
    $Document.Application.Selection.TypeParagraph()
    
    Write-Host "[OK] Image inserted: $ImagePath" -ForegroundColor Green
}

# ============================================================================
# STYLE APPLICATION
# ============================================================================

function Apply-CorporateStyle {
    <#
    .SYNOPSIS
    Applies corporate style to document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [string]$StyleType = "modern" # modern, traditional, minimal
    )
    
    Write-Host "Applying $StyleType corporate style..." -ForegroundColor Yellow
    
    # Modern Corporate Style
    if ($StyleType -eq "modern") {
        # Title style
        $titleStyle = $Document.Styles["Title"]
        $titleStyle.Font.Name = "Calibri Light"
        $titleStyle.Font.Size = 28
        $titleStyle.Font.Color = 0x0052A5 # Corporate Blue
        
        # Heading 1
        $h1Style = $Document.Styles["Heading 1"]
        $h1Style.Font.Name = "Calibri"
        $h1Style.Font.Size = 18
        $h1Style.Font.Bold = 1
        $h1Style.Font.Color = 0x0052A5
        
        # Heading 2
        $h2Style = $Document.Styles["Heading 2"]
        $h2Style.Font.Name = "Calibri"
        $h2Style.Font.Size = 14
        $h2Style.Font.Bold = 1
        $h2Style.Font.Color = 0x4D4D4D
        
        # Normal text
        $normalStyle = $Document.Styles["Normal"]
        $normalStyle.Font.Name = "Calibri"
        $normalStyle.Font.Size = 11
        $normalStyle.ParagraphFormat.LineSpacing = 15.6 # 1.3 line spacing
    }
    
    # Traditional Corporate Style
    elseif ($StyleType -eq "traditional") {
        $titleStyle = $Document.Styles["Title"]
        $titleStyle.Font.Name = "Times New Roman"
        $titleStyle.Font.Size = 26
        $titleStyle.Font.Bold = 1
        
        $normalStyle = $Document.Styles["Normal"]
        $normalStyle.Font.Name = "Times New Roman"
        $normalStyle.Font.Size = 12
    }
    
    # Minimal Style
    elseif ($StyleType -eq "minimal") {
        $titleStyle = $Document.Styles["Title"]
        $titleStyle.Font.Name = "Helvetica"
        $titleStyle.Font.Size = 24
        $titleStyle.Font.Bold = 0
        
        $normalStyle = $Document.Styles["Normal"]
        $normalStyle.Font.Name = "Helvetica"
        $normalStyle.Font.Size = 10
    }
    
    Write-Host "[OK] Style applied: $StyleType" -ForegroundColor Green
}

# ============================================================================
# DOCUMENT GENERATORS
# ============================================================================

function New-CorporateReport {
    <#
    .SYNOPSIS
    Generates complete corporate report
    
    .EXAMPLE
    New-CorporateReport -Word $word -Title "Q4 Financial Report" -OutputPath "report.docx"
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [string]$Title = "Corporate Report",
        [string]$Subtitle = "",
        [string]$Author = $env:USERNAME,
        [string]$Company = "ACME Corporation",
        [string]$Date = (Get-Date -Format "MMMM dd, yyyy"),
        [string]$Style = "modern",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\report.docx"
    )
    
    Write-Host "`n=== CORPORATE REPORT GENERATOR ===" -ForegroundColor Cyan
    Write-Host "Title: $Title" -ForegroundColor Yellow
    Write-Host "Company: $Company" -ForegroundColor Yellow
    
    $doc = New-WordDocument -Word $Word
    
    # Apply style
    Apply-CorporateStyle -Document $doc -StyleType $Style
    
    # Cover page
    Add-WordText -Document $doc -Text $Company -Style "Normal" -FontSize 14 -Alignment "Center"
    Add-WordText -Document $doc -Text "" # Empty line
    Add-WordText -Document $doc -Text "" 
    Add-WordText -Document $doc -Text "" 
    
    Add-WordText -Document $doc -Text $Title -Style "Title" -Alignment "Center"
    
    if ($Subtitle) {
        Add-WordText -Document $doc -Text $Subtitle -Style "Subtitle" -Alignment "Center"
    }
    
    Add-WordText -Document $doc -Text "" 
    Add-WordText -Document $doc -Text "" 
    Add-WordText -Document $doc -Text "Prepared by: $Author" -Alignment "Center"
    Add-WordText -Document $doc -Text $Date -Alignment "Center"
    
    # Page break
    $Word.Selection.InsertBreak(7) # wdPageBreak
    
    # Table of Contents
    Add-WordHeading -Document $doc -Text "Table of Contents" -Level 1
    $Word.Selection.TypeText("(Table of Contents will be generated here)")
    $Word.Selection.TypeParagraph()
    
    # Page break
    $Word.Selection.InsertBreak(7)
    
    # Executive Summary
    Add-WordHeading -Document $doc -Text "Executive Summary" -Level 1
    Add-WordParagraph -Document $doc -Text "This section provides a high-level overview of the report findings and recommendations."
    Add-WordText -Document $doc -Text ""
    
    # Section 1
    Add-WordHeading -Document $doc -Text "Introduction" -Level 1
    Add-WordParagraph -Document $doc -Text "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    Add-WordText -Document $doc -Text ""
    
    # Section 2
    Add-WordHeading -Document $doc -Text "Key Findings" -Level 1
    Add-WordHeading -Document $doc -Text "Finding 1: Market Analysis" -Level 2
    Add-WordParagraph -Document $doc -Text "Detailed analysis of market trends and competitive landscape."
    Add-WordText -Document $doc -Text ""
    
    Add-WordHeading -Document $doc -Text "Finding 2: Performance Metrics" -Level 2
    Add-WordParagraph -Document $doc -Text "Key performance indicators and benchmarks."
    Add-WordText -Document $doc -Text ""
    
    # Sample table
    Add-WordHeading -Document $doc -Text "Data Summary" -Level 1
    $tableData = @(
        @("Quarter", "Revenue", "Growth"),
        @("Q1 2026", "$2.5M", "12%"),
        @("Q2 2026", "$2.8M", "15%"),
        @("Q3 2026", "$3.1M", "18%"),
        @("Q4 2026", "$3.5M", "20%")
    )
    Add-WordTable -Document $doc -Data $tableData -Style "Grid Table 4 - Accent 1" -HeaderRow -AutoFit
    
    # Conclusion
    Add-WordHeading -Document $doc -Text "Conclusion" -Level 1
    Add-WordParagraph -Document $doc -Text "In conclusion, the findings demonstrate significant growth opportunities and strategic advantages."
    
    # Footer
    $doc.Sections.Item(1).Footers.Item(1).Range.Text = "Confidential - $Company | Page "
    $doc.Sections.Item(1).Footers.Item(1).PageNumbers.Add()
    
    # Save
    Save-WordDocument -Document $doc -Path $OutputPath -Format "docx"
    
    Write-Host "`n[OK] CORPORATE REPORT COMPLETE" -ForegroundColor Green
    Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
    
    return $doc
}

function New-Certificate {
    <#
    .SYNOPSIS
    Generates certificate document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [string]$RecipientName = "John Smith",
        [string]$CertificateTitle = "Certificate of Achievement",
        [string]$Description = "Has successfully completed the Advanced Leadership Program",
        [string]$Date = (Get-Date -Format "MMMM dd, yyyy"),
        [string]$Signatory = "Jane Doe, Director",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\certificate.docx"
    )
    
    Write-Host "`n=== CERTIFICATE GENERATOR ===" -ForegroundColor Cyan
    Write-Host "Recipient: $RecipientName" -ForegroundColor Yellow
    
    $doc = New-WordDocument -Word $Word
    
    # Page setup - Landscape
    $doc.PageSetup.Orientation = 1 # wdOrientLandscape
    
    # Add border
    $doc.Sections.Item(1).Borders.Enable = 1
    $doc.Sections.Item(1).Borders.Item(1).LineStyle = 1
    $doc.Sections.Item(1).Borders.Item(1).LineWidth = 24 # wdLineWidth225pt
    
    # Spacing
    for ($i = 0; $i -lt 5; $i++) {
        Add-WordText -Document $doc -Text ""
    }
    
    # Certificate Title
    Add-WordText -Document $doc -Text $CertificateTitle `
        -FontName "Trajan Pro" -FontSize 36 -Bold -Alignment "Center"
    
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    
    # Recipient
    Add-WordText -Document $doc -Text "This is to certify that" -FontSize 14 -Alignment "Center"
    Add-WordText -Document $doc -Text ""
    
    Add-WordText -Document $doc -Text $RecipientName `
        -FontName "Lucida Handwriting" -FontSize 28 -Bold -Alignment "Center"
    
    Add-WordText -Document $doc -Text ""
    
    # Description
    Add-WordText -Document $doc -Text $Description -FontSize 14 -Alignment "Center"
    
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    
    # Date
    Add-WordText -Document $doc -Text "Date: $Date" -FontSize 12 -Alignment "Center"
    
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    
    # Signature line
    Add-WordText -Document $doc -Text "_____________________________" -Alignment "Center"
    Add-WordText -Document $doc -Text $Signatory -FontSize 12 -Alignment "Center"
    
    # Save
    Save-WordDocument -Document $doc -Path $OutputPath -Format "docx"
    
    Write-Host "[OK] Certificate generated: $OutputPath" -ForegroundColor Green
    
    return $doc
}

function New-BusinessLetter {
    <#
    .SYNOPSIS
    Generates formal business letter
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [string]$SenderName = "John Doe",
        [string]$SenderTitle = "CEO",
        [string]$SenderCompany = "ACME Corporation",
        [string]$SenderAddress = "123 Business St, City, State 12345",
        
        [string]$RecipientName = "Jane Smith",
        [string]$RecipientTitle = "Director",
        [string]$RecipientCompany = "XYZ Inc",
        [string]$RecipientAddress = "456 Corporate Ave, City, State 67890",
        
        [string]$Subject = "Business Proposal",
        [string]$Body = "Lorem ipsum dolor sit amet...",
        [string]$OutputPath = "$env:USERPROFILE\Desktop\letter.docx"
    )
    
    $doc = New-WordDocument -Word $Word
    
    $date = Get-Date -Format "MMMM dd, yyyy"
    
    # Sender info
    Add-WordText -Document $doc -Text $SenderCompany -Bold
    Add-WordText -Document $doc -Text $SenderAddress
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text $date
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    
    # Recipient info
    Add-WordText -Document $doc -Text $RecipientName
    Add-WordText -Document $doc -Text $RecipientTitle
    Add-WordText -Document $doc -Text $RecipientCompany
    Add-WordText -Document $doc -Text $RecipientAddress
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    
    # Subject
    Add-WordText -Document $doc -Text "RE: $Subject" -Bold
    Add-WordText -Document $doc -Text ""
    
    # Body
    Add-WordText -Document $doc -Text "Dear $RecipientName,"
    Add-WordText -Document $doc -Text ""
    Add-WordParagraph -Document $doc -Text $Body
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text "Sincerely,"
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text ""
    Add-WordText -Document $doc -Text $SenderName
    Add-WordText -Document $doc -Text $SenderTitle
    
    Save-WordDocument -Document $doc -Path $OutputPath
    
    Write-Host "[OK] Business letter generated: $OutputPath" -ForegroundColor Green
    
    return $doc
}

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

function New-BatchCertificates {
    <#
    .SYNOPSIS
    Generates multiple certificates from CSV
    
    .EXAMPLE
    New-BatchCertificates -Word $word -CSVPath "recipients.csv"
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [Parameter(Mandatory = $true)]
        [string]$CSVPath,
        
        [string]$CertificateTitle = "Certificate of Achievement",
        [string]$OutputFolder = "$env:USERPROFILE\Desktop\certificates"
    )
    
    if (-not (Test-Path $CSVPath)) {
        Write-Error "CSV file not found: $CSVPath"
        return
    }
    
    # Create output folder
    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder | Out-Null
    }
    
    $recipients = Import-Csv -Path $CSVPath
    
    Write-Host "`n=== BATCH CERTIFICATE GENERATION ===" -ForegroundColor Cyan
    Write-Host "Total recipients: $($recipients.Count)" -ForegroundColor Yellow
    
    foreach ($recipient in $recipients) {
        $outputPath = Join-Path $OutputFolder "$($recipient.Name -replace ' ','_')_certificate.docx"
        
        Write-Host "Generating certificate for: $($recipient.Name)" -ForegroundColor Yellow
        
        New-Certificate -Word $Word `
            -RecipientName $recipient.Name `
            -CertificateTitle $CertificateTitle `
            -Description $recipient.Description `
            -Date $recipient.Date `
            -Signatory $recipient.Signatory `
            -OutputPath $outputPath
        
        # Close document
        $Word.ActiveDocument.Close()
        
        Write-Host "  [OK] Certificate generated" -ForegroundColor Green
    }
    
    Write-Host "`n[OK] BATCH COMPLETE" -ForegroundColor Green
    Write-Host "  Total: $($recipients.Count)" -ForegroundColor Cyan
    Write-Host "  Output: $OutputFolder" -ForegroundColor Cyan
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function ConvertFrom-HexColor {
    <#
    .SYNOPSIS
    Converts hex color to RGB
    #>
    param([string]$HexColor)
    
    $hex = $HexColor.TrimStart('#')
    
    return @{
        R = [Convert]::ToInt32($hex.Substring(0, 2), 16)
        G = [Convert]::ToInt32($hex.Substring(2, 2), 16)
        B = [Convert]::ToInt32($hex.Substring(4, 2), 16)
    }
}

function Export-WordToPDF {
    <#
    .SYNOPSIS
    Exports Word document to PDF
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )
    

    $Document.SaveAs([ref]$OutputPath, [ref]17) # wdFormatPDF
    Write-Host "[OK] Exported to PDF: $OutputPath" -ForegroundColor Green
}

# ============================================================================
# EXPORT MODULE
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-Word',
    'Disconnect-Word',
    'New-WordDocument',
    'Open-WordDocument',
    'Save-WordDocument',
    'Add-WordText',
    'Add-WordHeading',
    'Add-WordParagraph',
    'Add-WordTable',
    'Add-WordTableFromCSV',
    'Add-WordImage',
    'Apply-CorporateStyle',
    'New-CorporateReport',
    'New-Certificate',
    'New-BusinessLetter',
    'New-BatchCertificates',
    'Export-WordToPDF'
)

Write-Host "ONI.Word.Automation module loaded" -ForegroundColor Green
Write-Host "Use: Get-Command -Module ONI.Word.Automation" -ForegroundColor Yellow