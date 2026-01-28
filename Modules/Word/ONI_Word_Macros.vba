' ============================================================================
' ONI.Word.Macros.vba - Microsoft Word Automation Macros
' Version: 1.0
' Description: VBA macros for document automation and styling
' ============================================================================
'
' INSTALLATION:
' 1. Open Microsoft Word
' 2. Press Alt+F11 to open VBA Editor
' 3. Insert > Module
' 4. Paste this code
' 5. Close VBA Editor
' 6. Run macros: View > Macros (Alt+F8)
'
' ============================================================================

' ============================================================================
' MACRO 1: Apply Corporate Style
' ============================================================================
Sub ApplyCorporateStyle()
    '
    ' Description: Applies modern corporate styling to active document
    ' Usage: Run on any document to standardize formatting
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Title Style
    With doc.Styles(wdStyleTitle)
        .Font.Name = "Calibri Light"
        .Font.Size = 28
        .Font.Bold = False
        .Font.Color = RGB(0, 82, 165) ' Corporate Blue
        .ParagraphFormat.Alignment = wdAlignParagraphLeft
        .ParagraphFormat.SpaceAfter = 12
    End With
    
    ' Heading 1
    With doc.Styles(wdStyleHeading1)
        .Font.Name = "Calibri"
        .Font.Size = 18
        .Font.Bold = True
        .Font.Color = RGB(0, 82, 165)
        .ParagraphFormat.SpaceBefore = 18
        .ParagraphFormat.SpaceAfter = 6
        .ParagraphFormat.KeepWithNext = True
    End With
    
    ' Heading 2
    With doc.Styles(wdStyleHeading2)
        .Font.Name = "Calibri"
        .Font.Size = 14
        .Font.Bold = True
        .Font.Color = RGB(77, 77, 77)
        .ParagraphFormat.SpaceBefore = 12
        .ParagraphFormat.SpaceAfter = 3
    End With
    
    ' Normal Style
    With doc.Styles(wdStyleNormal)
        .Font.Name = "Calibri"
        .Font.Size = 11
        .Font.Color = RGB(0, 0, 0)
        .ParagraphFormat.LineSpacing = LinesToPoints(1.3)
        .ParagraphFormat.SpaceAfter = 8
    End With
    
    MsgBox "Corporate style applied successfully!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 2: Create Corporate Report Template
' ============================================================================
Sub CreateCorporateReport()
    '
    ' Description: Creates complete corporate report structure
    ' Usage: Run in blank document
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Apply corporate style first
    Call ApplyCorporateStyle
    
    ' Cover Page
    Selection.Style = wdStyleTitle
    Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter
    Selection.TypeText "CORPORATE REPORT"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleNormal
    Selection.Font.Size = 14
    Selection.TypeText "Q4 Financial Results"
    Selection.TypeParagraph
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    Selection.Font.Size = 11
    Selection.TypeText "Prepared by: " & Application.UserName
    Selection.TypeParagraph
    Selection.TypeText Format(Now, "mmmm dd, yyyy")
    
    ' Page Break
    Selection.InsertBreak Type:=wdPageBreak
    
    ' Table of Contents
    Selection.Style = wdStyleHeading1
    Selection.TypeText "Table of Contents"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleNormal
    Selection.TypeText "[Table of Contents will be generated here]"
    Selection.TypeParagraph
    
    ' Page Break
    Selection.InsertBreak Type:=wdPageBreak
    
    ' Executive Summary
    Selection.Style = wdStyleHeading1
    Selection.TypeText "Executive Summary"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleNormal
    Selection.TypeText "This section provides a high-level overview of the report findings."
    Selection.TypeParagraph
    
    ' Introduction
    Selection.InsertBreak Type:=wdPageBreak
    Selection.Style = wdStyleHeading1
    Selection.TypeText "1. Introduction"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleNormal
    Selection.TypeText "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    Selection.TypeParagraph
    
    ' Key Findings
    Selection.Style = wdStyleHeading1
    Selection.TypeText "2. Key Findings"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleHeading2
    Selection.TypeText "2.1 Market Analysis"
    Selection.TypeParagraph
    
    Selection.Style = wdStyleNormal
    Selection.TypeText "Market analysis content goes here."
    Selection.TypeParagraph
    
    ' Footer
    With doc.Sections(1).Footers(wdHeaderFooterPrimary).Range
        .ParagraphFormat.Alignment = wdAlignParagraphCenter
        .Font.Size = 9
        .Font.Color = RGB(77, 77, 77)
        .Text = "Confidential | Page "
        .Fields.Add Range:=.Duplicate, Type:=wdFieldPage
    End With
    
    MsgBox "Corporate report template created!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 3: Format Table with Corporate Style
