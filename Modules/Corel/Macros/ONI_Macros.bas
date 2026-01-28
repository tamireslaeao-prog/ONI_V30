' ============================================================================
' ONI.Macros.vba - CorelDRAW Automation Macros
' Version: 1.0
' Description: Automate style application and effects in CorelDRAW
' ============================================================================
' 
' INSTALLATION:
' 1. Open CorelDRAW
' 2. Tools > Visual Basic > Visual Basic Editor (Alt+F11)
' 3. Insert > Module
' 4. Paste this code
' 5. Tools > Macros > Run Macro (Alt+F8)
' 
' ============================================================================

' ============================================================================
' MACRO 1: Apply Cyberpunk Neon Effect
' ============================================================================
Sub ApplyCyberpunkNeon()
    '
    ' Description: Applies neon glow effect to selected text or shape
    ' Usage: Select object, run macro
    '
    
    Dim OrigSelection As ShapeRange
    Dim s As Shape
    
    ' Check if anything is selected
    If ActiveSelection.Shapes.Count = 0 Then
        MsgBox "Please select an object first!", vbExclamation, "ONI Cyberpunk"
        Exit Sub
    End If
    
    Set OrigSelection = ActiveSelection.Shapes
    
    ' Apply to each selected object
    For Each s In OrigSelection
        ' Set outline
        s.Outline.Width = 2
        s.Outline.Color.CMYKAssign 100, 0, 0, 0 ' Cyan
        
        ' Apply contour effect
        With s.CreateContour(cdrContourInside, 5, 1, _
            CreateCMYKColor(100, 0, 0, 0), _
            CreateCMYKColor(0, 0, 0, 100), _
            cdrContourLinearFountainFill)
            .Separation = 1
            .AccelerationValue = 0
        End With
        
        ' Apply glow (drop shadow with glow preset)
        With s.CreateDropShadow(cdrDropShadowGlow)
            .Opacity = 75
            .Feather = 15
            .FadeRate = 0
            .Color.CMYKAssign 100, 0, 0, 0 ' Cyan glow
            .MergeMode = cdrMergeModeScreen
        End With
        
    Next s
    
    MsgBox "Cyberpunk Neon effect applied!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 2: Create Technical Badge Layout
' ============================================================================
Sub CreateTechnicalBadge()
    '
    ' Description: Creates complete badge layout with photo zone, text fields, barcode
    ' Usage: Run on blank document
    '
    
    Dim doc As Document
    Dim page As page
    Dim rect As Shape, txt As Shape
    Dim x As Double, y As Double
    
    Set doc = ActiveDocument
    Set page = ActivePage
    
    ' Set page size to ID-1 standard (85.6mm x 53.98mm)
    page.SetSize 85.6, 53.98
    
    ' Create background
    Set rect = page.ActiveLayer.CreateRectangle(0, 53.98, 85.6, 0)
    rect.Fill.UniformColor.CMYKAssign 0, 0, 0, 100 ' Rich black
    rect.Outline.Width = 0
    
    ' Create photo container
    Set rect = page.ActiveLayer.CreateRectangle(5, 48.98, 30, 18.98)
    rect.Fill.UniformColor.CMYKAssign 0, 0, 0, 70 ' Gray placeholder
    rect.Outline.Width = 0.5
    rect.Outline.Color.CMYKAssign 0, 0, 0, 100
    
    ' Add "PHOTO" text
    Set txt = page.ActiveLayer.CreateArtisticText(15, 35, "PHOTO")
    txt.Text.size = 8
    txt.Text.Font = "Helvetica"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 0 ' White
    
    ' Create name field
    Set txt = page.ActiveLayer.CreateArtisticText(35, 45, "[NAME]")
    txt.Text.size = 12
    txt.Text.Font = "Helvetica Bold"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 0
    
    ' Create title field
    Set txt = page.ActiveLayer.CreateArtisticText(35, 38, "[TITLE]")
    txt.Text.size = 8
    txt.Text.Font = "Helvetica"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 0
    
    ' Create employee ID field
    Set txt = page.ActiveLayer.CreateArtisticText(35, 32, "ID: [00000]")
    txt.Text.size = 7
    txt.Text.Font = "Helvetica"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 0
    
    ' Create barcode placeholder
    Set rect = page.ActiveLayer.CreateRectangle(5, 15, 50, 5)
    rect.Fill.UniformColor.CMYKAssign 0, 0, 0, 0
    rect.Outline.Width = 0.25
    rect.Outline.Color.CMYKAssign 0, 0, 0, 100
    
    ' Add barcode text
    Set txt = page.ActiveLayer.CreateArtisticText(15, 8, "BARCODE")
    txt.Text.size = 6
    txt.Text.Font = "Courier New"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 100
    
    ' Create QR code placeholder
    Set rect = page.ActiveLayer.CreateRectangle(60, 20, 80, 5)
    rect.Fill.UniformColor.CMYKAssign 0, 0, 0, 0
    rect.Outline.Width = 0.25
    rect.Outline.Color.CMYKAssign 0, 0, 0, 100
    
    ' Add serial number
    Set txt = page.ActiveLayer.CreateArtisticText(5, 3, "SN: XXX-XXXXX-XX")
    txt.Text.size = 5
    txt.Text.Font = "Courier New"
    txt.Fill.UniformColor.CMYKAssign 0, 0, 0, 100
    
    ActiveWindow.Refresh
    MsgBox "Technical badge layout created!" & vbCrLf & _
           "Replace placeholders with actual data.", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 3: Apply Random Tech Greebles
