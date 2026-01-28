# 🖼️ ILLUSTRATOR KNOWLEDGE BASE

> **Módulo:** Modules/Illustrator
> **Versão:** V24
> **Status:** Vector Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Ferramenta Seleção | V |
| Caneta | P |
| Texto | T |
| Zoom | Z |
| Mão | H (espaço) |

### Comandos Bridge
```python
from ONI_Illustrator_Bridge import IllustratorBridge

ai = IllustratorBridge()
ai.connect()
ai.create_document(1920, 1080)
ai.add_rectangle(0, 0, 200, 100)
ai.save_as("design.ai")
ai.export_png("output.png")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI.Illustrator.js` - JavaScript ExtendScript (24KB)
- `ONI.Illustrator.ps1` - PowerShell (20KB)
- `ONI_Illustrator_Bridge.py` - Python COM (14KB)
- `styles_db.json` - Estilos (23KB)

### Capacidades
- **Documentos:** Criar, abrir, salvar
- **Objetos:** Retângulos, elipses, paths
- **Texto:** Text frames, estilos
- **Cores:** RGB, CMYK, Swatches
- **Export:** PNG, PDF, SVG, EPS

---

## 💡 Dicas Avançadas

### Conexão COM (Python)
```python
import win32com.client
ai = win32com.client.Dispatch("Illustrator.Application")
doc = ai.Documents.Add()
```

### ExtendScript (JSX)
```javascript
var doc = app.documents.add();
var rect = doc.pathItems.rectangle(100, 100, 200, 150);
rect.fillColor = new RGBColor();
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| COM connection failed | Illustrator não está aberto |
| Script timeout | Aumentar DocumentColorSpace |
