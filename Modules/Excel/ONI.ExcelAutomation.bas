' ============================================================================
' ONI.ExcelAutomation.bas - Excel Badge Generation System
' Version: 1.0
' Description: Create styled badges and ID cards in Excel
' ============================================================================

Option Explicit

' ============================================================================
' BADGE TEMPLATE CREATION
' ============================================================================

Public Sub CreateBadgeTemplate(WS As Worksheet, StartRow As Long, StartCol As Long)
    '
    ' Create badge template structure in worksheet
    '
    ' Args:
    '     WS: Target worksheet
    '     StartRow: Starting row for badge
    '     StartCol: Starting column for badge
    '
    
    Dim BadgeRange As Range
    Dim HeaderRange As Range
    Dim PhotoRange As Range
    
    With WS
        ' Main badge area (10 rows x 6 columns)
        Set BadgeRange = .Range(.Cells(StartRow, StartCol), _
                                .Cells(StartRow + 9, StartCol + 5))
        
        ' Header section (rows 1-2)
        Set HeaderRange = .Range(.Cells(StartRow, StartCol), _
                                 .Cells(StartRow + 1, StartCol + 5))
        
        ' Photo placeholder (rows 3-6, cols 1-2)
        Set PhotoRange = .Range(.Cells(StartRow + 2, StartCol), _
                               .Cells(StartRow + 5, StartCol + 1))
        
        ' Format badge border
        With BadgeRange
            .Borders.LineStyle = xlContinuous
            .Borders.Weight = xlThick
            .Borders.Color = RGB(0, 0, 0)
        End With
        
        ' Format header
        With HeaderRange
            .Merge
            .Value = "BADGE TEMPLATE"
            .Font.Bold = True
            .Font.Size = 16
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = RGB(0, 120, 215)
            .Font.Color = RGB(255, 255, 255)
        End With
        
        ' Format photo area
        With PhotoRange
            .Merge
            .Value = "PHOTO"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = RGB(220, 220, 220)
            .Font.Color = RGB(100, 100, 100)
            .Font.Size = 12
        End With
        
        ' Name label
        .Cells(StartRow + 2, StartCol + 3).Value = "Name:"
        .Cells(StartRow + 2, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 2, StartCol + 4).Value = "[NAME]"
        
        ' Title label
        .Cells(StartRow + 3, StartCol + 3).Value = "Title:"
        .Cells(StartRow + 3, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 3, StartCol + 4).Value = "[TITLE]"
        
        ' ID label
        .Cells(StartRow + 4, StartCol + 3).Value = "ID:"
        .Cells(StartRow + 4, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 4, StartCol + 4).Value = "[ID]"
        
        ' Department label
        .Cells(StartRow + 5, StartCol + 3).Value = "Dept:"
        .Cells(StartRow + 5, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 5, StartCol + 4).Value = "[DEPT]"
        
        ' Barcode placeholder
        Dim BarcodeRange As Range
        Set BarcodeRange = .Range(.Cells(StartRow + 7, StartCol), _
                                  .Cells(StartRow + 8, StartCol + 5))
        With BarcodeRange
            .Merge
            .Value = "BARCODE PLACEHOLDER"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = RGB(255, 255, 255)
            .Font.Name = "Courier New"
            .Font.Size = 10
            .Borders.LineStyle = xlContinuous
        End With
        
        ' Footer
        .Cells(StartRow + 9, StartCol).Value = "Valid Until: [DATE]"
        .Cells(StartRow + 9, StartCol).Font.Size = 8
        
    End With
    
End Sub

' ============================================================================
' CYBERPUNK BADGE GENERATION
' ============================================================================

