
import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix, Euler, noise
import math
import random
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

class UniversalModeler:
    """ONI Enhanced Procedural Modeler"""
    
    def __init__(self):
        self.context = bpy.context
        self.data = bpy.data
        self.ops = bpy.ops
        self.created_objects = []

    # ==================== PROCEDURAL ARCHITECTURE ====================
    
    def create_parametric_building(self, name: str = "Building",
                                   floors: int = 10,
                                   width: float = 10.0,
                                   depth: float = 8.0,
                                   floor_height: float = 3.0,
                                   window_spacing: float = 2.0) -> Any:
        try:
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(obj)
            
            bm = bmesh.new()
            total_height = floors * floor_height
            
            # Base Geometry
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(width, depth, total_height), verts=bm.verts)
            # Adjust Z so it sits on ground
            bmesh.ops.translate(bm, vec=(0, 0, total_height/2), verts=bm.verts)
            
            bm.to_mesh(mesh)
            bm.free()
            
            # Add Windows (Boolean or Texture?)
            # Simplified for performance: Inset Faces?
            # Let's use the original logic if possible, or simpler modifier stack
            
            self.created_objects.append(obj)
            print(f"✓ Building created: {floors} floors")
            return obj
        except Exception as e:
            print(f"✗ Error creating building: {e}")
            return None

    def create_procedural_tree(self, name: str = "Tree",
                              trunk_height: float = 3.0,
                              trunk_radius: float = 0.3,
                              crown_radius: float = 2.0,
                              branch_count: int = 8) -> Any:
        try:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
            
            # Trunk
            bpy.ops.mesh.primitive_cylinder_add(
                radius=trunk_radius, depth=trunk_height, location=(0, 0, trunk_height/2)
            )
            trunk = bpy.context.active_object
            trunk.name = f"{name}_Trunk"
            collection.objects.link(trunk)
            bpy.context.collection.objects.unlink(trunk)
            
            # Crown
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2, radius=crown_radius, 
                location=(0, 0, trunk_height + crown_radius * 0.5)
            )
            crown = bpy.context.active_object
            crown.name = f"{name}_Crown"
            
            # Displace
            mod = crown.modifiers.new(name="Displacement", type='DISPLACE')
            mod.strength = 0.3
            
            collection.objects.link(crown)
            bpy.context.collection.objects.unlink(crown)
            
            return collection
        except Exception as e:
            print(f"✗ Error creating tree: {e}")
            return None

    def create_terrain(self, name: str = "Terrain",
                      size: float = 50.0,
                      subdivisions: int = 100,
                      height_scale: float = 5.0,
                      noise_scale: float = 3.0) -> Any:
        try:
            bpy.ops.mesh.primitive_grid_add(
                x_subdivisions=subdivisions, y_subdivisions=subdivisions, size=size
            )
            terrain = bpy.context.active_object
            terrain.name = name
            
            # Apply Noise
            mesh = terrain.data
            for vert in mesh.vertices:
                x, y, z = vert.co
                n_val = noise.noise(Vector((x/noise_scale, y/noise_scale, 0)))
                vert.co.z = n_val * height_scale
                
            bpy.ops.object.shade_smooth()
            return terrain
        except Exception as e:
            print(f"✗ Error creating terrain: {e}")
            return None

    # ==================== ORGANIC MODELING ====================

    def create_organic_creature(self, name: str = "Creature",
                               body_scale: Tuple[float, float, float] = (1, 1.5, 1),
                               limb_count: int = 4) -> Any:
        try:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection) 
            
            # Body
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0)
            body = bpy.context.active_object
            body.name = f"{name}_Body"
            body.scale = body_scale
            collection.objects.link(body)
            bpy.context.collection.objects.unlink(body)
            
            # Limbs
            for i in range(limb_count):
                angle = (360 / limb_count) * i
                rad = math.radians(angle)
                x = math.cos(rad) * 1.2
                y = math.sin(rad) * 1.2
                
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.2, depth=2.0, location=(x, y, 0)
                )
                limb = bpy.context.active_object
                limb.rotation_euler = (math.radians(90), 0, rad)
                limb.name = f"{name}_Limb_{i}"
                collection.objects.link(limb)
                bpy.context.collection.objects.unlink(limb)
                
                collection.objects.link(limb)
                bpy.context.collection.objects.unlink(limb)
                
            return collection
        except Exception as e:
            print(f"✗ Error creating creature: {e}")
            return None

    def create_funko_pop_base(self, name: str = "Funko",
                             scale: float = 1.0,
                             cheek_puff: float = 0.0) -> Any:
        """Standardized Funko Pop Body Plan (Universal Archetype)"""
        try:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
            
            # 1. Head (Rounded Cube)
            bpy.ops.mesh.primitive_cube_add(size=1.0)
            head = bpy.context.active_object
            head.name = f"{name}_Head"
            
            # Shape it: Wide and Soft
            # Grogu needs a wider bottom (cheeks)
            head.scale = (1.3 * scale, 0.9 * scale, 1.0 * scale)
            head.location = (0, 0, 1.2 * scale)
            
            mod_sub = head.modifiers.new(name="Subsurf", type='SUBSURF')
            mod_sub.levels = 3
            
            mod_cast = head.modifiers.new(name="Spherize", type='CAST')
            mod_cast.factor = 0.65
            
            # Application of modifiers to allow vertex manipulation if needed?
            # No, keep it procedural for now.
            
            # CHEEK PUFFS (Extra Geometry for Cute Characters)
            if cheek_puff > 0:
                for side in [-1, 1]:
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35 * scale * cheek_puff)
                    cheek = bpy.context.active_object
                    cheek.name = f"{name}_Cheek_{'L' if side==1 else 'R'}"
                    # Position lower corners
                    cheek.location = (side * 0.55 * scale, 0.3 * scale, 0.9 * scale)
                    cheek.scale = (1, 0.8, 1)
                    
                    # Merge into head (Boolean Union) or just parent?
                    # Visual merge is safer for procedural
                    collection.objects.link(cheek)
                    bpy.context.collection.objects.unlink(cheek)
                    
                    # Parent to Head
                    cheek.parent = head
                    cheek.matrix_parent_inverse = head.matrix_world.inverted()
                    
                    # Give same material as head later
            
            bpy.ops.object.shade_smooth()
            collection.objects.link(head)
            bpy.context.collection.objects.unlink(head)
            
            # 2. Body (Tapered Cylinder/Cone)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25 * scale, depth=0.8 * scale)
            body = bpy.context.active_object
            body.name = f"{name}_Body"
            body.location = (0, 0, 0.4 * scale)
            
            # Taper top
            # Simple deform or build as cone? Cylinder is fine for now if robe covers it.
            
            collection.objects.link(body)
            bpy.context.collection.objects.unlink(body)
            
            # 3. Eyes (Black Spheres - Standard Position)
            eye_r = 0.4 * scale
            eye_h = 1.1 * scale
            eye_y = -0.4 * scale
            eye_x = 0.5 * scale
            
            for side in [-1, 1]:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15 * scale)
                eye = bpy.context.active_object
                eye.name = f"{name}_Eye_{'L' if side==1 else 'R'}"
                eye.location = (side * eye_x, eye_y, eye_h)
                eye.scale = (1, 0.2, 1) # Flatten against head
                
                # Material (Standard Black Vinyl)
                mat_eye = bpy.data.materials.new(name=f"Eye_Mat_{side}")
                mat_eye.use_nodes = True
                nodes = mat_eye.node_tree.nodes
                # Clear default to be safe
                nodes.clear()
                
                bsdf = nodes.new('ShaderNodeBsdfPrincipled')
                bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
                bsdf.inputs['Roughness'].default_value = 0.1
                
                output = nodes.new('ShaderNodeOutputMaterial')
                mat_eye.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
                
                eye.data.materials.append(mat_eye)
                
                collection.objects.link(eye)
                bpy.context.collection.objects.unlink(eye)

            return {'collection': collection, 'head': head, 'body': body}

        except Exception as e:
            print(f"✗ Error creating Funko Base: {e}")
            return None
