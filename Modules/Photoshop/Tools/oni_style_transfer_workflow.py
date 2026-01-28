import os
import sys
import time
import argparse

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ONI_Photoshop_Bridge import PhotoshopBridge

bridge = PhotoshopBridge()
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTOR = os.path.join(TOOLS_DIR, "oni_style_extractor.jsx")
APPLICATOR = os.path.join(TOOLS_DIR, "oni_style_applicator.jsx")

def run_transfer(source_file=None):
    print("🎨 ONI STYLE TRANSFER WORKFLOW")
    
    # 1. Open Source (if provided)
    if source_file:
        print(f"📂 Opening Source: {source_file}")
        bridge.execute_code(f'app.open(new File("{source_file.replace(os.sep, "/") }"));')
        time.sleep(2) # Wait for load
    
    print("⏳ Please ensure the TARGET LAYER is active in Photoshop.")
    # In a real auto-flow, we'd use code to select the layer with effects.
    # For now, we assume the opened doc has the style we want active.
    
    # 2. Extract
    print("⬇️ Extracting Style from Active Layer...")
    res = bridge.execute_jsx(EXTRACTOR)
    print(f"   Extractor Result: {res}")
    
    # Check if JSON exists
    json_path = os.path.join(os.path.expanduser("~"), "Desktop", "ONI_STYLE_DATA.json") # Default export path
    # Check "Transfer" logic? 
    # Actually extractor saves to Desktop/ONI_STYLE_DATA_Master.json usually, need to check source.
    # oni_style_extractor.jsx line 137: layer_name used in suffix.
    # We might need to handle dynamic filenames.
    
    # 3. Apply
    print("✨ To apply this style to another document:")
    print("   1. Switch to Target Document.")
    print("   2. Select Target Layer.")
    print("   3. Run: python oni_style_transfer_workflow.py --apply")

def run_apply():
    print("🎨 APPLYING STYLE...")
    res = bridge.execute_jsx(APPLICATOR)
    print(f"   Applicator Result: {res}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Path to PSD file source")
    parser.add_argument("--apply", action="store_true", help="Apply extracted style to current doc")
    args = parser.parse_args()
    
    if args.apply:
        run_apply()
    else:
        run_transfer(args.source)