' ============================================================================
Sub ApplyRandomGreebles()
    '
    ' Description: Adds random technical details to empty areas
    ' Usage: Run on existing design
    '
    
    Dim i As Integer
    Dim x As Double, y As Double
    Dim size As Double, rotation As Double
    Dim greeble As Shape
    Dim greebleType As Integer
    
    ' Randomize seed
    Randomize Timer
    
    ' Create 10-20 random greebles
    For i = 1 To Int(Rnd * 10) + 10
        ' Random position
        x = Rnd * ActivePage.SizeWidth
        y = Rnd * ActivePage.SizeHeight
        
        ' Random size
        size = Rnd * 3 + 1
        
        ' Random rotation
        rotation = Rnd * 360
        
        ' Random greeble type
        greebleType = Int(Rnd * 5)
        
        Select Case greebleType
            Case 0 ' Small square
                Set greeble = ActiveLayer.CreateRectangle(x, y + size, x + size, y)
                greeble.Fill.UniformColor.CMYKAssign 100, 0, 0, 0
                greeble.Outline.Width = 0
                
            Case 1 ' Circle
                Set greeble = ActiveLayer.CreateEllipse(x, y + size, x + size, y)
                greeble.Fill.UniformColor.CMYKAssign 0, 100, 0, 0
                greeble.Outline.Width = 0
                
            Case 2 ' Triangle
                Set greeble = ActiveLayer.CreatePolygon(x, y, size / 2, 3, 0, False)
                greeble.Fill.UniformColor.CMYKAssign 0, 0, 100, 0
                greeble.Outline.Width = 0
                
            Case 3 ' Line
                Set greeble = ActiveLayer.CreateLineSegment(x, y, x + size, y + size)
                greeble.Outline.Width = 0.5
                greeble.Outline.Color.CMYKAssign 100, 0, 0, 0
                
            Case 4 ' Plus sign
                Set greeble = ActiveLayer.CreateArtisticText(x, y, "+")
                greeble.Text.size = size * 3
                greeble.Fill.UniformColor.CMYKAssign 0, 100, 100, 0
        End Select
        
        ' Apply rotation
        If Not greeble Is Nothing Then
            greeble.Rotate rotation
            greeble.Transparency.ApplyUniformTransparency 30 + (Rnd * 40)
        End If
    Next i
    
    MsgBox "Greebles applied! Total: " & i - 1, vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 4: Create Synthwave Gradient Background
