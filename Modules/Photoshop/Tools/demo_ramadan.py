import sys
import os
import time
import shutil
import glob

# ROBUST PATH SETUP
# We are in Modules/Photoshop/Tools
# We need to import from Modules/Photoshop
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
EXTRACTOR = os.path.join(TOOLS_DIR, "oni_style_extractor.jsx")
APPLICATOR = os.path.join(TOOLS_DIR, "oni_style_applicator.jsx")
SOURCE_FILE = r"D:\DESIGN\psd_sources\37749682_ramadan_text_effect.psd"
JS_SOURCE = SOURCE_FILE.replace("\\", "/")

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
MASTER_JSON = os.path.join(DESKTOP, "ONI_STYLE_DATA.json")

def cleanup_old_json():
    """Remove old style data to ensure we capture fresh."""
    for f in glob.glob(os.path.join(DESKTOP, "ONI_STYLE_DATA*.json")):
        try:
            os.remove(f)
        except:
            pass

def find_best_style_json():
    """Find the best style JSON (Prioritize 'Surface' or 'Face')."""
    files = glob.glob(os.path.join(DESKTOP, "ONI_STYLE_DATA_*.json"))
    if not files:
        return None
    
    candidates = [f for f in files if "ONI_STYLE_DATA.json" not in f]
    if not candidates: return None

    # Priority 1: Keyword "Surface" or "Body" or "Face"
    priority = [f for f in candidates if any(k in f.lower() for k in ["surface", "face", "body", "main"])]
    
    if priority:
        # If we have priority matches, pick the largest of THOSE
        best = max(priority, key=os.path.getsize)
        print(f"   🎯 Priority Match: {os.path.basename(best)}")
        return best

    # Fallback: Largest file
    best = max(candidates, key=os.path.getsize)
    print(f"   ⚖️ Size Heuristic: {os.path.basename(best)}")
    return best

def demo_ramadan_clone():
    print("🌙 RAMADAN STYLE CLONING DEMO (CORRECTED)")
    
    # 0. Cleanup
    cleanup_old_json()

    # 1. Open Source
    print(f"📂 Opening {SOURCE_FILE}...")
    bridge.execute_code(f'app.open(new File("{JS_SOURCE}"));')
    time.sleep(5) 
    
    # 2. Extract Style
    print("⬇️ Extracting 'Ramadan' DNA (All Layers)...")
    bridge.execute_jsx(EXTRACTOR)
    time.sleep(3)
    
    # 3. Coordinate JSON
    print("🔄 Identifying 'Hero' Style...")
    best = find_best_style_json()
    if best:
        shutil.copy(best, MASTER_JSON)
        print(f"   ✅ HERO STYLE LOCKED: {os.path.basename(best)}")
    else:
        print("❌ ERROR: No Style Data extracted!")
        return
    
    # 4. Create Target
    print("🆕 Creating Verification Canvas...")
    bridge.canvas.create(1920, 1080, "ONI_RAMADAN_CLONE")
    bridge.execute_code('ONI_PS.Canvas.FillBackground(ONI_PS.Core.HexColor("101010"));')
    
    # 5. Create Text
    print("✍️ Writing 'ONI AI'...")
    bridge.layers.create_text("ONI AI", 960, 540, 250, "FFFFFF")
    
    # 6. Apply Style
    print("✨ Applying Hero Style...")
    bridge.execute_jsx(APPLICATOR)
    
    print("✅ DEMO COMPLETE.")

if __name__ == "__main__":
    demo_ramadan_clone()
