"""
SOVEREIGN LOGO GENERATOR - Blender 3D
Creates a professional 3D logo with metallic materials.

Design Concept:
- Text: "SOVEREIGN" with gold metallic finish
- Symbol: Tríade (three interlocking circles representing UBIE+ONI+ANT)
- Materials: Brushed gold, platinum, subtle glass accent
- Lighting: HDRI studio with accent lights

Usage: Run this script from Blender or via bridge.
"""

import bpy
import math
from mathutils import Vector


def clear_scene():
    """Clear default scene objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Also clear any leftover data
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)


def create_gold_material():
    """Create brushed gold PBR material."""
    mat = bpy.data.materials.new(name="SovereignGold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Gold color (RGB: 212, 175, 55) -> normalized
    bsdf.inputs['Base Color'].default_value = (0.831, 0.686, 0.216, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_platinum_material():
    """Create platinum/silver PBR material."""
    mat = bpy.data.materials.new(name="SovereignPlatinum")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear and recreate properly
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    bsdf.inputs['Base Color'].default_value = (0.85, 0.85, 0.88, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.15
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_accent_material():
    """Create deep blue accent material."""
    mat = bpy.data.materials.new(name="SovereignAccent")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear and recreate properly
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    bsdf.inputs['Base Color'].default_value = (0.02, 0.08, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Emission Color'].default_value = (0.02, 0.08, 0.25, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.3
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_text_3d(text, location=(0, 0, 0)):
    """Create 3D text object."""
    # Create text data
    font_data = bpy.data.curves.new(name=f"TextCurve_{text}", type='FONT')
    font_data.body = text
    font_data.extrude = 0.15
    font_data.bevel_depth = 0.02
    font_data.bevel_resolution = 4
    font_data.align_x = 'CENTER'
    font_data.align_y = 'CENTER'
    
    # Create object
    text_obj = bpy.data.objects.new(f"Text_{text}", font_data)
    bpy.context.collection.objects.link(text_obj)
    
    text_obj.location = location
    text_obj.rotation_euler = (math.radians(90), 0, 0)
    
    return text_obj


def create_triad_symbol(location=(0, 0, 0)):
    """Create the Tríade symbol (three interlocking tori)."""
    tori = []
    
    # Three tori representing UBIE, ONI, ANT
    angles = [0, 120, 240]  # Degrees
    colors = [
        (0.2, 0.5, 0.9, 1.0),   # Blue (UBIE - Mind)
        (0.9, 0.3, 0.1, 1.0),   # Orange (ONI - Hands)
        (0.1, 0.8, 0.3, 1.0),   # Green (ANT - Forge)
    ]
    
    radius_major = 0.4
    radius_minor = 0.08
    
    for i, (angle, color) in enumerate(zip(angles, colors)):
        # Create torus
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius_major,
            minor_radius=radius_minor,
            location=location
        )
        torus = bpy.context.active_object
        torus.name = f"Triad_Ring_{i}"
        
        # Rotate and offset
        torus.rotation_euler = (math.radians(60), 0, math.radians(angle))
        
        # Create material for this ring (properly with nodes)
        mat = bpy.data.materials.new(name=f"TriadColor_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes and create fresh
        for node in nodes:
            nodes.remove(node)
        
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.2
        bsdf.inputs['Emission Color'].default_value = color
        bsdf.inputs['Emission Strength'].default_value = 0.5
        
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        torus.data.materials.append(mat)
        tori.append(torus)
    
    return tori


def setup_camera():
    """Create and position camera for logo shot."""
    # Create camera data
    cam_data = bpy.data.cameras.new(name="LogoCamera")
    cam_data.lens = 85  # Portrait lens for nice perspective
    
    # Create camera object
    cam_obj = bpy.data.objects.new("LogoCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    # Position camera
    cam_obj.location = (0, -6, 2)
    cam_obj.rotation_euler = (math.radians(75), 0, 0)
    
    # Set as active camera
    bpy.context.scene.camera = cam_obj
    
    return cam_obj


def setup_lighting():
    """Create professional 3-point lighting."""
    lights = []
    
    # Key Light (warm, main illumination)
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 500
    key_data.color = (1.0, 0.95, 0.9)  # Warm
    key_data.size = 3
    
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (4, -3, 4)
    key_obj.rotation_euler = (math.radians(45), 0, math.radians(30))
    lights.append(key_obj)
    
    # Fill Light (cool, softer)
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 200
    fill_data.color = (0.9, 0.95, 1.0)  # Cool
    fill_data.size = 4
    
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-4, -2, 3)
    fill_obj.rotation_euler = (math.radians(50), 0, math.radians(-30))
    lights.append(fill_obj)
    
    # Rim/Back Light (dramatic edge)
    rim_data = bpy.data.lights.new(name="RimLight", type='SPOT')
    rim_data.energy = 800
    rim_data.color = (1.0, 0.9, 0.8)
    rim_data.spot_size = math.radians(45)
    
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (0, 4, 3)
    rim_obj.rotation_euler = (math.radians(120), 0, 0)
    lights.append(rim_obj)
    
    return lights


def setup_background():
    """Create gradient background plane."""
    # Create plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 5, -1))
    bg = bpy.context.active_object
    bg.name = "Background"
    bg.rotation_euler = (math.radians(-90), 0, 0)
    
    # Create gradient material
    mat = bpy.data.materials.new(name="BackgroundGradient")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear and rebuild
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (400, 0)
    emission.inputs['Strength'].default_value = 0.5
    
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.location = (0, 0)
    
    coord = nodes.new('ShaderNodeTexCoord')
    coord.location = (-200, 0)
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.05, 1.0)  # Dark blue
    ramp.color_ramp.elements[1].color = (0.08, 0.08, 0.12, 1.0)  # Light navy
    
    links.new(coord.outputs['UV'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    bg.data.materials.append(mat)
    return bg


def setup_render_settings():
    """Configure render settings for quality output."""
    scene = bpy.context.scene
    
    # Use EEVEE for fast high-quality preview (CYCLES not available in this config)
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # EEVEE settings
    scene.eevee.taa_render_samples = 128
    
    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Film
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'


def main():
    """Main function to create the Sovereign logo."""
    print("=" * 60)
    print("SOVEREIGN LOGO GENERATOR")
    print("Creating professional 3D logo...")
    print("=" * 60)
    
    # Step 1: Clear scene
    print("[1/8] Clearing scene...")
    clear_scene()
    
    # Step 2: Create materials
    print("[2/8] Creating materials...")
    gold_mat = create_gold_material()
    platinum_mat = create_platinum_material()
    accent_mat = create_accent_material()
    
    # Step 3: Create main text
    print("[3/8] Creating 3D text 'SOVEREIGN'...")
    text_obj = create_text_3d("SOVEREIGN", location=(0, 0, 0))
    text_obj.data.materials.append(gold_mat)
    
    # Step 4: Create tríade symbol
    print("[4/8] Creating Tríade symbol...")
    tori = create_triad_symbol(location=(0, 0, 0.8))
    
    # Step 5: Setup camera
    print("[5/8] Setting up camera...")
    camera = setup_camera()
    
    # Step 6: Setup lighting
    print("[6/8] Setting up professional lighting...")
    lights = setup_lighting()
    
    # Step 7: Setup background
    print("[7/8] Creating background...")
    bg = setup_background()
    
    # Step 8: Configure render
    print("[8/8] Configuring render settings...")
    setup_render_settings()
    
    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 1
    
    print("=" * 60)
    print("✅ SOVEREIGN LOGO CREATED SUCCESSFULLY!")
    print("   Text: 'SOVEREIGN' with gold metallic finish")
    print("   Symbol: Tríade (3 colored rings)")
    print("   Lighting: 3-point professional setup")
    print("   Ready to render or adjust in viewport!")
    print("=" * 60)
    
    # Switch to rendered view
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    break


# Execute
if __name__ == "__main__":
    main()