' ============================================================================
Sub CreateSynthwaveGradient()
    '
    ' Description: Creates multi-color synthwave gradient background
    ' Usage: Run on blank document
    '
    
    Dim rect As Shape
    Dim page As page
    
    Set page = ActivePage
    
    ' Create full-page rectangle
    Set rect = page.ActiveLayer.CreateRectangle(0, page.SizeHeight, page.SizeWidth, 0)
    
    ' Apply fountain fill with multiple color stops
    With rect.Fill
        .Type = cdrFountainFill
        .Fountain.Type = cdrLinearFountainFill
        .Fountain.Angle = 90
        
        ' Create color blend: Pink -> Purple -> Blue
        .Fountain.Colors.RemoveAll
        
        ' Hot Pink at 0%
        .Fountain.Colors.Add CreateRGBColor(255, 0, 110), 0
        
        ' Electric Purple at 33%
        .Fountain.Colors.Add CreateRGBColor(131, 56, 236), 33
        
        ' Cyber Blue at 66%
        .Fountain.Colors.Add CreateRGBColor(58, 134, 255), 66
        
        ' Cyan at 100%
        .Fountain.Colors.Add CreateRGBColor(6, 255, 165), 100
    End With
    
    rect.Outline.Width = 0
    
    ' Send to back
    rect.OrderToBack
    
    MsgBox "Synthwave gradient created!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 5: Apply Print-Safe CMYK Conversion
' ============================================================================
Sub ConvertToPrintSafeCMYK()
    '
    ' Description: Converts all RGB colors to CMYK and applies rich black
    ' Usage: Run on completed design before print export
    '
    
    Dim s As Shape
    Dim sr As ShapeRange
    
    ' Get all shapes on page
    Set sr = ActivePage.Shapes.All
    
    ' Convert document color mode
    ActiveDocument.ColorMode = cdrCMYK
    
    For Each s In sr
        ' Convert fill colors
        If s.Fill.Type = cdrUniformFill Then
            If s.Fill.UniformColor.Type = cdrColorRGB Then
                ' Check if it's meant to be black
                If s.Fill.UniformColor.RGBRed < 20 And _
                   s.Fill.UniformColor.RGBGreen < 20 And _
                   s.Fill.UniformColor.RGBBlue < 20 Then
                    ' Apply rich black
                    s.Fill.UniformColor.CMYKAssign 60, 40, 40, 100
                Else
                    ' Standard RGB to CMYK conversion
                    s.Fill.UniformColor.ConvertToCMYK
                End If
            End If
        End If
        
        ' Convert outline colors
        If s.Outline.Type <> cdrNoOutline Then
            If s.Outline.Color.Type = cdrColorRGB Then
                If s.Outline.Color.RGBRed < 20 And _
                   s.Outline.Color.RGBGreen < 20 And _
                   s.Outline.Color.RGBBlue < 20 Then
                    s.Outline.Color.CMYKAssign 60, 40, 40, 100
                Else
                    s.Outline.Color.ConvertToCMYK
                End If
            End If
        End If
        
        ' Set black text to overprint
        If s.Type = cdrTextShape Then
            If s.Fill.UniformColor.Type = cdrColorCMYK Then
                If s.Fill.UniformColor.CMYKCyan >= 60 And _
                   s.Fill.UniformColor.CMYKBlack = 100 Then
                    s.Overprint = True
                End If
            End If
        End If
    Next s
    
    MsgBox "Design converted to print-safe CMYK!" & vbCrLf & _
           "Black text set to overprint.", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 6: Create Scanline Effect (Cyberpunk)
' ============================================================================
Sub CreateScanlineEffect()
    '
    ' Description: Creates horizontal scanlines overlay
    ' Usage: Run to add cyberpunk scanline texture
    '
    
    Dim i As Integer
    Dim line As Shape
    Dim spacing As Double
    Dim pageHeight As Double, pageWidth As Double
    
    pageHeight = ActivePage.SizeHeight
    pageWidth = ActivePage.SizeWidth
    spacing = 4 ' 4mm between lines
    
    ' Create new layer for scanlines
    ActivePage.CreateLayer "Scanlines"
    
    ' Create horizontal lines
    For i = 0 To Int(pageHeight / spacing)
        Set line = ActiveLayer.CreateLineSegment(0, i * spacing, pageWidth, i * spacing)
        line.Outline.Width = 0.25
        line.Outline.Color.CMYKAssign 100, 0, 0, 0 ' Cyan
        line.Transparency.ApplyUniformTransparency 85 ' 15% visible
    Next i
    
    ' Set blend mode
    For Each line In ActiveLayer.Shapes.All
        line.Transparency.MergeMode = cdrMergeModeScreen
    Next line
    
    MsgBox "Scanlines created! Total lines: " & i, vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 7: Batch Export (PDF, PNG, SVG)
