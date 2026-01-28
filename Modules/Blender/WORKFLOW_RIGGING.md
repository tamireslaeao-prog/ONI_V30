---
description: Como animar rigs Mixamo em Blender com walk cycle e poses personalizadas
---

# 3D RIG - ANIMAÇÃO DE CHARACTERS COM MIXAMO

**Caso de Sucesso:** UBIE Walk + Arms Cross (150 frames)

## Contexto
Animar characters 3D com rigs Mixamo em Blender 5.0, incluindo walk cycles e poses personalizadas, com automação completa via Python.

---

## Descobertas Críticas

### 1. Mixamo Bone Naming
**Problema:** Bones não têm nomes simples como "RightArm"  
**Realidade:** `mixamorig:RightArm.44`, `mixamorig:LeftArm.15`

**Solução:**
```python
def find_bone(armature, name_pattern):
    """Find bone by pattern (handles Mixamo naming)"""
    for bone in armature.pose.bones:
        if name_pattern in bone.name and 'ForeArm' not in bone.name:
            return bone
    return None

right_arm = find_bone(armature, 'RightArm')
left_arm = find_bone(armature, 'LeftArm')
```

### 2. Context Issues (Blender 5.0)
**Problema:** `bpy.context.active_object` não existe em headless mode  
**Solução:** Criar objetos via `bpy.data` antes de adicionar à cena

```python
# ❌ ERRADO (falha em headless)
bpy.ops.object.camera_add(location=(5, -2.5, 1.5))
cam = bpy.context.active_object

# ✅ CORRETO
cam_data = bpy.data.cameras.new(name="Tracking_Camera")
cam = bpy.data.objects.new("Tracking_Camera", cam_data)
bpy.context.collection.objects.link(cam)
```

### 3. Keyframe Animation
**Keyframes devem ser criados em AMBOS os extremos:**

```python
# Frame 1: Pose inicial
scene.frame_set(1)
right_arm.rotation_euler = (0, 0, 0)
right_arm.keyframe_insert("rotation_euler", frame=1)

# Frame 60: Pose final
scene.frame_set(60)
right_arm.rotation_euler[2] = math.radians(-90)
right_arm.keyframe_insert("rotation_euler", frame=60)
```

---

## Walk Cycle - Implementação

### Parâmetros
```python
walk_speed = 0.03  # Units per frame
step_duration = 30  # frames per step
leg_swing = math.radians(30)  # degrees
```

### Loop de Animação
```python
for frame in range(1, 151):
    scene.frame_set(frame)
    
    # Hips move forward
    hips.location = (0, -frame * walk_speed, 0)
    hips.keyframe_insert("location", frame=frame)
    
    # Leg swing (alternating)
    phase = (frame % step_duration) / step_duration
    
    right_angle = leg_swing * math.sin(phase * 2 * math.pi)
    left_angle = -right_angle
    
    right_leg.rotation_euler[0] = right_angle
    left_leg.rotation_euler[0] = left_angle
    
    if frame % 5 == 0:
        right_leg.keyframe_insert("rotation_euler", frame=frame)
        left_leg.keyframe_insert("rotation_euler", frame=frame)
```

---

## Poses Personalizadas

### Arms Cross (Frames 60-120)

**Transição:**
```python
# Frame 60: Neutral
right_arm.rotation_euler = (math.radians(20), 0, 0)

# Frame 90: Crossed
right_arm.rotation_euler = (math.radians(-10), math.radians(15), math.radians(70))
left_arm.rotation_euler = (math.radians(-10), math.radians(-15), math.radians(-70))

# Frame 120: Return to walk
```

---

## Camera Tracking

### Side-Scrolling Follow
```python
for frame in range(1, 151, 10):
    scene.frame_set(frame)
    # Camera follows hips Y position
    cam.location = (5, hips.location.y, 1.5)
    cam.keyframe_insert("location", frame=frame)
```

---

## Lighting Cinematográfico

### 3-Point Setup
```python
# Key Light (Front-Right)
key_data = bpy.data.lights.new(name="Key", type='AREA')
key = bpy.data.objects.new("Key", key_data)
key.location = (3, -2, 3)
key_data.energy = 400

# Fill Light (Front-Left, softer)
fill_data = bpy.data.lights.new(name="Fill", type='AREA')
fill.location = (-3, -2, 2)
fill_data.energy = 150
fill_data.color = (0.8, 0.9, 1.0)  # Cool tone

# Rim Light (Back, high)
rim_data = bpy.data.lights.new(name="Rim", type='SPOT')
rim.location = (0, -4, 3)
rim_data.energy = 500
```

---

## Render Settings Otimizados

```python
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50  # 960x540 para testes rápidos
```

**IMPORTANTE:** 64 samples @ 1080p = ~2-3 min/frame  
**Para testes:** Use `resolution_percentage = 50` (4x mais rápido)

---

## Troubleshooting

### Problema: Frames Pretos
**Causa:** Câmera não vê o character  
**Solução:** Calcular posição baseada em bounding box:
```python
# Get character bounds
all_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
# Calculate center
# Position camera appropriately
```

### Problema: Movimento Robótico
**Causa:** Poucos keyframes  
**Solução:** Keyframe a cada 5-10 frames para suavidade

### Problema: Character Z muito alto
**Causa:** Mixamo characters têm diferentes escalas  
**Solução:** Verificar `hips.location.z` e ajustar câmera

---

## Arquivos de Referência

**Scripts de Sucesso:**
- `temp/ubie/ubie_showcase_animation.py` - Script completo
- `temp/ubie/ubie_walk_arms.blend` - Projeto final
- `temp/ubie/ubie_wave_FINAL.py` - Exemplo de pose simples

**Key Learnings:**
- Sempre detectar bones dinamicamente (não hardcode)
- Criar actions para organizar animações
- Testar com poucos frames antes de render completo
- Blender 5.0 tem APIs diferentes do 4.x

---

## Checklist de Execução

- [ ] Carregar arquivo .blend com rig Mixamo
- [ ] Detectar bones (find_bone pattern matching)
- [ ] Criar action para animação
- [ ] Criar walk cycle (hips + legs)
- [ ] Adicionar poses personalizadas
- [ ] Setup câmera tracking
- [ ] Setup iluminação 3-point
- [ ] Testar render 1 frame
- [ ] Render completo ou usar GUI para preview

---

**Status:** ✅ VALIDADO EM PRODUÇÃO (UBIE Showcase)  
**Versão:** 1.0  
**Data:** 2026-01-13
