"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
============================================================================
ONI.BlenderAutomation.py - Blender Automation Bridge
Version: 1.0
Description: Python API for procedural generation in Blender
============================================================================
"""

import bpy
import bmesh
import math
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

# Import ONI core
try:
    from ONI_Gen import (
        seed_manager, color_gen, geometry_gen, 
        variation_gen, greebles_gen, glitch_gen
    )
except ImportError:
    print("Warning: ONI_Gen module not found. Some features may not work.")


# ============================================================================
# BLENDER CONNECTION
# ============================================================================

class BlenderConnection:
    """Manages Blender context and scene"""
    
    @staticmethod
    def get_context():
        """Get current Blender context"""
        return bpy.context
    
    @staticmethod
    def get_scene():
        """Get current scene"""
        return bpy.context.scene
    
    @staticmethod
    def get_collection(name: str = "Collection"):
        """Get or create collection"""
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        else:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
            return col
    
    @staticmethod
    def clear_scene():
        """Clear all objects from scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    
    @staticmethod
    def clear_collection(collection_name: str):
        """Clear specific collection"""
        if collection_name in bpy.data.collections:
            col = bpy.data.collections[collection_name]
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)


# ============================================================================
# OBJECT CREATION
# ============================================================================

class ONIObjectCreator:
    """Create 3D objects in Blender"""
    
    @staticmethod
    def create_plane(name: str = "Plane",
                    size: float = 2.0,
                    location: Tuple[float, float, float] = (0, 0, 0),
                    collection: Optional[str] = None) -> bpy.types.Object:
        """Create plane object"""
        bpy.ops.mesh.primitive_plane_add(size=size, location=location)
        obj = bpy.context.active_object
        obj.name = name
        
        if collection:
            col = BlenderConnection.get_collection(collection)
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        
        return obj
    
    @staticmethod
    def create_cube(name: str = "Cube",
                   size: float = 2.0,
                   location: Tuple[float, float, float] = (0, 0, 0),
                   collection: Optional[str] = None) -> bpy.types.Object:
        """Create cube object"""
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = bpy.context.active_object
        obj.name = name
        
        if collection:
            col = BlenderConnection.get_collection(collection)
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        
        return obj
    
    @staticmethod
    def create_cylinder(name: str = "Cylinder",
                       radius: float = 1.0,
                       depth: float = 2.0,
                       location: Tuple[float, float, float] = (0, 0, 0),
                       collection: Optional[str] = None) -> bpy.types.Object:
        """Create cylinder object"""
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        
        if collection:
            col = BlenderConnection.get_collection(collection)
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        
        return obj
    
    @staticmethod
    def create_sphere(name: str = "Sphere",
                     radius: float = 1.0,
                     location: Tuple[float, float, float] = (0, 0, 0),
                     subdivisions: int = 2,
                     collection: Optional[str] = None) -> bpy.types.Object:
        """Create UV sphere"""
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        
        # Subdivide if needed
        if subdivisions > 0:
            bpy.ops.object.modifier_add(type='SUBSURF')
            obj.modifiers["Subdivision"].levels = subdivisions
        
        if collection:
            col = BlenderConnection.get_collection(collection)
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        
        return obj
    
    @staticmethod
    def create_text(text: str = "Text",
                   name: str = "Text",
                   location: Tuple[float, float, float] = (0, 0, 0),
                   size: float = 1.0,
                   extrude: float = 0.1,
                   collection: Optional[str] = None) -> bpy.types.Object:
        """Create 3D text object"""
        bpy.ops.object.text_add(location=location)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.body = text
        obj.data.size = size
        obj.data.extrude = extrude
        
        if collection:
            col = BlenderConnection.get_collection(collection)
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        
        return obj


# ============================================================================
# MATERIAL SYSTEM
# ============================================================================

