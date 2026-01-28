# ============================================================================
# FUNKO POP FRIEZA v2 - Blender 3D Model (Corrigido)
# Domo roxo ajustado para ficar visível
# ============================================================================

import bpy
import math
import bmesh

# Limpar cena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for material in bpy.data.materials:
    if not material.users:
        bpy.data.materials.remove(material)

# ============================================================================
# MATERIAIS
# ============================================================================

def create_white_plastic():
    mat = bpy.data.materials.new(name="White_Plastic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.95, 0.92, 0.90, 1.0)
    principled.inputs['Roughness'].default_value = 0.4
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_purple_plastic():
    mat = bpy.data.materials.new(name="Purple_Plastic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.65, 0.30, 0.60, 1.0)
    principled.inputs['Roughness'].default_value = 0.35
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_black_glossy():
    mat = bpy.data.materials.new(name="Black_Glossy")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1.0)
    principled.inputs['Roughness'].default_value = 0.1
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

mat_white = create_white_plastic()
mat_purple = create_purple_plastic()
mat_black = create_black_glossy()

scale = 0.5

# ============================================================================
# CABEÇA - Parte inferior branca
# ============================================================================

# Criar esfera para a cabeça branca (parte de baixo é branca)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=24,
    radius=1.8 * scale,
    location=(0, 0, 3.5 * scale)
)
head_white = bpy.context.active_object
head_white.name = "Head_White"
head_white.data.materials.append(mat_white)

# ============================================================================
# CABEÇA - Domo roxo (parte de cima)
# ============================================================================

# Criar esfera para o domo roxo - maior e mais para frente
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=24,
    radius=1.6 * scale,
    location=(0, -0.2 * scale, 4.2 * scale)
)
head_dome = bpy.context.active_object
head_dome.name = "Head_Dome_Purple"

# Modificar para ficar como domo (cortar parte de baixo)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Usar boolean para cortar - ou simplesmente escalar
head_dome.scale = (1.0, 0.9, 0.7)
bpy.ops.object.transform_apply(scale=True)
head_dome.location = (0, 0.1 * scale, 4.3 * scale)
head_dome.data.materials.append(mat_purple)

# ============================================================================
# FACE BRANCA (formato de losango)
# ============================================================================

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=1.2 * scale,
    location=(0, -1.3 * scale, 3.4 * scale)
)
face = bpy.context.active_object
face.name = "Face_White"
face.scale = (0.7, 0.3, 0.9)
bpy.ops.object.transform_apply(scale=True)
face.data.materials.append(mat_white)

# ============================================================================
# OLHOS (grandes e pretos - estilo Funko)
# ============================================================================

# Olho esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.5 * scale,
    location=(-0.45 * scale, -1.55 * scale, 3.5 * scale)
)
eye_left = bpy.context.active_object
eye_left.name = "Eye_Left"
eye_left.scale = (1.0, 0.4, 1.0)
bpy.ops.object.transform_apply(scale=True)
eye_left.data.materials.append(mat_black)

# Olho direito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.5 * scale,
    location=(0.45 * scale, -1.55 * scale, 3.5 * scale)
)
eye_right = bpy.context.active_object
eye_right.name = "Eye_Right"
eye_right.scale = (1.0, 0.4, 1.0)
bpy.ops.object.transform_apply(scale=True)
eye_right.data.materials.append(mat_black)

# ============================================================================
# LINHAS DOS OLHOS (marcas características)
# ============================================================================

# Linha esquerda
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.025 * scale,
    depth=0.5 * scale,
    location=(-0.42 * scale, -1.45 * scale, 2.9 * scale)
)
line_left = bpy.context.active_object
line_left.name = "Eye_Line_Left"
line_left.rotation_euler = (0, 0, 0)
line_left.data.materials.append(mat_purple)

# Linha direita
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.025 * scale,
    depth=0.5 * scale,
    location=(0.42 * scale, -1.45 * scale, 2.9 * scale)
)
line_right = bpy.context.active_object
line_right.name = "Eye_Line_Right"
line_right.data.materials.append(mat_purple)

# ============================================================================
# TORSO
# ============================================================================

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.7 * scale,
    location=(0, 0, 1.8 * scale)
)
torso = bpy.context.active_object
torso.name = "Torso"
torso.scale = (1.0, 0.7, 1.2)
bpy.ops.object.transform_apply(scale=True)
torso.data.materials.append(mat_white)

