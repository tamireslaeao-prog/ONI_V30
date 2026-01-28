"""
SOVEREIGN LOGO V3 - CORPORATE EDITION
Professional minimalist logo like premium office signage.

Style: Clean, elegant, corporate - think luxury brand signage.
"""

import bpy
import math
from mathutils import Vector


def clear_scene():
    """Clear all objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.curves:
        bpy.data.curves.remove(block)


def create_brushed_gold():
    """Brushed gold - realistic corporate signage material."""
    mat = bpy.data.materials.new(name="BrushedGold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    
    # Elegant gold - not too yellow, slightly muted
    bsdf.inputs['Base Color'].default_value = (0.83, 0.69, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.28  # Brushed = slightly rough
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    
    # Add anisotropic for brushed effect
    bsdf.inputs['Anisotropic'].default_value = 0.5
    bsdf.inputs['Anisotropic Rotation'].default_value = 0.0
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_matte_black():
    """Matte black background material."""
    mat = bpy.data.materials.new(name="MatteBlack")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    # Deep matte black
    bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.02, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.9
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_wall_texture():
    """Dark textured wall material."""
    mat = bpy.data.materials.new(name="DarkWall")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    # Dark charcoal with subtle texture feel
    bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.035, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_corporate_text():
    """Create clean corporate typography."""
    # Main text "SOVEREIGN"
    font_data = bpy.data.curves.new(name="LogoText", type='FONT')
    font_data.body = "SOVEREIGN"
    font_data.extrude = 0.08  # Shallow for elegance
    font_data.bevel_depth = 0.008
    font_data.bevel_resolution = 3
    font_data.align_x = 'CENTER'
    font_data.align_y = 'CENTER'
    font_data.size = 0.8
    font_data.space_character = 1.3  # Wide letter spacing = luxury feel
    
    text_obj = bpy.data.objects.new("Text_SOVEREIGN", font_data)
    bpy.context.collection.objects.link(text_obj)
    
    text_obj.location = (0, 0.05, 0)
    text_obj.rotation_euler = (math.radians(90), 0, 0)
    
    return text_obj


def create_accent_line():
    """Create elegant horizontal accent line below text."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, -0.6))
    line = bpy.context.active_object
    line.name = "AccentLine"
    line.scale = (3.5, 0.02, 0.015)
    
    # Add slight bevel
    bevel = line.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.005
    bevel.segments = 2
    
    return line


def create_symbol():
    """Create a simple, elegant 'S' monogram or abstract mark."""
    # Simple geometric symbol - three stacked horizontal lines (abstract crown/hierarchy)
    symbols = []
    
    positions = [0.2, 0, -0.2]
    widths = [0.4, 0.6, 0.4]
    
    for i, (z_offset, width) in enumerate(zip(positions, widths)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, 1.2 + z_offset))
        bar = bpy.context.active_object
        bar.name = f"Symbol_Bar_{i}"
        bar.scale = (width, 0.025, 0.04)
        
        bevel = bar.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.01
        bevel.segments = 2
        
        symbols.append(bar)
    
    return symbols


def create_backing_plate():
    """Create the dark backing plate (like office signage)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.15, 0.3))
    plate = bpy.context.active_object
    plate.name = "BackingPlate"
    plate.scale = (5.0, 0.08, 2.5)
    
    # Rounded corners
    bevel = plate.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.1
    bevel.segments = 4
    
    return plate


def create_wall():
    """Create background wall."""
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 1, 0))
    wall = bpy.context.active_object
    wall.name = "Wall"
    wall.rotation_euler = (math.radians(90), 0, 0)
    
    return wall


def setup_lighting():
    """Professional photography-style lighting."""
    lights = []
    
    # Main soft light from front-top
    main_data = bpy.data.lights.new(name="MainLight", type='AREA')
    main_data.energy = 400
    main_data.color = (1.0, 0.98, 0.95)
    main_data.size = 5
    
    main = bpy.data.objects.new("MainLight", main_data)
    bpy.context.collection.objects.link(main)
    main.location = (0, -4, 3)
    main.rotation_euler = (math.radians(50), 0, 0)
    lights.append(main)
    
    # Edge light from left
    edge_data = bpy.data.lights.new(name="EdgeLight", type='AREA')
    edge_data.energy = 200
    edge_data.color = (1.0, 0.95, 0.9)
    edge_data.size = 2
    
    edge = bpy.data.objects.new("EdgeLight", edge_data)
    bpy.context.collection.objects.link(edge)
    edge.location = (-4, -2, 1)
    edge.rotation_euler = (math.radians(60), 0, math.radians(-45))
    lights.append(edge)
    
    # Subtle fill from right
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 100
    fill_data.color = (0.95, 0.97, 1.0)
    fill_data.size = 3
    
    fill = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (4, -3, 2)
    fill.rotation_euler = (math.radians(55), 0, math.radians(30))
    lights.append(fill)
    
    return lights


def setup_camera():
    """Setup camera for product shot."""
    cam_data = bpy.data.cameras.new(name="ProductCamera")
    cam_data.lens = 85
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 4.0
    
    cam = bpy.data.objects.new("ProductCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    
    cam.location = (0, -6, 0.5)
    cam.rotation_euler = (math.radians(85), 0, 0)
    
    bpy.context.scene.camera = cam
    return cam


def setup_world():
    """Setup minimal world."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("CorporateWorld")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (400, 0)
    
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (200, 0)
    bg.inputs['Color'].default_value = (0.015, 0.015, 0.02, 1.0)
    bg.inputs['Strength'].default_value = 0.5
    
    links.new(bg.outputs['Background'], output.inputs['Surface'])


def setup_render():
    """Configure render."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 256
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'


def main():
    print("=" * 70)
    print("SOVEREIGN LOGO V3 - CORPORATE EDITION")
    print("Professional minimalist signage style")
    print("=" * 70)
    
    print("[1/9] Clearing scene...")
    clear_scene()
    
    print("[2/9] Creating materials...")
    gold = create_brushed_gold()
    black = create_matte_black()
    wall_mat = create_wall_texture()
    
    print("[3/9] Creating backing plate...")
    plate = create_backing_plate()
    plate.data.materials.append(black)
    
    print("[4/9] Creating text...")
    text = create_corporate_text()
    text.data.materials.append(gold)
    
    print("[5/9] Creating accent line...")
    line = create_accent_line()
    line.data.materials.append(gold)
    
    print("[6/9] Creating symbol...")
    symbols = create_symbol()
    for s in symbols:
        s.data.materials.append(gold)
    
    print("[7/9] Creating wall...")
    wall = create_wall()
    wall.data.materials.append(wall_mat)
    
    print("[8/9] Setting up lighting & camera...")
    setup_lighting()
    setup_camera()
    setup_world()
    
    print("[9/9] Configuring render...")
    setup_render()
    
    # Viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'
                    break
    
    print("=" * 70)
    print("✅ SOVEREIGN V3 CORPORATE LOGO CREATED")
    print("   Style: Premium office signage")
    print("   Materials: Brushed gold on matte black")
    print("   Clean typography with wide tracking")
    print("=" * 70)


if __name__ == "__main__":
    main()