class ONIMaterialCreator:
    """Create and manage materials"""
    
    @staticmethod
    def create_emission_material(name: str,
                                 color: Tuple[float, float, float, float],
                                 strength: float = 2.0) -> bpy.types.Material:
        """Create emission (glow) material"""
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create nodes
        emission = nodes.new('ShaderNodeEmission')
        output = nodes.new('ShaderNodeOutputMaterial')
        
        # Set values
        emission.inputs['Color'].default_value = color
        emission.inputs['Strength'].default_value = strength
        
        # Link nodes
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        return mat
    
    @staticmethod
    def create_principled_material(name: str,
                                  base_color: Tuple[float, float, float, float],
                                  metallic: float = 0.0,
                                  roughness: float = 0.5,
                                  emission: Optional[Tuple[float, float, float, float]] = None,
                                  emission_strength: float = 1.0) -> bpy.types.Material:
        """Create PBR material with Principled BSDF"""
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Get Principled BSDF (default node)
        principled = nodes.get('Principled BSDF')
        if not principled:
            principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Set values
        principled.inputs['Base Color'].default_value = base_color
        principled.inputs['Metallic'].default_value = metallic
        principled.inputs['Roughness'].default_value = roughness
        
        if emission:
            principled.inputs['Emission'].default_value = emission
            principled.inputs['Emission Strength'].default_value = emission_strength
        
        return mat
    
    @staticmethod
    def create_cyberpunk_material(name: str,
                                 hex_color: str,
                                 glow_intensity: float = 2.0) -> bpy.types.Material:
        """Create neon cyberpunk material"""
        rgba = color_gen.hex_to_rgba(hex_color)
        
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        nodes.clear()
        
        # Create nodes
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        emission = nodes.new('ShaderNodeEmission')
        add_shader = nodes.new('ShaderNodeAddShader')
        output = nodes.new('ShaderNodeOutputMaterial')
        
        # Principled settings (base material)
        principled.inputs['Base Color'].default_value = rgba
        principled.inputs['Metallic'].default_value = 0.8
        principled.inputs['Roughness'].default_value = 0.2
        
        # Emission settings (glow)
        emission.inputs['Color'].default_value = rgba
        emission.inputs['Strength'].default_value = glow_intensity
        
        # Link nodes
        links.new(principled.outputs['BSDF'], add_shader.inputs[0])
        links.new(emission.outputs['Emission'], add_shader.inputs[1])
        links.new(add_shader.outputs['Shader'], output.inputs['Surface'])
        
        return mat
    
    @staticmethod
    def apply_material(obj: bpy.types.Object, material: bpy.types.Material):
        """Apply material to object"""
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)


# ============================================================================
# BADGE GENERATION
# ============================================================================