# Marca roxa do peito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.2 * scale,
    location=(0, -0.45 * scale, 1.85 * scale)
)
chest_mark = bpy.context.active_object
chest_mark.name = "Chest_Mark"
chest_mark.scale = (1.5, 0.4, 0.8)
bpy.ops.object.transform_apply(scale=True)
chest_mark.data.materials.append(mat_purple)

# ============================================================================
# OMBROS E MARCAS
# ============================================================================

# Ombro esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 * scale, location=(-0.75 * scale, 0, 2.1 * scale))
shoulder_l = bpy.context.active_object
shoulder_l.name = "Shoulder_Left"
shoulder_l.data.materials.append(mat_white)

# Marca ombro esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15 * scale, location=(-0.9 * scale, -0.15 * scale, 2.15 * scale))
mark_l = bpy.context.active_object
mark_l.name = "Shoulder_Mark_L"
mark_l.data.materials.append(mat_purple)

# Ombro direito
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 * scale, location=(0.75 * scale, 0, 2.1 * scale))
shoulder_r = bpy.context.active_object
shoulder_r.name = "Shoulder_Right"
shoulder_r.data.materials.append(mat_white)

# Marca ombro direito
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15 * scale, location=(0.9 * scale, -0.15 * scale, 2.15 * scale))
mark_r = bpy.context.active_object
mark_r.name = "Shoulder_Mark_R"
mark_r.data.materials.append(mat_purple)

# ============================================================================
# BRAÇOS
# ============================================================================

# Braço esquerdo
bpy.ops.mesh.primitive_cylinder_add(radius=0.15 * scale, depth=0.7 * scale, location=(-0.95 * scale, 0, 1.6 * scale))
arm_l = bpy.context.active_object
arm_l.name = "Arm_Left"
arm_l.rotation_euler = (0, math.radians(12), 0)
arm_l.data.materials.append(mat_white)

# Braço direito
bpy.ops.mesh.primitive_cylinder_add(radius=0.15 * scale, depth=0.7 * scale, location=(0.95 * scale, 0, 1.6 * scale))
arm_r = bpy.context.active_object
arm_r.name = "Arm_Right"
arm_r.rotation_euler = (0, math.radians(-12), 0)
arm_r.data.materials.append(mat_white)

# ============================================================================
# MÃOS COM 3 DEDOS
# ============================================================================

# Mão esquerda
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18 * scale, location=(-1.05 * scale, 0, 1.15 * scale))
hand_l = bpy.context.active_object
hand_l.name = "Hand_Left"
hand_l.data.materials.append(mat_white)

# Dedos mão esquerda
for i in range(3):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04 * scale,
        depth=0.2 * scale,
        location=(-1.15 * scale + 0.07 * i * scale, -0.08 * scale, 0.98 * scale)
    )
    finger = bpy.context.active_object
    finger.name = f"Finger_L_{i}"
    finger.rotation_euler = (math.radians(50), 0, 0)
    finger.data.materials.append(mat_white)

# Mão direita
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18 * scale, location=(1.05 * scale, 0, 1.15 * scale))
hand_r = bpy.context.active_object
hand_r.name = "Hand_Right"
hand_r.data.materials.append(mat_white)

# Dedos mão direita
for i in range(3):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04 * scale,
        depth=0.2 * scale,
        location=(0.95 * scale + 0.07 * i * scale, -0.08 * scale, 0.98 * scale)
    )
    finger = bpy.context.active_object
    finger.name = f"Finger_R_{i}"
    finger.rotation_euler = (math.radians(50), 0, 0)
    finger.data.materials.append(mat_white)

# ============================================================================
# QUADRIL
# ============================================================================

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45 * scale, location=(0, 0, 1.15 * scale))
hip = bpy.context.active_object
hip.name = "Hip"
hip.scale = (1.3, 0.8, 0.8)
bpy.ops.object.transform_apply(scale=True)
hip.data.materials.append(mat_white)

# Marca do quadril
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12 * scale, location=(0, -0.35 * scale, 1.1 * scale))
hip_mark = bpy.context.active_object
hip_mark.name = "Hip_Mark"
hip_mark.data.materials.append(mat_purple)

# ============================================================================
# PERNAS
# ============================================================================

# Perna esquerda
bpy.ops.mesh.primitive_cylinder_add(radius=0.17 * scale, depth=0.55 * scale, location=(-0.32 * scale, 0, 0.55 * scale))
leg_l = bpy.context.active_object
leg_l.name = "Leg_Left"
leg_l.data.materials.append(mat_white)

