# ============================================================================
# FUNKO POP FRIEZA (Final Form) - Blender 3D Model
# Modelagem procedural completa do personagem
# ============================================================================

import bpy
import math
import bmesh

# Limpar cena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Limpar materiais órfãos
for material in bpy.data.materials:
    if not material.users:
        bpy.data.materials.remove(material)

# ============================================================================
# MATERIAIS
# ============================================================================

def create_white_plastic():
    """Material plástico branco/creme (corpo principal)"""
    mat = bpy.data.materials.new(name="White_Plastic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Cor creme/branco levemente rosado
    principled.inputs['Base Color'].default_value = (0.95, 0.92, 0.90, 1.0)
    principled.inputs['Roughness'].default_value = 0.4
    principled.inputs['Specular IOR Level'].default_value = 0.5
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_purple_plastic():
    """Material plástico roxo/magenta (detalhes)"""
    mat = bpy.data.materials.new(name="Purple_Plastic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Cor magenta/roxo do Frieza
    principled.inputs['Base Color'].default_value = (0.6, 0.25, 0.55, 1.0)
    principled.inputs['Roughness'].default_value = 0.35
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_black_glossy():
    """Material preto brilhante (olhos)"""
    mat = bpy.data.materials.new(name="Black_Glossy")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    principled.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1.0)
    principled.inputs['Roughness'].default_value = 0.1
    principled.inputs['Specular IOR Level'].default_value = 1.0
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Criar materiais
mat_white = create_white_plastic()
mat_purple = create_purple_plastic()
mat_black = create_black_glossy()

# ============================================================================
# CORPO (FUNKO POP STYLE)
# ============================================================================

# Escala base
scale = 0.5

# 1. CABEÇA (forma principal - grande e redonda estilo Funko)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.8 * scale,
    location=(0, 0, 3.5 * scale)
)
head = bpy.context.active_object
head.name = "Head"

# Achatar um pouco a cabeça na frente
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(head.data)
for v in bm.verts:
    if v.co.y < -0.5 * scale:
        v.co.y *= 0.85
    # Achatar levemente em cima
    if v.co.z > 4.5 * scale:
        v.co.z *= 0.95
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode='OBJECT')
head.data.materials.append(mat_white)

# 2. DOMO ROXO DA CABEÇA (parte de cima)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.5 * scale,
    location=(0, 0.1 * scale, 4.0 * scale)
)
head_dome = bpy.context.active_object
head_dome.name = "Head_Dome"

# Cortar metade inferior
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(head_dome.data)
verts_to_delete = [v for v in bm.verts if v.co.z < 3.5 * scale]
bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
bmesh.update_edit_mesh(head_dome.data)
bpy.ops.object.mode_set(mode='OBJECT')
head_dome.data.materials.append(mat_purple)

# 3. FACE (área branca da face - losango)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=1.0 * scale,
    location=(0, -1.4 * scale, 3.3 * scale)
)
face_white = bpy.context.active_object
face_white.name = "Face_White"
face_white.scale = (0.8, 0.3, 1.0)
bpy.ops.object.transform_apply(scale=True)
face_white.data.materials.append(mat_white)

# 4. OLHOS (grandes e pretos - estilo Funko)
# Olho esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.45 * scale,
    location=(-0.5 * scale, -1.6 * scale, 3.5 * scale)
)
eye_left = bpy.context.active_object
eye_left.name = "Eye_Left"
eye_left.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(scale=True)
eye_left.data.materials.append(mat_black)

# Olho direito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.45 * scale,
    location=(0.5 * scale, -1.6 * scale, 3.5 * scale)
)
eye_right = bpy.context.active_object
eye_right.name = "Eye_Right"
eye_right.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(scale=True)
eye_right.data.materials.append(mat_black)

# 5. LINHAS DOS OLHOS (marcas roxas abaixo dos olhos)
# Linha esquerda
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.03 * scale,
    depth=0.6 * scale,
    location=(-0.45 * scale, -1.5 * scale, 3.0 * scale)
)
line_left = bpy.context.active_object
line_left.name = "Eye_Line_Left"
line_left.rotation_euler = (math.radians(90), 0, 0)
line_left.data.materials.append(mat_purple)

# Linha direita
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.03 * scale,
    depth=0.6 * scale,
    location=(0.45 * scale, -1.5 * scale, 3.0 * scale)
)
line_right = bpy.context.active_object
line_right.name = "Eye_Line_Right"
line_right.rotation_euler = (math.radians(90), 0, 0)
line_right.data.materials.append(mat_purple)

# 6. TORSO (corpo pequeno estilo Funko)
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

