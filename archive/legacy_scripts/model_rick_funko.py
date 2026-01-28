import bpy
import math

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_color_mat(name, hex_color, roughness=0.5, metallic=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Hex to RGB
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    bsdf.inputs['Base Color'].default_value = (rgb[0], rgb[1], rgb[2], 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

def create_rick():
    # --- MATERIALS ---
    mat_skin = create_color_mat("Rick_Skin", "#F2C4B1", 0.4)
    mat_hair = create_color_mat("Rick_Hair", "#A3D8F5", 0.5) # Light Blue
    mat_shirt = create_color_mat("Rick_Shirt", "#00FFFF", 0.6) # Cyan
    mat_coat = create_color_mat("Rick_Coat", "#FFFFFF", 0.8)
    mat_pants = create_color_mat("Rick_Pants", "#4B3621", 0.7)
    mat_shoes = create_color_mat("Rick_Shoes", "#111111", 0.3)
    mat_eyes = create_color_mat("Rick_Eyes", "#000000", 0.9, 0.0) # Shiny black
    mat_flask = create_color_mat("Rick_Flask", "#C0C0C0", 0.2, 0.8) # Silver
    mat_gold = create_color_mat("Rick_Buckle", "#FFD700", 0.3, 0.9)
    mat_drool = create_color_mat("Rick_Drool", "#00FF00", 0.1)
    
    # 1. HEAD (Squircle)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 2.8))
    head = bpy.context.active_object
    head.name = "Head"
    head.data.materials.append(mat_skin)
    
    # Subsurf to make it squircle
    mod_sub = head.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_sub.levels = 3
    mod_sub.render_levels = 3
    # Cast modifier to Sphere factor 0.6 for that Funko shape
    mod_cast = head.modifiers.new(name="Cast", type='CAST')
    mod_cast.factor = 0.6
    mod_cast.radius = 1.2
    
    # 2. HAIR (Spikes)
    # 9 Cones radiating
    hair_positions = [
        (0, 0, 1.2), # Top center
        (0.8, 0, 0.9), # Right
        (-0.8, 0, 0.9), # Left
        (0.5, 0.6, 1.0), # Back R
        (-0.5, 0.6, 1.0), # Back L
        (1.2, 0, 0.4), # Side R
        (-1.2, 0, 0.4), # Side L
        (0, 0.8, 0.8), # Back Center
        (0, -0.2, 1.3) # Front Top
    ]
    
    for i, pos in enumerate(hair_positions):
        bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0, depth=1.5, location=(0,0,0))
        spike = bpy.context.active_object
        spike.name = f"Hair_Spike_{i}"
        
        # Position relative to head center
        loc_x = head.location.x + pos[0]
        loc_y = head.location.y + pos[1]
        loc_z = head.location.z + pos[2]
        spike.location = (loc_x, loc_y, loc_z)
        
        # Rotate to point out from head center approx
        # Simple Math: atan2
        dx = pos[0]
        dy = pos[1]
        dz = pos[2]
        # Align Z to vector
        # Using simple look_at logic via constraint or just random rotations for "messy hair"
        # Rick's hair is "Star" shaped.
        
        # Manual rotations for simplicity in script
        if i==0: spike.rotation_euler = (0,0,0) # Top
        elif i==1: spike.rotation_euler = (0, math.radians(45), 0)
        elif i==2: spike.rotation_euler = (0, math.radians(-45), 0)
        elif i==3: spike.rotation_euler = (math.radians(-30), math.radians(30), 0)
        elif i==4: spike.rotation_euler = (math.radians(-30), math.radians(-30), 0)
        elif i==5: spike.rotation_euler = (0, math.radians(80), 0)
        elif i==6: spike.rotation_euler = (0, math.radians(-80), 0)
        elif i==7: spike.rotation_euler = (math.radians(-45), 0, 0)
        elif i==8: spike.rotation_euler = (math.radians(20), 0, 0)

        spike.data.materials.append(mat_hair)
        spike.parent = head

    # 3. EYES
    eye_offset_x = 0.5
    eye_offset_y = -0.85 # Front
    eye_offset_z = 0.0
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(eye_offset_x, eye_offset_y, eye_offset_z))
    eye_r = bpy.context.active_object
    eye_r.name = "Eye_R"
    eye_r.data.materials.append(mat_eyes)
    eye_r.parent = head
    # Flatten slightly
    eye_r.scale = (1, 0.6, 1)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(-eye_offset_x, eye_offset_y, eye_offset_z))
    eye_l = bpy.context.active_object
    eye_l.name = "Eye_L"
    eye_l.data.materials.append(mat_eyes)
    eye_l.parent = head
    eye_l.scale = (1, 0.6, 1)

    # 4. NOSE
    bpy.ops.mesh.primitive_cone_add(radius1=0.1, radius2=0, depth=0.3, location=(0, -0.9, -0.2))
    nose = bpy.context.active_object
    nose.rotation_euler = (math.radians(-90), 0, 0)
    nose.data.materials.append(mat_skin)
    nose.parent = head

    # 5. UNIBROW
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.2, location=(0, -0.9, 0.45))
    brow = bpy.context.active_object
    brow.rotation_euler = (0, math.radians(90), 0)
    # Bend it? SimpleDeform bend
    mod_bend = brow.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
    mod_bend.deform_method = 'BEND'
    mod_bend.angle = math.radians(30)
    mod_bend.deform_axis = 'Z'
    brow.data.materials.append(mat_hair)
    brow.parent = head

    # 6. DROOL
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.2, -0.9, -0.6))
    drool = bpy.context.active_object
    drool.name = "Drool"
    drool.data.materials.append(mat_drool)
    drool.parent = head
    
    # 7. BODY (Torso)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.2, location=(0, 0, 1.2))
    torso = bpy.context.active_object
    torso.name = "Torso"
    torso.data.materials.append(mat_shirt)
    
    # Lab Coat (Duplicate torso, scale up, white)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.1, location=(0, 0, 1.25))
    coat = bpy.context.active_object
    coat.name = "Lab_Coat"
    coat.data.materials.append(mat_coat)
    # Cut front open? Boolean or just texture. Let's assume solid for Funko look usually simplified.
    # Actually, let's squish it to look like open coat
    coat.scale = (1, 0.8, 1) 

    # 8. LEGS
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.8, location=(0.2, 0, 0.4))
    leg_r = bpy.context.active_object
    leg_r.data.materials.append(mat_pants)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.8, location=(-0.2, 0, 0.4))
    leg_l = bpy.context.active_object
    leg_l.data.materials.append(mat_pants)

    # 9. SHOES
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.2, -0.1, 0))
    shoe_r = bpy.context.active_object
    shoe_r.scale = (1, 1.5, 0.6)
    shoe_r.data.materials.append(mat_shoes)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(-0.2, -0.1, 0))
    shoe_l = bpy.context.active_object
    shoe_l.scale = (1, 1.5, 0.6)
    shoe_l.data.materials.append(mat_shoes)

    # 10. ARMS
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, location=(0.55, 0, 1.4))
    arm_r = bpy.context.active_object
    arm_r.rotation_euler = (0, math.radians(20), 0)
    arm_r.data.materials.append(mat_coat)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, location=(-0.55, 0, 1.4))
    arm_l = bpy.context.active_object
    arm_l.rotation_euler = (0, math.radians(-20), 0)
    arm_l.data.materials.append(mat_coat)
    
    # HANDS
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.65, 0, 0.9))
    hand_r = bpy.context.active_object
    hand_r.data.materials.append(mat_skin)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(-0.65, 0, 0.9))
    hand_l = bpy.context.active_object
    hand_l.data.materials.append(mat_skin)

    # 11. FLASK (In Right Hand)
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.65, -0.1, 0.9))
    flask = bpy.context.active_object
    flask.scale = (0.8, 0.3, 1)
    flask.rotation_euler = (math.radians(20), 0, 0)
    flask.data.materials.append(mat_flask)

    # Setup Camera
    bpy.ops.object.camera_add(location=(0, -6, 2.5))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(85), 0, 0)
    bpy.context.scene.camera = cam
    
    # Setup Light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    light = bpy.context.active_object
    light.data.energy = 5
    
    # Area fill
    bpy.ops.object.light_add(type='AREA', location=(-3, -3, 2))
    fill = bpy.context.active_object
    fill.data.energy = 200

def log(msg):
    with open(r"C:\Users\user\Desktop\ONIV24\blender_debug_log.txt", "a") as f:
        f.write(msg + "\n")

def main():
    try:
        log("Script start.")
        clean_scene()
        log("Scene cleaned.")
        create_rick()
        log("Rick created.")
        
        # Save file to verify
        save_path = r"C:\Users\user\Desktop\ONIV24\temp\mkt\blender\rick_funko_v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=save_path)
        log(f"Saved to {save_path}")
        
    except Exception as e:
        log(f"ERROR: {str(e)}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
