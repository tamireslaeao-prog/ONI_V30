"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
ONI Add-on Operators
All operations available in the UI
"""

import bpy
from bpy.types import Operator
from pathlib import Path
import sys

# Import ONI modules
addon_dir = Path(__file__).parent.parent
sys.path.append(str(addon_dir))

try:
    from ONI_Gen import seed_manager, color_gen
    from ONI_BlenderAutomation import (
        ONIBadgeGenerator, ONICameraSetup, ONILightingSetup,
        ONIExporter, BlenderConnection
    )
except ImportError as e:
    print(f"Warning: Could not import ONI modules: {e}")


# ============================================================================
# MAIN GENERATION OPERATOR
# ============================================================================

class ONI_OT_GenerateBadge(Operator):
    """Generate 3D badge with ONI system"""
    bl_idname = "oni.generate_badge"
    bl_label = "Generate Badge"
    bl_description = "Generate procedural 3D badge"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        oni = scene.oni
        
        try:
            # Generate seed if needed
            if not oni.current_seed or oni.auto_generate_seed:
                seed = seed_manager.generate_seed(oni.seed_prefix)
                oni.current_seed = seed
                self.report({'INFO'}, f"Generated seed: {seed}")
            else:
                seed_manager.set_seed(oni.current_seed)
            
            # Clear scene if requested
            if oni.clear_before_generate:
                BlenderConnection.clear_scene()
            
            # Generate badge
            result = ONIBadgeGenerator.create_cyberpunk_badge(
                name=oni.badge_name,
                title=oni.badge_title,
                badge_id=oni.badge_id,
                style=oni.style_palette
            )
            
            # Setup camera and lighting if requested
            if oni.auto_setup_camera:
                ONICameraSetup.create_badge_camera()
            
            if oni.auto_setup_lighting:
                ONILightingSetup.create_cyberpunk_lighting()
            
            self.report({'INFO'}, f"Badge generated successfully! Seed: {result['seed']}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate badge: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ============================================================================
# SEED OPERATORS
# ============================================================================

class ONI_OT_NewSeed(Operator):
    """Generate new random seed"""
    bl_idname = "oni.new_seed"
    bl_label = "New Seed"
    bl_description = "Generate new random seed"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        oni = context.scene.oni
        
        try:
            seed = seed_manager.generate_seed(oni.seed_prefix)
            oni.current_seed = seed
            oni.seed_history.append(seed)
            
            self.report({'INFO'}, f"New seed: {seed}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate seed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ============================================================================
# STYLE OPERATORS
# ============================================================================

class ONI_OT_ApplyStyle(Operator):
    """Apply style from database to selected objects"""
    bl_idname = "oni.apply_style"
    bl_label = "Apply Style"
    bl_description = "Apply selected style to objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        oni = context.scene.oni
        selected = context.selected_objects
        
        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        try:
            # Get color from style
            hex_color = color_gen.get_random_color(
                oni.style_palette,
                oni.color_category
            )
            
            rgba = color_gen.hex_to_rgba(hex_color)
            
            # Apply to selected objects
            for obj in selected:
                if obj.type == 'MESH':
                    # Create or get material
                    mat_name = f"ONI_{oni.style_palette}"
                    if mat_name in bpy.data.materials:
                        mat = bpy.data.materials[mat_name]
                    else:
                        mat = bpy.data.materials.new(name=mat_name)
                        mat.use_nodes = True
                        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = rgba
                    
                    # Assign material
                    if obj.data.materials:
                        obj.data.materials[0] = mat
                    else:
                        obj.data.materials.append(mat)
            
            self.report({'INFO'}, f"Applied style {oni.style_palette} with color {hex_color}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply style: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ============================================================================
# GREEBLES OPERATOR
# ============================================================================

class ONI_OT_GenerateGreebles(Operator):
    """Generate random greebles on surface"""
    bl_idname = "oni.generate_greebles"
    bl_label = "Generate Greebles"
    bl_description = "Add random technical details"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        oni = context.scene.oni
        
        try:
            from ONI_Gen import greebles_gen
            
            # Get greeble data
            greebles_data = greebles_gen.generate_greebles(
                count=oni.greeble_count,
                area_bounds=(-5, 5, -5, 5),
                size_range=(oni.greeble_min_size, oni.greeble_max_size)
            )
            
            # Create greebles
            col = BlenderConnection.get_collection("ONI_Greebles")
            
            for i, g in enumerate(greebles_data):
                # Create primitive based on type
                if g['type'] == 'cube':
                    bpy.ops.mesh.primitive_cube_add(
                        size=g['size'],
                        location=g['position']
                    )
                elif g['type'] == 'cylinder':
                    bpy.ops.mesh.primitive_cylinder_add(
                        radius=g['size']/2,
                        depth=g['size'],
                        location=g['position']
                    )
                elif g['type'] == 'sphere':
                    bpy.ops.mesh.primitive_uv_sphere_add(
                        radius=g['size']/2,
                        location=g['position']
                    )
                
                obj = context.active_object
                obj.name = f"Greeble_{i}"
                obj.rotation_euler = g['rotation']
                
                # Move to collection
                col.objects.link(obj)
                context.scene.collection.objects.unlink(obj)
            
            self.report({'INFO'}, f"Generated {len(greebles_data)} greebles")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate greebles: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ============================================================================
# SCENE SETUP OPERATORS
# ============================================================================

class ONI_OT_ClearScene(Operator):
    """Clear all objects from scene"""
    bl_idname = "oni.clear_scene"
    bl_label = "Clear Scene"
    bl_description = "Remove all objects from scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            BlenderConnection.clear_scene()
            self.report({'INFO'}, "Scene cleared")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear scene: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class ONI_OT_SetupCamera(Operator):
    """Setup camera for badge view"""
    bl_idname = "oni.setup_camera"
    bl_label = "Setup Camera"
    bl_description = "Create and position camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            ONICameraSetup.create_badge_camera()
            self.report({'INFO'}, "Camera setup complete")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup camera: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class ONI_OT_SetupLighting(Operator):
    """Setup scene lighting"""
    bl_idname = "oni.setup_lighting"
    bl_label = "Setup Lighting"
    bl_description = "Create lighting setup"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        oni = context.scene.oni
        
        try:
            if oni.lighting_style == 'THREE_POINT':
                ONILightingSetup.create_three_point_lighting()
            else:
                ONILightingSetup.create_cyberpunk_lighting()
            
            self.report({'INFO'}, "Lighting setup complete")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup lighting: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ============================================================================
# EXPORT OPERATORS
# ============================================================================

class ONI_OT_RenderBadge(Operator):
    """Render badge to image"""
    bl_idname = "oni.render_badge"
    bl_label = "Render Badge"
    bl_description = "Render current view to image"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        oni = context.scene.oni
        
        try:
            output_path = bpy.path.abspath(oni.export_path)
            if not output_path.endswith('.png'):
                output_path += '.png'
            
            ONIExporter.render_image(
                output_path,
                resolution_x=oni.render_resolution_x,
                resolution_y=oni.render_resolution_y,
                samples=oni.render_samples
            )
            
            self.report({'INFO'}, f"Rendered to: {output_path}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to render: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class ONI_OT_ExportBadge(Operator):
    """Export badge to 3D format"""
    bl_idname = "oni.export_badge"
    bl_label = "Export Badge"
    bl_description = "Export to 3D file format"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        oni = context.scene.oni
        
        try:
            output_path = bpy.path.abspath(oni.export_path)
            
            if oni.export_format == 'GLTF':
                if not output_path.endswith('.glb'):
                    output_path += '.glb'
                ONIExporter.export_gltf(output_path)
            
            elif oni.export_format == 'FBX':
                if not output_path.endswith('.fbx'):
                    output_path += '.fbx'
                ONIExporter.export_fbx(output_path)
            
            self.report({'INFO'}, f"Exported to: {output_path}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

