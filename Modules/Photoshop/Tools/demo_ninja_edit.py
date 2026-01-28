import sys
import os
import time

# Path Setup
# Path Setup (Portable)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) # Modules/Photoshop -> Modules -> ONI_V30
sys.path.append(os.path.join(MODULE_ROOT, "Modules", "Photoshop"))

try:
    from ONI_Photoshop_Bridge import PhotoshopBridge
except ImportError:
    # If module structure is different, try direct append
    sys.path.append(os.path.dirname(SCRIPT_DIR)) 
    from ONI_Photoshop_Bridge import PhotoshopBridge

bridge = PhotoshopBridge()
TOOLS_DIR = current_dir
REPLACER = os.path.join(TOOLS_DIR, "oni_smart_text_replacer.jsx")

def demo_ninja_edit():
    print("🐱‍👤 NINJA EDIT: UPDATING SMART OBJECT TEXT")
    
    # Assumes the Target Document (ONI_HARVEST_TARGET) is active and the Smart Object is selected.
    # We will trigger "Edit Contents"
    
    print("🔓 Opening Smart Object...")
    # This runs: app.activeDocument.activeLayer = app.activeDocument.activeLayer; executeAction(stringIDToTypeID("placedLayerEditContents")...
    bridge.smart_objects.edit_contents()
    
    time.sleep(4) # Wait for PSB to open
    
    print("✍️ Updating Text to 'ONI'...")
    bridge.execute_jsx(REPLACER)
    time.sleep(1)
    
    print("💾 Saving & Closing PSB...")
    bridge.execute_code("app.activeDocument.close(SaveOptions.SAVECHANGES);")
    time.sleep(3) # Wait for render update in main doc
    
    print("✅ NINJA STRIKE SUCCESSFUL.")
    print("   Check your main document.")

if __name__ == "__main__":
    demo_ninja_edit()
