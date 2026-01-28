# 📐 AUTOCAD KNOWLEDGE BASE

> **Módulo:** Modules/AutoCAD
> **Versão:** V24
> **Status:** Technical Drawing Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Comando |
|------|---------|
| Linha | L + Enter |
| Círculo | C + Enter |
| Retângulo | REC + Enter |
| Dimensão | DIM + Enter |
| Zoom Extents | Z + E + Enter |

### Comandos Bridge
```python
from ONI_AutoCAD_Bridge import AutoCADBridge

cad = AutoCADBridge()
cad.connect()
cad.draw_line((0,0), (100,0))
cad.draw_circle((50,50), 25)
cad.add_dimension("linear", (0,0), (100,0))
cad.save_as("desenho.dwg")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI_AutoCAD_Bridge.py` - Bridge COM (631 linhas)
- `AutoCAD_Adapter.psm1` - PowerShell wrapper
- `AutoCAD_Test_Draw.py` - Script de teste

### Capacidades
- **Conexão COM:** ActiveX automation
- **Primitivas:** Line, Circle, Rectangle, Arc
- **Dimensionamento:** Linear, Angular, Radius
- **Layers:** Criar, colorir, organizar
- **Export:** DWG, DXF, PDF

---

## 💡 Dicas Avançadas

### Conexão COM
```python
import win32com.client
acad = win32com.client.Dispatch("AutoCAD.Application")
doc = acad.Documents.Add()
ms = doc.ModelSpace
```

### Unidades
- Sempre trabalhar em mm para precisão
- `acadApp.Preferences.Drawing.Units = acUnitsMillimeters`

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| COM connection failed | Verificar se AutoCAD está aberto |
| Dimension falha | Usar SendCommand como fallback |
