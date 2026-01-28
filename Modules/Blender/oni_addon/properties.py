"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
ONI Add-on Properties
All properties for the ONI system
"""

import bpy
from bpy.props import (
    StringProperty, BoolProperty, IntProperty,
    FloatProperty, EnumProperty, CollectionProperty
)
from bpy.types import PropertyGroup


class ONIProperties(PropertyGroup):
    """ONI system properties"""
    
    # Badge parameters
    badge_name: StringProperty(
        name="Name",
        description="Name to display on badge",
        default="AGENT NAME"
    )
    
    badge_title: StringProperty(
        name="Title",
        description="Title/role to display",
        default="SECURITY"
    )
    
    badge_id: StringProperty(
        name="ID",
        description="Badge ID number",
        default="A7F3-9182"
    )
    
    # Seed management
    current_seed: StringProperty(
        name="Current Seed",
        description="Current random seed",
        default=""
    )
    
    seed_prefix: StringProperty(
        name="Seed Prefix",
        description="3-letter prefix for seed generation",
        default="BLD",
        maxlen=3
    )
    
    auto_generate_seed: BoolProperty(
        name="Auto Generate Seed",
        description="Automatically generate new seed for each badge",
        default=True
    )
    
    seed_history: CollectionProperty(
        type=bpy.types.PropertyGroup,
        name="Seed History"
    )
    
    # Style selection
    style_palette: EnumProperty(
        name="Style Palette",
        description="Choose style from database",
        items=[
            ('cyberpunk_v1', 'Cyberpunk Neon', 'High-tech dystopian aesthetic'),
            ('brutalism_v1', 'Digital Brutalism', 'Raw utilitarian design'),
            ('minimalism_v1', 'Minimalism', 'Clean and simple'),
            ('glitch_art_v1', 'Glitch Art', 'Digital corruption aesthetic'),
            ('vaporwave_v1', 'Vaporwave', '80s/90s retro aesthetic'),
            ('japanese_tech_v1', 'Japanese Tech', 'Neo-Tokyo interface'),
            ('organic_synthwave_v1', 'Synthwave', '80s neon gradient'),
            ('industrial_v1', 'Industrial', 'Mechanical and rugged'),
        ],
        default='cyberpunk_v1'
    )
    
    color_category: EnumProperty(
        name="Color Category",
        description="Color category from palette",
        items=[
            ('primary', 'Primary', 'Primary colors'),
            ('accent', 'Accent', 'Accent colors'),
            ('background', 'Background', 'Background colors'),
        ],
        default='primary'
    )
    
    # Greebles
    greeble_count: IntProperty(
        name="Greeble Count",
        description="Number of greebles to generate",
        default=15,
        min=0,
        max=100
    )
    
    greeble_min_size: FloatProperty(
        name="Min Size",
        description="Minimum greeble size",
        default=0.05,
        min=0.01,
        max=1.0
    )
    
    greeble_max_size: FloatProperty(
        name="Max Size",
        description="Maximum greeble size",
        default=0.15,
        min=0.01,
        max=2.0
    )
    
    # Scene setup
    clear_before_generate: BoolProperty(
        name="Clear Scene",
        description="Clear scene before generating new badge",
        default=True
    )
    
    auto_setup_camera: BoolProperty(
        name="Auto Setup Camera",
        description="Automatically setup camera",
        default=True
    )
    
    auto_setup_lighting: BoolProperty(
        name="Auto Setup Lighting",
        description="Automatically setup lighting",
        default=True
    )
    
    lighting_style: EnumProperty(
        name="Lighting Style",
        description="Lighting setup style",
        items=[
            ('THREE_POINT', 'Three-Point', 'Classic 3-point lighting'),
            ('CYBERPUNK', 'Cyberpunk', 'Neon cyberpunk lighting'),
        ],
        default='CYBERPUNK'
    )
    
    # Render settings
    render_resolution_x: IntProperty(
        name="Resolution X",
        description="Render resolution width",
        default=1920,
        min=128,
        max=8192
    )
    
    render_resolution_y: IntProperty(
        name="Resolution Y",
        description="Render resolution height",
        default=1080,
        min=128,
        max=8192
    )
    
    render_samples: IntProperty(
        name="Samples",
        description="Render samples for quality",
        default=128,
        min=1,
        max=4096
    )
    
    # Export settings
    export_path: StringProperty(
        name="Export Path",
        description="Path to export files",
        default="//output/badge",
        subtype='FILE_PATH'
    )
    
    export_format: EnumProperty(
        name="Export Format",
        description="3D file export format",
        items=[
            ('GLTF', 'glTF/GLB', 'Export as glTF/GLB format'),
            ('FBX', 'FBX', 'Export as FBX format'),
        ],
        default='GLTF'
    )