Public Sub GenerateCyberpunkBadge(WS As Worksheet, StartRow As Long, StartCol As Long, _
                                  BadgeName As String, BadgeTitle As String, _
                                  BadgeID As String, Optional StyleSeed As String = "")
    '
    ' Generate cyberpunk-styled badge
    '
    
    ' Set seed if provided
    If StyleSeed <> "" Then
        SetONISeed StyleSeed
    Else
        StyleSeed = GenerateONISeed("CYB")
    End If
    
    Dim PrimaryColor As Long
    Dim AccentColor As Long
    Dim BgColor As Long
    
    ' Get random colors
    PrimaryColor = GetRandomColorFromPalette("cyberpunk_v1", "primary")
    AccentColor = GetRandomColorFromPalette("cyberpunk_v1", "accent")
    BgColor = GetRandomColorFromPalette("cyberpunk_v1", "background")
    
    With WS
        ' Main badge border (10 rows x 6 columns)
        Dim BadgeRange As Range
        Set BadgeRange = .Range(.Cells(StartRow, StartCol), _
                               .Cells(StartRow + 9, StartCol + 5))
        
        With BadgeRange
            .Borders.LineStyle = xlContinuous
            .Borders.Weight = xlThick
            .Borders.Color = PrimaryColor
            .Interior.Color = BgColor
        End With
        
        ' Header with neon effect
        Dim HeaderRange As Range
        Set HeaderRange = .Range(.Cells(StartRow, StartCol), _
                                .Cells(StartRow + 1, StartCol + 5))
        With HeaderRange
            .Merge
            .Value = "◢ CYBERPUNK ID ◣"
            .Font.Bold = True
            .Font.Size = 14
            .Font.Name = "Consolas"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = PrimaryColor
            .Font.Color = BgColor
        End With
        
        ' Photo area with tech grid
        Dim PhotoRange As Range
        Set PhotoRange = .Range(.Cells(StartRow + 2, StartCol), _
                               .Cells(StartRow + 5, StartCol + 1))
        With PhotoRange
            .Merge
            .Value = "█▓▒░ PHOTO ░▒▓█"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = RGB(26, 26, 32)
            .Font.Color = PrimaryColor
            .Font.Size = 10
            .Font.Name = "Consolas"
            .Borders.LineStyle = xlContinuous
            .Borders.Color = AccentColor
        End With
        
        ' Name (large, bold)
        .Cells(StartRow + 2, StartCol + 3).Value = "▸ NAME"
        .Cells(StartRow + 2, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 2, StartCol + 3).Font.Color = AccentColor
        .Cells(StartRow + 2, StartCol + 3).Font.Size = 9
        
        Dim NameRange As Range
        Set NameRange = .Range(.Cells(StartRow + 3, StartCol + 2), _
                              .Cells(StartRow + 3, StartCol + 5))
        With NameRange
            .Merge
            .Value = UCase(BadgeName)
            .Font.Bold = True
            .Font.Size = 12
            .Font.Color = PrimaryColor
            .HorizontalAlignment = xlCenter
        End With
        
        ' Title
        .Cells(StartRow + 4, StartCol + 3).Value = "▸ CLEARANCE"
        .Cells(StartRow + 4, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 4, StartCol + 3).Font.Color = AccentColor
        .Cells(StartRow + 4, StartCol + 3).Font.Size = 8
        
        Dim TitleRange As Range
        Set TitleRange = .Range(.Cells(StartRow + 5, StartCol + 2), _
                               .Cells(StartRow + 5, StartCol + 5))
        With TitleRange
            .Merge
            .Value = UCase(BadgeTitle)
            .Font.Size = 10
            .Font.Color = RGB(255, 255, 255)
            .HorizontalAlignment = xlCenter
        End With
        
        ' ID with tech styling
        Dim IDRange As Range
        Set IDRange = .Range(.Cells(StartRow + 6, StartCol), _
                            .Cells(StartRow + 6, StartCol + 5))
        With IDRange
            .Merge
            .Value = "━━━ ID: " & BadgeID & " ━━━"
            .Font.Name = "Courier New"
            .Font.Size = 10
            .Font.Color = AccentColor
            .HorizontalAlignment = xlCenter
            .Interior.Color = RGB(16, 16, 21)
        End With
        
        ' Tech greebles (random decorative elements)
        Dim i As Integer
        For i = 1 To 3
            Dim GreebleRow As Long
            Dim GreebleCol As Long
            GreebleRow = StartRow + 7 + GetRandomInteger(0, 1)
            GreebleCol = StartCol + GetRandomInteger(0, 5)
            
            .Cells(GreebleRow, GreebleCol).Value = GetRandomChoice(Array("▪", "▫", "▸", "◂", "●", "○"))
            .Cells(GreebleRow, GreebleCol).Font.Color = AccentColor
            .Cells(GreebleRow, GreebleCol).Font.Size = 8
        Next i
        
        ' Barcode representation
        Dim BarcodeRange As Range
        Set BarcodeRange = .Range(.Cells(StartRow + 8, StartCol), _
                                  .Cells(StartRow + 8, StartCol + 5))
        With BarcodeRange
            .Merge
            .Value = "║││║│││║║││║││║│║││"
            .Font.Name = "Courier New"
            .Font.Size = 14
            .Font.Color = RGB(255, 255, 255)
            .HorizontalAlignment = xlCenter
            .Interior.Color = RGB(255, 255, 255)
        End With
        
        ' Footer with seed
        .Cells(StartRow + 9, StartCol).Value = "SEED: " & StyleSeed
        .Cells(StartRow + 9, StartCol).Font.Size = 7
        .Cells(StartRow + 9, StartCol).Font.Color = RGB(100, 100, 100)
        
        .Cells(StartRow + 9, StartCol + 4).Value = Format(Date, "MM/YYYY")
        .Cells(StartRow + 9, StartCol + 4).Font.Size = 7
        .Cells(StartRow + 9, StartCol + 4).Font.Color = RGB(100, 100, 100)
        .Cells(StartRow + 9, StartCol + 4).HorizontalAlignment = xlRight
        
    End With
    
    ' Add note with seed
    Application.StatusBar = "✓ Cyberpunk badge generated with seed: " & StyleSeed
    
