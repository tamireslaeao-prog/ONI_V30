"""
ONI V23 - SOBERANO - Desenho Técnico de Molde no AutoCAD
Desenha o padrão/molde em escala 1:1 (unidades em CM) com todas as cotas.

Medidas extraídas da imagem:
- Altura total: 41.5cm
- Topo: 8.5cm altura + 5cm arco + 0.5cm recuo
- Largura topo: 9cm
- Corpo: 12cm + 9cm + 12cm = 33cm
- Largura corpo: 9.5cm
- Aba esquerda: 8cm
- Largura base: 9cm
- 2 furos circulares
"""

import sys
import os
# Determine Project Root (Assumes: Project/Modules/Oni_Engine/Scripts/script.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
APP_SCRIPTS = os.path.join(PROJECT_ROOT, "app", "scripts")

sys.path.insert(0, APP_SCRIPTS)

from ONI_AutoCAD_Bridge import AutoCADController
import math

def main():
    print("=" * 60)
    print("SOBERANO: DESENHO TÉCNICO DE MOLDE")
    print("Escala 1:1 (unidades em centímetros)")
    print("=" * 60)
    
    cad = AutoCADController()
    if not cad.connect():
        print("ERRO: Não foi possível conectar ao AutoCAD")
        return
    
    print("[1/5] Conectado ao AutoCAD")
    
    # Limpar desenho atual (opcional - comentar se quiser manter)
    # cad.clear_drawing()
    
    # =========================================================================
    # MEDIDAS (em centímetros - escala 1:1)
    # =========================================================================
    # Convertendo da imagem
    
    # Topo
    TOPO_LARGURA = 9.0
    TOPO_RECUO = 0.5
    TOPO_ALTURA_ARCO = 5.0
    TOPO_ALTURA_RETA = 8.5
    
    # Corpo principal
    CORPO_ALTURA_1 = 12.0  # Seção superior do corpo
    CORPO_ALTURA_2 = 9.0   # Seção média
    CORPO_ALTURA_3 = 12.0  # Seção inferior
    CORPO_LARGURA = 9.5
    
    # Aba lateral esquerda
    ABA_ALTURA = 8.0
    
    # Base
    BASE_LARGURA = 9.0
    
    # Altura total
    ALTURA_TOTAL = 41.5
    
    # Furos (diâmetro aproximado)
    FURO_RAIO = 0.4
    
    # =========================================================================
    # PONTO DE ORIGEM (canto inferior esquerdo do corpo principal)
    # =========================================================================
    ORIGEM_X = 0
    ORIGEM_Y = 0
    
    print("[2/5] Desenhando contorno...")
    
    # =========================================================================
    # DESENHAR CONTORNO (sentido anti-horário começando do canto inf esq)
    # =========================================================================
    
    # Calculando pontos chave
    # O desenho tem formato de "cruz" com o topo arredondado
    
    # Vou desenhar em partes:
    # 1. Base retangular inferior
    # 2. Aba esquerda
    # 3. Corpo central
    # 4. Topo com arco
    
    # Base inferior (9cm x 12cm)
    base_x1 = (CORPO_LARGURA - BASE_LARGURA) / 2  # Centralizado
    base_y1 = 0
    base_x2 = base_x1 + BASE_LARGURA
    base_y2 = CORPO_ALTURA_3
    
    # Corpo médio (9.5cm x 9cm) - com abas
    corpo_medio_y1 = base_y2
    corpo_medio_y2 = corpo_medio_y1 + CORPO_ALTURA_2
    
    # Aba esquerda (-8cm de largura x 8cm de altura)
    aba_x = -ABA_ALTURA  # Estende para esquerda
    
    # Corpo superior (9.5cm x 12cm)
    corpo_sup_y1 = corpo_medio_y2
    corpo_sup_y2 = corpo_sup_y1 + CORPO_ALTURA_1
    
    # Topo (9cm x ~13.5cm) - centralizado, com arco
    topo_x1 = (CORPO_LARGURA - TOPO_LARGURA) / 2
    topo_x2 = topo_x1 + TOPO_LARGURA
    topo_y1 = corpo_sup_y2
    topo_y2 = topo_y1 + TOPO_ALTURA_RETA + TOPO_ALTURA_ARCO  # ~13.5
    
    # Recuo do topo
    recuo_y = topo_y1 + TOPO_RECUO
    
    # =========================================================================
    # DESENHAR COM POLYLINE
    # =========================================================================
    
    # Contorno externo completo (aproximação do formato)
    # Começando do canto inferior esquerdo, sentido anti-horário
    
    pontos = [
        # Base inferior
        (base_x1, base_y1, 0),
        (base_x2, base_y1, 0),
        (base_x2, base_y2, 0),
        
        # Sobe para corpo médio (lado direito)
        (CORPO_LARGURA, base_y2, 0),
        (CORPO_LARGURA, corpo_medio_y2, 0),
        
        # Sobe para corpo superior
        (CORPO_LARGURA, corpo_sup_y2, 0),
        
        # Recuo para topo mais estreito
        (topo_x2, corpo_sup_y2, 0),
        (topo_x2, topo_y2 - 5, 0),  # Antes do arco
        
        # Topo superior (aproximar arco com linhas)
        (topo_x2, topo_y2 - 2.5, 0),
        (topo_x2 - 1, topo_y2 - 0.5, 0),
        (topo_x2 - 2.5, topo_y2, 0),  # Centro do arco
        (topo_x1 + 2.5, topo_y2, 0),
        (topo_x1 + 1, topo_y2 - 0.5, 0),
        (topo_x1, topo_y2 - 2.5, 0),
        
        # Desce topo esquerdo
        (topo_x1, corpo_sup_y2, 0),
        
        # Desce corpo superior esquerdo
        (0, corpo_sup_y2, 0),
        
        # Aba esquerda
        (0, corpo_medio_y2, 0),
        (aba_x, corpo_medio_y2, 0),
        (aba_x, corpo_medio_y2 - ABA_ALTURA, 0),
        (0, corpo_medio_y2 - ABA_ALTURA, 0),
        
        # Desce para base
        (0, base_y2, 0),
        (base_x1, base_y2, 0),
        (base_x1, base_y1, 0),  # Fecha
    ]
    
    cad.draw_polyline(pontos)
    
    print("[3/5] Desenhando furos...")
    
    # =========================================================================
    # FUROS CIRCULARES
    # =========================================================================
    # Furo superior (no topo direito)
    furo1_x = topo_x2 - 1.5
    furo1_y = topo_y2 - 4
    cad.draw_circle(furo1_x, furo1_y, 0, FURO_RAIO)
    
    # Furo inferior (na base)
    furo2_x = (base_x1 + base_x2) / 2
    furo2_y = 1.0  # Próximo da base
    cad.draw_circle(furo2_x, furo2_y, 0, FURO_RAIO)
    
    print("[4/5] Adicionando cotas...")
    
    # =========================================================================
    # COTAS (usando add_dim_aligned)
    # =========================================================================
    
    # Cota altura total (41.5cm) - lado direito
    cad.add_dim_aligned(
        CORPO_LARGURA + 2, base_y1, 0,
        CORPO_LARGURA + 2, topo_y2, 0,
        CORPO_LARGURA + 5, (base_y1 + topo_y2) / 2, 0
    )
    
    # Cota largura base (9cm)
    cad.add_dim_aligned(
        base_x1, base_y1 - 2, 0,
        base_x2, base_y1 - 2, 0,
        (base_x1 + base_x2) / 2, base_y1 - 4, 0
    )
    
    # Cota largura corpo (9.5cm)
    cad.add_dim_aligned(
        0, corpo_medio_y1 + 2, 0,
        CORPO_LARGURA, corpo_medio_y1 + 2, 0,
        CORPO_LARGURA / 2, corpo_medio_y1 + 5, 0
    )
    
    # Cota altura seção base (12cm)
    cad.add_dim_aligned(
        base_x2 + 1, base_y1, 0,
        base_x2 + 1, base_y2, 0,
        base_x2 + 3, (base_y1 + base_y2) / 2, 0
    )
    
    # Cota altura seção média (9cm)
    cad.add_dim_aligned(
        CORPO_LARGURA + 1, corpo_medio_y1, 0,
        CORPO_LARGURA + 1, corpo_medio_y2, 0,
        CORPO_LARGURA + 3, (corpo_medio_y1 + corpo_medio_y2) / 2, 0
    )
    
    # Cota altura seção superior corpo (12cm)
    cad.add_dim_aligned(
        CORPO_LARGURA + 1, corpo_sup_y1, 0,
        CORPO_LARGURA + 1, corpo_sup_y2, 0,
        CORPO_LARGURA + 3, (corpo_sup_y1 + corpo_sup_y2) / 2, 0
    )
    
    # Cota aba esquerda (8cm)
    cad.add_dim_aligned(
        aba_x, corpo_medio_y2 - ABA_ALTURA - 1, 0,
        0, corpo_medio_y2 - ABA_ALTURA - 1, 0,
        aba_x / 2, corpo_medio_y2 - ABA_ALTURA - 3, 0
    )
    
    # Cota largura topo (9cm)
    cad.add_dim_aligned(
        topo_x1, corpo_sup_y2 + 3, 0,
        topo_x2, corpo_sup_y2 + 3, 0,
        (topo_x1 + topo_x2) / 2, corpo_sup_y2 + 6, 0
    )
    
    # Cota altura topo (8.5cm parte reta + 5cm arco)
    cad.add_dim_aligned(
        topo_x2 + 1, corpo_sup_y2, 0,
        topo_x2 + 1, topo_y2 - 5, 0,
        topo_x2 + 3, corpo_sup_y2 + 4, 0
    )
    
    print("[5/5] Zoom Extents...")
    
    # Zoom para ver tudo
    cad.send_command("ZOOM E ")
    
    # Adicionar texto de título
    cad.draw_text("MOLDE - ESCALA 1:1", -5, topo_y2 + 5, 0, 2.0)
    cad.draw_text("UNIDADES: CM", -5, topo_y2 + 2, 0, 1.5)
    cad.draw_text("PLIURE (DOBRA)", CORPO_LARGURA + 1, corpo_medio_y1 + 4, 0, 1.0)
    
    print("=" * 60)
    print("✅ DESENHO TÉCNICO CONCLUÍDO!")
    print("   Contorno: Polyline fechada")
    print("   Furos: 2 círculos")
    print("   Cotas: 9+ dimensões")
    print("   Escala: 1:1 (CM)")
    print("=" * 60)


if __name__ == "__main__":
    main()