class ONIBadgeGenerator:
    """Generate 3D badges and ID cards"""
    
    @staticmethod
    def create_badge_base(width: float = 8.56,
                         height: float = 5.398,
                         thickness: float = 0.1,
                         corner_radius: float = 0.3) -> bpy.types.Object:
        """Create badge base card (ID-1 standard size in cm)"""
        # Create base cube
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.name = "Badge_Base"
        
        # Scale to badge dimensions
        obj.scale = (width/2, height/2, thickness/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Add bevel for rounded corners
        bpy.ops.object.modifier_add(type='BEVEL')
        obj.modifiers["Bevel"].width = corner_radius
        obj.modifiers["Bevel"].segments = 4
        
        return obj
    
    @staticmethod
    def create_cyberpunk_badge(name: str = "AGENT",
                              title: str = "SECURITY",
                              badge_id: str = "A7F3-9182",
                              style: str = "cyberpunk_v1") -> Dict[str, Any]:
        """
        Create complete cyberpunk badge in 3D
        
        Returns:
            Dictionary with all created objects
        """
        objects = {}
        
        # Generate seed
        seed = seed_manager.generate_seed("CYB")
        print(f"Badge seed: {seed}")
        
        # Create collection
        collection = BlenderConnection.get_collection("ONI_Badge")
        
        # 1. Base card
        base = ONIBadgeGenerator.create_badge_base()
        collection.objects.link(base)
        bpy.context.scene.collection.objects.unlink(base)
        objects['base'] = base
        
        # Base material (dark)
        base_mat = ONIMaterialCreator.create_principled_material(
            "Badge_Base_Mat",
            base_color=(0.04, 0.04, 0.06, 1.0),
            metallic=0.1,
            roughness=0.8
        )
        ONIMaterialCreator.apply_material(base, base_mat)
        
        # 2. Main frame (neon outline)
        frame_color = color_gen.get_random_color(style, "primary")
        
        # Create frame as curve
        bpy.ops.curve.primitive_bezier_square_add()
        frame = bpy.context.active_object
        frame.name = "Badge_Frame"
        frame.location = (0, 0, 0.06)
        frame.scale = (3.5, 2.3, 1)
        frame.data.bevel_depth = 0.02
        
        # Frame material
        frame_mat = ONIMaterialCreator.create_emission_material(
            "Frame_Mat",
            color=color_gen.hex_to_rgba(frame_color),
            strength=3.0
        )
        ONIMaterialCreator.apply_material(frame, frame_mat)
        
        collection.objects.link(frame)
        bpy.context.scene.collection.objects.unlink(frame)
        objects['frame'] = frame
        
        # 3. Photo zone
        photo = ONIObjectCreator.create_plane(
            "Photo_Zone",
            size=2.5,
            location=(0, 0.8, 0.055),
            collection="ONI_Badge"
        )
        photo.scale = (1.2, 1.6, 1)
        
        photo_mat = ONIMaterialCreator.create_principled_material(
            "Photo_Mat",
            base_color=(0.1, 0.1, 0.12, 1.0),
            metallic=0.0,
            roughness=0.9
        )
        ONIMaterialCreator.apply_material(photo, photo_mat)
        objects['photo'] = photo
        
        # 4. Name text
        name_text = ONIObjectCreator.create_text(
            text=name,
            name="Name_Text",
            location=(-2.5, -0.8, 0.055),
            size=0.4,
            extrude=0.05,
            collection="ONI_Badge"
        )
        
        accent_color = color_gen.get_random_color(style, "accent")
        name_mat = ONIMaterialCreator.create_cyberpunk_material(
            "Name_Mat",
            hex_color=accent_color,
            glow_intensity=2.5
        )
        ONIMaterialCreator.apply_material(name_text, name_mat)
        objects['name'] = name_text
        
        # 5. Title text
        title_text = ONIObjectCreator.create_text(
            text=title,
            name="Title_Text",
            location=(-2.5, -1.4, 0.055),
            size=0.25,
            extrude=0.03,
            collection="ONI_Badge"
        )
        
        title_mat = ONIMaterialCreator.create_principled_material(
            "Title_Mat",
            base_color=(1, 1, 1, 1),
            metallic=0.3,
            roughness=0.5
        )
        ONIMaterialCreator.apply_material(title_text, title_mat)
        objects['title'] = title_text
        
        # 6. ID text
        id_text = ONIObjectCreator.create_text(
            text=f"ID: {badge_id}",
            name="ID_Text",
            location=(-2.5, -1.9, 0.055),
            size=0.18,
            extrude=0.02,
            collection="ONI_Badge"
        )
        
        id_mat = ONIMaterialCreator.create_emission_material(
            "ID_Mat",
            color=color_gen.hex_to_rgba(frame_color),
            strength=1.5
        )
        ONIMaterialCreator.apply_material(id_text, id_mat)
        objects['id'] = id_text
        
        # 7. Greebles (technical details)
        greebles_data = greebles_gen.generate_greebles(
            count=15,
            area_bounds=(-3.5, 3.5, -2, -2.5),
            size_range=(0.05, 0.15)
        )
        
        objects['greebles'] = []
        for i, g in enumerate(greebles_data):
            if g['type'] == 'cube':
                greeble = ONIObjectCreator.create_cube(
                    f"Greeble_{i}",
                    size=g['size'],
                    location=(g['position'][0], g['position'][1], 0.06),
                    collection="ONI_Badge"
                )
            elif g['type'] == 'cylinder':
                greeble = ONIObjectCreator.create_cylinder(
                    f"Greeble_{i}",
                    radius=g['size']/2,
                    depth=g['size'],
                    location=(g['position'][0], g['position'][1], 0.06),
                    collection="ONI_Badge"
                )
            else:
                greeble = ONIObjectCreator.create_sphere(
                    f"Greeble_{i}",
                    radius=g['size']/2,
                    location=(g['position'][0], g['position'][1], 0.06),
                    collection="ONI_Badge"
                )
            
            # Random greeble color
            g_color = color_gen.get_random_color(style, "accent")
            g_mat = ONIMaterialCreator.create_emission_material(
                f"Greeble_Mat_{i}",
                color=color_gen.hex_to_rgba(g_color),
                strength=1.5
            )
            ONIMaterialCreator.apply_material(greeble, g_mat)
            objects['greebles'].append(greeble)
        
        print(f"✓ Cyberpunk badge created with seed: {seed}")
        return {
            'objects': objects,
            'seed': seed,
            'style': style
        }


# ============================================================================
# LIGHTING SETUP
# ============================================================================

class ONILightingSetup:
    """Setup scene lighting"""
    
    @staticmethod
    def create_three_point_lighting(target_location: Tuple[float, float, float] = (0, 0, 0)):
        """Create classic 3-point lighting setup"""
        
        # Key light
        bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
        key = bpy.context.active_object
        key.name = "Key_Light"
        key.data.energy = 300
        key.data.size = 5
        
        # Point light at target
        constraint = key.constraints.new('TRACK_TO')
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        # Fill light
        bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
        fill = bpy.context.active_object
        fill.name = "Fill_Light"
        fill.data.energy = 150
        fill.data.size = 4
        
        # Rim light
        bpy.ops.object.light_add(type='SPOT', location=(0, 3, 4))
        rim = bpy.context.active_object
        rim.name = "Rim_Light"
        rim.data.energy = 200
        rim.rotation_euler = (math.radians(135), 0, 0)
    
    @staticmethod
    def create_cyberpunk_lighting(neon_color: str = "#00F0FF"):
        """Create cyberpunk neon lighting"""
        rgba = color_gen.hex_to_rgba(neon_color)
        
        # Neon area light
        bpy.ops.object.light_add(type='AREA', location=(0, -8, 3))
        neon = bpy.context.active_object
        neon.name = "Neon_Light"
        neon.data.energy = 500
        neon.data.size = 10
        neon.data.color = rgba[:3]
        
        # Ambient HDRI would go here if available


# ============================================================================
# CAMERA SETUP
# ============================================================================

class ONICameraSetup:
    """Setup scene cameras"""
    
    @staticmethod
    def create_badge_camera(distance: float = 12.0) -> bpy.types.Object:
        """Create camera positioned for badge view"""
        bpy.ops.object.camera_add(location=(0, -distance, 3))
        camera = bpy.context.active_object
        camera.name = "Badge_Camera"
        camera.rotation_euler = (math.radians(80), 0, 0)
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        # Camera settings
        camera.data.lens = 50
        camera.data.sensor_width = 36
        
        return camera
    
    @staticmethod
    def create_orthographic_camera() -> bpy.types.Object:
        """Create top-down orthographic camera"""
        bpy.ops.object.camera_add(location=(0, 0, 10))
        camera = bpy.context.active_object
        camera.name = "Ortho_Camera"
        camera.rotation_euler = (0, 0, 0)
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = 10
        
        bpy.context.scene.camera = camera
        return camera


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

class ONIExporter:
    """Export rendered images and 3D files"""
    
    @staticmethod
    def render_image(output_path: str,
                    resolution_x: int = 1920,
                    resolution_y: int = 1080,
                    samples: int = 128):
        """Render current scene to image"""
        scene = bpy.context.scene
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        scene.render.filepath = output_path
        
        # Use Cycles for better quality
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = samples
        
        bpy.ops.render.render(write_still=True)
        print(f"✓ Rendered to: {output_path}")
    
    @staticmethod
    def export_gltf(output_path: str, selected_only: bool = True):
        """Export to GLTF format"""
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=selected_only,
            export_format='GLB'
        )
        print(f"✓ Exported GLTF to: {output_path}")
    
    @staticmethod
    def export_fbx(output_path: str, selected_only: bool = True):
        """Export to FBX format"""
        bpy.ops.export_scene.fbx(
            filepath=output_path,
            use_selection=selected_only
        )
        print(f"✓ Exported FBX to: {output_path}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_badge(name: str = "AGENT", 
               title: str = "SECURITY",
               badge_id: str = "A7F3-9182") -> Dict:
    """Quick badge generation"""
    
    # Clear scene
    BlenderConnection.clear_scene()
    
    # Generate badge
    result = ONIBadgeGenerator.create_cyberpunk_badge(name, title, badge_id)
    
    # Setup camera
    ONICameraSetup.create_badge_camera()
    
    # Setup lighting
    ONILightingSetup.create_cyberpunk_lighting()
    
    return result


if __name__ == "__main__":
    print("ONI.BlenderAutomation loaded successfully!")
    print("Use: quick_badge('YOUR NAME', 'YOUR TITLE', 'ID-001')")

