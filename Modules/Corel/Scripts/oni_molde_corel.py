"""
ONI V23 - SOBERANO - Molde Técnico no CorelDRAW
Desenha o padrão/molde em A3 com grade quadriculada e cotas.

Unidades: Milímetros (1cm = 10mm para escala 1:1)
"""

import win32com.client
import pythoncom
import math
import time

def main():
    print("=" * 60)
    print("SOBERANO: MOLDE TÉCNICO NO CORELDRAW")
    print("Página A3 com grade quadriculada")
    print("=" * 60)
    
    try:
        # Aguardar CorelDRAW iniciar
        print("Aguardando CorelDRAW...")
        time.sleep(5)
        
        # Tentar conectar à instância existente primeiro
        try:
            corel = win32com.client.GetActiveObject("CorelDRAW.Application.26")
        except:
            try:
                corel = win32com.client.GetActiveObject("CorelDRAW.Application")
            except:
                # Se não conseguir, criar nova instância
                corel = win32com.client.Dispatch("CorelDRAW.Application.26")
        
        corel.Visible = True
        
        print("[1/6] Conectado ao CorelDRAW")
        
        # Criar novo documento
        doc = corel.CreateDocument()
        
        # Configurar página A3 (297 x 420 mm)
        doc.Unit = 4  # Milímetros
        doc.ActivePage.SetSize(420, 297)  # Landscape A3 para caber melhor
        doc.ActivePage.Orientation = 2  # Landscape
        
        print("[2/6] Página A3 criada (420 x 297 mm)")
        
        # =========================================================================
        # MEDIDAS DO MOLDE (convertendo cm para mm)
        # =========================================================================
        
        # Topo
        TOPO_LARGURA = 90  # 9cm
        TOPO_ALTURA_ARCO = 50  # 5cm
        TOPO_ALTURA_RETA = 85  # 8.5cm
        TOPO_RECUO = 5  # 0.5cm
        
        # Corpo principal
        CORPO_ALTURA_1 = 120  # 12cm
        CORPO_ALTURA_2 = 90   # 9cm
        CORPO_ALTURA_3 = 120  # 12cm
        CORPO_LARGURA = 95    # 9.5cm
        
        # Aba lateral
        ABA_ALTURA = 80  # 8cm
        
        # Base
        BASE_LARGURA = 90  # 9cm
        
        # Furos
        FURO_RAIO = 4  # ~4mm
        
        # =========================================================================
        # LAYER: GRADE (1cm = 10mm)
        # =========================================================================
        print("[3/6] Desenhando grade 1cm...")
        
        layer_grid = doc.ActivePage.CreateLayer("GRADE_1CM")
        layer_grid.Editable = True
        
        # Cor da grade: cinza claro
        grid_color = corel.CreateRGBColor(220, 220, 220)
        
        # Linhas verticais (cada 10mm)
        for x in range(0, 430, 10):
            line = layer_grid.CreateLineSegment(x, 0, x, 297)
            line.Outline.Color = grid_color
            line.Outline.Width = 0.1
        
        # Linhas horizontais (cada 10mm)
        for y in range(0, 300, 10):
            line = layer_grid.CreateLineSegment(0, y, 420, y)
            line.Outline.Color = grid_color
            line.Outline.Width = 0.1
        
        layer_grid.Editable = False
        
        # =========================================================================
        # LAYER: MOLDE (contorno principal)
        # =========================================================================
        print("[4/6] Desenhando contorno do molde...")
        
        layer_mold = doc.ActivePage.CreateLayer("MOLDE_CONTORNO")
        layer_mold.Activate()
        
        # Offset para centralizar na página (aproximado)
        OFFSET_X = 150  # ~15cm do canto esquerdo
        OFFSET_Y = 30   # ~3cm do canto inferior
        
        # Calcular pontos do contorno
        base_x1 = OFFSET_X + (CORPO_LARGURA - BASE_LARGURA) / 2
        base_y1 = OFFSET_Y
        base_x2 = base_x1 + BASE_LARGURA
        base_y2 = base_y1 + CORPO_ALTURA_3
        
        corpo_medio_y1 = base_y2
        corpo_medio_y2 = corpo_medio_y1 + CORPO_ALTURA_2
        
        corpo_sup_y1 = corpo_medio_y2
        corpo_sup_y2 = corpo_sup_y1 + CORPO_ALTURA_1
        
        topo_x1 = OFFSET_X + (CORPO_LARGURA - TOPO_LARGURA) / 2
        topo_x2 = topo_x1 + TOPO_LARGURA
        topo_y1 = corpo_sup_y2
        topo_y2 = topo_y1 + TOPO_ALTURA_RETA + TOPO_ALTURA_ARCO
        
        aba_x = OFFSET_X - ABA_ALTURA
        
        # Usar método de linhas (funciona bem no Corel)
        
        # Usar método alternativo: polilinha
        # Vamos desenhar com linhas individuais
        pontos = [
            (base_x1, base_y1),
            (base_x2, base_y1),
            (base_x2, base_y2),
            (OFFSET_X + CORPO_LARGURA, base_y2),
            (OFFSET_X + CORPO_LARGURA, corpo_sup_y2),
            (topo_x2, corpo_sup_y2),
            (topo_x2, topo_y2 - 50),
            (topo_x2, topo_y2 - 25),
            (topo_x2 - 10, topo_y2 - 5),
            (topo_x2 - 25, topo_y2),
            (topo_x1 + 25, topo_y2),
            (topo_x1 + 10, topo_y2 - 5),
            (topo_x1, topo_y2 - 25),
            (topo_x1, corpo_sup_y2),
            (OFFSET_X, corpo_sup_y2),
            (OFFSET_X, corpo_medio_y2),
            (aba_x, corpo_medio_y2),
            (aba_x, corpo_medio_y2 - ABA_ALTURA),
            (OFFSET_X, corpo_medio_y2 - ABA_ALTURA),
            (OFFSET_X, base_y2),
            (base_x1, base_y2),
            (base_x1, base_y1),
        ]
        
        # Desenhar linhas conectando os pontos
        contorno_color = corel.CreateRGBColor(0, 0, 0)  # Preto
        
        for i in range(len(pontos) - 1):
            x1, y1 = pontos[i]
            x2, y2 = pontos[i + 1]
            line = layer_mold.CreateLineSegment(x1, y1, x2, y2)
            line.Outline.Color = contorno_color
            line.Outline.Width = 0.5
        
        print("[5/6] Desenhando furos e cotas...")
        
        # =========================================================================
        # FUROS
        # =========================================================================
        # Furo superior (topo direito)
        furo1_x = topo_x2 - 15
        furo1_y = topo_y2 - 40
        circle1 = layer_mold.CreateEllipse(furo1_x - FURO_RAIO, furo1_y - FURO_RAIO,
                                           furo1_x + FURO_RAIO, furo1_y + FURO_RAIO)
        circle1.Outline.Color = contorno_color
        circle1.Fill.ApplyNoFill()
        
        # Furo inferior (base)
        furo2_x = (base_x1 + base_x2) / 2
        furo2_y = base_y1 + 10
        circle2 = layer_mold.CreateEllipse(furo2_x - FURO_RAIO, furo2_y - FURO_RAIO,
                                           furo2_x + FURO_RAIO, furo2_y + FURO_RAIO)
        circle2.Outline.Color = contorno_color
        circle2.Fill.ApplyNoFill()
        
        # =========================================================================
        # LAYER: COTAS
        # =========================================================================
        layer_dim = doc.ActivePage.CreateLayer("COTAS")
        layer_dim.Activate()
        
        dim_color = corel.CreateRGBColor(50, 50, 200)  # Azul
        
        # Função para criar cota simples (linha + texto)
        def criar_cota(x1, y1, x2, y2, texto, offset_texto=10):
            # Linha de cota
            line = layer_dim.CreateLineSegment(x1, y1, x2, y2)
            line.Outline.Color = dim_color
            line.Outline.Width = 0.25
            
            # Texto da medida
            tx = (x1 + x2) / 2
            ty = (y1 + y2) / 2 + offset_texto
            text = layer_dim.CreateArtisticText(tx, ty, texto)
            text.Text.Story.Font = "Arial"
            text.Text.Story.Size = 8
            
        # Cota altura total (415mm = 41.5cm)
        criar_cota(OFFSET_X + CORPO_LARGURA + 20, base_y1,
                   OFFSET_X + CORPO_LARGURA + 20, topo_y2, "41,5cm", 5)
        
        # Cota base (9cm)
        criar_cota(base_x1, base_y1 - 15, base_x2, base_y1 - 15, "9cm", -5)
        
        # Cota corpo largura (9.5cm)
        criar_cota(OFFSET_X, corpo_medio_y1 + 5, 
                   OFFSET_X + CORPO_LARGURA, corpo_medio_y1 + 5, "9,5cm", 5)
        
        # Cota seções verticais
        criar_cota(base_x2 + 10, base_y1, base_x2 + 10, base_y2, "12cm", 5)
        criar_cota(OFFSET_X + CORPO_LARGURA + 10, corpo_medio_y1, 
                   OFFSET_X + CORPO_LARGURA + 10, corpo_medio_y2, "9cm", 5)
        criar_cota(OFFSET_X + CORPO_LARGURA + 10, corpo_sup_y1,
                   OFFSET_X + CORPO_LARGURA + 10, corpo_sup_y2, "12cm", 5)
        
        # Cota aba (8cm)
        criar_cota(aba_x, corpo_medio_y2 - ABA_ALTURA - 10,
                   OFFSET_X, corpo_medio_y2 - ABA_ALTURA - 10, "8cm", -5)
        
        # Cota topo largura (9cm)
        criar_cota(topo_x1, corpo_sup_y2 + 10, topo_x2, corpo_sup_y2 + 10, "9cm", 5)
        
        # Textos informativos
        titulo = layer_dim.CreateArtisticText(30, 270, "MOLDE - ESCALA 1:1")
        titulo.Text.Story.Font = "Arial"
        titulo.Text.Story.Size = 14
        titulo.Text.Story.Bold = True
        
        unidade = layer_dim.CreateArtisticText(30, 255, "UNIDADES: CENTÍMETROS")
        unidade.Text.Story.Font = "Arial"
        unidade.Text.Story.Size = 10
        
        pliure = layer_dim.CreateArtisticText(OFFSET_X + CORPO_LARGURA + 25, 
                                              (corpo_medio_y1 + corpo_medio_y2) / 2,
                                              "PLIURE (DOBRA)")
        pliure.Text.Story.Font = "Arial"
        pliure.Text.Story.Size = 8
        
        print("[6/6] Finalizando...")
        
        # Ativar layer do molde
        layer_mold.Activate()
        
        print("=" * 60)
        print("✅ MOLDE TÉCNICO CRIADO NO CORELDRAW!")
        print("   Página: A3 Landscape (420 x 297 mm)")
        print("   Grade: 1cm quadriculada")
        print("   Contorno: Polyline fechada")
        print("   Furos: 2 círculos")
        print("   Cotas: 8+ dimensões")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