# Marca perna esquerda
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09 * scale, location=(-0.32 * scale, -0.18 * scale, 0.45 * scale))
leg_mark_l = bpy.context.active_object
leg_mark_l.name = "Leg_Mark_L"
leg_mark_l.data.materials.append(mat_purple)

# Perna direita
bpy.ops.mesh.primitive_cylinder_add(radius=0.17 * scale, depth=0.55 * scale, location=(0.32 * scale, 0, 0.55 * scale))
leg_r = bpy.context.active_object
leg_r.name = "Leg_Right"
leg_r.data.materials.append(mat_white)

# Marca perna direita
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09 * scale, location=(0.32 * scale, -0.18 * scale, 0.45 * scale))
leg_mark_r = bpy.context.active_object
leg_mark_r.name = "Leg_Mark_R"
leg_mark_r.data.materials.append(mat_purple)

# ============================================================================
# PÉS COM 3 DEDOS
# ============================================================================

# Pé esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22 * scale, location=(-0.32 * scale, -0.05 * scale, 0.12 * scale))
foot_l = bpy.context.active_object
foot_l.name = "Foot_Left"
foot_l.scale = (1.0, 1.4, 0.5)
bpy.ops.object.transform_apply(scale=True)
foot_l.data.materials.append(mat_white)

# Dedos pé esquerdo
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06 * scale, location=(-0.42 * scale + 0.1 * i * scale, -0.28 * scale, 0.04 * scale))
    toe = bpy.context.active_object
    toe.name = f"Toe_L_{i}"
    toe.scale = (0.8, 1.4, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    toe.data.materials.append(mat_white)

# Pé direito
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22 * scale, location=(0.32 * scale, -0.05 * scale, 0.12 * scale))
foot_r = bpy.context.active_object
foot_r.name = "Foot_Right"
foot_r.scale = (1.0, 1.4, 0.5)
bpy.ops.object.transform_apply(scale=True)
foot_r.data.materials.append(mat_white)

# Dedos pé direito
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06 * scale, location=(0.22 * scale + 0.1 * i * scale, -0.28 * scale, 0.04 * scale))
    toe = bpy.context.active_object
    toe.name = f"Toe_R_{i}"
    toe.scale = (0.8, 1.4, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    toe.data.materials.append(mat_white)

# ============================================================================
# BASE
# ============================================================================

bpy.ops.mesh.primitive_cylinder_add(radius=1.0 * scale, depth=0.08 * scale, location=(0, 0, -0.04 * scale))
base = bpy.context.active_object
base.name = "Base"
base.data.materials.append(mat_black)

# ============================================================================
# ILUMINAÇÃO DE ESTÚDIO
# ============================================================================

# Key Light
bpy.ops.object.light_add(type='AREA', location=(2, -4, 5))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 400
key.data.size = 4
key.rotation_euler = (math.radians(55), math.radians(15), 0)

# Fill Light
bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 150
fill.data.size = 3

# Rim Light
bpy.ops.object.light_add(type='AREA', location=(0, 4, 4))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 200
rim.data.size = 2

# ============================================================================
# CÂMERA
# ============================================================================

bpy.ops.object.camera_add(location=(0, -5.5, 2.2))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (math.radians(72), 0, 0)
bpy.context.scene.camera = camera

# ============================================================================
# RENDER
# ============================================================================

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 128
scene.render.resolution_x = 1080
scene.render.resolution_y = 1350
scene.render.resolution_percentage = 100

# Fundo branco
scene.world.use_nodes = True
world_bg = scene.world.node_tree.nodes.get('Background')
if world_bg:
    world_bg.inputs['Color'].default_value = (0.95, 0.95, 0.95, 1.0)

# Salvar - resolução dinâmica de caminho
import os as _os
_script_dir = _os.path.dirname(_os.path.abspath(__file__)) if '__file__' in dir() else ""
_oni_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_script_dir))) if _script_dir else "C:/temp"
_temp_dir = _os.path.join(_oni_root, "temp")
_os.makedirs(_temp_dir, exist_ok=True)

output_path = _os.path.join(_temp_dir, "Funko_Frieza_v2.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

render_path = _os.path.join(_temp_dir, "Funko_Frieza_v2_Render.png")
scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)

print(f"Funko Pop Frieza v2 - CORRIGIDO!")
print(f"Arquivo: {output_path}")
print(f"Render: {render_path}")
