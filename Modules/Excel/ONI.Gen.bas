' ============================================================================
' ONI.Gen.bas - ONI Generative Core (VBA)
' Version: 1.0
' Description: Core functions for randomness, seeding, and color palettes
' ============================================================================

Option Explicit

Private CurrentSeed As String

' ============================================================================
' SEED MANAGEMENT
' ============================================================================

Public Function GenerateONISeed(prefix As String) As String
    Dim timestamp As String
    Dim rndVal As String
    Dim hash As String
    
    timestamp = Format(Now, "yyyymmdd")
    rndVal = CStr(Rnd())
    
    ' Simple pseudo-hash
    hash = Right(Hex(CLng(Val(rndVal) * 100000)), 4)
    If Len(hash) < 4 Then hash = String(4 - Len(hash), "0") & hash
    
    GenerateONISeed = "ONI-" & prefix & "-" & timestamp & "-" & hash
    CurrentSeed = GenerateONISeed
End Function

Public Sub SetONISeed(seed As String)
    CurrentSeed = seed
    ' Seeding Rnd in VBA is limited, but we can restart sequence
    Dim val As Long
    On Error Resume Next
    val = CLng("&H" & Right(seed, 4))
    Rnd (-1)
    Randomize val
    On Error GoTo 0
End Sub

' ============================================================================
' RANDOM FUNCTIONS
' ============================================================================

Public Function GetRandomChoice(arr As Variant) As Variant
    Randomize
    GetRandomChoice = arr(LBound(arr) + Int((UBound(arr) - LBound(arr) + 1) * Rnd))
End Function

Public Function GetRandomInteger(min As Integer, max As Integer) As Integer
    Randomize
    GetRandomInteger = Int((max - min + 1) * Rnd + min)
End Function

' ============================================================================
' COLOR PALETTES
' ============================================================================

Public Function GetRandomColorFromPalette(paletteName As String, category As String) As Long
    Dim hexColor As String
    
    ' Cyberpunk V1 Palette
    If paletteName = "cyberpunk_v1" Then
        If category = "primary" Then
            hexColor = GetRandomChoice(Array("00F0FF", "FF0055", "B026FF", "39FF14"))
        ElseIf category = "accent" Then
            hexColor = GetRandomChoice(Array("FFFF00", "00FF88", "FF6B00"))
        ElseIf category = "background" Then
            hexColor = GetRandomChoice(Array("0A0A0F", "1A1A20", "101015"))
        End If
        
    ' Minimalism V1 Palette
    ElseIf paletteName = "minimalism_v1" Then
        If category = "primary" Then
            hexColor = GetRandomChoice(Array("0052A5", "4D4D4D", "FFFFFF"))
        ElseIf category = "accent" Then
            hexColor = GetRandomChoice(Array("0072CE", "D9D9D9"))
        ElseIf category = "background" Then
            hexColor = GetRandomChoice(Array("F5F5F5", "FFFFFF"))
        End If
    
    ' Default
    Else
        hexColor = "FFFFFF"
    End If
    
    If hexColor = "" Then hexColor = "FFFFFF"
    
    ' Convert HTML Hex (RRGGBB) to Excel Long (BBGGRR)
    ' This is a simplified conversion
    Dim R As Long, G As Long, B As Long
    R = CLng("&H" & Left(hexColor, 2))
    G = CLng("&H" & Mid(hexColor, 3, 2))
    B = CLng("&H" & Right(hexColor, 2))
    
    GetRandomColorFromPalette = RGB(R, G, B)
End Function