' ============================================================================
Sub FormatTableCorporate()
    '
    ' Description: Formats selected table with corporate colors
    ' Usage: Select table first, then run macro
    '
    
    If Selection.Tables.Count = 0 Then
        MsgBox "Please select a table first!", vbExclamation, "ONI Error"
        Exit Sub
    End If
    
    Dim tbl As Table
    Set tbl = Selection.Tables(1)
    
    ' Apply table style
    tbl.Style = "Grid Table 4 - Accent 1"
    tbl.ApplyStyleHeadingRows = True
    tbl.ApplyStyleRowBands = True
    
    ' Format header row
    With tbl.Rows(1).Range
        .Font.Bold = True
        .Font.Color = RGB(255, 255, 255) ' White
        .Shading.BackgroundPatternColor = RGB(0, 82, 165) ' Corporate Blue
    End With
    
    ' Auto fit
    tbl.AutoFitBehavior wdAutoFitContent
    
    MsgBox "Table formatted with corporate style!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 4: Insert Header with Logo Placeholder
' ============================================================================
Sub InsertCorporateHeader()
    '
    ' Description: Inserts corporate header with logo placeholder
    ' Usage: Run to add header to document
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Add header
    With doc.Sections(1).Headers(wdHeaderFooterPrimary).Range
        .ParagraphFormat.Alignment = wdAlignParagraphRight
        .Font.Name = "Calibri"
        .Font.Size = 9
        .Font.Color = RGB(77, 77, 77)
        .Text = "ACME Corporation"
        
        ' Add border
        .Borders(wdBorderBottom).LineStyle = wdLineStyleSingle
        .Borders(wdBorderBottom).Color = RGB(217, 217, 217)
    End With
    
    MsgBox "Corporate header inserted!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 5: Insert Footer with Page Numbers
' ============================================================================
Sub InsertCorporateFooter()
    '
    ' Description: Inserts corporate footer with page numbers
    ' Usage: Run to add footer to document
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    With doc.Sections(1).Footers(wdHeaderFooterPrimary).Range
        .ParagraphFormat.Alignment = wdAlignParagraphCenter
        .Font.Name = "Calibri"
        .Font.Size = 9
        .Font.Color = RGB(77, 77, 77)
        
        ' Add border
        .Borders(wdBorderTop).LineStyle = wdLineStyleSingle
        .Borders(wdBorderTop).Color = RGB(217, 217, 217)
        
        .Text = "Confidential | Page "
        .Fields.Add Range:=.Duplicate, Type:=wdFieldPage
        .InsertAfter " of "
        .Fields.Add Range:=.Duplicate, Type:=wdFieldNumPages
    End With
    
    MsgBox "Corporate footer inserted!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 6: Create Certificate
' ============================================================================
Sub CreateCertificate()
    '
    ' Description: Creates formal certificate document
    ' Usage: Run in blank document
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Page setup - Landscape
    doc.PageSetup.Orientation = wdOrientLandscape
    
    ' Add decorative border
    With doc.Sections(1).Borders
        .Enable = True
        .Shadow = False
        .OutsideLineStyle = wdLineStyleDouble
        .OutsideLineWidth = wdLineWidth225pt
        .OutsideColor = RGB(0, 51, 102) ' Navy Blue
    End With
    
    ' Add spacing
    Dim i As Integer
    For i = 1 To 5
        Selection.TypeParagraph
    Next i
    
    ' Certificate Title
    Selection.ParagraphFormat.Alignment = wdAlignParagraphCenter
    Selection.Font.Name = "Trajan Pro"
    Selection.Font.Size = 36
    Selection.Font.Bold = True
    Selection.Font.Color = RGB(0, 51, 102)
    Selection.TypeText "CERTIFICATE OF ACHIEVEMENT"
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    ' Body text
    Selection.Font.Name = "Garamond"
    Selection.Font.Size = 14
    Selection.Font.Bold = False
    Selection.Font.Color = RGB(0, 0, 0)
    Selection.TypeText "This is to certify that"
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    ' Recipient name
    Selection.Font.Name = "Lucida Handwriting"
    Selection.Font.Size = 28
    Selection.Font.Bold = True
    Selection.TypeText "[Recipient Name]"
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    ' Achievement text
    Selection.Font.Name = "Garamond"
    Selection.Font.Size = 14
    Selection.Font.Bold = False
    Selection.TypeText "Has successfully completed the Advanced Leadership Program"
    Selection.TypeParagraph
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    ' Date
    Selection.Font.Size = 12
    Selection.TypeText "Date: " & Format(Now, "mmmm dd, yyyy")
    Selection.TypeParagraph
    Selection.TypeParagraph
    Selection.TypeParagraph
    
    ' Signature line
    Selection.TypeText String(40, "_")
    Selection.TypeParagraph
    Selection.TypeText "Authorized Signature"
    
    MsgBox "Certificate template created!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 7: Insert Data Table from Selection
' ============================================================================
Sub ConvertTextToTable()
    '
    ' Description: Converts selected text to formatted table
    ' Usage: Select text (tab or comma separated), then run
    '
    
    If Selection.Type <> wdSelectionNormal Then
        MsgBox "Please select text first!", vbExclamation, "ONI Error"
        Exit Sub
    End If
    
    ' Convert to table (tab separated)
    Selection.ConvertToTable Separator:=wdSeparateByTabs, _
        NumColumns:=3, NumRows:=Selection.Rows.Count, _
        AutoFitBehavior:=wdAutoFitContent
    
    ' Format table
    Call FormatTableCorporate
    
    MsgBox "Text converted to table!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 8: Apply Bullet List Style
