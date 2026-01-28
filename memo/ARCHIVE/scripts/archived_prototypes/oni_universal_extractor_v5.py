"""
ONI Universal Extractor V5 (Hybrid Bridge)
------------------------------------------
The Ultimate Solution: Python Logic + Photoshop Engine.

Workflow:
1. Scans folder for PSDs.
2. Opens Photoshop via COM.
3. Opens each PSD.
4. Injects 'oni_extract_style_generic.jsx' to extract Deep Data (Colors/Gradients).
5. Reads the generated JSON.
6. Auto-Categorizes the style (Gold/Metal/etc).
7. Moves JSON to library.

Requirement: pip install pywin32
"""

import os
import json
import time
import shutil
import traceback
from pathlib import Path

# Try importing win32com, graceful exit if missing
try:
    import win32com.client
except ImportError:
    print("CRITICAL: 'pywin32' not installed. Please install it to drive Photoshop.")
    exit(1)

# CONFIG
TARGET_DIR = Path(r"C:\Users\user\Desktop\ONIV24\temp\Nova pasta")
OUTPUT_BASE = Path(r"C:\Users\user\Desktop\ONIV24\data\styles")
JSX_SCRIPT = Path(r"C:\Users\user\Desktop\ONIV24\app\scripts\oni_extract_style_generic.jsx")

TEMP_JSON = Path(os.path.expanduser("~")) / "Desktop" / "ONI_TEMP_EXTRACTION.json"
TEMP_ERROR = Path(os.path.expanduser("~")) / "Desktop" / "ONI_TEMP_ERROR.txt"

def categorize_style(json_data):
    """
    Analyzes style data to determine category: Gold, Metal, Neon, Generic.
    Heuristic: Look for colors + Keywords.
    """
    # Quick heuristics based on keywords or dominant colors
    # For now, simplistic check, can be expanded with Color Theory logic later.
    
    score_gold = 0
    score_metal = 0
    
    # Flatten all colors relevant to the style
    all_hexes = []
    
    for style in json_data.get('styles', []):
        for fx in style.get('effects', []):
            # Check effect types
            if fx.get('type') == 'bevel_emboss': score_metal += 1
            if fx.get('type') == 'gradient_overlay': score_metal += 1
            
            # Check colors inside gradients
            if 'gradient' in fx and 'colors' in fx['gradient']:
                for stop in fx['gradient']['colors']:
                    if 'color' in stop and 'hex' in stop['color']:
                        all_hexes.append(stop['color']['hex'])
            
            # Check basic colors
            if 'color' in fx and 'hex' in fx['color']:
                all_hexes.append(fx['color']['hex'])

    # Analyze Hexes for "Gold-ness" (Yellow/Orange)
    # Simple check: R > B and G > B (Yellowish)
    for h in all_hexes:
        try:
            r = int(h[1:3], 16)
            g = int(h[3:5], 16)
            b = int(h[5:7], 16)
            
            if r > 180 and g > 150 and b < 100: # Typical Gold
                score_gold += 5
            elif r > 150 and g > 150 and b > 150 and abs(r-g) < 20: # Silver/Gray
                score_metal += 2
        except: pass

    if score_gold > score_metal and score_gold > 5: return "gold"
    if score_metal > 5: return "metal"
    return "generic"

def main():
    print("🚀 ONI Universal Extractor V5 (Hybrid Mode)")
    print(f"Target: {TARGET_DIR}")
    
    if not TARGET_DIR.exists():
        print(f"Error: Directory not found: {TARGET_DIR}")
        return

    # Initialize Photoshop
    try:
        print("🔌 Connecting to Photoshop...")
        ps_app = win32com.client.Dispatch("Photoshop.Application")
        ps_app.DisplayDialogs = 3 # PsDisplayNoDialogs
    except Exception as e:
        print(f"❌ Failed to connect to Photoshop: {e}")
        return

    # Scan Files
    psd_files = list(TARGET_DIR.rglob("*.psd"))
    print(f"Found {len(psd_files)} PSDs.")

    for i, psd_file in enumerate(psd_files):
        print(f"\nProcessing [{i+1}/{len(psd_files)}]: {psd_file.name}")
        
        try:
            # 1. Open File
            print("  Opening...")
            doc = ps_app.Open(str(psd_file))
            
            # 2. Cleanup Temp Files
            if TEMP_JSON.exists(): TEMP_JSON.unlink()
            if TEMP_ERROR.exists(): TEMP_ERROR.unlink()
            
            # 3. Run JSX
            print("  Extracting Deep Data...")
            ps_app.DoJavaScriptFile(str(JSX_SCRIPT))
            
            # 4. Check Result
            if TEMP_ERROR.exists():
                err_msg = TEMP_ERROR.read_text(encoding='utf-8')
                print(f"  ❌ JSX Error: {err_msg}")
            
            elif TEMP_JSON.exists():
                print("  ✅ Extraction Successful!")
                
                # Load JSON
                with open(TEMP_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Categorize
                category = categorize_style(data)
                print(f"  🏷️  Category: {category.upper()}")
                
                # Move to Library
                cat_dir = OUTPUT_BASE / category
                cat_dir.mkdir(parents=True, exist_ok=True)
                
                final_path = cat_dir / f"{psd_file.stem}.json"
                with open(final_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"  💾 Saved to: {final_path}")
                
            else:
                print("  ⚠️ No output generated (Silent Failure)")

            # 5. Close File (No Save)
            doc.Close(2) # 2 = dsDoNotSaveChanges
            
        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
            # Try to force close doc if stuck?
            try:
                ps_app.ActiveDocument.Close(2)
            except: pass

    print("\n🏁 All tasks completed.")

if __name__ == "__main__":
    main()
