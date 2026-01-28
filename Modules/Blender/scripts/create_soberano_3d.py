# ============================================================================
# ONI SOBERANO 3D LOGO - Blender Script
# Logo 3D épico com geometria procedural, materiais metálicos e iluminação
# ============================================================================

import bpy
import math
import os

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

def create_gold_material():
    """Material dourado metálico premium"""
    mat = bpy.data.materials.new(name="Gold_Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Cor dourada
    principled.inputs['Base Color'].default_value = (0.83, 0.68, 0.21, 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = 0.2
    principled.inputs['IOR'].default_value = 1.45
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    output.location = (300, 0)
    principled.location = (0, 0)
    
    return mat

def create_purple_emission():
    """Material emissor roxo para efeitos de luz"""
    mat = bpy.data.materials.new(name="Purple_Emission")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    
    emission.inputs['Color'].default_value = (0.55, 0.23, 0.9, 1.0)
    emission.inputs['Strength'].default_value = 5.0
    
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    return mat

def create_dark_metal():
    """Metal escuro para base"""
    mat = bpy.data.materials.new(name="Dark_Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    principled.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0)
    principled.inputs['Metallic'].default_value = 0.9
    principled.inputs['Roughness'].default_value = 0.3
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_chrome_material():
    """Chrome brilhante"""
    mat = bpy.data.materials.new(name="Chrome")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = 0.05
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_red_emission():
    """Emissor vermelho para olho"""
    mat = bpy.data.materials.new(name="Red_Emission")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    
    emission.inputs['Color'].default_value = (1.0, 0.1, 0.1, 1.0)
    emission.inputs['Strength'].default_value = 10.0
    
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    return mat

# Criar materiais
mat_gold = create_gold_material()
mat_purple = create_purple_emission()
mat_dark = create_dark_metal()
mat_chrome = create_chrome_material()
mat_red = create_red_emission()

# ============================================================================
# GEOMETRIA DO LOGO
# ============================================================================

# 1. Base hexagonal
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6,
    radius=3,
    depth=0.3,
    location=(0, 0, 0)
)
base_hex = bpy.context.active_object
base_hex.name = "Base_Hexagon"
base_hex.data.materials.append(mat_dark)

# 2. Anel externo 1
bpy.ops.mesh.primitive_torus_add(
    major_radius=3.5,
    minor_radius=0.1,
    location=(0, 0, 0.2)
)
ring1 = bpy.context.active_object
ring1.name = "Ring_Outer_1"
ring1.data.materials.append(mat_gold)

# 3. Anel externo 2
bpy.ops.mesh.primitive_torus_add(
    major_radius=4.0,
    minor_radius=0.08,
    location=(0, 0, 0.15)
)
ring2 = bpy.context.active_object
ring2.name = "Ring_Outer_2"
ring2.data.materials.append(mat_chrome)

# 4. Anel externo 3 (emissor)
bpy.ops.mesh.primitive_torus_add(
    major_radius=4.5,
    minor_radius=0.05,
    location=(0, 0, 0.1)
)
ring3 = bpy.context.active_object
ring3.name = "Ring_Outer_3"
ring3.data.materials.append(mat_purple)

# 5. Hexágono central elevado
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6,
    radius=2,
    depth=0.5,
    location=(0, 0, 0.4)
)
hex_center = bpy.context.active_object
hex_center.name = "Hex_Center"
hex_center.data.materials.append(mat_gold)

# 6. Olho central (esfera)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    location=(0, 0, 0.8)
)
eye = bpy.context.active_object
eye.name = "Eye_Core"
eye.data.materials.append(mat_red)

# 7. Olho - íris (torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.6,
    minor_radius=0.1,
    location=(0, 0, 0.8)
)
iris = bpy.context.active_object
iris.name = "Eye_Iris"
iris.data.materials.append(mat_purple)

# 8-13. Linhas de circuito (cilindros finos)
circuit_angles = [0, 60, 120, 180, 240, 300]
for i, angle in enumerate(circuit_angles):
    rad = math.radians(angle)
    x = 2.5 * math.cos(rad)
    y = 2.5 * math.sin(rad)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=2,
        location=(x/2, y/2, 0.3)
    )
    circuit = bpy.context.active_object
    circuit.name = f"Circuit_{i+1}"
    circuit.rotation_euler = (0, math.radians(90), rad)
    circuit.data.materials.append(mat_purple)

# 14-19. Nós de conexão (esferas pequenas)
for i, angle in enumerate(circuit_angles):
    rad = math.radians(angle)
    x = 2.5 * math.cos(rad)
    y = 2.5 * math.sin(rad)
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.15,
        location=(x, y, 0.3)
    )
    node = bpy.context.active_object
    node.name = f"Node_{i+1}"
    node.data.materials.append(mat_gold)

