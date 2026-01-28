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
HARVESTER = os.path.join(TOOLS_DIR, "oni_element_harvester.jsx")
SOURCE_FILE = r"D:\DESIGN\psd_sources\37749682_ramadan_text_effect.psd" # Ramadan
JS_SOURCE = SOURCE_FILE.replace("\\", "/")

def demo_smart_transfer():
    print("🚀 ONI SMART ELEMENT TRANSFER")
    print("   Strategy: Clone the entire Group/SmartObject instead of styles.")
    
    # 1. Open Source
    print(f"📂 Opening Source: {os.path.basename(SOURCE_FILE)}...")
    bridge.execute_code(f'app.open(new File("{JS_SOURCE}"));')
    time.sleep(4) 
    
    # 2. Select the 'Hero' Element
    # In 'Ramadan', the main effect is efficiently grouped or is a Smart Object.
    # We will try to select the main group 'Ramadan' or similar.
    # PSD Structure allows us to scan for "Text" or "Effect" groups.
    print("🔍 Selecting Hero Element...")
    js_select = """
    function selectHero() {
        var doc = app.activeDocument;
        var hero = null;
        
        // Try exact name match from user knowledge or generic 'Effect'
        // Scan top level layers
        for (var i=0; i < doc.layers.length; i++) {
            var name = doc.layers[i].name.toLowerCase();
            if (name.indexOf("ramadan") != -1 || name.indexOf("text") != -1 || name.indexOf("effect") != -1) {
                doc.activeLayer = doc.layers[i];
                return doc.layers[i].name;
            }
        }
        return "Manual Selection (Active)";
    }
    selectHero();
    """
    res = bridge.execute_code(js_select)
    print(f"   Selected: {res['output']}")
    
    # 3. Harvest
    print("📦 Harvesting Element to Target...")
    # This script automatically finds the *other* open document (ONI_RAMADAN_CLONE) or creates one
    bridge.execute_jsx(HARVESTER)
    
    print("✅ TRANSFER COMPLETE.")
    print("   The entire element is now in your target document.")
    print("   You may edit the Smart Object text to customize it.")

if __name__ == "__main__":
    demo_smart_transfer()
