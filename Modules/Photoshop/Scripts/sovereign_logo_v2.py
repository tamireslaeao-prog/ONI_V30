"""
SOVEREIGN LOGO V2 - PREMIUM EDITION
Creates a highly sophisticated 3D logo with elaborate geometry and materials.

Design Concept V2:
- Central Shield with crown motif
- "SOVEREIGN" text with premium bevel and gold gradient
- Three gems (representing UBIE/ONI/ANT) embedded in shield
- Ornate frame with decorative elements
- HDRI lighting for realistic reflections
- Metallic materials with proper IOR and anisotropy
"""

import bpy
import math
from mathutils import Vector


def clear_scene():
    """Clear all objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)


# =============================================================================
# PREMIUM MATERIALS
# =============================================================================

def create_gold_premium():
    """Create premium gold material with realistic properties."""
    mat = bpy.data.materials.new(name="PremiumGold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    # Premium gold color (warm, rich)
    bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)  # Rich gold
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Specular IOR Level'].default_value = 0.8
    bsdf.inputs['Coat Weight'].default_value = 0.3
    bsdf.inputs['Coat Roughness'].default_value = 0.1
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_dark_steel():
    """Create dark brushed steel material."""
    mat = bpy.data.materials.new(name="DarkSteel")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.18, 1.0)  # Dark gunmetal
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_gem_material(color, name):
    """Create a gem/crystal material with emission."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 2.4  # Diamond-like
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = 2.0
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


# =============================================================================
# GEOMETRY
# =============================================================================

def create_shield():
    """Create an ornate shield shape."""
    # Create base shield using a modified cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    shield = bpy.context.active_object
    shield.name = "Shield_Base"
    
    # Scale to shield proportions
    shield.scale = (2.0, 0.2, 2.5)
    
    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Add bevel modifier for rounded edges
    bevel = shield.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.08
    bevel.segments = 4
    
    # Add subdivision for smoothness
    subsurf = shield.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    return shield


def create_crown():
    """Create a crown symbol on top of shield."""
    crown_parts = []
    
    # Base ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.5,
        minor_radius=0.08,
        location=(0, -0.15, 1.5)
    )
    base = bpy.context.active_object
    base.name = "Crown_Base"
    base.rotation_euler = (math.radians(90), 0, 0)
    crown_parts.append(base)
    
    # Crown points (5 spikes)
    for i in range(5):
        angle = (i / 5) * 2 * math.pi - math.pi/2
        x = 0.4 * math.cos(angle)
        z = 1.5 + 0.4 * math.sin(angle) + 0.3
        
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.08,
            radius2=0.02,
            depth=0.4,
            location=(x, -0.15, z)
        )
        spike = bpy.context.active_object
        spike.name = f"Crown_Spike_{i}"
        spike.rotation_euler = (0, 0, 0)
        crown_parts.append(spike)
    
    return crown_parts


def create_gems():
    """Create three gems representing the personas."""
    gems = []
    
    gem_configs = [
        {"pos": (-0.6, -0.12, 0.3), "color": (0.1, 0.4, 0.9, 1.0), "name": "Gem_UBIE"},  # Sapphire
        {"pos": (0.0, -0.12, -0.3), "color": (0.9, 0.5, 0.1, 1.0), "name": "Gem_ONI"},   # Amber
        {"pos": (0.6, -0.12, 0.3), "color": (0.1, 0.8, 0.3, 1.0), "name": "Gem_ANT"},    # Emerald
    ]
    
    for config in gem_configs:
        # Create gem (octahedron-like)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=0.15,
            location=config["pos"]
        )
        gem = bpy.context.active_object
        gem.name = config["name"]
        
        # Create and assign material
        mat = create_gem_material(config["color"], f"Mat_{config['name']}")
        gem.data.materials.append(mat)
        
        gems.append(gem)
    
    return gems


def create_text_premium():
    """Create premium 3D text with elaborate bevel."""
    font_data = bpy.data.curves.new(name="SovereignText", type='FONT')
    font_data.body = "SOVEREIGN"
    font_data.extrude = 0.12
    font_data.bevel_depth = 0.025
    font_data.bevel_resolution = 6
    font_data.align_x = 'CENTER'
    font_data.align_y = 'CENTER'
    font_data.size = 0.45
    
    # Offset for tracking (letter spacing)
    font_data.space_character = 1.1
    
    text_obj = bpy.data.objects.new("Text_SOVEREIGN", font_data)
    bpy.context.collection.objects.link(text_obj)
    
    text_obj.location = (0, -0.25, -1.8)
    text_obj.rotation_euler = (math.radians(90), 0, 0)
    
    return text_obj


def create_ornate_frame():
    """Create decorative frame around the shield."""
    frame_parts = []
    
    # Outer ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=2.8,
        minor_radius=0.1,
        location=(0, -0.1, 0)
    )
    ring = bpy.context.active_object
    ring.name = "Frame_Ring"
    ring.rotation_euler = (math.radians(90), 0, 0)
    frame_parts.append(ring)
    
    # Decorative corners (4 flourishes)
    corners = [
        (2.2, -0.1, 2.2),
        (-2.2, -0.1, 2.2),
        (2.2, -0.1, -2.2),
        (-2.2, -0.1, -2.2),
    ]
    
    for i, pos in enumerate(corners):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.2,
            location=pos
        )
        flourish = bpy.context.active_object
        flourish.name = f"Frame_Corner_{i}"
        flourish.scale = (1.5, 0.5, 1.5)
        frame_parts.append(flourish)
    
    return frame_parts


