import bpy
import math
import random
import os

# --- CONFIG ---
OUTPUT_PATH = r"C:\Users\user\Desktop\ONI_V30\temp\vile_blender_render.png"
NEON_COLOR = (0.0, 1.0, 1.0, 1.0) # Cyan
DARK_COLOR = (0.05, 0.05, 0.05, 1.0) # Obsidian

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def setup_eevee():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.5
    scene.eevee.bloom_radius = 6.0
    scene.eevee.use_gtao = True # Ambient Occlusion
    scene.eevee.use_ssr = True # Screen Space Reflections
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

def create_neon_material():
    mat = bpy.data.materials.new(name="Neon_Vein")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default
    nodes.clear()
    
    # Emission
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs[0].default_value = NEON_COLOR
    node_emission.inputs[1].default_value = 15.0 # Strength
    
    # Output
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    
    links.new(node_emission.outputs[0], node_out.inputs[0])
    return mat

def create_obsidian_material():
    mat = bpy.data.materials.new(name="Obsidian")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Principled BSDF is default
    node_bsdf = nodes.get("Principled BSDF")
    if node_bsdf:
        node_bsdf.inputs['Base Color'].default_value = DARK_COLOR
        node_bsdf.inputs['Metallic'].default_value = 0.9
        node_bsdf.inputs['Roughness'].default_value = 0.1
    
    return mat

def create_text_logo():
    # 1. Main Text "VILE"
    bpy.ops.object.text_add(location=(0, 0, 0))
    text_obj = bpy.context.active_object
    text_obj.name = "Logo_Text_Main"
    text_obj.data.body = "VILE"
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'
    text_obj.data.size = 2.5
    text_obj.data.extrude = 0.2
    text_obj.data.bevel_depth = 0.02
    
    # Material: Neon Core
    text_obj.data.materials.append(create_neon_material())
    
    # 2. Sub Text "PROJETOS"
    bpy.ops.object.text_add(location=(0, -1.2, 0))
    sub_obj = bpy.context.active_object
    sub_obj.name = "Logo_Text_Sub"
    sub_obj.data.body = "PROJETOS"
    sub_obj.data.align_x = 'CENTER'
    sub_obj.data.align_y = 'CENTER'
    sub_obj.data.size = 1.2
    sub_obj.data.extrude = 0.1
    sub_obj.data.bevel_depth = 0.01
    
    # Material: Obsidian
    sub_obj.data.materials.append(create_obsidian_material())
    
    # 3. Backplate/Frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.5, -0.2))
    plate = bpy.context.active_object
    plate.name = "Backplate"
    plate.scale = (4.5, 2.5, 0.1)
    
    plate.data.materials.append(create_obsidian_material())
    
    # Conversion to Mesh removed for headless stability (Text renders natively)
    # bpy.ops.object.select_all(action='DESELECT')
    # text_obj.select_set(True)
    # sub_obj.select_set(True)
    # bpy.ops.object.convert(target='MESH')

def setup_lighting():
    # Top Light
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    light = bpy.context.active_object
    light.data.energy = 500
    light.data.color = (1.0, 1.0, 1.0)
    
    # Side Rim (Blue)
    bpy.ops.object.light_add(type='POINT', location=(4, -4, 2))
    light = bpy.context.active_object
    light.data.energy = 300
    light.data.color = (0.0, 0.5, 1.0)
    
    # Side Rim (Purple)
    bpy.ops.object.light_add(type='POINT', location=(-4, 4, 3))
    light = bpy.context.active_object
    light.data.energy = 300
    light.data.color = (0.8, 0.0, 1.0)

def setup_camera():
    bpy.ops.object.camera_add(location=(0, -6, 2))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(75), 0, 0)
    bpy.context.scene.camera = cam

def render_scene():
    scene = bpy.context.scene
    scene.render.filepath = OUTPUT_PATH
    bpy.ops.render.render(write_still=True)
    print(f"Render saved to {OUTPUT_PATH}")
    
    # Save Blend File
    blend_path = r"C:\Users\user\Desktop\ONI_V30\temp\vile_procedural.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Blend file saved to {blend_path}")

# --- MAIN ---
if __name__ == "__main__":
    clean_scene()
    setup_eevee()
    create_text_logo()
    setup_lighting()
    setup_camera()
    
    # No rotation needed for text
    
    render_scene()
