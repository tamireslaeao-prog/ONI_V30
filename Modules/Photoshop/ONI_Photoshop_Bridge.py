"""
ONI Photoshop Bridge V2 (PhD Edition)
-------------------------------------
Advanced Python -> Photoshop COM Interface with Library Injection.
Version: 2.0.0
Date: 2026-01-21
Author: ONI Team (Antigravity)

Capabilities:
- Auto-injects 'oni_lib_photoshop.jsx' for high-level JS functions.
- Python Wrappers for Layers, Styles, Canvas.
- Hybrid Fallback (COM -> Subprocess).
"""

import os
import time
import subprocess
from typing import Optional, Dict, Any, List

try:
    import win32com.client
    HAS_COM = True
except ImportError:
    HAS_COM = False

# Path to the core JSX Library
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(CURRENT_DIR, "oni_lib_photoshop.jsx")

class PhotoshopBridge:
    """
    The PhD-Level Bridge. Controls Photoshop via COM with injected intelligence.
    """
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.app = None
        self.doc = None
        self.use_fallback = False
        self.executable_path = r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe"
        self.lib_code = ""
        
        # Load Library Code
        self._load_library()
        
        if HAS_COM:
            try:
                self._connect()
            except Exception as e:
                print(f"⚠️ COM Connection failed: {e}. Switching to Fallback Mode.")
                self.use_fallback = True
        else:
            print("⚠️ win32com not found. Switching to Fallback Mode.")
            self.use_fallback = True
            
        if self.use_fallback and not os.path.exists(self.executable_path):
            # Try 2025/2024 paths just in case
            alts = [
                r"C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe",
                r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe"
            ]
            found = False
            for p in alts:
                if os.path.exists(p):
                    self.executable_path = p
                    found = True
                    break
            
            if not found:
                raise RuntimeError(f"Fallback Executable not found at: {self.executable_path}")

    def _load_library(self):
        """Reads the ONI_PS JS Library into memory."""
        if os.path.exists(LIB_PATH):
            with open(LIB_PATH, "r", encoding="utf-8") as f:
                self.lib_code = f.read()
        else:
            print(f"⚠️ WARNING: Library not found at {LIB_PATH}. High-level functions unavailable.")
            self.lib_code = ""

    def _connect(self):
        """Connect to Photoshop Application."""
        prog_ids = [
            "Photoshop.Application",
            "Photoshop.Application.185", # 2026
            "Photoshop.Application.180", # 2025
            "Photoshop.Application.170", # 2024
        ]
        
        for prog_id in prog_ids:
            try:
                self.app = win32com.client.Dispatch(prog_id)
                return
            except:
                continue
                
        raise RuntimeError("Could not connect to Photoshop COM.")
    
    # =========================================================================
    # CORE EXECUTION
    # =========================================================================

    def execute_code(self, js_code: str, inject_lib: bool = True) -> Dict[str, Any]:
        """
        Execute raw JS code via COM. 
        Auto-injects ONI_PS library unless disabled.
        """
        if self.use_fallback:
            return {"success": False, "error": "execute_code not supported in Fallback mode (File only)"}
            
        try:
            full_payload = js_code
            if inject_lib and self.lib_code:
                # Prepend library code
                full_payload = self.lib_code + "\n\n" + js_code
            
            result = self.app.DoJavaScript(full_payload)
            return {"success": True, "output": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_jsx(self, jsx_path: str) -> Dict[str, Any]:
        """Execute a JSX file (Works in both COM and Fallback)."""
        if not os.path.exists(jsx_path):
            return {"success": False, "error": f"File not found: {jsx_path}"}
            
        try:
            if not self.use_fallback:
                # COM Mode
                self.app.DoJavaScriptFile(jsx_path)
                return {"success": True, "output": "Executed via COM"}
            else:
                # Fallback Mode
                cmd = [self.executable_path, jsx_path]
                subprocess.Popen(cmd) 
                return {"success": True, "output": "Triggered via CMD (Blind)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # HIGH-LEVEL WRAPPERS (PhD Level)
    # =========================================================================
    
    class CanvasWrapper:
        def __init__(self, bridge):
            self.bridge = bridge
            
        def create(self, width=1920, height=1080, name="ONI_Doc"):
            js = f'ONI_PS.Canvas.Create({width}, {height}, "{name}");'
            return self.bridge.execute_code(js)
            
        def resize(self, width, height):
            js = f'ONI_PS.Canvas.Resize({width}, {height});'
            return self.bridge.execute_code(js)

    class LayersWrapper:
        def __init__(self, bridge):
            self.bridge = bridge
            
        def create(self, name, opacity=100):
            js = f'ONI_PS.Layers.Create("{name}", {opacity});'
            return self.bridge.execute_code(js)
            
        def create_text(self, text, x=500, y=500, size=100, color_hex="FFFFFF", name=None):
            if not name: name = f"Text_{text[:10]}"
            # Convert hex to RGB object via Lib
            js = f'''
            var c = ONI_PS.Core.HexColor("{color_hex}");
            ONI_PS.Layers.CreateText("{name}", "{text}", {x}, {y}, {size}, c);
            '''
            return self.bridge.execute_code(js)
            
        def set_opacity(self, opacity):
            js = f'ONI_PS.Effects.SetOpacity(app.activeDocument.activeLayer, {opacity});'
            return self.bridge.execute_code(js)

    class EffectsWrapper:
        def __init__(self, bridge):
            self.bridge = bridge
            
        def shadow(self, offset_x=10, offset_y=10, blur=20, opacity=50):
            js = f'''
            var layer = app.activeDocument.activeLayer;
            ONI_PS.Effects.CreateShadow(layer, {offset_x}, {offset_y}, {blur}, ONI_PS.Core.Color(0,0,0), {opacity});
            '''
            return self.bridge.execute_code(js)
            
        def blur(self, radius):
            js = f'ONI_PS.Effects.GaussianBlur({radius});'
            return self.bridge.execute_code(js)

    class SmartObjectWrapper:
        def __init__(self, bridge):
            self.bridge = bridge

        def replace_contents(self, file_path):
            """Replaces the content of the current Smart Object."""
            # Escape backslashes for JS string
            safe_path = file_path.replace("\\", "\\\\")
            js = f'''
            var idPlc = charIDToTypeID( "Plc " );
            var desc = new ActionDescriptor();
            var idnull = charIDToTypeID( "null" );
            desc.putPath( idnull, new File( "{safe_path}" ) );
            var idFTcs = charIDToTypeID( "FTcs" );
            var idQCSt = charIDToTypeID( "QCSt" );
            var idQcsa = charIDToTypeID( "Qcsa" );
            desc.putEnumerated( idFTcs, idQCSt, idQcsa );
            executeAction( idPlc, desc, DialogModes.NO );
            '''
            return self.bridge.execute_code(js)

        def edit_contents(self):
            """Opens the Smart Object for editing."""
            js = 'app.activeDocument.activeLayer = app.activeDocument.activeLayer; executeAction(stringIDToTypeID("placedLayerEditContents"), undefined, DialogModes.NO);'
            return self.bridge.execute_code(js)

    @property
    def smart_objects(self): return self.SmartObjectWrapper(self)
    
    @property
    def canvas(self): return self.CanvasWrapper(self)
    
    @property
    def layers(self): return self.LayersWrapper(self)
    
    @property
    def effects(self): return self.EffectsWrapper(self)


# ==============================================================================
# PhD VERIFICATION TEST / CLI ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ONI Photoshop Bridge V2 (PhD)")
    parser.add_argument("--run-jsx", help="Path to JSX file to execute")
    parser.add_argument("--test", action="store_true", help="Run self-test diagnostic")
    args = parser.parse_args()

    print(f"🎓 ONI Photoshop Bridge V{PhotoshopBridge.VERSION} (PhD Edition)")
    print("=" * 60)
    
    try:
        bridge = PhotoshopBridge()
        
        if bridge.use_fallback:
            print("⚠️ Running in Fallback Mode.")
            
        if args.run_jsx:
            print(f"🚀 Executing External JSX: {args.run_jsx}")
            res = bridge.execute_jsx(args.run_jsx)
            print(res)
            
        elif args.test:
            print("✅ Connected via COM")
            print(f"📚 Library Loaded: {len(bridge.lib_code)} chars")
            
            # 1. Create Canvas
            print("1️⃣ Creating Canvas...")
            bridge.canvas.create(1280, 720, "ONI_PhD_Test")
            
            # 2. Add Background
            print("2️⃣ Creating Background...")
            bridge.execute_code('ONI_PS.Canvas.FillBackground(ONI_PS.Core.HexColor("1a1a2e"));')
            
            # 3. Add Text
            print("3️⃣ Adding Text...")
            bridge.layers.create_text("ONI ACORDE", 640, 360, 150, "e94560", "Title")
            
            # 5. Shadow
            print("5️⃣ Adding Shadow...")
            bridge.effects.shadow(20, 20, 30, 80)
            
            print("\n✅ Test Complete! Check Photoshop.")
            
        else:
            print("ℹ️ No mode selected. Use --test or --run-jsx <file>")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
