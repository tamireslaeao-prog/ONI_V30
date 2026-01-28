"""
ONI SCULPTOR ENGINE v1.0
=========================
Advanced Procedural Modeling Library for Blender
Goes beyond primitives: real mesh manipulation, topology control, organic shapes.

Usage:
    sculptor = ONISculptor()
    sculptor.create_base_mesh("cube")
    sculptor.extrude_faces_by_normal((0, 0, 1), distance=0.5)
    sculptor.add_edge_loop(0.5)
    sculptor.apply_noise_displacement(0.3, 0.1)
    sculptor.subdivide(2)
    mesh = sculptor.finalize()
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, noise


class ONISculptor:
    """
    Advanced mesh sculptor that provides real modeling operations.
    """
    
    def __init__(self, name: str = "ONI_Sculpture"):
        import bpy
        import bmesh
        
        self.name = name
        self.bm = bmesh.new()
        self.obj = None
        self.mesh = None
        
    # =========================================================================
    # BASE MESH CREATION
    # =========================================================================
    
    def create_base_cube(self, size: float = 1.0, subdivisions: int = 0):
        """Create a cube base mesh with optional subdivisions."""
        import bmesh
        bmesh.ops.create_cube(self.bm, size=size)
        if subdivisions > 0:
            bmesh.ops.subdivide_edges(
                self.bm, 
                edges=self.bm.edges[:], 
                cuts=subdivisions,
                use_grid_fill=True
            )
        return self
    
    def create_base_sphere(self, radius: float = 1.0, segments: int = 32):
        """Create an icosphere base mesh."""
        import bmesh
        bmesh.ops.create_icosphere(
            self.bm, 
            subdivisions=int(math.log2(segments/4)) if segments > 4 else 1,
            radius=radius
        )
        return self
    
    def create_base_cylinder(self, radius: float = 1.0, depth: float = 2.0, segments: int = 32):
        """Create a cylinder base mesh."""
        import bmesh
        bmesh.ops.create_cone(
            self.bm,
            cap_ends=True,
            cap_tris=False,
            segments=segments,
            radius1=radius,
            radius2=radius,
            depth=depth
        )
        return self
    
    def create_base_plane(self, size: float = 2.0, subdivisions: int = 10):
        """Create a subdivided plane (for terrains, cloth, etc)."""
        import bmesh
        # Create grid
        bmesh.ops.create_grid(
            self.bm,
            x_segments=subdivisions,
            y_segments=subdivisions,
            size=size
        )
        return self
    
    # =========================================================================
    # FACE SELECTION
    # =========================================================================
    
    def select_faces_by_normal(self, direction: tuple, threshold: float = 0.7):
        """Select faces pointing in a specific direction."""
        dir_vec = Vector(direction).normalized()
        selected = []
        for face in self.bm.faces:
            if face.normal.dot(dir_vec) > threshold:
                selected.append(face)
        return selected
    
    def select_faces_by_height(self, min_z: float = None, max_z: float = None):
        """Select faces based on their center height."""
        selected = []
        for face in self.bm.faces:
            center_z = face.calc_center_median().z
            if min_z is not None and center_z < min_z:
                continue
            if max_z is not None and center_z > max_z:
                continue
            selected.append(face)
        return selected
    
    def select_faces_by_area(self, min_area: float = 0, max_area: float = float('inf')):
        """Select faces based on their surface area."""
        selected = []
        for face in self.bm.faces:
            area = face.calc_area()
            if min_area <= area <= max_area:
                selected.append(face)
        return selected
    
    # =========================================================================
    # EXTRUSION OPERATIONS
    # =========================================================================
    
    def extrude_faces(self, faces: list, distance: float, scale: float = 1.0):
        """Extrude selected faces outward along their normals."""
        import bmesh
        
        if not faces:
            return self
            
        result = bmesh.ops.extrude_face_region(self.bm, geom=faces)
        extruded_verts = [e for e in result['geom'] if isinstance(e, bmesh.types.BMVert)]
        
        # Move along average normal
        avg_normal = Vector((0, 0, 0))
        for f in faces:
            avg_normal += f.normal
        avg_normal.normalize()
        
        # Translate extruded verts
        bmesh.ops.translate(
            self.bm,
            verts=extruded_verts,
            vec=avg_normal * distance
        )
        
        # Scale if needed
        if scale != 1.0:
            center = Vector((0, 0, 0))
            for v in extruded_verts:
                center += v.co
            center /= len(extruded_verts)
            
            for v in extruded_verts:
                v.co = center + (v.co - center) * scale
        
        return self
    
    def extrude_faces_by_normal(self, direction: tuple, distance: float, 
                                 threshold: float = 0.7, scale: float = 1.0):
        """Extrude faces pointing in a direction."""
        faces = self.select_faces_by_normal(direction, threshold)
        return self.extrude_faces(faces, distance, scale)
    
    def inset_faces(self, faces: list, thickness: float, depth: float = 0):
        """Inset selected faces."""
        import bmesh
        
        if not faces:
            return self
            
        bmesh.ops.inset_region(
            self.bm,
            faces=faces,
            thickness=thickness,
            depth=depth,
            use_even_offset=True
        )
        return self
    
    # =========================================================================
    # EDGE OPERATIONS
    # =========================================================================
    
    def add_edge_loop(self, edges: list = None, cuts: int = 1):
        """Add edge loop by subdividing edges."""
        import bmesh
        
        if edges is None:
            edges = self.bm.edges[:]
            
        bmesh.ops.subdivide_edges(
            self.bm,
            edges=edges,
            cuts=cuts,
            use_grid_fill=False
        )
        return self
    
    def bevel_edges(self, edges: list = None, width: float = 0.1, segments: int = 2):
        """Bevel edges for smoother transitions."""
        import bmesh
        
        if edges is None:
            edges = self.bm.edges[:]
            
        bmesh.ops.bevel(
            self.bm,
            geom=edges,
            offset=width,
            segments=segments,
            affect='EDGES'
        )
        return self
    
    def set_edge_crease(self, edges: list, crease: float = 1.0):
        """Set crease value for edges (affects subdivision)."""
        crease_layer = self.bm.edges.layers.crease.verify()
        for e in edges:
            e[crease_layer] = crease
        return self
    
    # =========================================================================
    # VERTEX MANIPULATION
    # =========================================================================
    
    def apply_noise_displacement(self, frequency: float = 1.0, amplitude: float = 0.1,
                                  seed: int = 0):
        """Displace vertices using Perlin noise."""
        from mathutils import noise as mn
        
        for v in self.bm.verts:
            # Use vertex position as noise input
            noise_pos = v.co * frequency + Vector((seed, seed, seed))
            noise_val = mn.noise(noise_pos)
            v.co += v.normal * noise_val * amplitude
            
        return self
    
    def smooth_vertices(self, iterations: int = 1, factor: float = 0.5, 
                        verts: list = None):
        """Smooth vertices by averaging with neighbors."""
        import bmesh
        
        if verts is None:
            verts = self.bm.verts[:]
            
        for _ in range(iterations):
            bmesh.ops.smooth_vert(
                self.bm,
                verts=verts,
                factor=factor,
                use_axis_x=True,
                use_axis_y=True,
                use_axis_z=True
            )
        return self
    
    def inflate(self, amount: float = 0.1, verts: list = None):
        """Inflate/deflate mesh by moving verts along normals."""
        if verts is None:
            verts = self.bm.verts[:]
            
        for v in verts:
            v.co += v.normal * amount
            
        return self
    
    def taper(self, axis: str = 'Z', factor: float = 0.5):
        """Taper mesh along an axis."""
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 2)
        
        # Find bounds
        min_val = min(v.co[axis_idx] for v in self.bm.verts)
        max_val = max(v.co[axis_idx] for v in self.bm.verts)
        range_val = max_val - min_val
        
        if range_val == 0:
            return self
            
        for v in self.bm.verts:
            # Calculate taper based on position
            t = (v.co[axis_idx] - min_val) / range_val
            scale = 1.0 - t * (1.0 - factor)
            
            # Scale other axes
            for i in range(3):
                if i != axis_idx:
                    v.co[i] *= scale
                    
        return self
    
    def twist(self, axis: str = 'Z', angle: float = 45.0):
        """Twist mesh around an axis."""
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 2)
        
        # Find bounds
        min_val = min(v.co[axis_idx] for v in self.bm.verts)
        max_val = max(v.co[axis_idx] for v in self.bm.verts)
        range_val = max_val - min_val
        
        if range_val == 0:
            return self
            
        angle_rad = math.radians(angle)
        
        for v in self.bm.verts:
            t = (v.co[axis_idx] - min_val) / range_val
            rot_angle = t * angle_rad
            
            # Rotate around axis
            if axis_idx == 2:  # Z
                x, y = v.co.x, v.co.y
                v.co.x = x * math.cos(rot_angle) - y * math.sin(rot_angle)
                v.co.y = x * math.sin(rot_angle) + y * math.cos(rot_angle)
            elif axis_idx == 1:  # Y
                x, z = v.co.x, v.co.z
                v.co.x = x * math.cos(rot_angle) - z * math.sin(rot_angle)
                v.co.z = x * math.sin(rot_angle) + z * math.cos(rot_angle)
            else:  # X
                y, z = v.co.y, v.co.z
                v.co.y = y * math.cos(rot_angle) - z * math.sin(rot_angle)
                v.co.z = y * math.sin(rot_angle) + z * math.cos(rot_angle)
                
        return self
    
    def bend(self, axis: str = 'X', angle: float = 45.0, center: tuple = (0, 0, 0)):
        """Bend mesh around an axis through a center point."""
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 0)
        center_vec = Vector(center)
        angle_rad = math.radians(angle)
        
        # Find bounds along the bend axis
        bend_axis = (axis_idx + 1) % 3  # Perpendicular axis
        min_val = min(v.co[bend_axis] for v in self.bm.verts)
        max_val = max(v.co[bend_axis] for v in self.bm.verts)
        range_val = max_val - min_val
        
        if range_val == 0:
            return self
            
        for v in self.bm.verts:
            t = (v.co[bend_axis] - min_val) / range_val
            rot_angle = t * angle_rad
            
            # Calculate bend (arc)
            radius = range_val / angle_rad if angle_rad != 0 else range_val
            arc_length = v.co[bend_axis] - min_val
            
            # Apply rotation
            if axis_idx == 0:  # X axis
                y_offset = v.co.y - center_vec.y
                z_offset = v.co.z - center_vec.z
                v.co.y = center_vec.y + (radius + y_offset) * math.cos(rot_angle) - radius
                v.co.z = center_vec.z + (radius + y_offset) * math.sin(rot_angle)
                
        return self
    
    # =========================================================================
    # BOOLEAN OPERATIONS
    # =========================================================================
    
    def boolean_union(self, other_bm):
        """Combine this mesh with another (union)."""
        import bmesh
        
        # Merge other bmesh into this one
        other_verts = list(other_bm.verts)
        other_edges = list(other_bm.edges)
        other_faces = list(other_bm.faces)
        
        # This is simplified - real boolean would need proper algorithm
        # For now, just merge geometry
        vert_map = {}
        for v in other_verts:
            new_v = self.bm.verts.new(v.co)
            vert_map[v] = new_v
            
        for f in other_faces:
            try:
                self.bm.faces.new([vert_map[v] for v in f.verts])
            except:
                pass
                
        return self
    
    # =========================================================================
    # SYMMETRY
    # =========================================================================
    
    def mirror(self, axis: str = 'X', merge_threshold: float = 0.001):
        """Mirror mesh across an axis."""
        import bmesh
        
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 0)
        
        # Duplicate all geometry
        geom = self.bm.verts[:] + self.bm.edges[:] + self.bm.faces[:]
        result = bmesh.ops.duplicate(self.bm, geom=geom)
        
        new_verts = [e for e in result['geom'] if isinstance(e, bmesh.types.BMVert)]
        
        # Flip across axis
        for v in new_verts:
            v.co[axis_idx] *= -1
            
        # Merge vertices at center
        bmesh.ops.remove_doubles(
            self.bm,
            verts=self.bm.verts[:],
            dist=merge_threshold
        )
        
        # Recalculate normals
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        
        return self
    
    # =========================================================================
    # SUBDIVISION
    # =========================================================================
    
    def subdivide(self, levels: int = 1, smooth: float = 1.0):
        """Subdivide the mesh (Catmull-Clark style)."""
        import bmesh
        
        for _ in range(levels):
            bmesh.ops.subdivide_edges(
                self.bm,
                edges=self.bm.edges[:],
                cuts=1,
                use_grid_fill=True,
                smooth=smooth
            )
        return self
    
    # =========================================================================
    # GENERATORS
    # =========================================================================
    
    def generate_terrain(self, size: float = 10.0, resolution: int = 50,
                         height_scale: float = 2.0, noise_scale: float = 0.5):
        """Generate procedural terrain."""
        from mathutils import noise as mn
        
        self.create_base_plane(size, resolution)
        
        for v in self.bm.verts:
            noise_val = mn.fractal(
                v.co * noise_scale,
                1.0,  # H
                2.0,  # lacunarity
                4,    # octaves
                noise_basis='PERLIN_ORIGINAL'
            )
            v.co.z = noise_val * height_scale
            
        return self
    
    def generate_rock(self, size: float = 1.0, detail: int = 3, 
                      roughness: float = 0.3):
        """Generate procedural rock shape."""
        self.create_base_sphere(size, 16)
        self.subdivide(detail, smooth=0.5)
        self.apply_noise_displacement(2.0, roughness)
        return self
    
    def generate_tree_trunk(self, height: float = 3.0, base_radius: float = 0.3,
                            top_radius: float = 0.1, segments: int = 12):
        """Generate a tapered tree trunk."""
        import bmesh
        
        bmesh.ops.create_cone(
            self.bm,
            cap_ends=True,
            cap_tris=False,
            segments=segments,
            radius1=base_radius,
            radius2=top_radius,
            depth=height
        )
        
        # Add some noise for organic feel
        self.apply_noise_displacement(3.0, 0.02)
        
        return self
    
    # =========================================================================
    # LOFTING (Create surface from curves/profiles)
    # =========================================================================
    
    def loft_profiles(self, profiles: list, closed: bool = False):
        """
        Create a surface by connecting profile curves.
        profiles: list of lists of (x, y, z) tuples representing cross-sections
        """
        import bmesh
        
        if len(profiles) < 2:
            return self
            
        # Create vertices for each profile
        all_profile_verts = []
        for profile in profiles:
            profile_verts = []
            for point in profile:
                v = self.bm.verts.new(Vector(point))
                profile_verts.append(v)
            all_profile_verts.append(profile_verts)
        
        # Create faces between adjacent profiles
        for i in range(len(all_profile_verts) - 1):
            current = all_profile_verts[i]
            next_profile = all_profile_verts[i + 1]
            
            n = min(len(current), len(next_profile))
            for j in range(n):
                j_next = (j + 1) % n
                try:
                    self.bm.faces.new([
                        current[j],
                        current[j_next],
                        next_profile[j_next],
                        next_profile[j]
                    ])
                except:
                    pass
        
        return self
    
    # =========================================================================
    # FINALIZATION
    # =========================================================================
    
    def finalize(self, location: tuple = (0, 0, 0)):
        """Convert BMesh to actual Blender object."""
        import bpy
        
        self.mesh = bpy.data.meshes.new(self.name + "_mesh")
        self.bm.to_mesh(self.mesh)
        self.bm.free()
        
        self.obj = bpy.data.objects.new(self.name, self.mesh)
        bpy.context.collection.objects.link(self.obj)
        
        self.obj.location = Vector(location)
        
        # Set as active
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        
        return self.obj
    
    def apply_modifier(self, mod_type: str, **kwargs):
        """Apply a modifier to the final object."""
        if not self.obj:
            self.finalize()
            
        mod = self.obj.modifiers.new(name=mod_type, type=mod_type.upper())
        
        for key, value in kwargs.items():
            if hasattr(mod, key):
                setattr(mod, key, value)
                
        return self
    
    def apply_material(self, color: tuple, metallic: float = 0.0, 
                       roughness: float = 0.5, name: str = None):
        """Apply a PBR material to the object."""
        import bpy
        
        if not self.obj:
            self.finalize()
            
        mat_name = name or f"{self.name}_material"
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
        
        if self.obj.data.materials:
            self.obj.data.materials[0] = mat
        else:
            self.obj.data.materials.append(mat)
            
        return self


# ================================================================================
# CONVENIENCE FUNCTIONS
# ================================================================================

def sculpt_organic_creature():
    """Demo: Create an organic creature using the sculptor."""
    sculptor = ONISculptor("Creature")
    
    # Body
    sculptor.create_base_sphere(1.0, 16)
    sculptor.subdivide(2)
    sculptor.apply_noise_displacement(1.5, 0.15)
    
    # Taper for body shape
    sculptor.taper('Z', 0.6)
    
    return sculptor.finalize()


def sculpt_stylized_head():
    """Demo: Create a stylized head shape."""
    sculptor = ONISculptor("Head")
    
    # Start with cube
    sculptor.create_base_cube(1.0, subdivisions=2)
    
    # Extrude front for face
    front_faces = sculptor.select_faces_by_normal((0, -1, 0), 0.7)
    sculptor.extrude_faces(front_faces, 0.3, scale=0.8)
    
    # Extrude again for nose area
    sculptor.extrude_faces(front_faces[:1], 0.2, scale=0.5)
    
    # Smooth and subdivide
    sculptor.smooth_vertices(2)
    sculptor.subdivide(2)
    
    return sculptor.finalize()


def sculpt_terrain():
    """Demo: Create procedural terrain."""
    sculptor = ONISculptor("Terrain")
    sculptor.generate_terrain(20.0, 100, 3.0, 0.3)
    return sculptor.finalize()
