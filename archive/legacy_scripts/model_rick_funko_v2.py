import bpy
import math

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def log(msg):
    with open(r"C:\Users\user\Desktop\ONIV24\blender_debug_log.txt", "a") as f:
        f.write(msg + "\n")

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
    
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    bsdf.inputs['Base Color'].default_value = (rgb[0], rgb[1], rgb[2], 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

def create_rick_v2():
    # --- MATERIALS ---
    mat_skin = create_color_mat("Rick_Skin", "#F2C4B1", 0.4)
    mat_hair = create_color_mat("Rick_Hair", "#A3D8F5", 0.5)
    mat_shirt = create_color_mat("Rick_Shirt", "#00FFFF", 0.6)
    mat_coat = create_color_mat("Rick_Coat", "#FFFFFF", 0.9)
    mat_pants = create_color_mat("Rick_Pants", "#4B3621", 0.7)
    mat_shoes = create_color_mat("Rick_Shoes", "#111111", 0.3)
    mat_eyes = create_color_mat("Rick_Eyes", "#000000", 0.1)
    mat_flask = create_color_mat("Rick_Flask", "#C0C0C0", 0.2, 0.8)
    mat_buckle = create_color_mat("Rick_Buckle", "#FFD700", 0.3, 0.9)
    mat_drool = create_color_mat("Rick_Drool", "#00FF00", 0.1)
    
    # === HEAD ===
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 2.8))
    head = bpy.context.active_object
    head.name = "Head_Base"
    
    # Squircle Modifier
    mod_sub = head.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_sub.levels = 4
    mod_cast = head.modifiers.new(name="Cast", type='CAST')
    mod_cast.factor = 0.65
    mod_cast.radius = 1.3
    bpy.ops.object.shade_smooth()
    head.data.materials.append(mat_skin)

    # === HAIR (Integrated) ===
    # Create hair cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.05, location=(0, 0, 2.9))
    hair_cap = bpy.context.active_object
    hair_cap.name = "Hair_Mass"
    
    # Spikes
    hair_positions = [
        (0, 0, 1.2, 0),             # Top
        (0.8, 0, 0.9, -45),         # R
        (-0.8, 0, 0.9, 45),         # L
        (1.1, 0, 0.2, -80),         # Side R
        (-1.1, 0, 0.2, 80),         # Side L
        (0.6, 0.6, 1.0, -30),       # Back R
        (-0.6, 0.6, 1.0, 30),       # Back L
        (0, 0.8, 0.8, 0),           # Back C
        (0, -0.3, 1.3, 20)          # Front Top
    ]
    
    spikes = []
    for i, (x, y, z, rot) in enumerate(hair_positions):
        bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0, depth=1.6)
        spike = bpy.context.active_object
        
        # calc world pos relative to head center (approx)
        hx, hy, hz = 0, 0, 2.8
        spike.location = (hx+x, hy+y, hz+z)
        
        # Rotation 
        spike.rotation_euler = (math.radians(rot if i==8 else 0), math.radians(rot if i!=8 else 0), 0)
        
        spikes.append(spike)
    
    # Join all hair parts
    ctx = bpy.context.copy()
    ctx['active_object'] = hair_cap
    ctx['selected_editable_objects'] = spikes + [hair_cap]
    bpy.ops.object.join(ctx)
    
    # Remesh to look like one piece
    mod_remesh = hair_cap.modifiers.new(name="Remesh", type='REMESH')
    mod_remesh.mode = 'VOXEL'
    mod_remesh.voxel_size = 0.05
    mod_remesh.adaptivity = 0.1
    
    mod_smooth = hair_cap.modifiers.new(name="Smooth", type='CORRECTIVE_SMOOTH')
    mod_smooth.iterations = 20
    
    hair_cap.data.materials.append(mat_hair)
    hair_cap.parent = head

    # === FACE DETAILS (V2) ===
    # Eyes
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0.5, -0.85, 2.8))
    eye_r = bpy.context.active_object
    eye_r.scale = (1, 0.5, 1)
    eye_r.data.materials.append(mat_eyes)
    eye_r.parent = head
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(-0.5, -0.85, 2.8))
    eye_l = bpy.context.active_object
    eye_l.scale = (1, 0.5, 1)
    eye_l.data.materials.append(mat_eyes)
    eye_l.parent = head
    
    # Eye Bags (Torus)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.02, location=(0.5, -0.87, 2.7))
    bag_r = bpy.context.active_object
    bag_r.scale = (1, 0.5, 0.5) 
    bag_r.rotation_euler = (math.radians(90), 0, 0)
    bag_r.data.materials.append(mat_skin) 
    bag_r.parent = head

    bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.02, location=(-0.5, -0.87, 2.7))
    bag_l = bpy.context.active_object
    bag_l.scale = (1, 0.5, 0.5)
    bag_l.rotation_euler = (math.radians(90), 0, 0)
    bag_l.data.materials.append(mat_skin)
    bag_l.parent = head

    # Unibrow (V2 - Curve path for smoothness)
    bpy.ops.curve.primitive_nurbs_path_add(location=(0, -0.95, 3.3))
    brow = bpy.context.active_object
    brow.scale = (0.7, 1, 1)
    brow.data.bevel_depth = 0.06
    brow.data.materials.append(mat_hair)
    brow.parent = head

    # Mouth (Torus segment or thin cylinder)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.6, location=(0, -0.92, 2.3))
    mouth = bpy.context.active_object
    mouth.rotation_euler = (0, math.radians(90), 0)
    mouth.data.materials.append(mat_shoes) # Black
    mouth.parent = head
    
    # Drool
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.15, -0.95, 2.25))
    drool1 = bpy.context.active_object
    drool1.data.materials.append(mat_drool)
    drool1.parent = head
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.22, -0.92, 2.18))
    drool2 = bpy.context.active_object
    drool2.data.materials.append(mat_drool)
    drool2.parent = head

    # === BODY (V2) ===
    # Shirt
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.4, location=(0, 0, 1.2))
    torso = bpy.context.active_object
    torso.data.materials.append(mat_shirt)
    
    # Coat (Solid + Open Front)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=1.35, location=(0, 0, 1.25))
    coat = bpy.context.active_object
    coat.name = "Coat_Geo"
    coat.data.materials.append(mat_coat)
    
    # Cut the front open
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.5, 1.25))
    cutter = bpy.context.active_object
    cutter.scale = (0.4, 0.5, 1.5) # Width of opening
    
    mod_bool = coat.modifiers.new(name="CutFront", type='BOOLEAN')
    mod_bool.object = cutter
    mod_bool.operation = 'DIFFERENCE'
    
    # Move cutter to hidden collection or delete?
    cutter.display_type = 'WIRE'
    cutter.hide_render = True
    
    # Belt & Buckle
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0, -0.48, 0.7))
    buckle = bpy.context.active_object
    buckle.scale = (1.5, 0.5, 1)
    buckle.data.materials.append(mat_buckle)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=0.1, location=(0, 0, 0.7))
    belt = bpy.context.active_object
    belt.data.materials.append(mat_shoes) # Black belt

    # === LIMBS ===
    # Legs
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.8, location=(0.25, 0, 0.4))
    leg_r = bpy.context.active_object
    leg_r.data.materials.append(mat_pants)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.8, location=(-0.25, 0, 0.4))
    leg_l = bpy.context.active_object
    leg_l.data.materials.append(mat_pants)

    # Shoes
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.25, -0.1, 0))
    shoe_r = bpy.context.active_object
    shoe_r.scale = (1, 1.4, 0.6)
    shoe_r.data.materials.append(mat_shoes)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(-0.25, -0.1, 0))
    shoe_l = bpy.context.active_object
    shoe_l.scale = (1, 1.4, 0.6)
    shoe_l.data.materials.append(mat_shoes)
    
    # Arm R (With Flask)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, location=(0.65, 0, 1.3))
    arm_r = bpy.context.active_object
    arm_r.rotation_euler = (0, 0, math.radians(-15))
    arm_r.data.materials.append(mat_coat)
    
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.7, -0.2, 0.8))
    hand_r = bpy.context.active_object
    hand_r.data.materials.append(mat_skin)
    
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0.7, -0.25, 0.85))
    flask = bpy.context.active_object
    flask.scale = (0.6, 0.2, 1)
    flask.rotation_euler = (math.radians(10), 0, math.radians(-15))
    flask.data.materials.append(mat_flask)
    
    # Arm L (Hanging)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, location=(-0.65, 0, 1.3))
    arm_l = bpy.context.active_object
    arm_l.rotation_euler = (0, 0, math.radians(15))
    arm_l.data.materials.append(mat_coat)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(-0.8, 0, 0.9))
    hand_l = bpy.context.active_object
    hand_l.data.materials.append(mat_skin)

    # === LIGHTING & CAM ===
    bpy.ops.object.camera_add(location=(0, -6, 2.5))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(85), 0, 0)
    bpy.context.scene.camera = cam
    
    bpy.ops.object.light_add(type='AREA', location=(3, -4, 5))
    key = bpy.context.active_object
    key.data.energy = 500
    
    bpy.ops.object.light_add(type='POINT', location=(-2, -2, 3))
    fill = bpy.context.active_object
    fill.data.energy = 200
    fill.data.color = (0.8, 0.9, 1.0)

def main():
    try:
        log("V2 Start")
        clean_scene()
        create_rick_v2()
        log("Rick V2 Created")
        
        save_path = r"C:\Users\user\Desktop\ONIV24\temp\mkt\blender\rick_funko_v2.blend"
        bpy.ops.wm.save_as_mainfile(filepath=save_path)
        log("Saved V2")
        
    except Exception as e:
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
