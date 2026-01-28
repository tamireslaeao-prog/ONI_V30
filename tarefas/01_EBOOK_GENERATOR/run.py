import os
import sys
import shutil
import logging
from pathlib import Path

# Setup Path to include modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
sys.path.append(MODULES_DIR)

# Config - Dynamic Paths
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Initialize Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("="*60)
    print(f"ONI EBOOK GENERATOR v1.0")
    print(f"Base Dir: {BASE_DIR}")
    print("="*60)

    # 1. Verification
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] Input directory missing: {INPUT_DIR}")
        return
    
    # Clean Output (Optional, maybe ask user? For now just ensure exists)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Check for content file
    content_file = os.path.join(INPUT_DIR, 'content.md')
    if not os.path.exists(content_file):
        print("[WARNING] 'content.md' not found in input. Using default/placeholder logic?")
        # Real implementation: Stop or template
    
    # 2. Image Processing (Hero & Mold)
    try:
        from modules import mold_gen
        print("\n[1/3] Generating Technical Mold...")
        mold_path = mold_gen.generate(OUTPUT_DIR) # Generates SVG into Output
        print(f"      -> Mold created: {os.path.basename(mold_path)}")
    except Exception as e:
        print(f"[ERROR] Mold Generation failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. PDF Generation
    try:
        from modules import pdf_builder
        print("\n[2/3] Building PDF...")
        # We pass absolute paths to the builder so it can resolve assets/css correctly
        output_pdf = pdf_builder.build_pdf(
            input_dir=INPUT_DIR,
            output_dir=OUTPUT_DIR,
            assets_dir=ASSETS_DIR
        )
        print(f"      -> PDF Created: {output_pdf}")
    except Exception as e:
        print(f"[ERROR] PDF Builder failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("JOB DONE. Please check the 'output' folder.")
    print("="*60)

if __name__ == "__main__":
    main()