# 7. MARCA ROXA DO PEITO
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.25 * scale,
    location=(0, -0.5 * scale, 1.9 * scale)
)
chest_mark = bpy.context.active_object
chest_mark.name = "Chest_Mark"
chest_mark.scale = (1.2, 0.3, 0.8)
bpy.ops.object.transform_apply(scale=True)
chest_mark.data.materials.append(mat_purple)

# 8. OMBROS
# Ombro esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.35 * scale,
    location=(-0.8 * scale, 0, 2.2 * scale)
)
shoulder_left = bpy.context.active_object
shoulder_left.name = "Shoulder_Left"
shoulder_left.data.materials.append(mat_white)

# Marca roxa do ombro esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.18 * scale,
    location=(-0.95 * scale, -0.15 * scale, 2.25 * scale)
)
shoulder_mark_left = bpy.context.active_object
shoulder_mark_left.name = "Shoulder_Mark_Left"
shoulder_mark_left.data.materials.append(mat_purple)

# Ombro direito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.35 * scale,
    location=(0.8 * scale, 0, 2.2 * scale)
)
shoulder_right = bpy.context.active_object
shoulder_right.name = "Shoulder_Right"
shoulder_right.data.materials.append(mat_white)

# Marca roxa do ombro direito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.18 * scale,
    location=(0.95 * scale, -0.15 * scale, 2.25 * scale)
)
shoulder_mark_right = bpy.context.active_object
shoulder_mark_right.name = "Shoulder_Mark_Right"
shoulder_mark_right.data.materials.append(mat_purple)

# 9. BRAÇOS
# Braço esquerdo
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.18 * scale,
    depth=0.8 * scale,
    location=(-1.0 * scale, 0, 1.7 * scale)
)
arm_left = bpy.context.active_object
arm_left.name = "Arm_Left"
arm_left.rotation_euler = (0, math.radians(15), 0)
arm_left.data.materials.append(mat_white)

# Braço direito
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.18 * scale,
    depth=0.8 * scale,
    location=(1.0 * scale, 0, 1.7 * scale)
)
arm_right = bpy.context.active_object
arm_right.name = "Arm_Right"
arm_right.rotation_euler = (0, math.radians(-15), 0)
arm_right.data.materials.append(mat_white)

# 10. MÃOS (3 dedos estilo Frieza)
# Mão esquerda
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.2 * scale,
    location=(-1.1 * scale, 0, 1.2 * scale)
)
hand_left = bpy.context.active_object
hand_left.name = "Hand_Left"
hand_left.data.materials.append(mat_white)

# Dedos mão esquerda
for i in range(3):
    angle = math.radians(-30 + i * 30)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05 * scale,
        depth=0.25 * scale,
        location=(-1.2 * scale + 0.08 * i * scale, -0.1 * scale, 1.0 * scale)
    )
    finger = bpy.context.active_object
    finger.name = f"Finger_Left_{i}"
    finger.rotation_euler = (math.radians(45), angle, 0)
    finger.data.materials.append(mat_white)

# Mão direita
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.2 * scale,
    location=(1.1 * scale, 0, 1.2 * scale)
)
hand_right = bpy.context.active_object
hand_right.name = "Hand_Right"
hand_right.data.materials.append(mat_white)

# Dedos mão direita
for i in range(3):
    angle = math.radians(30 - i * 30)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05 * scale,
        depth=0.25 * scale,
        location=(1.2 * scale - 0.08 * i * scale, -0.1 * scale, 1.0 * scale)
    )
    finger = bpy.context.active_object
    finger.name = f"Finger_Right_{i}"
    finger.rotation_euler = (math.radians(45), angle, 0)
    finger.data.materials.append(mat_white)

# 11. QUADRIL
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.5 * scale,
    location=(0, 0, 1.2 * scale)
)
hip = bpy.context.active_object
hip.name = "Hip"
hip.scale = (1.2, 0.8, 0.8)
bpy.ops.object.transform_apply(scale=True)
hip.data.materials.append(mat_white)

# Marca roxa do quadril
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.15 * scale,
    location=(0, -0.4 * scale, 1.15 * scale)
)
hip_mark = bpy.context.active_object
hip_mark.name = "Hip_Mark"
hip_mark.data.materials.append(mat_purple)

# 12. PERNAS
# Perna esquerda
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.2 * scale,
    depth=0.6 * scale,
    location=(-0.35 * scale, 0, 0.6 * scale)
)
leg_left = bpy.context.active_object
leg_left.name = "Leg_Left"
leg_left.data.materials.append(mat_white)

