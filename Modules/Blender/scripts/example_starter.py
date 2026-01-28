"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
============================================================================
Complete Badge Generation Example
Save as: generate_complete_badge.py
Run in Blender: Alt+P in Text Editor
============================================================================
"""

import bpy
import sys
from pathlib import Path

# ============================================================================
# SETUP: Add ONI to path
# ============================================================================

# AUTOMATICALLY POINT TO CURRENT PROJECT ROOT
SCRIPT_PATH = Path(__file__).resolve()
ONI_PATH = str(SCRIPT_PATH.parent.parent) 

if ONI_PATH not in sys.path:
    sys.path.append(ONI_PATH)

# Import ONI modules
try:
    from ONI_Gen import seed_manager, color_gen, geometry_gen
    from ONI_BlenderAutomation import (
        ONIBadgeGenerator, 
        ONICameraSetup, 
        ONILightingSetup,
        ONIExporter,
        BlenderConnection,
        ONIMaterialCreator,
        ONIObjectCreator
    )
    print("✓ ONI modules loaded")
except ImportError as e:
    print(f"✗ Error: {e}")
    print("Make sure ONI_PATH is correct!")


# ============================================================================
# EXAMPLE 1: Quick Badge
# ============================================================================

def example_quick_badge():
    """Simplest way to generate a badge"""
    
    print("\n=== Example 1: Quick Badge ===")
    
    # Clear scene
    BlenderConnection.clear_scene()
    
    # Generate badge
    result = ONIBadgeGenerator.create_cyberpunk_badge(
        name="ALEX MERCER",
        title="CYBER SECURITY",
        badge_id="CS-4729",
        style="cyberpunk_v1"
    )
    
    # Setup camera and lighting
    ONICameraSetup.create_badge_camera()
    ONILightingSetup.create_cyberpunk_lighting("#00F0FF")
    
    print(f"✓ Badge created with seed: {result['seed']}")
    print(f"  Objects: {len(result['objects'])} items")


# ============================================================================
# EXAMPLE 2: Custom Badge with Specific Seed
# ============================================================================

def example_custom_seed():
    """Generate badge with reproducible seed"""
    
    print("\n=== Example 2: Custom Seed ===")
    
    # Set specific seed for reproducibility
    seed = "ONI-DEMO-20260104-A1B2"
    seed_manager.set_seed(seed)
    print(f"Using seed: {seed}")
    
    # Clear and generate
    BlenderConnection.clear_scene()
    
    result = ONIBadgeGenerator.create_cyberpunk_badge(
        name="REPRODUCTION TEST",
        title="SAME EVERY TIME",
        badge_id="REP-0001"
    )
    
    ONICameraSetup.create_badge_camera()
    ONILightingSetup.create_cyberpunk_lighting()
    
    print("✓ Badge will look identical every time with this seed")


# ============================================================================
# EXAMPLE 3: Custom Materials and Colors
# ============================================================================

def example_custom_materials():
    """Create badge with custom materials"""
    
    print("\n=== Example 3: Custom Materials ===")
    
    BlenderConnection.clear_scene()
    
    # Get random colors from palette
    primary_color = color_gen.get_random_color("cyberpunk_v1", "primary")
    accent_color = color_gen.get_random_color("cyberpunk_v1", "accent")
    
    print(f"Primary color: {primary_color}")
    print(f"Accent color: {accent_color}")
    
    # Create badge base
    base = ONIBadgeGenerator.create_badge_base(
        width=8.56,
        height=5.398,
        thickness=0.1,
        corner_radius=0.3
    )
    
    # Create custom material
    custom_mat = ONIMaterialCreator.create_cyberpunk_material(
        "Custom_Badge_Mat",
        hex_color=primary_color,
        glow_intensity=3.0
    )
    
    ONIMaterialCreator.apply_material(base, custom_mat)
    
    # Add text
    name_text = ONIObjectCreator.create_text(
        text="CUSTOM DESIGN",
        location=(-2, 0, 0.1),
        size=0.5,
        extrude=0.1
    )
    
    text_mat = ONIMaterialCreator.create_emission_material(
        "Text_Mat",
        color=color_gen.hex_to_rgba(accent_color),
        strength=2.5
    )
    
    ONIMaterialCreator.apply_material(name_text, text_mat)
    
    print("✓ Custom materials applied")


# ============================================================================
# EXAMPLE 4: Multiple Variations
# ============================================================================

def example_variations():
    """Generate multiple badge variations"""
    
    print("\n=== Example 4: Multiple Variations ===")
    
    BlenderConnection.clear_scene()
    
    names = ["AGENT ALPHA", "AGENT BETA", "AGENT GAMMA"]
    
    for i, name in enumerate(names):
        # Generate seed
        seed = seed_manager.generate_seed(f"VAR")
        print(f"Variation {i+1} seed: {seed}")
        
        # Create badge (offset position for each)
        result = ONIBadgeGenerator.create_cyberpunk_badge(
            name=name,
            title=f"OPERATIVE {i+1}",
            badge_id=f"OP-{i+1:04d}"
        )
        
        # Move badge to avoid overlap
        for obj in result['objects']['greebles']:
            obj.location.x += i * 10
        
        result['objects']['base'].location.x += i * 10
    
    # Single camera for all
    camera = ONICameraSetup.create_badge_camera()
    camera.location.x = 10  # Center on middle badge
    
    ONILightingSetup.create_cyberpunk_lighting()
    
    print(f"✓ Created {len(names)} variations")


# ============================================================================
# EXAMPLE 5: Batch Generation from Data
# ============================================================================

def example_batch_from_data():
    """Generate badges from employee data"""
    
    print("\n=== Example 5: Batch Generation ===")
    
    # Sample employee data
    employees = [
        {"name": "John Smith", "title": "Manager", "id": "EMP-001"},
        {"name": "Jane Doe", "title": "Engineer", "id": "EMP-002"},
        {"name": "Bob Johnson", "title": "Designer", "id": "EMP-003"},
    ]
    
    for i, emp in enumerate(employees):
        print(f"Processing: {emp['name']}")
        
        # Clear scene
        BlenderConnection.clear_scene()
        
        # Generate badge
        seed = seed_manager.generate_seed("BATCH")
        result = ONIBadgeGenerator.create_cyberpunk_badge(
            name=emp['name'],
            title=emp['title'],
            badge_id=emp['id']
        )
        
        # Setup scene
        ONICameraSetup.create_badge_camera()
        ONILightingSetup.create_cyberpunk_lighting()
        
        # Render to file
        output_path = f"//output/badge_{emp['id']}.png"
        bpy.context.scene.render.filepath = output_path
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        
        # Optional: Uncomment to actually render
        # bpy.ops.render.render(write_still=True)
        
        print(f"  ✓ Badge ready (render path: {output_path})")
    
    print(f"\n✓ Processed {len(employees)} employees")


# ============================================================================
# EXAMPLE 6: Custom Geometry
# ============================================================================

def example_custom_geometry():
    """Create badge with custom geometric elements"""
    
    print("\n=== Example 6: Custom Geometry ===")
    
    BlenderConnection.clear_scene()
    
    # Create collection
    col = BlenderConnection.get_collection("Custom_Badge")
    
    # Base card
    base = ONIBadgeGenerator.create_badge_base()
    col.objects.link(base)
    bpy.context.scene.collection.objects.unlink(base)
    
    # Add geometric greebles manually
    primary_color = color_gen.get_random_color("cyberpunk_v1", "primary")
    
    for i in range(20):
        # Random position
        pos = geometry_gen.random_point_3d(
            x_min=-3, x_max=3,
            y_min=-2, y_max=2,
            z_min=0.06, z_max=0.06
        )
        
        # Random type
        greeble_type = ["cube", "cylinder", "sphere"][i % 3]
        
        if greeble_type == "cube":
            obj = ONIObjectCreator.create_cube(
                f"Greeble_{i}",
                size=0.1,
                location=pos,
                collection="Custom_Badge"
            )
        elif greeble_type == "cylinder":
            obj = ONIObjectCreator.create_cylinder(
                f"Greeble_{i}",
                radius=0.05,
                depth=0.1,
                location=pos,
                collection="Custom_Badge"
            )
        else:
            obj = ONIObjectCreator.create_sphere(
                f"Greeble_{i}",
                radius=0.05,
                location=pos,
                collection="Custom_Badge"
            )
        
        # Apply material
        mat = ONIMaterialCreator.create_emission_material(
            f"Greeble_Mat_{i}",
            color=color_gen.hex_to_rgba(primary_color),
            strength=2.0
        )
        ONIMaterialCreator.apply_material(obj, mat)
    
    ONICameraSetup.create_badge_camera()
    ONILightingSetup.create_cyberpunk_lighting()
    
    print("✓ Custom geometry badge created")


# ============================================================================
# EXAMPLE 7: Export to Multiple Formats
# ============================================================================

def example_export_formats():
    """Generate and export to multiple formats"""
    
    print("\n=== Example 7: Export Formats ===")
    
    BlenderConnection.clear_scene()
    
    # Generate badge
    result = ONIBadgeGenerator.create_cyberpunk_badge(
        name="EXPORT TEST",
        title="MULTI-FORMAT",
        badge_id="EXP-001"
    )
    
    ONICameraSetup.create_badge_camera()
    ONILightingSetup.create_cyberpunk_lighting()
    
    # Export to different formats
    base_path = "//output/export_test"
    
    # PNG render
    print("Rendering PNG...")
    bpy.context.scene.render.filepath = f"{base_path}.png"
    # bpy.ops.render.render(write_still=True)  # Uncomment to render
    
    # glTF export
    print("Exporting glTF...")
    # ONIExporter.export_gltf(f"{base_path}.glb")  # Uncomment to export
    
    # FBX export
    print("Exporting FBX...")
    # ONIExporter.export_fbx(f"{base_path}.fbx")  # Uncomment to export
    
    print("✓ Export setup complete (uncomment lines to actually export)")


# ============================================================================
# MAIN: Run Examples
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ONI BLENDER - Complete Examples")
    print("="*60)
    
    # Run desired example (uncomment one)
    
    example_quick_badge()           # Example 1: Simplest usage
    # example_custom_seed()          # Example 2: Reproducible results
    # example_custom_materials()     # Example 3: Custom materials
    # example_variations()           # Example 4: Multiple badges
    # example_batch_from_data()      # Example 5: Batch processing
    # example_custom_geometry()      # Example 6: Custom geometry
    # example_export_formats()       # Example 7: Export formats
    
    print("\n" + "="*60)
    print("✓ Example complete!")
    print("="*60)
    print("\nTips:")
    print("- Press Numpad 0 for camera view")
    print("- Press Z → Material Preview for colors")
    print("- Press F12 to render")
    print("- Uncomment other examples to try them")


# ============================================================================
# QUICK FUNCTIONS (call these directly)
# ============================================================================

def quick_badge(name="AGENT", title="SECURITY", id="ID-001"):
    """Quick badge - copy to console"""
    BlenderConnection.clear_scene()
    result = ONIBadgeGenerator.create_cyberpunk_badge(name, title, id)
    ONICameraSetup.create_badge_camera()
    ONILightingSetup.create_cyberpunk_lighting()
    return result

def clear():
    """Quick clear scene"""
    BlenderConnection.clear_scene()

def new_seed(prefix="BLD"):
    """Generate and print new seed"""
    seed = seed_manager.generate_seed(prefix)
    print(f"New seed: {seed}")
    return seed


# ============================================================================
# CONSOLE COMMANDS
# ============================================================================

"""
Copy these to Blender Python Console for quick testing:

# Generate quick badge
quick_badge("YOUR NAME", "YOUR TITLE", "ID-001")

# Clear scene
clear()

# New seed
new_seed("TEST")

# Get random color
from ONI_Gen import color_gen
color_gen.get_random_color("cyberpunk_v1", "primary")

# Create single object
from ONI_BlenderAutomation import ONIObjectCreator
ONIObjectCreator.create_cube("Test", size=2, location=(0,0,0))
"""

