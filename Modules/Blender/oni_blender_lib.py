import bpy
import bmesh
import math
from math import pi

class BlenderController:
    """Controlador wrapper para simplificar BPY"""
    def __init__(self):
        pass

    def create_material(self, name, color, metallic=0.0, roughness=0.5, emission=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Emission Strength'].default_value = emission
        if emission > 0:
            bsdf.inputs['Emission Color'].default_value = color
        return mat

    def create_cube(self, name, loc=(0,0,0), scale=(1,1,1), mat=None):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        if mat: self._apply_mat(obj, mat)
        return obj

    def create_sphere(self, name, loc=(0,0,0), radius=1.0, mat=None):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.shade_smooth()
        if mat: self._apply_mat(obj, mat)
        return obj
    
    def create_cylinder(self, name, loc=(0,0,0), radius=1.0, depth=2.0, mat=None):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.shade_smooth()
        if mat: self._apply_mat(obj, mat)
        return obj
        
    def create_cone(self, name, loc=(0,0,0), radius=1.0, depth=2.0, mat=None):
        bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0, depth=depth, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.shade_smooth()
        if mat: self._apply_mat(obj, mat)
        return obj

    def apply_subsurf(self, obj, levels=2):
        mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
        mod.levels = levels
        mod.render_levels = levels

    def _apply_mat(self, obj, mat):
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

# --- RESTORED FRIEZA BUILDER (V11 is the best one) ---
class FriezaBuilderV11:
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.c_white = (0.92, 0.92, 0.92, 1)
        self.c_purple = (0.45, 0.1, 0.55, 1)
        self.c_black = (0.02, 0.02, 0.02, 1)
        
        self.m_white = ctrl.create_material("VinylWhiteV11", self.c_white, roughness=0.35)
        self.m_purple = ctrl.create_material("VinylPurpleV11", self.c_purple, metallic=0.1, roughness=0.35)
        self.m_eye = ctrl.create_material("EyeGlossV11", self.c_black, roughness=0.05)
        self.m_lines = ctrl.create_material("LineBlackV11", self.c_black, roughness=0.9)

    def build_head_sculpted_v11(self):
        # 1. Base Geometry - WIDE FUNKO
        mesh = bpy.data.meshes.new("Head_V11_Mesh")
        obj = bpy.data.objects.new("Head_V11", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (0, 0, 1.7)
        
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
        bmesh.ops.scale(bm, vec=(1.45, 1.1, 0.95), verts=bm.verts)
        
        top_faces = [f for f in bm.faces if f.calc_center_median().z > 0.4]
        res_ext = bmesh.ops.extrude_face_region(bm, geom=top_faces)
        verts_ext = [e for e in res_ext['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts_ext, vec=(0, 0, 0.04))
        
        # Color index
        for f in res_ext['geom']:
            if isinstance(f, bmesh.types.BMFace): f.material_index = 1
            
        bm.to_mesh(mesh)
        bm.free()
        
        obj.data.materials.append(self.m_white)
        obj.data.materials.append(self.m_purple)
        
        self.ctrl.apply_subsurf(obj, 3)
        
        # Eyes...
        # (Simplified for restoration - logic remains)
        return obj

    def build(self):
        head = self.build_head_sculpted_v11()
        # Additional parts logic would go here
        return head


def build_frieza_v11():
    ctrl = BlenderController()
    builder = FriezaBuilderV11(ctrl)
    builder.build()
    return "Frieza V11 Built"
import bpy
import bmesh
import math
import random
from mathutils import Vector

class LionSculptor: # RENAMED FOR LIB
    def __init__(self):
        import bpy
        self.bpy = bpy
        
        # Clean Slate
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        self.mat_body = self.create_mat("LionKing_Body", (0.8, 0.55, 0.2, 1), 0.4) 
        self.mat_mane = self.create_mat("LionKing_Mane", (0.25, 0.1, 0.05, 1), 0.9) 
        self.mat_nose = self.create_mat("LionKing_Black", (0.05, 0.05, 0.05, 1), 0.2) 

    def create_mat(self, name, color, roughness):
        import bpy
        if name in bpy.data.materials: return bpy.data.materials[name]
        
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        bsdf = None
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
        
        if not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            output = nodes.get("Material Output")
            if not output: output = nodes.new(type='ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])

        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        return mat

    def build(self):
        import bpy
        import bmesh
        from mathutils import Vector
        
        # 1. THE BODY (Box Modeling)
        mesh = bpy.data.meshes.new("LionBody")
        obj = bpy.data.objects.new("Lion", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        bm = bmesh.new()
        
        # -- TORSO --
        bmesh.ops.create_cube(bm, size=1.0)
        chest_verts = [v for v in bm.verts]
        bmesh.ops.scale(bm, vec=(0.9, 0.8, 0.9), verts=chest_verts)
        bmesh.ops.translate(bm, vec=(0, -0.4, 1.4), verts=chest_verts)
        
        bmesh.ops.create_cube(bm, size=1.0)
        current_verts = set(bm.verts)
        previous_verts = set(chest_verts)
        hips_verts = list(current_verts - previous_verts)
        
        bmesh.ops.scale(bm, vec=(0.85, 0.8, 0.85), verts=hips_verts)
        bmesh.ops.translate(bm, vec=(0, 0.5, 1.35), verts=hips_verts)
        
        # -- LEGS --
        leg_locs = [
            (0.5, -0.6, 0.7), # FL
            (-0.5, -0.6, 0.7), # FR
            (0.45, 0.6, 0.7), # BL
            (-0.45, 0.6, 0.7) # BR
        ]
        
        for loc in leg_locs:
            pre_leg_verts = set(bm.verts)
            bmesh.ops.create_cube(bm, size=1.0)
            new_leg_verts = list(set(bm.verts) - pre_leg_verts)
            
            bmesh.ops.scale(bm, vec=(0.35, 0.35, 1.4), verts=new_leg_verts)
            bmesh.ops.translate(bm, vec=loc, verts=new_leg_verts)

        # -- HEAD --
        pre_head_verts = set(bm.verts)
        bmesh.ops.create_cube(bm, size=1.0)
        head_verts = list(set(bm.verts) - pre_head_verts)
        bmesh.ops.scale(bm, vec=(0.7, 0.8, 0.7), verts=head_verts)
        bmesh.ops.translate(bm, vec=(0, -1.1, 2.1), verts=head_verts)
        
        # -- SNOUT --
        pre_snout_verts = set(bm.verts)
        bmesh.ops.create_cube(bm, size=1.0)
        snout_verts = list(set(bm.verts) - pre_snout_verts)
        bmesh.ops.scale(bm, vec=(0.35, 0.4, 0.3), verts=snout_verts)
        bmesh.ops.translate(bm, vec=(0, -1.6, 1.9), verts=snout_verts)

        bm.to_mesh(mesh)
        bm.free()
        
        if obj.data.materials: obj.data.materials[0] = self.mat_body
        else: obj.data.materials.append(self.mat_body)
        
        mod_bev = obj.modifiers.new("Bevel", 'BEVEL')
        mod_bev.width = 0.05
        mod_bev.segments = 3
        
        bpy.ops.object.shade_smooth()
        self.build_mane_volumetric()
        self.build_details()
        return obj

    def build_mane_volumetric(self):
        import bpy
        import bmesh
        import random
        from mathutils import Vector
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.65)
        mane = bpy.context.active_object
        mane.name = "LionMane"
        mane.location = (0, -1.0, 2.15)
        mane.scale = (1, 0.8, 1)
        
        bm = bmesh.new()
        bm.from_mesh(mane.data)
        
        for v in bm.verts:
            noise = Vector((random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)))
            v.co += noise * 0.15
            
        bm.to_mesh(mane.data)
        bm.free()
        bpy.ops.object.shade_flat()
        mane.data.materials.append(self.mat_mane)

    def build_details(self):
        import bpy
        import math
        
        # Nose
        bpy.ops.mesh.primitive_cube_add(size=0.15)
        nose = bpy.context.active_object
        nose.location = (0, -1.8, 2.0)
        nose.data.materials.append(self.mat_nose)
        
        # Eyes
        for x in [-0.2, 0.2]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08)
            eye = bpy.context.active_object
            eye.location = (x, -1.5, 2.2)
            eye.data.materials.append(self.mat_nose)
            
        # Tail
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.2)
        tail = bpy.context.active_object
        tail.rotation_euler = (math.radians(60), 0, 0)
        tail.location = (0, 0.9, 1.4)
        tail.data.materials.append(self.mat_body)
        
        # Tail Tuft
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15)
        tuft = bpy.context.active_object
        tuft.location = (0, 1.4, 1.9)
        tuft.data.materials.append(self.mat_mane)

# EXECUTE


import bpy
import math
import random

def :
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def make_material(name, diffuse):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = diffuse
    return mat

class EagleBuilder_V3:
    def build(self):
    # Materials
    mat_brown = make_material("Brown", (0.2, 0.1, 0.05, 1))
    mat_white = make_material("White", (0.9, 0.9, 0.9, 1))
    mat_yellow = make_material("Yellow", (1.0, 0.8, 0.0, 1))
    mat_black = make_material("Black", (0.05, 0.05, 0.05, 1))

    # Collection
    col = bpy.data.collections.new("Eagle_V3")
    bpy.context.scene.collection.children.link(col)
    
    # helper
    def add_obj(name, mesh_func, mat):
        mesh_func()
        obj = bpy.context.active_object
        obj.name = name
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        # Move to collection
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        return obj

    # 1. BODY
    body = add_obj("Body", lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1), mat_brown)
    body.scale = (0.7, 1.2, 0.7)
    body.rotation_euler[0] = math.radians(20) # Tilt forward

    # 2. HEAD
    head = add_obj("Head", lambda: bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6), mat_white)
    head.location = (0, 0.9, 0.8)
    head.parent = body
    
    # 3. BEAK
    beak = add_obj("Beak", lambda: bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.6), mat_yellow)
    beak.rotation_euler[0] = math.radians(-90)
    beak.location = (0, 0.55, 0)
    beak.parent = head

    # 4. EYES
    for s in [-1, 1]:
        eye = add_obj(f"Eye_{s}", lambda: bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08), mat_black)
        eye.location = (s * 0.25, 0.4, 0.2)
        eye.parent = head

    # 5. WINGS (Manual Geometry for reliability)
    # Instead of procedural mess, let's make solid wings out of cubes first
    def make_wing(side):
        # Arm
        arm = add_obj(f"WingArm_{side}", lambda: bpy.ops.mesh.primitive_cube_add(size=1), mat_brown)
        arm.scale = (1.5, 0.4, 0.1)
        arm.location = (side * 1.6, 0.2, 0.5)
        arm.rotation_euler[1] = math.radians(side * 15)
        
        # Parent to body (inverse transform roughly)
        arm.parent = body
        
        # Feathers (Cubes) attached to Arm
        for i in range(8):
            f = add_obj(f"Feather_{side}_{i}", lambda: bpy.ops.mesh.primitive_cube_add(size=1), mat_black)
            f.scale = (0.2, 1.5, 0.05)
            # Position relative to arm logic
            x_offset = (side * 0.6) + (side * i * 0.15)
            y_offset = -0.5 - (abs(i-3)*0.1)
            
            f.location = (x_offset, y_offset, 0)
            f.rotation_euler[2] = math.radians(side * -10 * i)
            
            # Simple parenting didn't work well in v2 due to context. 
            # Here we just place them absolute? No, let's parent to arm.
            # Resetting matrix to avoid jump
            f.parent = arm
            f.matrix_parent_inverse = arm.matrix_world.inverted()

    make_wing(1)
    make_wing(-1)

    # 6. TAIL
    tail = add_obj("Tail", lambda: bpy.ops.mesh.primitive_cube_add(size=1), mat_white)
    tail.scale = (1.2, 1.5, 0.1)
    tail.location = (0, -1.2, -0.2)
    tail.rotation_euler[0] = math.radians(-20)
    tail.parent = body

    # Camera
    bpy.ops.object.camera_add(location=(4, -5, 3), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.active_object
    
    # Light
    bpy.ops.object.light_add(type='SUN', location=(5,5,10))