def create_pedestal():
    """Create a pedestal/base for the logo."""
    # Main platform
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3.5,
        depth=0.3,
        location=(0, 0.3, -3)
    )
    base = bpy.context.active_object
    base.name = "Pedestal_Base"
    base.rotation_euler = (math.radians(90), 0, 0)
    
    # Add bevel
    bevel = base.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 3
    
    return base


# =============================================================================
# LIGHTING & ENVIRONMENT
# =============================================================================

def setup_premium_lighting():
    """Create premium 3-point lighting setup."""
    lights = []
    
    # Key Light - warm, strong
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 800
    key_data.color = (1.0, 0.95, 0.85)
    key_data.size = 4
    
    key = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.collection.objects.link(key)
    key.location = (5, -5, 6)
    key.rotation_euler = (math.radians(55), 0, math.radians(45))
    lights.append(key)
    
    # Fill Light - cool, softer
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 300
    fill_data.color = (0.85, 0.9, 1.0)
    fill_data.size = 6
    
    fill = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (-5, -3, 4)
    fill.rotation_euler = (math.radians(60), 0, math.radians(-40))
    lights.append(fill)
    
    # Rim Light - dramatic back light
    rim_data = bpy.data.lights.new(name="RimLight", type='SPOT')
    rim_data.energy = 1500
    rim_data.color = (1.0, 0.9, 0.7)
    rim_data.spot_size = math.radians(60)
    
    rim = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.collection.objects.link(rim)
    rim.location = (0, 6, 4)
    rim.rotation_euler = (math.radians(110), 0, 0)
    lights.append(rim)
    
    # Ground bounce
    bounce_data = bpy.data.lights.new(name="BounceLight", type='AREA')
    bounce_data.energy = 150
    bounce_data.color = (0.7, 0.7, 0.8)
    bounce_data.size = 8
    
    bounce = bpy.data.objects.new("BounceLight", bounce_data)
    bpy.context.collection.objects.link(bounce)
    bounce.location = (0, 0, -5)
    bounce.rotation_euler = (math.radians(-90), 0, 0)
    lights.append(bounce)
    
    return lights


def setup_world():
    """Setup world with gradient background."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("SovereignWorld")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (600, 0)
    
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (300, 0)
    bg.inputs['Strength'].default_value = 0.3
    
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.location = (0, 0)
    
    coord = nodes.new('ShaderNodeTexCoord')
    coord.location = (-200, 0)
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (150, 0)
    ramp.color_ramp.elements[0].color = (0.01, 0.01, 0.02, 1.0)  # Near black
    ramp.color_ramp.elements[1].color = (0.05, 0.05, 0.08, 1.0)  # Dark blue
    
    links.new(coord.outputs['Generated'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_camera():
    """Setup camera for hero shot."""
    cam_data = bpy.data.cameras.new(name="HeroCamera")
    cam_data.lens = 85
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 2.8
    
    cam = bpy.data.objects.new("HeroCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    
    cam.location = (0, -10, 2)
    cam.rotation_euler = (math.radians(80), 0, 0)
    
    bpy.context.scene.camera = cam
    
    return cam


def setup_render():
    """Configure render settings."""
    scene = bpy.context.scene
    
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 256
    
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("SOVEREIGN LOGO V2 - PREMIUM EDITION")
    print("Creating sophisticated 3D logo...")
    print("=" * 70)
    
    # Clear
    print("[1/10] Clearing scene...")
    clear_scene()
    
    # Materials
    print("[2/10] Creating premium materials...")
    gold_mat = create_gold_premium()
    steel_mat = create_dark_steel()
    
    # Shield
    print("[3/10] Creating ornate shield...")
    shield = create_shield()
    shield.data.materials.append(steel_mat)
    
    # Crown
    print("[4/10] Creating crown...")
    crown_parts = create_crown()
    for part in crown_parts:
        part.data.materials.append(gold_mat)
    
    # Gems
    print("[5/10] Creating persona gems...")
    gems = create_gems()
    
    # Text
    print("[6/10] Creating premium text...")
    text = create_text_premium()
    text.data.materials.append(gold_mat)
    
    # Frame
    print("[7/10] Creating ornate frame...")
    frame_parts = create_ornate_frame()
    for part in frame_parts:
        part.data.materials.append(gold_mat)
    
    # Pedestal
    print("[8/10] Creating pedestal...")
    pedestal = create_pedestal()
    pedestal.data.materials.append(steel_mat)
    
    # Lighting & Environment
    print("[9/10] Setting up premium lighting...")
    setup_premium_lighting()
    setup_world()
    setup_camera()
    
    # Render
    print("[10/10] Configuring render...")
    setup_render()
    
    # Set viewport to material preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    break
    
    print("=" * 70)
    print("✅ SOVEREIGN LOGO V2 CREATED!")
    print("   Shield with crown motif")
    print("   Three persona gems (Sapphire, Amber, Emerald)")
    print("   Premium gold and gunmetal materials")
    print("   Professional 4-point lighting")
    print("=" * 70)


if __name__ == "__main__":
    main()
