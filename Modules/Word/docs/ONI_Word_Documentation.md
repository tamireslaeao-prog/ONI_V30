# 📄 ONI SYSTEM FOR MICROSOFT WORD

## Complete Document Automation Framework

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Usage Examples](#usage-examples)
6. [Style System](#style-system)
7. [VBA Macros](#vba-macros)
8. [Batch Processing](#batch-processing)
9. [Templates](#templates)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 SYSTEM OVERVIEW

O **ONI System for Microsoft Word** é uma framework completa de automação para criação de documentos corporativos, relatórios, certificados e templates profissionais.

### Features Principais

- ✅ **PowerShell Automation**: Controle completo via linha de comando
- ✅ **VBA Macros**: 12+ macros prontos para uso
- ✅ **Style Database**: 8 estilos profissionais (Corporate, Formal, Minimal, etc)
- ✅ **Document Generators**: Reports, Certificates, Letters, Invoices
- ✅ **Batch Processing**: Geração em massa a partir de CSV
- ✅ **Multi-Format Export**: DOCX, PDF, HTML, RTF

### Arquitetura do Sistema

```
ONI-Word/
├── ONI.Word.Automation.ps1      # PowerShell automation
├── word_styles_db.json          # Style database
├── ONI_Word_Macros.vba          # VBA macros
├── templates/
│   ├── corporate_report.dotx
│   ├── certificate_formal.dotx
│   ├── business_letter.dotx
│   └── invoice_modern.dotx
├── data/
│   └── sample_recipients.csv
└── docs/
    └── ONI_Word_Documentation.md
```

---

## 🔧 INSTALLATION

### Prerequisites

1. **Microsoft Word** 2019, 2021, or Microsoft 365
2. **Windows PowerShell** 5.1 or later
3. **Macro-enabled Word** (trust VBA projects)

### Step 1: Copy Files

```powershell
# Create ONI directory
New-Item -ItemType Directory -Path "C:\ONI\Word"

# Copy files
Copy-Item ONI.Word.Automation.ps1 "C:\ONI\Word\"
Copy-Item word_styles_db.json "C:\ONI\Word\"
Copy-Item ONI_Word_Macros.vba "C:\ONI\Word\"
```

### Step 2: Enable Macros in Word

1. Open Word
2. Go to: **File > Options > Trust Center > Trust Center Settings**
3. Select: **Macro Settings**
4. Choose: **Enable all macros** (for development)
5. Check: **Trust access to the VBA project object model**
6. Click **OK** and restart Word

### Step 3: Install VBA Macros

```
1. Open Word
2. Press Alt+F11 (VBA Editor)
3. Insert > Module
4. Open ONI_Word_Macros.vba in Notepad
5. Copy all content
6. Paste into VBA Module
7. File > Save
8. Close VBA Editor
```

### Step 4: Load PowerShell Module

```powershell
Import-Module "C:\ONI\Word\ONI.Word.Automation.ps1"
```

### Step 5: Verify Installation

```powershell
$word = Connect-Word
New-WordDocument -Word $word
Add-WordText -Document $word.ActiveDocument -Text "ONI System Test" -Style "Title"
```

---

## 🚀 QUICK START

### Example 1: Create Corporate Report

```powershell
# Connect to Word
$word = Connect-Word

# Generate corporate report
New-CorporateReport -Word $word `
    -Title "Q4 Financial Report" `
    -Subtitle "2025 Year End Results" `
    -Company "ACME Corporation" `
    -Author "Finance Department" `
    -Style "modern" `
    -OutputPath "C:\reports\Q4_Report.docx"

# Export to PDF
Export-WordToPDF -Document $word.ActiveDocument `
    -OutputPath "C:\reports\Q4_Report.pdf"
```

### Example 2: Generate Certificate

```powershell
New-Certificate -Word $word `
    -RecipientName "John Smith" `
    -CertificateTitle "Certificate of Excellence" `
    -Description "Has completed Advanced Leadership Training" `
    -Date "January 4, 2026" `
    -Signatory "Jane Doe, Director" `
    -OutputPath "C:\certificates\john_smith.docx"
```

### Example 3: Batch Generate Certificates

```csv
# recipients.csv
Name,Description,Date,Signatory
John Smith,Advanced Leadership Training,January 4 2026,Jane Doe Director
Alice Johnson,Data Analytics Certification,January 4 2026,Jane Doe Director
Bob Wilson,Project Management Course,January 4 2026,Jane Doe Director
```

```powershell
New-BatchCertificates -Word $word `
    -CSVPath "C:\data\recipients.csv" `
    -CertificateTitle "Certificate of Completion" `
    -OutputFolder "C:\certificates\batch"
```

---

## 🧩 CORE COMPONENTS

### 1. Connection Management

```powershell
# Connect to Word
$word = Connect-Word

# Disconnect
Disconnect-Word -Word $word

# Close Word application
Disconnect-Word -Word $word -Close
```

### 2. Document Operations

```powershell
# Create new document
$doc = New-WordDocument -Word $word

# Open existing document
$doc = Open-WordDocument -Word $word -Path "C:\docs\report.docx"

# Save document
Save-WordDocument -Document $doc -Path "C:\output\report.docx"

# Save as different format
Save-WordDocument -Document $doc -Path "C:\output\report.pdf" -Format "pdf"
```

### 3. Adding Content

```powershell
# Add text with formatting
Add-WordText -Document $doc `
    -Text "Hello World" `
    -Style "Heading 1" `
    -FontName "Calibri" `
    -FontSize 18 `
    -Bold `
    -FontColor "#0052A5" `
    -Alignment "Center"

# Add heading
Add-WordHeading -Document $doc -Text "Introduction" -Level 1

# Add paragraph with spacing
Add-WordParagraph -Document $doc `
    -Text "This is the introduction paragraph." `
    -SpaceBefore 12 `
    -SpaceAfter 6 `
    -LineSpacing 1.5
```

### 4. Tables

```powershell
# Create table from array
$tableData = @(
    @("Name", "Age", "City"),
    @("John", "30", "NYC"),
    @("Jane", "25", "LA"),
    @("Bob", "35", "Chicago")
)

Add-WordTable -Document $doc `
    -Data $tableData `
    -Style "Grid Table 4 - Accent 1" `
    -HeaderRow `
    -AutoFit

# Create table from CSV
Add-WordTableFromCSV -Document $doc `
    -CSVPath "C:\data\employees.csv" `
    -Style "Grid Table 4 - Accent 1"
```

### 5. Images

```powershell
# Insert image
Add-WordImage -Document $doc `
    -ImagePath "C:\images\logo.png" `
    -Width 200 `
    -Height 100 `
    -Alignment "Center"
```

### 6. Styling

```powershell
# Apply corporate style
Apply-CorporateStyle -Document $doc -StyleType "modern"

# Available styles: modern, traditional, minimal
```

---

## 🎨 STYLE SYSTEM

### 1. Modern Corporate Style

**Best for:** Business reports, proposals, white papers

**Characteristics:**
- Font: Calibri / Calibri Light
- Colors: Corporate Blue (#0052A5), Professional Gray
- Layout: Clean, generous whitespace
- Headers: Left-aligned, bold
- Line spacing: 1.3

**Example:**
```powershell
Apply-CorporateStyle -Document $doc -StyleType "modern"
```

### 2. Traditional Formal Style

**Best for:** Legal documents, academic papers

**Characteristics:**
- Font: Times New Roman
- Colors: Black and grayscale
- Layout: Dense, justified text
- Headers: Centered, numbered
- Line spacing: 2.0 (double)

### 3. Minimal Modern Style

**Best for:** Creative proposals, portfolios

**Characteristics:**
- Font: Helvetica / Arial
- Colors: Monochrome
- Layout: Ultra-clean, wide margins
- Headers: Minimal formatting
- Line spacing: 1.8

### 4. Certificate Formal Style

**Best for:** Certificates, awards, diplomas

**Characteristics:**
- Font: Trajan Pro, Garamond
- Colors: Navy Blue, Gold accents
- Layout: Landscape, decorative borders
- Special: Signature lines, seals

### 5. Resume Professional Style

**Best for:** Resumes, CVs

**Characteristics:**
- Font: Calibri
- Colors: Corporate Blue accents
- Layout: ATS-friendly, single column
- Sections: Contact, Summary, Experience, Education

### 6. Invoice Modern Style

**Best for:** Invoices, billing statements

**Characteristics:**
- Font: Calibri
- Colors: Corporate Blue header
- Layout: Structured tables
- Elements: Logo, line items, totals

---

## 🔨 VBA MACROS

### Quick Access Macros

#### 1. ApplyCorporateStyle
Aplica estilo corporativo moderno ao documento.
```
Alt+F8 > ApplyCorporateStyle > Run
```

#### 2. CreateCorporateReport
Cria estrutura completa de relatório corporativo.
```
Alt+F8 > CreateCorporateReport > Run
```

#### 3. FormatTableCorporate
Formata tabela selecionada com cores corporativas.
```
1. Select table
2. Alt+F8 > FormatTableCorporate > Run
```

#### 4. InsertCorporateHeader
Insere cabeçalho corporativo padronizado.
```
Alt+F8 > InsertCorporateHeader > Run
```

#### 5. InsertCorporateFooter
Insere rodapé com numeração de páginas.
```
Alt+F8 > InsertCorporateFooter > Run
```

#### 6. CreateCertificate
Cria template de certificado formal.
```
Alt+F8 > CreateCertificate > Run
```

#### 7. InsertCalloutBox
Insere caixa destacada para informações importantes.
```
Alt+F8 > InsertCalloutBox > Run
```

#### 8. ExportToPDF
Exporta documento ativo como PDF.
```
Alt+F8 > ExportToPDF > Run
```

#### 9. CleanUpFormatting
Remove espaços extras e inconsistências.
```
Alt+F8 > CleanUpFormatting > Run
```

### Assigning Keyboard Shortcuts

```
1. View > Macros (Alt+F8)
2. Select macro > Options
3. Enter shortcut key (e.g., Ctrl+Shift+C)
4. OK
```

**Recommended Shortcuts:**
- `Ctrl+Shift+S` - ApplyCorporateStyle
- `Ctrl+Shift+R` - CreateCorporateReport
- `Ctrl+Shift+T` - FormatTableCorporate
- `Ctrl+Shift+H` - InsertCorporateHeader
- `Ctrl+Shift+P` - ExportToPDF

---

## 💼 USAGE EXAMPLES

### Example 1: Complete Business Report

```powershell
$word = Connect-Word

# Create report
$doc = New-CorporateReport -Word $word `
    -Title "2025 Strategic Plan" `
    -Subtitle "Digital Transformation Initiative" `
    -Company "Tech Innovations Inc." `
    -Author "Strategy Team" `
    -Date "January 2026" `
    -Style "modern"

# Add custom sections
Add-WordHeading -Document $doc -Text "Market Analysis" -Level 1

$marketData = @(
    @("Region", "Revenue", "Growth"),
    @("North America", "$2.5M", "15%"),
    @("Europe", "$1.8M", "12%"),
    @("Asia Pacific", "$3.2M", "22%")
)
Add-WordTable -Document $doc -Data $marketData -HeaderRow -AutoFit

# Add chart/image
Add-WordImage -Document $doc `
    -ImagePath "C:\charts\revenue_chart.png" `
    -Width 400 `
    -Alignment "Center"

# Save and export
Save-WordDocument -Document $doc -Path "C:\reports\strategic_plan.docx"
Export-WordToPDF -Document $doc -OutputPath "C:\reports\strategic_plan.pdf"
```

### Example 2: Mass Certificate Generation

```powershell
# CSV structure:
# Name,Course,Date,Grade
# John Smith,Python Advanced,Jan 2026,A
# Jane Doe,Data Science,Jan 2026,A+

$word = Connect-Word

$recipients = Import-Csv "C:\data\graduates.csv"

foreach ($recipient in $recipients) {
    $outputPath = "C:\certificates\$($recipient.Name -replace ' ','_').docx"
    
    New-Certificate -Word $word `
        -RecipientName $recipient.Name `
        -CertificateTitle "Certificate of Achievement" `
        -Description "Has successfully completed $($recipient.Course) with grade $($recipient.Grade)" `
        -Date $recipient.Date `
        -Signatory "Dr. Sarah Chen, Dean" `
        -OutputPath $outputPath
    
    # Export to PDF
    Export-WordToPDF -Document $word.ActiveDocument `
        -OutputPath $outputPath.Replace(".docx", ".pdf")
    
    # Close document
    $word.ActiveDocument.Close()
    
    Write-Host "✓ Certificate generated for: $($recipient.Name)"
}

Write-Host "`n✓ All certificates generated!"
```

### Example 3: Automated Business Letters

```powershell
$clients = Import-Csv "C:\data\clients.csv"

foreach ($client in $clients) {
    New-BusinessLetter -Word $word `
        -SenderName "John CEO" `
        -SenderTitle "Chief Executive Officer" `
        -SenderCompany "ACME Corp" `
        -SenderAddress "123 Business St, NYC 10001" `
        -RecipientName $client.ContactName `
        -RecipientTitle $client.Title `
        -RecipientCompany $client.Company `
        -RecipientAddress $client.Address `
        -Subject "Partnership Opportunity" `
        -Body "Dear $($client.ContactName),`n`nWe are pleased to present..." `
        -OutputPath "C:\letters\$($client.Company).docx"
    
    $word.ActiveDocument.Close()
}
```

### Example 4: Invoice Generation

```powershell
# Create invoice
$doc = New-WordDocument -Word $word
Apply-CorporateStyle -Document $doc -StyleType "modern"

# Header
Add-WordText -Document $doc -Text "INVOICE" `
    -FontSize 28 -Bold -FontColor "#0052A5"
Add-WordText -Document $doc -Text "Invoice #INV-2026-001" -FontSize 12

# Company info
Add-WordText -Document $doc -Text "`nACME Corporation"
Add-WordText -Document $doc -Text "123 Business Street"
Add-WordText -Document $doc -Text "New York, NY 10001"

# Bill to
Add-WordText -Document $doc -Text "`nBILL TO:" -Bold
Add-WordText -Document $doc -Text "Client Company Inc."
Add-WordText -Document $doc -Text "456 Corporate Ave"

# Line items table
$lineItems = @(
    @("Description", "Qty", "Rate", "Amount"),
    @("Consulting Services", "10", "$150", "$1,500"),
    @("Software License", "1", "$500", "$500"),
    @("Support Package", "1", "$250", "$250")
)
Add-WordTable -Document $doc -Data $lineItems -HeaderRow -AutoFit

# Totals
Add-WordText -Document $doc -Text "`nSubtotal: $2,250" -Alignment "Right"
Add-WordText -Document $doc -Text "Tax (8%): $180" -Alignment "Right"
Add-WordText -Document $doc -Text "TOTAL: $2,430" -Bold -Alignment "Right"

Save-WordDocument -Document $doc -Path "C:\invoices\INV-2026-001.docx"
```

---

## 📊 TEMPLATES

### Creating Custom Templates

1. **Design Document in Word**
   - Apply all formatting
   - Use placeholders: `[NAME]`, `[DATE]`, `[COMPANY]`
   - Add header/footer

2. **Save as Template**
   ```
   File > Save As > Word Template (*.dotx)
   Location: C:\ONI\Word\templates\
   ```

3. **Use Template in PowerShell**
   ```powershell
   $templatePath = "C:\ONI\Word\templates\my_template.dotx"
   $doc = New-WordDocument -Word $word -Template $templatePath
   
   # Replace placeholders
   $doc.Content.Find.Execute( `
       FindText:="[NAME]", `
       ReplaceWith:="John Smith", `
       Replace:=2)  # wdReplaceAll
   ```

### Template Variables

Common placeholders to use:
- `[NAME]` - Recipient name
- `[COMPANY]` - Company name
- `[DATE]` - Current date
- `[TITLE]` - Job title / document title
- `[ID]` - Employee/Client ID
- `[AMOUNT]` - Financial amount
- `[SIGNATURE]` - Signature name

---

## 🔄 BATCH PROCESSING

### Workflow 1: Bulk Report Generation

```powershell
# reports_data.csv:
# ReportID,Title,Author,Department
# R001,Q1 Sales Report,John Smith,Sales
# R002,Q2 Marketing Report,Jane Doe,Marketing

$reports = Import-Csv "C:\data\reports_data.csv"

foreach ($report in $reports) {
    New-CorporateReport -Word $word `
        -Title $report.Title `
        -Author $report.Author `
        -Company "$($report.Department) Department" `
        -OutputPath "C:\reports\$($report.ReportID).docx"
    
    $word.ActiveDocument.Close()
}
```

### Workflow 2: Template Mail Merge Alternative

```powershell
$templatePath = "C:\ONI\Word\templates\welcome_letter.dotx"
$clients = Import-Csv "C:\data\new_clients.csv"

foreach ($client in $clients) {
    $doc = New-WordDocument -Word $word -Template $templatePath
    
    # Replace all placeholders
    $replacements = @{
        "[NAME]" = $client.Name
        "[COMPANY]" = $client.Company
        "[EMAIL]" = $client.Email
        "[DATE]" = Get-Date -Format "MMMM dd, yyyy"
    }
    
    foreach ($key in $replacements.Keys) {
        $doc.Content.Find.Execute( `
            FindText:=$key, `
            ReplaceWith:=$replacements[$key], `
            Replace:=2)
    }
    
    $outputPath = "C:\letters\$($client.Name -replace ' ','_').docx"
    Save-WordDocument -Document $doc -Path $outputPath
    
    $doc.Close()
}
```

---

## 🛠️ TROUBLESHOOTING

### Issue 1: "Cannot connect to Word"

**Solution:**
```powershell
# Check if Word is installed
Test-Path "HKLM:\SOFTWARE\Microsoft\Office\*\Word"

# Try launching Word manually first
Start-Process "winword"
Start-Sleep -Seconds 5

# Then connect
$word = Connect-Word
```

### Issue 2: "Macros are disabled"

**Solution:**
1. File > Options > Trust Center > Trust Center Settings
2. Macro Settings > Enable all macros
3. Check: Trust access to VBA project object model
4. Restart Word

### Issue 3: "Style not found"

**Solution:**
```powershell
# Check available styles
$doc.Styles | Select-Object NameLocal

# Use built-in style names
Add-WordText -Document $doc -Text "Title" -Style "Title"
```

### Issue 4: COM Object Errors

**Solution:**
```powershell
# Release COM objects properly
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```

### Issue 5: Font Not Found

**Solution:**
```powershell
# Check installed fonts
[System.Drawing.Text.InstalledFontCollection]::new().Families.Name

# Use fallback fonts
$fontName = "Calibri"
if (-not (Test-FontInstalled $fontName)) {
    $fontName = "Arial"  # Fallback
}
```

---

## 📚 ADDITIONAL RESOURCES

### Style Guide Best Practices

**Font Sizes:**
- Title: 24-36pt
- Heading 1: 16-18pt
- Heading 2: 14pt
- Body: 10-12pt
- Footer: 8-9pt

**Line Spacing:**
- Corporate documents: 1.15-1.3
- Academic papers: 2.0
- Creative content: 1.5-1.8

**Margins:**
- Standard: 1" all sides
- Narrow: 0.5" all sides
- Wide: 1.5" all sides

### Word VBA Object Model

- `Application` - Word application
- `Documents` - Collection of documents
- `Document` - Single document
- `Selection` - Current selection
- `Range` - Text range
- `Paragraphs` - Paragraph collection
- `Tables` - Table collection

### PowerShell + Word Constants

```powershell
# Alignment
$wdAlignParagraphLeft = 0
$wdAlignParagraphCenter = 1
$wdAlignParagraphRight = 2
$wdAlignParagraphJustify = 3

# Save formats
$wdFormatDocumentDefault = 16  # .docx
$wdFormatPDF = 17
$wdFormatHTML = 8
$wdFormatRTF = 6
```

---

## 📄 LICENSE

ONI System for Microsoft Word  
© 2026 - MIT License

---

## 🤝 CONTRIBUTING

Contribuições são bem-vindas!

1. Fork o repositório
2. Crie uma feature branch
3. Commit suas mudanças
4. Push e abra um Pull Request

---

## 📞 SUPPORT

Para suporte:
- GitHub Issues
- Email: oni-support@example.com
- Documentation: github.com/oni/word-docs

---

**Version:** 1.0  
**Last Updated:** 2026-01-04  
**Compatible with:** Microsoft Word 2019/2021/365  
**Platform:** Windows 10/11
