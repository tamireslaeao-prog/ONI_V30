"""
ONI V23 - Blender Shortcut Injector
Injects ONI custom keymap into Blender (any version)
Uses Python to modify userpref.blend directly
"""

import os
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "Config" / "blender_shortcuts.json"

def find_blender_config():
    """Find Blender config directory (auto-detect version)"""
    appdata = Path(os.getenv("APPDATA"))
    blender_base = appdata / "Blender Foundation" / "Blender"
    
    if not blender_base.exists():
        print(f"❌ Blender config not found at {blender_base}")
        return None
    
    # Find latest version
    versions = sorted([d for d in blender_base.iterdir() if d.is_dir()], reverse=True)
    
    if not versions:
        print("❌ No Blender versions found")
        return None
    
    latest = versions[0]
    print(f"✓ Detected Blender {latest.name}")
    
    config_dir = latest / "config"
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    
    return config_dir


def inject_shortcuts():
    """Inject ONI shortcuts into Blender keymap"""
    
    # Load config
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found: {CONFIG_PATH}")
        return False
    
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    # Find Blender config
    config_dir = find_blender_config()
    if not config_dir:
        return False
    
    # Create Python addon for keymap
    addon_dir = config_dir / "scripts" / "addons" / "oni_shortcuts"
    addon_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate addon __init__.py
    addon_code = f'''"""
ONI Custom Shortcuts for Blender
Auto-generated - DO NOT EDIT MANUALLY
"""

bl_info = {{
    "name": "ONI Shortcuts",
    "author": "ONI System",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "User Preferences > Keymaps",
    "description": "ONI custom keyboard shortcuts",
    "category": "System"
}}

import bpy

addon_keymaps = []

def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        # 3D View shortcuts
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
'''
    
    # Add shortcuts from config
    for shortcut in config.get('shortcuts', []):
        key = shortcut['key'].upper()
        command = shortcut['command']
        ctrl = shortcut.get('ctrl', False)
        shift = shortcut.get('shift', False)
        alt = shortcut.get('alt', False)
        
        addon_code += f'''        kmi = km.keymap_items.new('{command}', '{key}', 'PRESS', ctrl={ctrl}, shift={shift}, alt={alt})
        addon_keymaps.append((km, kmi))
        
'''
    
    addon_code += '''
def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
'''
    
    # Write addon
    init_file = addon_dir / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(addon_code)
    
    print(f"✓ Addon created: {init_file}")
    print("")
    print("To activate:")
    print("  1. Open Blender")
    print("  2. Edit > Preferences > Add-ons")
    print("  3. Enable 'ONI Shortcuts'")
    print("")
    
    return True


if __name__ == "__main__":
    success = inject_shortcuts()
    sys.exit(0 if success else 1)