# Marca roxa perna esquerda
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.1 * scale,
    location=(-0.35 * scale, -0.2 * scale, 0.5 * scale)
)
leg_mark_left = bpy.context.active_object
leg_mark_left.name = "Leg_Mark_Left"
leg_mark_left.data.materials.append(mat_purple)

# Perna direita
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.2 * scale,
    depth=0.6 * scale,
    location=(0.35 * scale, 0, 0.6 * scale)
)
leg_right = bpy.context.active_object
leg_right.name = "Leg_Right"
leg_right.data.materials.append(mat_white)

# Marca roxa perna direita
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.1 * scale,
    location=(0.35 * scale, -0.2 * scale, 0.5 * scale)
)
leg_mark_right = bpy.context.active_object
leg_mark_right.name = "Leg_Mark_Right"
leg_mark_right.data.materials.append(mat_purple)

# 13. PÉS (3 dedos estilo Frieza)
# Pé esquerdo
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.25 * scale,
    location=(-0.35 * scale, -0.1 * scale, 0.15 * scale)
)
foot_left = bpy.context.active_object
foot_left.name = "Foot_Left"
foot_left.scale = (1.0, 1.5, 0.5)
bpy.ops.object.transform_apply(scale=True)
foot_left.data.materials.append(mat_white)

# Dedos pé esquerdo
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8,
        ring_count=4,
        radius=0.08 * scale,
        location=(-0.45 * scale + 0.1 * i * scale, -0.35 * scale, 0.05 * scale)
    )
    toe = bpy.context.active_object
    toe.name = f"Toe_Left_{i}"
    toe.scale = (0.8, 1.5, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    toe.data.materials.append(mat_white)

# Pé direito
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=6,
    radius=0.25 * scale,
    location=(0.35 * scale, -0.1 * scale, 0.15 * scale)
)
foot_right = bpy.context.active_object
foot_right.name = "Foot_Right"
foot_right.scale = (1.0, 1.5, 0.5)
bpy.ops.object.transform_apply(scale=True)
foot_right.data.materials.append(mat_white)

# Dedos pé direito
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8,
        ring_count=4,
        radius=0.08 * scale,
        location=(0.25 * scale + 0.1 * i * scale, -0.35 * scale, 0.05 * scale)
    )
    toe = bpy.context.active_object
    toe.name = f"Toe_Right_{i}"
    toe.scale = (0.8, 1.5, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    toe.data.materials.append(mat_white)

# 14. BASE/PEDESTAL
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.2 * scale,
    depth=0.1 * scale,
    location=(0, 0, -0.05 * scale)
)
base = bpy.context.active_object
base.name = "Base"
base.data.materials.append(mat_black)

# ============================================================================
# ILUMINAÇÃO
# ============================================================================

# Luz principal frontal
bpy.ops.object.light_add(
    type='AREA',
    location=(0, -5, 4)
)
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 300
key_light.data.size = 4
key_light.data.color = (1.0, 0.98, 0.95)
key_light.rotation_euler = (math.radians(60), 0, 0)

# Luz de preenchimento lateral
bpy.ops.object.light_add(
    type='AREA',
    location=(4, -2, 3)
)
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 150
fill_light.data.size = 3

# Luz de contorno traseira
bpy.ops.object.light_add(
    type='AREA',
    location=(-2, 3, 4)
)
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 200
rim_light.data.size = 2
rim_light.data.color = (0.95, 0.95, 1.0)

# ============================================================================
# CÂMERA
# ============================================================================

bpy.ops.object.camera_add(
    location=(0, -6, 2.5)
)
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = camera

# ============================================================================
# CONFIGURAÇÕES DE RENDER
# ============================================================================

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 128

scene.render.resolution_x = 1080
scene.render.resolution_y = 1350
scene.render.resolution_percentage = 100

# Fundo branco
scene.world.use_nodes = True
world_nodes = scene.world.node_tree.nodes
world_bg = world_nodes.get('Background')
if world_bg:
    world_bg.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

# Salvar arquivo - resolução dinâmica de caminho
import os as _os
_script_dir = _os.path.dirname(_os.path.abspath(__file__)) if '__file__' in dir() else ""
_oni_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_script_dir))) if _script_dir else "C:/temp"
_temp_dir = _os.path.join(_oni_root, "temp")
_os.makedirs(_temp_dir, exist_ok=True)

output_path = _os.path.join(_temp_dir, "Funko_Frieza.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

# Render
render_path = _os.path.join(_temp_dir, "Funko_Frieza_Render.png")
scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)

print(f"Funko Pop Frieza modelado!")
print(f"Arquivo: {output_path}")
print(f"Render: {render_path}")
