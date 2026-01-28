"""
ONI V23 - DEEP CLEANER
Sanitizes the `temp` directory by archiving potentially useful files
and nuking the rest.
"""

import os
import shutil
import datetime

# Determine Project Root (Assumes: Project/Modules/Oni_Engine/Scripts/script.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))

TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")
ARCHIVE_ROOT = os.path.join(PROJECT_ROOT, "data", "ARCHIVE_TEMP")

def deep_clean():
    print("🧹 ONI DEEP CLEANER INITIALIZED")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(ARCHIVE_ROOT, f"RUN_{timestamp}")
    
    # 1. Create Archive
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        print(f"📦 Created Archive: {archive_path}")

    # 2. Scan and Move
    if os.path.exists(TEMP_DIR):
        items = os.listdir(TEMP_DIR)
        if not items:
            print("✨ Temp directory is already empty.")
            return

        for item in items:
            src = os.path.join(TEMP_DIR, item)
            dst = os.path.join(archive_path, item)
            
            try:
                print(f"   ➡️ Moving: {item}")
                shutil.move(src, dst)
            except Exception as e:
                print(f"   ❌ Failed to move {item}: {e}")
    else:
        os.makedirs(TEMP_DIR)
        print("✨ Created fresh temp directory.")

    print("-" * 50)
    print("✅ TEMP IS NOW EMPTY (0 bytes).")
    print(f"🗄️  Previous contents moved to: data/ARCHIVE_TEMP/RUN_{timestamp}")

if __name__ == "__main__":
    deep_clean()