End Sub

' ============================================================================
' MINIMAL CORPORATE BADGE
' ============================================================================

Public Sub GenerateMinimalBadge(WS As Worksheet, StartRow As Long, StartCol As Long, _
                               BadgeName As String, BadgeTitle As String, _
                               BadgeID As String, Optional StyleSeed As String = "")
    '
    ' Generate minimal corporate-styled badge
    '
    
    If StyleSeed = "" Then StyleSeed = GenerateONISeed("MIN")
    SetONISeed StyleSeed
    
    Dim CorporateBlue As Long
    Dim LightGray As Long
    
    CorporateBlue = RGB(0, 82, 165)
    LightGray = RGB(245, 245, 245)
    
    With WS
        ' Main badge border
        Dim BadgeRange As Range
        Set BadgeRange = .Range(.Cells(StartRow, StartCol), _
                               .Cells(StartRow + 9, StartCol + 5))
        
        With BadgeRange
            .Borders.LineStyle = xlContinuous
            .Borders.Weight = xlMedium
            .Borders.Color = RGB(200, 200, 200)
            .Interior.Color = RGB(255, 255, 255)
        End With
        
        ' Clean header
        Dim HeaderRange As Range
        Set HeaderRange = .Range(.Cells(StartRow, StartCol), _
                                .Cells(StartRow + 1, StartCol + 5))
        With HeaderRange
            .Merge
            .Value = "EMPLOYEE BADGE"
            .Font.Bold = True
            .Font.Size = 12
            .Font.Name = "Calibri"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = CorporateBlue
            .Font.Color = RGB(255, 255, 255)
        End With
        
        ' Photo area
        Dim PhotoRange As Range
        Set PhotoRange = .Range(.Cells(StartRow + 2, StartCol), _
                               .Cells(StartRow + 5, StartCol + 1))
        With PhotoRange
            .Merge
            .Value = "PHOTO"
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Interior.Color = LightGray
            .Font.Color = RGB(150, 150, 150)
            .Borders.LineStyle = xlContinuous
            .Borders.Color = RGB(200, 200, 200)
        End With
        
        ' Name section
        .Cells(StartRow + 2, StartCol + 3).Value = "Name:"
        .Cells(StartRow + 2, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 2, StartCol + 3).Font.Size = 9
        
        .Cells(StartRow + 3, StartCol + 3).Value = BadgeName
        .Cells(StartRow + 3, StartCol + 3).Font.Size = 11
        .Cells(StartRow + 3, StartCol + 3).Font.Bold = True
        
        ' Title
        .Cells(StartRow + 4, StartCol + 3).Value = "Title:"
        .Cells(StartRow + 4, StartCol + 3).Font.Bold = True
        .Cells(StartRow + 4, StartCol + 3).Font.Size = 9
        
        .Cells(StartRow + 5, StartCol + 3).Value = BadgeTitle
        .Cells(StartRow + 5, StartCol + 3).Font.Size = 10
        
        ' ID
        Dim IDRange As Range
        Set IDRange = .Range(.Cells(StartRow + 6, StartCol), _
                            .Cells(StartRow + 6, StartCol + 5))
        With IDRange
            .Merge
            .Value = "ID: " & BadgeID
            .Font.Size = 10
            .HorizontalAlignment = xlCenter
            .Interior.Color = LightGray
        End With
        
        ' Barcode
        Dim BarcodeRange As Range
        Set BarcodeRange = .Range(.Cells(StartRow + 7, StartCol), _
                                  .Cells(StartRow + 8, StartCol + 5))
        With BarcodeRange
            .Merge
            .Value = "| | || ||| | || | ||| ||"
            .Font.Name = "Libre Barcode 128"
            .Font.Size = 20
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
        End With
        
        ' Footer
        .Cells(StartRow + 9, StartCol).Value = "Valid: " & Format(Date, "MM/DD/YYYY")
        .Cells(StartRow + 9, StartCol).Font.Size = 8
        
    End With
    
    Application.StatusBar = "✓ Minimal badge generated with seed: " & StyleSeed
    
