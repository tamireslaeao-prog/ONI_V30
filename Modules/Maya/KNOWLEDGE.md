# 🎬 MAYA KNOWLEDGE BASE

> **Módulo:** Modules/Maya
> **Versão:** V24
> **Status:** 3D Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Mover | W |
| Rotacionar | E |
| Escalar | R |
| Frame seleção | F |
| Render | Ctrl+Shift+R |

### Comandos Bridge
```python
from ONI_Maya_Bridge import MayaBridge

maya = MayaBridge()
maya.connect()
maya.create_cube()
maya.set_material("lambert1", color=(1, 0, 0))
maya.render("output.png")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI_Maya_Bridge.py` - Bridge Python (14KB)

### Capacidades
- **Objetos:** Primitivas 3D
- **Materiais:** Lambert, Blinn, Arnold
- **Render:** Hardware, Arnold, V-Ray
- **Animation:** Keyframes, rigs

---

## 💡 Dicas Avançadas

### MEL Commands
```mel
polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1;
```

### Python in Maya
```python
import maya.cmds as cmds
cmds.polyCube()
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| Maya não encontrado | Verificar instalação Autodesk |
| Render timeout | Reduzir samples/quality |
