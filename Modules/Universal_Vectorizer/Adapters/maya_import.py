
import maya.cmds as cmds
import os
import sys

# ONI Maya Adapter
# This script is meant to be executed via 'mayapy.exe' or 'maya.exe -command "python..."'

def import_oni_svg():
    # Retrieve path from environment or temp file since argument passing to maya GUI is hard
    svg_path = os.environ.get("ONI_SVG_PATH")
    
    if not svg_path or not os.path.exists(svg_path):
        print("ONI Error: SVG Path not found in environment ONI_SVG_PATH")
        return

    print(f"ONI: Importing {svg_path} into Maya...")
    
    # Import
    # Maya 2022+ supports SVG import more reliably.
    try:
        # Group imported objects
        cmds.file(svg_path, i=True, type="SVG", groupReference=True, groupName="ONI_Vector_Group")
        
        # Center view
        cmds.viewFit(all=True)
        print("ONI: Import Successful.")
        
    except Exception as e:
        print(f"ONI Import Error: {e}")
        # Fallback suggestion
        print("Try converting to AI (Illustrator 8) format if SVG fails.")

if __name__ == "__main__":
    import_oni_svg()