' ============================================================================
Sub BatchExportFormats()
    '
    ' Description: Exports current document in multiple formats
    ' Usage: Save your document first, then run
    '
    
    Dim doc As Document
    Dim filePath As String
    Dim fileName As String
    Dim exportPath As String
    
    Set doc = ActiveDocument
    
    ' Check if document is saved
    If doc.FilePath = "" Then
        MsgBox "Please save the document first!", vbExclamation, "ONI Export"
        Exit Sub
    End If
    
    ' Get file path and name
    filePath = doc.FilePath
    fileName = doc.Name
    fileName = Left(fileName, InStrRev(fileName, ".") - 1) ' Remove extension
    
    ' Export PDF
    exportPath = filePath & fileName & "_print.pdf"
    doc.PublishToPDF exportPath
    
    ' Export PNG (300 DPI)
    exportPath = filePath & fileName & "_preview.png"
    ActivePage.Export exportPath, cdrPNG, cdrSelection, , _
        "Resolution:300;MaintainAspect:1;AntiAliasing:1"
    
    ' Export SVG
    exportPath = filePath & fileName & "_vector.svg"
    doc.Export exportPath, cdrSVG
    
    MsgBox "Batch export complete!" & vbCrLf & _
           "Files saved to: " & filePath, vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 8: Create Tech Border Frame
' ============================================================================
Sub CreateTechBorderFrame()
    '
    ' Description: Creates technical/mechanical border frame
    ' Usage: Run on existing design to add frame
    '
    
    Dim outerRect As Shape, innerRect As Shape
    Dim corner As Shape
    Dim i As Integer
    Dim margin As Double
    
    margin = 10 ' 10mm margin
    
    ' Create outer rectangle
    Set outerRect = ActiveLayer.CreateRectangle( _
        margin, _
        ActivePage.SizeHeight - margin, _
        ActivePage.SizeWidth - margin, _
        margin)
    
    outerRect.Outline.Width = 3
    outerRect.Outline.Color.CMYKAssign 100, 0, 0, 0 ' Cyan
    outerRect.Fill.Type = cdrNoFill
    
    ' Create inner rectangle (5mm inside outer)
    Set innerRect = ActiveLayer.CreateRectangle( _
        margin + 5, _
        ActivePage.SizeHeight - margin - 5, _
        ActivePage.SizeWidth - margin - 5, _
        margin + 5)
    
    innerRect.Outline.Width = 1
    innerRect.Outline.Color.CMYKAssign 100, 0, 0, 0
    innerRect.Fill.Type = cdrNoFill
    
    ' Add corner decorations (small diagonal lines)
    For i = 0 To 3
        Dim x1 As Double, y1 As Double, x2 As Double, y2 As Double
        
        Select Case i
            Case 0 ' Top-left
                x1 = margin: y1 = ActivePage.SizeHeight - margin
                x2 = margin + 8: y2 = ActivePage.SizeHeight - margin - 8
            Case 1 ' Top-right
                x1 = ActivePage.SizeWidth - margin: y1 = ActivePage.SizeHeight - margin
                x2 = ActivePage.SizeWidth - margin - 8: y2 = ActivePage.SizeHeight - margin - 8
            Case 2 ' Bottom-left
                x1 = margin: y1 = margin
                x2 = margin + 8: y2 = margin + 8
            Case 3 ' Bottom-right
                x1 = ActivePage.SizeWidth - margin: y1 = margin
                x2 = ActivePage.SizeWidth - margin - 8: y2 = margin + 8
        End Select
        
        Set corner = ActiveLayer.CreateLineSegment(x1, y1, x2, y2)
        corner.Outline.Width = 2
        corner.Outline.Color.CMYKAssign 0, 100, 0, 0 ' Magenta accent
    Next i
    
    MsgBox "Tech border frame created!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 9: Apply Japanese Vertical Text
