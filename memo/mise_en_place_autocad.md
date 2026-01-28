# 📐 Mise En Place: Padrão de Pasta (AutoCAD)

## 1. Definição Global
*   **Unidade:** CM (Centímetros)
*   **Origem:** Canto Inferior Direito (Ponto de Dobra Inferior) = `0,0`
*   **Eixo Y:** Linha de dobra direita ("Pliure")
*   **Eixo X:** Negativo para a esquerda

## 2. Coordenadas da Geometria (Anti-Horário)

### Corpo Principal (Coluna Direita)
| Ponto | Coord (X, Y) | Descrição |
|-------|--------------|-----------|
| P0 | `0, 0` | Origem (Inf. Dir) |
| P1 | `-9.0, 0` | Largura Inferior (9cm) |
| P2 | `-9.5, 12.0` | Início Seção Média (Opens to 9.5cm) |
| P3 | `-9.5, 21.0` | Fim Seção Média (Matches 9.5cm) |
| P4 | `-9.0, 33.0` | Fim Seção Superior (Tapers to 9cm) |
| P5 | `-8.5, 33.0` | Degrau (Recuo 0.5cm) |
| P6 | `-8.5, 38.0` | Fim Reto da Aba (5cm vertical) |
| P7 | `0, 41.5` | Topo da Curva (H=41.5cm Total) |

*Nota: A curva entre P6 e P7 será aproximada por um arco de 3 pontos ou Spline, pois H=3.5 e W=8.5 não formam arco circular perfeito tangente.*

### Aba Lateral (Esquerda)
*Anexada à Seção Média (Y=12 a Y=21)*
*   **Base:** Y=12 a Y=21 (Altura 9cm) na linha X=-9.5
*   **Comprimento:** Estimado em **12.0cm** (Visual)
*   **Ponta:** Altura 8cm (Centralizada em relação à base?)
    *   Centro Base: Y=16.5
    *   Faixa Ponta: Y=12.5 a Y=20.5 (8cm)
    *   X da Ponta: -9.5 - 12.0 = **-21.5**

| Ponto | Coord (X, Y) |
|-------|--------------|
| W1 (Inf) | `-21.5, 12.5` |
| W2 (Sup) | `-21.5, 20.5` |

### Furos (Círculos)
*Assumindo Ø1.0cm e posição visual*
*   **Furo Inf:** `0, 6.0` (Meio da seção inf?)
*   **Furo Sup:** `0, 39.0` (Aba superior)

## 3. Comandos AutoCAD (`.scr`)

### Setup
```autocad
LIMITS -30,0 10,50
ZOOM ALL
OSNAP OFF
GRID OFF
```

### Desenho (Polilinha)
```autocad
PLINE 0,0 -9,0 -9.5,12 -21.5,12.5 -21.5,20.5 -9.5,21 -9,33 -8.5,33 -8.5,38
ARC 0,41.5
LINE 0,41.5 0,0
CLOSE
```
*(Ajustar sintaxe para PLINE com Arc ou fazer Line loop)*

### Cotas (Dim)
*   **DIMLINEAR** V/H para todas as medidas originais.
*   **DIMALIGNED** para as inclinadas se necessário (mas o original usa linear).

## 4. Estratégia de Execução
1.  Gerar arquivo `draw_folder.scr`.
2.  Executar via PowerShell injetando o comando `SCRIPT` no AutoCAD ou instruir usuário.
