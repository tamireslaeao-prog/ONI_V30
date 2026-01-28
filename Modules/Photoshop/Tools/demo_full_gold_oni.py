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
REPLACER = os.path.join(TOOLS_DIR, "oni_smart_text_replacer.jsx")
SOURCE_FILE = r"D:\DESIGN\psd_sources\37749682_ramadan_text_effect.psd" 
JS_SOURCE = SOURCE_FILE.replace("\\", "/")

def run_full_gold_workflow():
    print("🌟 ONI GOLD PROTOCOL: INITIATING...")
    print("   Target: Produce 'ONI' text using Premium Gold Assets.")

    # 1. Open Source Asset
    print(f"📂 1. Opening Asset: {os.path.basename(SOURCE_FILE)}...")
    bridge.execute_code(f'app.open(new File("{JS_SOURCE}"));')
    time.sleep(5) 
    
    # 2. Select Hero Group (Ramadan)
    print("🎯 2. Identifying Hero Element...")
    js_select = """
    function selectHero() {
        var doc = app.activeDocument;
        for (var i=0; i < doc.layers.length; i++) {
            var name = doc.layers[i].name.toLowerCase();
            // Look for 'Ramadan' group or smart object
            if (name.indexOf("ramadan") != -1) {
                doc.activeLayer = doc.layers[i];
                return doc.layers[i].name;
            }
        }
        return "Manual Selection";
    }
    selectHero();
    """
    bridge.execute_code(js_select)
    
    # 3. Harvest to New Document
    print("📦 3. Transplaning to 'ONI_GOLD_MASTER'...")
    # Harvester creates "ONI_HARVEST_TARGET" if needed
    bridge.execute_jsx(HARVESTER)
    time.sleep(2)
    
    # 4. Close Source (Cleanup)
    print("🧹 4. Closing Source...")
    # We need to find the source doc and close it, leaving Target open.
    # But Harvester switches activeDoc to Target. So we assume Source is NOT active.
    # Safe way: Close '37749682...' by name.
    js_close_source = f'''
    var sourceName = "{os.path.basename(SOURCE_FILE)}";
    try {{
        app.documents.getByName(sourceName).close(SaveOptions.DONOTSAVECHANGES);
    }} catch(e) {{}}
    '''
    bridge.execute_code(js_close_source)
    time.sleep(1)
    
    # 5. Ninja Edit (Edit Content)
    print("🐱‍👤 5. Breaking into Smart Object...")
    # We are now in ONI_HARVEST_TARGET. Active layer is the harvested element.
    bridge.smart_objects.edit_contents()
    time.sleep(4) # Wait for PSB
    
    # 6. Replace Text
    print("✍️ 6. Rewriting History ('Ramadan' -> 'ONI')...")
    bridge.execute_jsx(REPLACER)
    time.sleep(1)
    
    # 7. Save & Exit Smart Object
    print("💾 7. Sealing Smart Object...")
    bridge.execute_code("app.activeDocument.close(SaveOptions.SAVECHANGES);")
    time.sleep(3)
    
    # 8. Save Final Result (The Main Doc)
    print("📀 8. Saving Final 'ONI_HARVEST_TARGET.psd'...")
    # It assumes the active document is now the main one
    js_save_final = """
    var doc = app.activeDocument;
    var file = new File(Folder.desktop + "/ONI_HARVEST_TARGET.psd");
    var opts = new PhotoshopSaveOptions();
    opts.layers = true;
    opts.embedColorProfile = true;
    
    // SURGICAL SILENCE
    var initialDialogMode = app.displayDialogs;
    app.displayDialogs = DialogModes.NO;
    
    try {
        doc.saveAs(file, opts, true, Extension.LOWERCASE);
    } catch(e) {
        // Retry with just save() if file exists and is active? 
        // No, saveAs with overwrite confirmation suppressed by DialogModes.NO
    } finally {
        app.displayDialogs = initialDialogMode;
        doc.close(SaveOptions.DONOTSAVECHANGES);
    }
    """
    bridge.execute_code(js_save_final)
    
    print("✨ GOLD PROTOCOL COMPLETE.")
    print("   File saved to Desktop: ONI_HARVEST_TARGET.psd")

if __name__ == "__main__":
    run_full_gold_workflow()
