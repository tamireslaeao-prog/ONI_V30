"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
============================================================================
ONI Creativity Engine - Blender Add-on
Version: 1.0.0
Description: Procedural 3D badge generation with style DNA
============================================================================
"""

bl_info = {
    "name": "ONI Creativity Engine",
    "author": "ONI Studio",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > ONI",
    "description": "Procedural badge generation with style DNA and random seeds",
    "category": "3D View",
    "doc_url": "https://github.com/oni-studio/blender-oni",
    "tracker_url": "https://github.com/oni-studio/blender-oni/issues"
}

import bpy
import sys
from pathlib import Path

# Add ONI modules to path
addon_dir = Path(__file__).parent
if str(addon_dir) not in sys.path:
    sys.path.append(str(addon_dir))

# Import ONI modules
from . import operators
from . import panels
from . import properties

# Classes to register
classes = (
    # Properties
    properties.ONIProperties,
    
    # Operators
    operators.ONI_OT_GenerateBadge,
    operators.ONI_OT_NewSeed,
    operators.ONI_OT_ApplyStyle,
    operators.ONI_OT_GenerateGreebles,
    operators.ONI_OT_ClearScene,
    operators.ONI_OT_SetupCamera,
    operators.ONI_OT_SetupLighting,
    operators.ONI_OT_RenderBadge,
    operators.ONI_OT_ExportBadge,
    
    # Panels
    panels.ONI_PT_MainPanel,
    panels.ONI_PT_SeedPanel,
    panels.ONI_PT_StylePanel,
    panels.ONI_PT_ScenePanel,
    panels.ONI_PT_ExportPanel,
)


def register():
    """Register add-on"""
    from bpy.utils import register_class
    
    # Register classes
    for cls in classes:
        register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.oni = bpy.props.PointerProperty(type=properties.ONIProperties)
    
    print("ONI Creativity Engine registered")


def unregister():
    """Unregister add-on"""
    from bpy.utils import unregister_class
    
    # Unregister classes
    for cls in reversed(classes):
        unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.oni
    
    print("ONI Creativity Engine unregistered")


if __name__ == "__main__":
    register()