End Sub

' ============================================================================
' BATCH BADGE GENERATION
' ============================================================================

Public Sub BatchGenerateBadges(DataRange As Range, OutputStartRow As Long, _
                               OutputStartCol As Long, BadgeStyle As String)
    '
    ' Generate multiple badges from data range
    '
    ' Args:
    '     DataRange: Range with columns: Name, Title, ID
    '     OutputStartRow: Starting row for first badge
    '     OutputStartCol: Starting column for badges
    '     BadgeStyle: "cyberpunk" or "minimal"
    '
    
    Dim WS As Worksheet
    Set WS = DataRange.Worksheet
    
    Dim i As Long
    Dim CurrentRow As Long
    Dim BadgeSpacing As Long
    
    BadgeSpacing = 12  ' Rows between badges
    CurrentRow = OutputStartRow
    
    Application.ScreenUpdating = False
    
    For i = 2 To DataRange.Rows.Count  ' Skip header row
        Dim EmpName As String
        Dim EmpTitle As String
        Dim EmpID As String
        
        EmpName = DataRange.Cells(i, 1).Value
        EmpTitle = DataRange.Cells(i, 2).Value
        EmpID = DataRange.Cells(i, 3).Value
        
        ' Generate badge based on style
        If BadgeStyle = "cyberpunk" Then
            GenerateCyberpunkBadge WS, CurrentRow, OutputStartCol, EmpName, EmpTitle, EmpID
        Else
            GenerateMinimalBadge WS, CurrentRow, OutputStartCol, EmpName, EmpTitle, EmpID
        End If
        
        CurrentRow = CurrentRow + BadgeSpacing
    Next i
    
    Application.ScreenUpdating = True
    
    MsgBox "Generated " & (DataRange.Rows.Count - 1) & " badges!", vbInformation, "ONI Batch Complete"
    
End Sub

' ============================================================================
' EXPORT FUNCTIONS
' ============================================================================

Public Sub ExportBadgeAsPDF(BadgeRange As Range, OutputPath As String)
    '
    ' Export badge range as PDF
    '
    BadgeRange.ExportAsFixedFormat Type:=xlTypePDF, _
                                   Filename:=OutputPath, _
                                   Quality:=xlQualityStandard, _
                                   IncludeDocProperties:=False, _
                                   IgnorePrintAreas:=False, _
                                   OpenAfterPublish:=False
End Sub

Public Sub ExportBadgeAsImage(BadgeRange As Range, OutputPath As String)
    '
    ' Export badge range as image (requires copying to chart)
    '
    ' Note: Excel doesn't natively export ranges as images
    ' This creates a chart as workaround
    '
    
    Dim ChartObj As ChartObject
    Set ChartObj = BadgeRange.Parent.ChartObjects.Add( _
        Left:=BadgeRange.Left, _
        Top:=BadgeRange.Top, _
        Width:=BadgeRange.Width, _
        Height:=BadgeRange.Height)
    
    BadgeRange.CopyPicture Appearance:=xlScreen, Format:=xlPicture
    ChartObj.Activate
    ActiveChart.Paste
    ActiveChart.Export Filename:=OutputPath, FilterName:="PNG"
    
    ChartObj.Delete
    
End Sub
