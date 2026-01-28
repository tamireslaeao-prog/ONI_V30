# 🎨 CORELDRAW KNOWLEDGE BASE

> **Módulo:** Modules/Corel
> **Versão:** V24
> **Status:** Ready to Vectorize (Level 9.5/10)

---

## 🎯 Quick Commands

### Atalhos Essenciais (422 mapeados em corelatalhos.csv)
| Ação | Atalho |
|------|--------|
| Novo documento | Ctrl+N |
| Converter para curvas | Ctrl+Q |
| Agrupar | Ctrl+G |
| Desagrupar | Ctrl+U |
| Soldar (Weld) | Menu > Objeto > Formatar |

### Comandos Bridge (Python COM)
```python
from ONI_Corel_Bridge import CorelBridge

corel = CorelBridge()
corel.connect()
corel.create_document()
corel.draw_rectangle(0, 0, 100, 50)  # mm
corel.save_document("output.cdr")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI_Corel_Bridge.py` - Bridge Python COM (390 linhas)
- `ONI_CorelAutomation.psm1` - PowerShell module
- `corelatalhos.csv` - 422 atalhos mapeados
- `styles_db.json` - Banco de estilos

### Tier 1: Fundação
- **VGCore:** Conexão COM Application Object
- **Estrutura:** Pages, Master Layers, Local Layers
- **Unidades:** `cdrMillimeter` para precisão técnica
- **Primitivas:** Rectangles, Ellipses, Polygons

### Tier 2: Shaping Lab
- **Booleanas:** Weld, Trim, Intersect, Simplify
- **PowerClip:** Container logic para masking
- **Curvas:**
  - `ConvertToCurves`: Edit destrutivo
  - Node editing: `Segment.Type` (Line vs Curve)
- **Vetorização Manual:** Linear, Bezier, Cusp

### Tier 3: Enterprise
- **CQL (Corel Query Language):**
  ```vb
  ActivePage.Shapes.FindShapes(Query:="@type = 'ellipse'")
  ```
- **VIP (Vector Injection Protocol):** SVG→Start-Process→Corel
- **Macros:** GlobalMacros para tools reutilizáveis

---

## 🎨 Assets Disponíveis

**Localização:** `Modules/Corel/`

- `corelatalhos.csv` - 422 atalhos PT-BR
- `styles_db.json` - Estilos (60KB)
- `ONI_Macros.bas` - Macros VBA
- `Library/` - Templates e greebles

---

## 💡 Dicas Avançadas

### Performance: Optimization Protocol
```vb
Application.Optimization = True
Application.EventsEnabled = False
' ... 10,000 operações ...
Application.Optimization = False
Application.ActiveWindow.Refresh
```

### VIP (Vector Injection Protocol)
Quando VBA bloqueado ou COM instável:
1. Gerar `.svg` com coordenadas mm
2. `Start-Process corel.exe "file.svg"`
3. Vetor perfeito 1:1

### ShapeRange: Batch Processing
```vb
Dim range As ShapeRange
range.Add shape1
range.Add shape2
range.SetOutlineProperties 2.0  ' Aplica a todos
```

---

## 🚨 Erros Conhecidos

| Erro | Causa | Solução |
|------|-------|---------|
| CO_E_SERVER_EXEC_FAILURE | COM instável | Usar VIP (SVG) |
| VBA Bloqueado | IT Policy | Usar VIP |
| Y-Flip em SVG | Origem diferente | `transform="scale(1,-1)"` |
| Sopa de linhas | Mão Livre | Usar Bezier fechado |
| Dimension Tool falha | API frágil | Desenhar manualmente |
