Attribute VB_Name = "ONI_Trace_Module"

Sub ONI_QuickTrace(ImagePath As String, DetailLevel As Integer, Smoothing As Integer)
    On Error GoTo ErrorHandler
    
    Dim doc As Document
    Dim s As Shape
    Dim impFilter As ImportFilter
    Dim t As TraceSettings
    
    Set doc = ActiveDocument
    If doc Is Nothing Then Set doc = CreateDocument()
    
    ' 1. Import Image
    ' Using basic Import (ImportEx allows generic structs but basic is often simpler for single layout)
    ' However, the original script used ImportEx, stick to it for consistency but verify imports.
    doc.ActiveLayer.Import ImagePath
    
    ' Check selection
    If doc.SelectionRange.Shapes.Count = 0 Then
        Err.Raise 1001, "ONI", "Image import failed or nothing selected."
    End If
    
    Set s = doc.SelectionRange.Shapes(1)
    
    ' 2. Validation
    If s.Type <> cdrBitmapShape Then
        ' Try converting? No, fail fast.
        Err.Raise 1002, "ONI", "Selected object is not a bitmap."
    End If
    
    ' 3. Trace (PowerTrace)
    ' Trace(TraceType) -> 3 = cdrTraceDetailedLogo (Check Corel documentation, usually 3 or similar)
    Set t = s.Bitmap.Trace(cdrTraceDetailedLogo) 
    
    If t Is Nothing Then
        Err.Raise 1003, "ONI", "Failed to initialize PowerTrace."
    End If
    
    t.DetailLevel = DetailLevel
    t.Smoothing = Smoothing
    
    ' Commit
    t.Finish
    
    ' 4. Cleanup
    s.Delete ' Delete original bitmap
    doc.ActiveWindow.ActiveView.ZoomContents
    
    ' Return success marker (commented out msgbox for silent op)
    ' MsgBox "Success" 
    Exit Sub
    
ErrorHandler:
    ' Re-throw for PowerShell to catch via check (or leave modification visible)
    Err.Raise Err.Number, "ONI_Trace", Err.Description
End Sub
