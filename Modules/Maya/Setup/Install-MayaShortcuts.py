"""
ONI V23 - Maya Shortcut Injector
Injects ONI custom hotkeys into Maya (any version)
Uses MEL script modification
"""

import os
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "Config" / "maya_shortcuts.json"

def find_maya_prefs():
    """Find Maya preferences directory (auto-detect version)"""
    home = Path.home()
    maya_base = home / "Documents" / "maya"
    
    if not maya_base.exists():
        print(f"❌ Maya prefs not found at {maya_base}")
        return None
    
    # Find latest version
    versions = sorted([d for d in maya_base.iterdir() if d.is_dir() and d.name.replace('.', '').isdigit()], reverse=True)
    
    if not versions:
        print("❌ No Maya versions found")
        return None
    
    latest = versions[0]
    print(f"✓ Detected Maya {latest.name}")
    
    prefs_dir = latest / "prefs"
    if not prefs_dir.exists():
        prefs_dir.mkdir(parents=True)
    
    return prefs_dir


def inject_shortcuts():
    """Inject ONI shortcuts into Maya hotkeys"""
    
    # Load config
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found: {CONFIG_PATH}")
        return False
    
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    # Find Maya prefs
    prefs_dir = find_maya_prefs()
    if not prefs_dir:
        return False
    
    # Generate MEL script for hotkeys
    hotkeys_file = prefs_dir / "userHotkeys.mel"
    
    # Backup existing
    if hotkeys_file.exists():
        backup_file = str(hotkeys_file) + ".bak"
        import shutil
        shutil.copy(hotkeys_file, backup_file)
        print(f"✓ Backup created: {backup_file}")
    
    mel_code = '''// ONI Custom Hotkeys
// Auto-generated - DO NOT EDIT MANUALLY

global proc oni_registerHotkeys() {
'''
    
    # Add hotkeys from config
    for shortcut in config.get('shortcuts', []):
        key = shortcut['key']
        command = shortcut['command']
        name = shortcut.get('name', command)
        
        mel_code += f'''
    // {name}
    nameCommand 
        -annotation "{name}" 
        -command "{command}"
        oni_{name.replace(" ", "_")};
    
    hotkey -keyShortcut "{key}" -name "oni_{name.replace(" ", "_")}";
'''
    
    mel_code += '''
}

// Auto-execute on Maya startup
oni_registerHotkeys();
'''
    
    # Write MEL file
    with open(hotkeys_file, 'w', encoding='utf-8') as f:
        f.write(mel_code)
    
    print(f"✓ Hotkeys injected: {hotkeys_file}")
    print("")
    print("✓ Shortcuts will be active on next Maya restart")
    print("")
    
    return True


if __name__ == "__main__":
    success = inject_shortcuts()
    sys.exit(0 if success else 1)