# 20. Texto "SOBERANO"
bpy.ops.object.text_add(location=(0, -5.5, 0))
text_obj = bpy.context.active_object
text_obj.name = "Text_SOBERANO"
text_obj.data.body = "SOBERANO"
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
text_obj.data.extrude = 0.2
text_obj.data.bevel_depth = 0.03
text_obj.data.bevel_resolution = 3
text_obj.data.size = 1.2
text_obj.location = (0, -5.5, 0.1)
text_obj.rotation_euler = (math.radians(90), 0, 0)

# Converter para mesh e aplicar material
bpy.ops.object.convert(target='MESH')
text_obj.data.materials.append(mat_chrome)

# 21. Texto "ONI"
bpy.ops.object.text_add(location=(0, 5, 0))
text_oni = bpy.context.active_object
text_oni.name = "Text_ONI"
text_oni.data.body = "ONI"
text_oni.data.align_x = 'CENTER'
text_oni.data.align_y = 'CENTER'
text_oni.data.extrude = 0.15
text_oni.data.bevel_depth = 0.02
text_oni.data.size = 0.8
text_oni.location = (0, 5, 0.1)
text_oni.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.convert(target='MESH')
text_oni.data.materials.append(mat_gold)

# 22-27. Triângulos decorativos
for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 5 * math.cos(angle)
    y = 5 * math.sin(angle)
    
    bpy.ops.mesh.primitive_cone_add(
        vertices=3,
        radius1=0.3,
        depth=0.1,
        location=(x, y, 0.05)
    )
    tri = bpy.context.active_object
    tri.name = f"Triangle_{i+1}"
    tri.rotation_euler = (0, 0, angle)
    tri.data.materials.append(mat_gold)

# 28. Plano de fundo
bpy.ops.mesh.primitive_plane_add(
    size=20,
    location=(0, 0, -0.5)
)
bg_plane = bpy.context.active_object
bg_plane.name = "Background"
bg_plane.data.materials.append(mat_dark)

# 29-34. Pontos de luz decorativos
for i in range(6):
    angle = math.radians(i * 60)
    x = 4 * math.cos(angle)
    y = 4 * math.sin(angle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.08,
        location=(x, y, 0.5)
    )
    light_point = bpy.context.active_object
    light_point.name = f"Light_Point_{i+1}"
    light_point.data.materials.append(mat_purple)

# ============================================================================
# ILUMINAÇÃO
# ============================================================================

# Luz principal (Key Light)
bpy.ops.object.light_add(
    type='AREA',
    location=(5, -5, 8)
)
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 500
key_light.data.size = 5
key_light.data.color = (1.0, 0.95, 0.9)
key_light.rotation_euler = (math.radians(45), math.radians(30), 0)

# Luz de preenchimento (Fill Light)
bpy.ops.object.light_add(
    type='AREA',
    location=(-5, -3, 5)
)
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 200
fill_light.data.size = 3
fill_light.data.color = (0.8, 0.8, 1.0)

# Luz de contorno (Rim Light)
bpy.ops.object.light_add(
    type='AREA',
    location=(0, 5, 6)
)
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 300
rim_light.data.size = 4
rim_light.data.color = (0.7, 0.5, 1.0)

# Luz ambiente (HDRI simulado com luz de área grande)
bpy.ops.object.light_add(
    type='AREA',
    location=(0, 0, 12)
)
ambient = bpy.context.active_object
ambient.name = "Ambient_Light"
ambient.data.energy = 100
ambient.data.size = 15

# ============================================================================
# CÂMERA
# ============================================================================

bpy.ops.object.camera_add(
    location=(0, -12, 8)
)
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(55), 0, 0)

# Definir como câmera ativa
bpy.context.scene.camera = camera

# ============================================================================
# CONFIGURAÇÕES DE RENDER
# ============================================================================

scene = bpy.context.scene

# Engine EEVEE para render rápido e bonito
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 128

# Resolução
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Cor de fundo
scene.world.use_nodes = True
world_nodes = scene.world.node_tree.nodes
world_bg = world_nodes.get('Background')
if world_bg:
    world_bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1.0)

# Salvar arquivo - resolução dinâmica de caminho
_script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else ""
_oni_root = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir))) if _script_dir else "C:/temp"
_temp_dir = os.path.join(_oni_root, "temp")
os.makedirs(_temp_dir, exist_ok=True)

output_path = os.path.join(_temp_dir, "SOBERANO_3D_Logo.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

# Render
render_path = os.path.join(_temp_dir, "SOBERANO_3D_Render.png")
scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)

print(f"Logo 3D SOBERANO criado!")
print(f"Arquivo: {output_path}")
print(f"Render: {render_path}")
