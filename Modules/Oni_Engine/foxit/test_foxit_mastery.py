
import sys
import os
import time
from pathlib import Path

# Portable path discovery - this file is at: ONIV24/Modules/Oni_Engine/foxit/test_foxit_mastery.py
_ONI_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(_ONI_ROOT))

try:
    from app.modules.foxit.foxit_wrapper import FoxitOptimus
    
    print("--- INITIATING FOXIT MASTER CONTROL ---")
    
    optimus = FoxitOptimus()
    
    # 1. Launch
    print("[1] Launching Foxit...")
    optimus.launch()
    
    # 2. Open PDF (portable path)
    pdf_path = str(_ONI_ROOT / "data" / "foxit_fonts" / "foxit-pdf-editor-quick-guide-2025.3.pdf")
    if os.path.exists(pdf_path):
        print(f"[2] Opening PDF: {pdf_path}")
        optimus.open_document(pdf_path)
    else:
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)
        
    time.sleep(2)
    
    # 3. Apply Hack (Stamp)
    print("[3] Applying Digital Stamp (Hack)...")
    optimus.add_stamp("APPROVED")
    
    time.sleep(1)
    
    # 4. Save As (Hacked Version) - portable path
    output_path = str(_ONI_ROOT / "temp" / "hacked_guide.pdf")
    print(f"[4] Saving Hacked Version to: {output_path}")
    optimus.save_as(output_path)
    
    print("--- SUCCESS: CONTROL ESTABLISHED ---")
    
except ImportError as e:
    print(f"FAILED to import module: {e}")
except Exception as e:
    print(f"RUNTIME ERROR: {e}")
