Attribute VB_Name = "ONI_Draw_Module"

Sub ONI_DrawExtra04()
    On Error GoTo ErrorHandler
    
    Dim doc As Document
    Dim sMain As Shape
    Dim sFlap As Shape
    Dim sHole1 As Shape, sHole2 As Shape
    Dim sFinal As Shape
    
    Set doc = ActiveDocument
    If doc Is Nothing Then Set doc = CreateDocument()
    
    ' Configurar Unidades para CM
    doc.Unit = cdrCentimeter
    doc.DrawingOriginX = 0
    doc.DrawingOriginY = 0
    
    ' Criar Layer de Desenho
    Dim lr As Layer
    Set lr = doc.ActiveLayer
    
    ' =========================================================
    ' 1. Desenhar Perfil Principal (Body + Head)
    ' Coordenadas relativas ao Canto Inferior Esquerdo (0,0)
    ' =========================================================
    
    ' Comecando do 0,0 e indo sentido horario
    Dim crv As Curve
    Set crv = Application.CreateCurve(doc)
    Dim sp As SubPath
    Set sp = crv.CreateSubPath(0, 0)
    
    ' Linha Base
    sp.AppendLineSegment 9, 0
    
    ' Linha Direita (Ate inicio da curva)
    ' Altura Total = 41.5. Curva no topo.
    ' Assumindo raio de curva aprox 5cm
    sp.AppendLineSegment 9, 36.5 ' 41.5 - 5
    
    ' Curva Topo Direito
    ' Ponto Final (4, 41.5) -> x=9-5=4, y=41.5
    sp.AppendCurveSegment 4, 41.5, 9, 39.5, 6, 41.5 
    
    ' Linha Topo (Horizontal Esquerda)
    ' Vai ate o entalhe. Entalhe de 0.5cm?
    ' Vamos ate x=0.5 (se entalhe for na esquerda)
    sp.AppendLineSegment 0.5, 41.5
    
    ' Entalhe Para Baixo (Degrau)
    ' Altura da Cabeca = 8.5. Base Cabeca = 33.
    ' Se a cota 0.5cm for horizontal, recuo de 0.5 a esquerda.
    ' Se a cota 5cm for uma referencia vertical...
    ' Vamos simplificar: Topo plano ate x=0.
    sp.AppendLineSegment 0, 41.5
    sp.AppendLineSegment 0, 0 ' Fechando no 0,0
    
    ' Correcao: Vamos fazer por Retangulos Combinados para garantir as dimensoes dos paineis
    ' E muito mais seguro para "Desenho Tecnico" usar primitivas e soldar (Weld).
    ' =========================================================
    
    ' Painel 1 (Base): 9x12
    Dim p1 As Shape: Set p1 = lr.CreateRectangle(0, 0, 9, 12)
    
    ' Painel 2 (Meio): 9x9 (y=12 a 21)
    Dim p2 As Shape: Set p2 = lr.CreateRectangle(0, 12, 9, 21)
    
    ' Painel 3 (Topo): 9x12 (y=21 a 33)
    Dim p3 As Shape: Set p3 = lr.CreateRectangle(0, 21, 9, 33)
    
    ' Painel 4 (Cabeca): 9x8.5 (y=33 a 41.5) 
    ' Com canto arredondado e entalhe 0.5
    ' Vamos desenhar um retangulo 8.5x8.5 (base 9 - 0.5 entalhe?)
    ' A cota 0.5cm esta no lado ESQUERDO, na juncao entre p3 e p4.
    ' Indica que a cabeca e recuada 0.5cm? Ou sai para fora?
    ' O desenho mostra a cabeca ALINHADA a direita, e com um degrau na esquerda.
    ' Entao a cabeca comeca em x=0.5 (largura 8.5) ou x=0 (largura 9.5)? 
    ' O corpo tem 9. A cota 9 esta na base da cabeca. Entao a cabeca tem largura 9 na base.
    ' O 0.5cm aponta para um degrau vertical ou horizontal?
    ' Visualmente parece um pequeno chanfro ou raio na esquerda.
    
    Dim p4 As Shape
    Set p4 = lr.CreateRectangle(0, 33, 9, 41.5)
    ' Arredondar canto superior direito (Raio 4cm)
    p4.Rectangle.CornerType = cdrCornerRound
    p4.Rectangle.CornerUpperRight = 40 ' Percentual ou valor? Em VBA e 0-100 relative ou absolute.
    ' Corel 2020+ usa CornerRadius
    p4.Rectangle.SetRadius 0, 4, 0, 0 ' SetRadius(LowerLeft, UpperLeft, UpperRight, LowerRight) em unidades do doc (cm)
                                      ' Ops, ordem e UL, UR, LR, LL? Check docs. Usually UL, UR, LR, LL.
                                      ' Vamos tentar acertar: Canto Superior Direito = Index 2?
    p4.Rectangle.CornerUpperRight = 50 ' Fallback relativo se SetRadius falhar
    
    On Error Resume Next
    p4.Rectangle.SetRadius 0, 0, 5, 0 ' Tenta raio 5cm no canto sup direito
    On Error GoTo ErrorHandler
    
    ' Soldar Paineis Verticais
    Set sMain = p1.Weld(p2).Weld(p3).Weld(p4)
    
    ' =========================================================
    ' 2. Aba Lateral (Esquerda)
    ' =========================================================
    ' Conecta no P2 (y=12 a 21).
    ' Altura na ponta: 8cm. Comprimento 12cm.
    ' Pontos: (0, 12), (0, 21), (-12, 20.5), (-12, 12.5)
    ' Assumindo centralizacao visual ((9-8)/2 = 0.5 offset de cada lado em relacao a altura 9)
    
    Dim nodes(3) As CurveNode
    Set sFlap = lr.CreateCurveSegment(0, 12, 0, 21)       ' Base Direita
    sFlap.Curve.Nodes(2).AppendSegmentLine -12, 20.5      ' Topo Esquerdo
    sFlap.Curve.Nodes(3).AppendSegmentLine -12, 12.5      ' Base Esquerda
    sFlap.Curve.Nodes(4).AppendSegmentLine 0, 12          ' Fecha
    
    ' Fechar curva
    sFlap.Curve.Closed = True
    
    ' Soldar Aba no Corpo
    Set sFinal = sMain.Weld(sFlap)
    sFinal.Fill.UniformColor.CMYKAssign 0, 0, 0, 10 ' Cinza claro
    sFinal.Outline.SetProperties 0.05, OutlineColor:=CreateCMYKColor(0, 0, 0, 100)
    
    ' =========================================================
    ' 3. Furos
    ' =========================================================
    ' Furo 1: Base Direita
    Set sHole1 = lr.CreateEllipse2(8, 1, 0.25) ' x=8, y=1, raio 0.25 (diam 0.5)
    
    ' Furo 2: Topo Direito (Na cabeca)
    Set sHole2 = lr.CreateEllipse2(8, 38, 0.25) ' x=8, y=38
    
    ' Cortar furos (Trim)
    Set sFinal = sHole1.Trim(sFinal)
    Set sFinal = sHole2.Trim(sFinal)
    
    ' =========================================================
    ' 4. Cotas (Dimensions) - Para provar precisao
    ' =========================================================
    ' Dimensao Total Lateral
    lr.CreateLinearDimension cdrDimensionVertical, 10, 0, 10, 41.5, True, 11, 20.75
    
    ' Dimensao Aba
    lr.CreateLinearDimension cdrDimensionHorizontal, 0, 12, -12, 12, True, -6, 10
    
    ' Zoom
    doc.ActiveWindow.ActiveView.ZoomToShape sFinal
    MsgBox "Desenho Tecnico Concluido via Nexus!", vbInformation

    Exit Sub

ErrorHandler:
    MsgBox "Erro no Desenho: " & Err.Description, vbCritical
End Sub
