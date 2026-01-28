
import bpy
import os
import sys

# Argument parsing for Blender scripts is tricky as acts as wrapper.
# We expect the last argument to be the SVG path.
argv = sys.argv
try:
    index = argv.index("--") + 1
except ValueError:
    index = len(argv)

if index < len(argv):
    svg_path = argv[index]
else:
    print("ONI: No SVG path provided.")
    # Fallback for testing or if injected differently
    svg_path = os.environ.get("ONI_SVG_PATH")

if svg_path and os.path.exists(svg_path):
    # clear default cube if it exists
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
        
    print(f"ONI: Importing {svg_path}...")
    bpy.ops.import_curve.svg(filepath=svg_path)
    
    # Post-process: Select all imported curves, scale, extrude
    # Imported SVG objects are usually curves.
    
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    imported_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE' and obj.select_get() == False] # Naive check?
    # Better: select by collection if SVG import creates one (usually creates a Collection named after file)
    
    # Just select all curves
    for obj in bpy.data.objects:
        if obj.type == 'CURVE':
            obj.select_set(True)
            # Extrude
            obj.data.extrude = 0.05
            obj.data.bevel_depth = 0.001
            
    # Scale up (SVG imports tiny in Blender usually)
    bpy.ops.transform.resize(value=(100, 100, 100))
    
    # Center
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    bpy.ops.view3d.camera_to_view_selected()
    
    print("ONI: Import & 3D Extrusion Complete.")
    
else:
    print(f"ONI Error: SVG not found: {svg_path}")