' ============================================================================
Sub CreateVerticalJapaneseText()
    '
    ' Description: Creates vertical text frame for Japanese typography
    ' Usage: Run and enter Japanese text
    '
    
    Dim txt As Shape
    Dim inputText As String
    
    ' Get text from user
    inputText = InputBox("Enter Japanese text:", "ONI Japanese Text", "テキスト")
    
    If inputText = "" Then Exit Sub
    
    ' Create artistic text
    Set txt = ActiveLayer.CreateArtisticText( _
        ActivePage.SizeWidth - 50, _
        ActivePage.SizeHeight - 50, _
        inputText)
    
    ' Set font
    txt.Text.Font = "Noto Sans JP"
    txt.Text.size = 48
    
    ' Apply vertical orientation
    txt.Text.Orientation = cdrTextVertical
    
    ' Set color to Japan Red
    txt.Fill.UniformColor.CMYKAssign 0, 100, 100, 0
    
    ' Add subtle outline
    txt.Outline.Width = 1
    txt.Outline.Color.CMYKAssign 60, 40, 40, 100
    
    MsgBox "Vertical Japanese text created!" & vbCrLf & _
           "Adjust position as needed.", vbInformation, "ONI Success"
End Sub

' ============================================================================
' MACRO 10: Smart Duplicate with Variation
' ============================================================================
Sub SmartDuplicateWithVariation()
    '
    ' Description: Duplicates selected object with random variations
    ' Usage: Select object, run to create 5 variations
    '
    
    Dim original As Shape
    Dim duplicate As Shape
    Dim i As Integer
    Dim offsetX As Double, offsetY As Double
    Dim scaleFactor As Double
    Dim rotateDegrees As Double
    
    If ActiveSelection.Shapes.Count = 0 Then
        MsgBox "Please select an object first!", vbExclamation, "ONI Duplicate"
        Exit Sub
    End If
    
    Set original = ActiveSelection.Shapes(1)
    Randomize Timer
    
    ' Create 5 variations
    For i = 1 To 5
        ' Duplicate
        Set duplicate = original.Duplicate()
        
        ' Random offset
        offsetX = (Rnd - 0.5) * 50
        offsetY = (Rnd - 0.5) * 50
        duplicate.Move offsetX, offsetY
        
        ' Random scale (80% to 120%)
        scaleFactor = 0.8 + (Rnd * 0.4)
        duplicate.SetSize duplicate.SizeWidth * scaleFactor, duplicate.SizeHeight * scaleFactor
        
        ' Random rotation
        rotateDegrees = (Rnd - 0.5) * 60
        duplicate.Rotate rotateDegrees
        
        ' Random transparency
        duplicate.Transparency.ApplyUniformTransparency 20 + (Rnd * 40)
        
        ' Slight color variation
        If duplicate.Fill.Type = cdrUniformFill Then
            Dim brighten As Double
            brighten = 0.8 + (Rnd * 0.4)
            
            If duplicate.Fill.UniformColor.Type = cdrColorRGB Then
                duplicate.Fill.UniformColor.RGBAssign _
                    Int(duplicate.Fill.UniformColor.RGBRed * brighten), _
                    Int(duplicate.Fill.UniformColor.RGBGreen * brighten), _
                    Int(duplicate.Fill.UniformColor.RGBBlue * brighten)
            End If
        End If
    Next i
    
    MsgBox "Created " & i - 1 & " variations!", vbInformation, "ONI Success"
End Sub

' ============================================================================
' HELPER FUNCTIONS
' ============================================================================

Function CreateRGBColor(r As Integer, g As Integer, b As Integer) As Color
    Dim col As New Color
    col.RGBAssign r, g, b
    Set CreateRGBColor = col
End Function

Function CreateCMYKColor(c As Integer, m As Integer, y As Integer, k As Integer) As Color
    Dim col As New Color
    col.CMYKAssign c, m, y, k
    Set CreateCMYKColor = col
End Function

' ============================================================================
' QUICK REFERENCE: How to Run Macros
' ============================================================================
'
' Method 1: Macro Menu
' 1. Tools > Macros > Run Macro (Alt+F8)
' 2. Select macro from list
' 3. Click Run
'
' Method 2: Quick Access Toolbar
' 1. Tools > Customization
' 2. Commands tab > Macros
' 3. Drag macro to Quick Access Toolbar
'
' Method 3: Keyboard Shortcut
' 1. Tools > Customization
' 2. Commands tab > Macros
' 3. Select macro > Shortcut Keys
' 4. Assign key combination (e.g., Ctrl+Shift+N)
'
' ============================================================================
