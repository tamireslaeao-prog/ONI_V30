# 🎨 PHOTOSHOP KNOWLEDGE BASE

> **Módulo:** Modules/Photoshop
> **Versão:** V24
> **Status:** Combat Ready (Level 10/10)

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Comando |
|------|---------|
| Novo documento via código | `app.documents.add(width, height, 72, "name")` |
| Abrir arquivo | `Ctrl+O` (preferir sobre Ctrl+N) |
| Salvar | `Ctrl+S` |
| Desfazer | `Ctrl+Z` |

### Comandos Bridge (PowerShell/JSX)
```powershell
# Conectar ao Photoshop
$ps = New-Object -ComObject Photoshop.Application

# Criar documento
$doc = $ps.Documents.Add(1920, 1080, 72, "MeuDoc")

# Executar JSX
$ps.DoJavaScript("app.activeDocument.artLayers.add()")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `oni_lib_photoshop.jsx` - Biblioteca ExtendScript completa (655 linhas)
- `app/skills/photoshop.json` - Guia de skills

### Tier 1: Fundação
- **Conexão:** Retry loop para `RPC_E_SERVERCALL_RETRYLATER`
- **Unidades:** Forçar Pixels (`Preferences.RulerUnits = 1`)
- **Canvas:** Document.add(), Resize, CanvasSize
- **Layers:** Criar, nomear, ordenar, opacity, lock

### Tier 2: Efeitos
- **Filtros:** GaussianBlur, AddNoise, UnsharpMask
- **Blending:** psMultiply, psScreen, psOverlay
- **FX Manual:**
  - Shadow: Duplicate→Fill Black→Blur→Multiply→Offset
  - Vignette: Ellipse→Invert→Feather→Fill Black→Multiply

### Tier 3: Avançado
- **Vetores JSX:** Bezier via `DoJavaScript("doc.pathItems.add(...)")`
- **Action Manager:** `executeAction` para Smart Objects, Select All
- **Clipping:** `Layer.Group = true`
- **Procedural Vectorizer:** `oni_vetorizar_photoshop.py` (Auto Selection -> Work Path -> Solid Color)

---

## 🎨 Assets Disponíveis

**Localização:** `Modules/Photoshop/Assets/`

- `assets_db.json` - Banco de assets (26KB)
- Scripts em `Scripts/`:
  - `ONI_Asset_Sentinel.ps1`
  - `ONI_PSD_Harvester.ps1`
  - `oni_lib_photoshop.js`

---

## 💡 Dicas Avançadas

### Performance: suspendHistory
```javascript
doc.suspendHistory("Operação", "código aqui")
// 10x mais rápido!
```

### Action Manager (Nuclear Option)
```javascript
var desc = new ActionDescriptor();
var ref = new ActionReference();
executeAction(stringIDToTypeID("comando"), desc, DialogModes.NO);
```

### Quirk: New Document 2026
- **Problema:** Botão "Create" escondido da automação
- **Solução:** Usar `app.documents.add()` via script

### Arrays Híbridos
PowerShell não marshalla `PathPointInfo[]`. Construir via JavaScript string.

---
 
 ## 🚨 Erros Conhecidos

| Erro | Causa | Solução |
|------|-------|---------|
| RPC_E_SERVERCALL_RETRYLATER | PS ocupado | Retry loop com delay |
| Fill falha em Text | API issue | Usar `TextItem.Color` |
| Rasterize(5) vs Rasterize(1) | Enum diferente | 5=Type, 1=Layer |
| Dialog "Create" travado | UI 2026 | Usar `documents.add()` |