' ============================================================================
Sub ApplyCorporateBullets()
    '
    ' Description: Applies custom bullet formatting
    ' Usage: Select paragraphs, then run
    '
    
    With Selection
        .Range.ListFormat.ApplyBulletDefault
        .Font.Name = "Calibri"
        .Font.Size = 11
        .ParagraphFormat.LeftIndent = InchesToPoints(0.25)
        .ParagraphFormat.FirstLineIndent = InchesToPoints(-0.25)
        .ParagraphFormat.SpaceAfter = 3
    End With
    
    MsgBox "Corporate bullet style applied!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 9: Insert Callout Box
' ============================================================================
Sub InsertCalloutBox()
    '
    ' Description: Inserts formatted callout/highlight box
    ' Usage: Run where you want callout
    '
    
    Selection.TypeParagraph
    
    With Selection
        .ParagraphFormat.LeftIndent = InchesToPoints(0.5)
        .ParagraphFormat.RightIndent = InchesToPoints(0.5)
        .ParagraphFormat.SpaceBefore = 6
        .ParagraphFormat.SpaceAfter = 6
        
        ' Add left border
        .Borders(wdBorderLeft).LineStyle = wdLineStyleSingle
        .Borders(wdBorderLeft).LineWidth = wdLineWidth225pt
        .Borders(wdBorderLeft).Color = RGB(0, 114, 206) ' Accent Blue
        
        ' Add background shading
        .Shading.BackgroundPatternColor = RGB(240, 248, 255) ' Light Blue
        
        .TypeText "[Insert callout text here]"
    End With
    
    Selection.TypeParagraph
    
    MsgBox "Callout box inserted!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 10: Export Document as PDF
' ============================================================================
Sub ExportToPDF()
    '
    ' Description: Exports active document as PDF
    ' Usage: Run to save PDF in same folder
    '
    
    Dim doc As Document
    Dim pdfPath As String
    
    Set doc = ActiveDocument
    
    ' Check if document is saved
    If doc.Path = "" Then
        MsgBox "Please save the document first!", vbExclamation, "ONI Error"
        Exit Sub
    End If
    
    ' Generate PDF path
    pdfPath = doc.Path & "\" & Replace(doc.Name, ".docx", ".pdf")
    
    ' Export as PDF
    doc.ExportAsFixedFormat _
        OutputFileName:=pdfPath, _
        ExportFormat:=wdExportFormatPDF, _
        OpenAfterExport:=False, _
        OptimizeFor:=wdExportOptimizeForPrint
    
    MsgBox "PDF exported to: " & pdfPath, vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 11: Clean Up Formatting
' ============================================================================
Sub CleanUpFormatting()
    '
    ' Description: Removes extra spaces and inconsistent formatting
    ' Usage: Run on entire document to clean up
    '
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Remove extra spaces
    With doc.Content.Find
        .ClearFormatting
        .Replacement.ClearFormatting
        
        ' Replace double spaces with single space
        .Text = "  "
        .Replacement.Text = " "
        .Forward = True
        .Wrap = wdFindContinue
        .Execute Replace:=wdReplaceAll
        
        ' Replace multiple paragraph marks
        .Text = "^p^p^p"
        .Replacement.Text = "^p^p"
        .Execute Replace:=wdReplaceAll
    End With
    
    MsgBox "Document formatting cleaned up!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 12: Insert Current Date/Time
' ============================================================================
Sub InsertDateTime()
    '
    ' Description: Inserts formatted date and time
    ' Usage: Run where you want date/time
    '
    
    Selection.TypeText Format(Now, "mmmm dd, yyyy - hh:mm AM/PM")
End Sub

' ============================================================================
' UTILITY FUNCTIONS
' ============================================================================

Function InchesToPoints(inches As Double) As Double
    ' Converts inches to points (Word measurement)
    InchesToPoints = inches * 72
End Function

Function LinesToPoints(lines As Double) As Double
    ' Converts line spacing to points
    LinesToPoints = lines * 12
End Function

' ============================================================================
' QUICK REFERENCE: How to Run Macros
' ============================================================================
'
' Method 1: Macros Dialog
' 1. View > Macros (Alt+F8)
' 2. Select macro from list
' 3. Click Run
'
' Method 2: Quick Access Toolbar
' 1. File > Options > Quick Access Toolbar
' 2. Choose "Macros" from dropdown
' 3. Add macro to toolbar
' 4. Click button to run
'
' Method 3: Keyboard Shortcut
' 1. View > Macros > View Macros
' 2. Select macro > Options
' 3. Assign keyboard shortcut (e.g., Ctrl+Shift+C)
'
' Method 4: Custom Ribbon Button
' 1. File > Options > Customize Ribbon
' 2. Create new tab/group
' 3. Add macros to custom group
'
' ============================================================================
