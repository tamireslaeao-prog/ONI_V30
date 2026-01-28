import bpy
import math
import os

# --- CONFIG ---
OUTPUT_BLEND = r"C:\Users\user\Desktop\ONI_V30\temp\rick_funko_procedural.blend"
OUTPUT_IMAGE = r"C:\Users\user\Desktop\ONI_V30\temp\rick_funko_render.png"

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_material(name, color, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

def create_rick_model():
    # Materials
    mat_skin = create_material("Skin", (0.8, 0.75, 0.7, 1.0)) # Pale Skin
    mat_hair = create_material("Hair", (0.4, 0.6, 0.9, 1.0)) # Light Blue
    mat_coat = create_material("Coat", (0.95, 0.95, 0.95, 1.0)) # White
    mat_shirt = create_material("Shirt", (0.2, 0.6, 0.6, 1.0)) # Teal
    mat_pants = create_material("Pants", (0.3, 0.25, 0.2, 1.0)) # Brown
    mat_eyes = create_material("Eyes", (0.05, 0.05, 0.05, 1.0), 0.1) # Black Glossy
    mat_brow = create_material("Brow", (0.4, 0.6, 0.9, 1.0)) # Blue Brow

    # --- HEAD ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.6))
    head = bpy.context.active_object
    head.name = "Rick_Head"
    head.scale = (1.1, 1.0, 0.9)
    # Rounded Funko Shape
    mod_sub = head.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_sub.levels = 3
    mod_sub.render_levels = 3
    # Apply Scale for consistent bevels/mods
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    head.data.materials.append(mat_skin)
    bpy.ops.object.shade_smooth()

    # --- EYES ---
    # Left
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.35, -0.42, 1.55))
    eye_l = bpy.context.active_object
    eye_l.data.materials.append(mat_eyes)
    bpy.ops.object.shade_smooth()
    # Right
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(-0.35, -0.42, 1.55))
    eye_r = bpy.context.active_object
    eye_r.data.materials.append(mat_eyes)
    bpy.ops.object.shade_smooth()

    # --- UNIBROW (Iconic) ---
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(0, -0.45, 1.75))
    brow = bpy.context.active_object
    brow.rotation_euler = (0, math.radians(90), 0)
    # Curve it slightly (Simple bend using proportional editing logic approach or just multiple segments)
    # Using simple geometry for speed
    brow.scale = (1.0, 1.0, 1.0) 
    brow.data.materials.append(mat_brow)

    # --- NOSE ---
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, -0.45, 1.45))
    nose = bpy.context.active_object
    nose.scale = (1, 0.5, 1) # Flattened
    nose.data.materials.append(mat_skin)
    bpy.ops.object.shade_smooth()

    # --- HAIR (The Spikes) ---
    spikes = []
    # Radial array of cones
    num_spikes = 9
    for i in range(num_spikes):
        angle = (math.pi / (num_spikes - 1)) * i # 0 to PI (180 deg around top)
        # Remap to fit head curve: spread across top/back
        # Heuristic placement
        x = -0.9 + (i * 0.22)
        z = 2.0 + math.sin(i*0.5)*0.2
        y = 0.0
        
        # Center Spike
        if i == 4: z = 2.3
        
        bpy.ops.mesh.primitive_cone_add(radius1=0.25, depth=1.2, location=(x, -0.1, z))
        spike = bpy.context.active_object
        
        # Rotate to point out
        rot_z = (i - 4) * -0.2
        spike.rotation_euler = (math.radians(-15), 0, rot_z)
        
        spike.data.materials.append(mat_hair)
        spikes.append(spike)

    # --- BODY ---
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, 0, 0.6))
    body = bpy.context.active_object
    body.scale = (0.8, 0.5, 1.2)
    body.data.materials.append(mat_shirt)
    
    # --- LAB COAT ---
    # Create coat overlapping body
    bpy.ops.mesh.primitive_cube_add(size=0.62, location=(0, 0, 0.6))
    coat = bpy.context.active_object
    coat.scale = (0.85, 0.55, 1.1)
    coat.data.materials.append(mat_coat)
    # Open front (Boolean or just texture hack? Let's use geometry scale)
    # Actually just coloring the front face teal would be easier, but let's separate geometry
    # Lets keep simple overlapping blocks
    
    # --- ARMS ---
    # Left Arm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.7, location=(0.55, 0, 0.8))
    arm_l = bpy.context.active_object
    arm_l.rotation_euler = (0, math.radians(45), 0) # T-Pose down
    arm_l.data.materials.append(mat_skin) # Hands are skin (actually coat usually covers arms)
    # Coat Sleeve
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.5, location=(0.5, 0, 0.9))
    sleeve_l = bpy.context.active_object
    sleeve_l.rotation_euler = (0, math.radians(45), 0)
    sleeve_l.data.materials.append(mat_coat)

    # Right Arm (Holding Flask)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.7, location=(-0.55, 0, 0.8))
    arm_r = bpy.context.active_object
    arm_r.rotation_euler = (0, math.radians(-45), 0)
    arm_r.data.materials.append(mat_skin)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.5, location=(-0.5, 0, 0.9))
    sleeve_r = bpy.context.active_object
    sleeve_r.rotation_euler = (0, math.radians(-45), 0)
    sleeve_r.data.materials.append(mat_coat)
    
    # --- FLASK ---
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.25, location=(-0.7, 0.1, 0.6))
    flask = bpy.context.active_object
    flask_mat = create_material("Flask", (0.8, 0.8, 0.8, 1.0), 0.2)
    flask.data.materials.append(flask_mat)
    
    # --- LEGS ---
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0.2, 0, 0.1))
    leg_l = bpy.context.active_object
    leg_l.scale = (1, 1, 3)
    leg_l.data.materials.append(mat_pants)
    
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(-0.2, 0, 0.1))
    leg_r = bpy.context.active_object
    leg_r.scale = (1, 1, 3)
    leg_r.data.materials.append(mat_pants)

    # --- SHOES ---
    bpy.ops.mesh.primitive_cube_add(size=0.25, location=(0.2, 0.05, -0.2))
    shoe_l = bpy.context.active_object
    shoe_l.scale = (1, 1.5, 0.5)
    mat_shoe = create_material("Shoe", (0.1, 0.1, 0.1, 1.0))
    shoe_l.data.materials.append(mat_shoe)
    
    bpy.ops.mesh.primitive_cube_add(size=0.25, location=(-0.2, 0.05, -0.2))
    shoe_r = bpy.context.active_object
    shoe_r.scale = (1, 1.5, 0.5)
    shoe_r.data.materials.append(mat_shoe)

    # Parent all to Head/Body? No, just keep as scene objects

def setup_lighting():
    # Key Light
    bpy.ops.object.light_add(type='AREA', location=(3, -5, 4))
    light = bpy.context.active_object
    light.data.energy = 800
    
    # Rim Light
    bpy.ops.object.light_add(type='POINT', location=(-3, 3, 3))
    light = bpy.context.active_object
    light.data.energy = 500
    light.data.color = (0.0, 0.5, 1.0) # Sci-fi Blue Rim

def setup_camera():
    bpy.ops.object.camera_add(location=(0, -4.5, 1.5))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(85), 0, 0)
    bpy.context.scene.camera = cam

def cleanup_collections():
    # Move everything to a collection
    pass

if __name__ == "__main__":
    clean_scene()
    
    # Setup EEVEE Next
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    
    create_rick_model()
    setup_lighting()
    setup_camera()
    
    # Save Render
    scene.render.filepath = OUTPUT_IMAGE
    bpy.ops.render.render(write_still=True)
    
    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
