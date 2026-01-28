import os
import zipfile
import datetime
import re
import sys

# CONFIGURATION
SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # ONI_V30 Root
BACKUP_ROOT = r"D:\ONI_BACKUPS"
TASK_FILE = os.path.join(os.environ['USERPROFILE'], ".gemini", "antigravity", "brain", "084c2297-60ba-4463-bb75-34a7872b0ffb", "task.md")

# EXCLUSIONS
# User Request: NO TEMP, NO DESIGN ASSETS, NO LEGACY DUMP
EXCLUDE_DIRS = {
    "venv", "node_modules", "__pycache__", ".git", ".vs", ".vscode", 
    "tmp", "temp", "LEGACY_DUMP", "Assets", "assets", "psd_sources", "render_cache"
}
EXCLUDE_EXTS = {".pyc", ".log", ".iso", ".tmp", ".bak", ".psd", ".mp4", ".mov"} # Excluding heavy media too just in case? User said "ASSETS DE DESIGN". PSDs are definitely assets.

def get_last_tag():
    """Reads task.md to find the last completed task for the tag."""
    tag = "WIP"
    try:
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Search from bottom up
            for line in reversed(lines):
                if "- [x]" in line:
                    # Extract text, remove markdown, limit length
                    clean = re.sub(r'\[.*?\]', '', line) # Remove links
                    clean = re.sub(r'[^a-zA-Z0-9]', '_', clean.split("]")[1]) # Keep only alphanumeric
                    clean = re.sub(r'_+', '_', clean).strip('_')
                    tag = clean[:30] # Max 30 chars
                    break
    except Exception as e:
        print(f"⚠️ Could not read task tag: {e}")
    
    return tag

def create_snapshot():
    if not os.path.exists(BACKUP_ROOT):
        try:
            os.makedirs(BACKUP_ROOT)
        except:
            print(f"❌ Critical: Cannot create {BACKUP_ROOT}. Check permissions.")
            return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    tag = get_last_tag()
    
    zip_name = f"ONI_V30_{timestamp}_{tag}.zip"
    zip_path = os.path.join(BACKUP_ROOT, zip_name)
    
    print(f"💾 STARTING BACKUP: {zip_name}")
    print(f"   Source: {SOURCE_DIR}")
    print(f"   Target: {zip_path}")
    
    file_count = 0
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(SOURCE_DIR):
                # Modify dirs in-place to skip excluded ones
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    if os.path.splitext(file)[1] in EXCLUDE_EXTS:
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, SOURCE_DIR)
                    
                    # Double check ignores (archives inside archives?)
                    if "archive" in rel_path and "LEGACY_DUMP" in rel_path:
                        continue
                        
                    zipf.write(file_path, rel_path)
                    file_count += 1
                    
                    if file_count % 100 == 0:
                        print(f"   ... Zipped {file_count} files", end='\r')
                        
        print(f"\n✅ BACKUP COMPLETE! ({file_count} files)")
        print(f"   Saved to: {zip_path}")
        
    except Exception as e:
        print(f"\n❌ BACKUP FAILED: {e}")

if __name__ == "__main__":
    create_snapshot()
