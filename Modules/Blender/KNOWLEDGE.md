# 🎮 BLENDER KNOWLEDGE BASE

> **Módulo:** Modules/Blender
> **Versão:** V24
> **Status:** Procedural Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Render | F12 |
| Modo Objeto | Tab |
| Adicionar objeto | Shift+A |
| Viewport shading | Z |

### Comandos Bridge
```python
from ONI_Blender_Bridge import BlenderBridge

blender = BlenderBridge()
blender.open_file("scene.blend")
blender.add_cube(location=(0, 0, 0), size=2)
blender.render("output.png", samples=128)
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI_Blender_Bridge.py` - Bridge principal (451 linhas)
- `ONI_Gen.py` - Geração procedural (480 linhas)
- `ONI_VRay_Blender.py` - Suporte V-Ray (36KB)
- `oni_addon/` - Addon Blender completo

### Capacidades
- **Headless Rendering:** `blender --background`
- **Procedural Generation:** Via ONI_Gen.py
- **V-Ray Support:** Render de alta qualidade
- **Animation:** Keyframes, bones, rigs Mixamo

---

## 🎨 Assets Disponíveis

- `blender_styles_db.json` - Estilos e materiais
- `scripts/example_starter.py` - Exemplos
- `output/` - Renders gerados

---

## 💡 Dicas Avançadas

### Blender 5.0 Context Issues
```python
# ❌ ERRADO (falha em headless)
bpy.ops.object.camera_add()
cam = bpy.context.active_object

# ✅ CORRETO
cam_data = bpy.data.cameras.new(name="Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
```

### Mixamo Bone Naming
```python
def find_bone(armature, pattern):
    for bone in armature.pose.bones:
        if pattern in bone.name and 'ForeArm' not in bone.name:
            return bone
    return None
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| Context issues headless | Usar bpy.data ao invés de bpy.ops |
| Frames pretos | Verificar posição da câmera |
| Bones não encontrados | Usar pattern matching |
