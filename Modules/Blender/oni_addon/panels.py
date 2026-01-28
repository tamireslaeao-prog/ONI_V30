"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
ONI Add-on UI Panels
Sidebar panels for the 3D viewport
"""

import bpy
from bpy.types import Panel


class ONI_PT_MainPanel(Panel):
    """Main ONI panel in 3D viewport sidebar"""
    bl_label = "ONI Creativity Engine"
    bl_idname = "ONI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    
    def draw(self, context):
        layout = self.layout
        oni = context.scene.oni
        
        # Header
        box = layout.box()
        box.label(text="Procedural Badge Generation", icon='MESH_CUBE')
        
        # Badge parameters
        box = layout.box()
        box.label(text="Badge Parameters:")
        box.prop(oni, "badge_name")
        box.prop(oni, "badge_title")
        box.prop(oni, "badge_id")
        
        # Generate button
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("oni.generate_badge", icon='PLAY')
        
        # Quick actions
        row = layout.row(align=True)
        row.operator("oni.clear_scene", icon='TRASH')
        row.operator("oni.setup_camera", icon='OUTLINER_OB_CAMERA')
        row.operator("oni.setup_lighting", icon='LIGHT')


class ONI_PT_SeedPanel(Panel):
    """Seed management panel"""
    bl_label = "Seed Management"
    bl_idname = "ONI_PT_seed_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    bl_parent_id = "ONI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        oni = context.scene.oni
        
        # Current seed
        box = layout.box()
        box.label(text="Current Seed:")
        row = box.row()
        row.prop(oni, "current_seed", text="")
        
        # Seed options
        col = layout.column()
        col.prop(oni, "auto_generate_seed")
        col.prop(oni, "seed_prefix")
        
        # Generate new seed
        layout.operator("oni.new_seed", icon='FILE_REFRESH')
        
        # Seed history
        if oni.seed_history:
            box = layout.box()
            box.label(text="Recent Seeds:")
            for seed in oni.seed_history[-5:]:  # Last 5 seeds
                box.label(text=seed, icon='DECORATE')


class ONI_PT_StylePanel(Panel):
    """Style selection panel"""
    bl_label = "Style & Colors"
    bl_idname = "ONI_PT_style_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    bl_parent_id = "ONI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        oni = context.scene.oni
        
        # Style selection
        box = layout.box()
        box.label(text="Style Palette:")
        box.prop(oni, "style_palette", text="")
        box.prop(oni, "color_category", text="Category")
        
        # Apply style
        layout.operator("oni.apply_style", icon='MATERIAL')
        
        # Greebles
        box = layout.box()
        box.label(text="Greebles:")
        box.prop(oni, "greeble_count")
        row = box.row(align=True)
        row.prop(oni, "greeble_min_size")
        row.prop(oni, "greeble_max_size")
        box.operator("oni.generate_greebles", icon='MESH_DATA')


class ONI_PT_ScenePanel(Panel):
    """Scene setup panel"""
    bl_label = "Scene Setup"
    bl_idname = "ONI_PT_scene_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    bl_parent_id = "ONI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        oni = context.scene.oni
        
        # Generation options
        box = layout.box()
        box.label(text="Generation Options:")
        box.prop(oni, "clear_before_generate")
        box.prop(oni, "auto_setup_camera")
        box.prop(oni, "auto_setup_lighting")
        
        # Lighting style
        box = layout.box()
        box.label(text="Lighting Style:")
        box.prop(oni, "lighting_style", text="")


class ONI_PT_ExportPanel(Panel):
    """Export and rendering panel"""
    bl_label = "Export & Render"
    bl_idname = "ONI_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    bl_parent_id = "ONI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        oni = context.scene.oni
        
        # Render settings
        box = layout.box()
        box.label(text="Render Settings:")
        row = box.row(align=True)
        row.prop(oni, "render_resolution_x", text="X")
        row.prop(oni, "render_resolution_y", text="Y")
        box.prop(oni, "render_samples")
        
        # Export path
        box = layout.box()
        box.label(text="Export Path:")
        box.prop(oni, "export_path", text="")
        box.prop(oni, "export_format", text="Format")
        
        # Export buttons
        col = layout.column(align=True)
        col.scale_y = 1.3
        col.operator("oni.render_badge", icon='RENDER_STILL')
        col.operator("oni.export_badge", icon='EXPORT')

