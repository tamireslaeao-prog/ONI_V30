
import sys
import os
import subprocess
import logging
import requests
import json
from pathlib import Path
import psutil

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Add project root to path
current_dir = Path(os.getcwd())
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from Modules.Universal_Vectorizer.svg_to_photoshop_jsx import SVGToPhotoshopJSX

# ...

    def _inject_photoshop(self):
        """
        Calls the Photoshop API/JSX adapter.
        UPDATED: Generates Native Shape Layers via JSX Reconstructor.
        """
        logger.info("  Generating Native Photoshop Script (Editable Paths)...")
        
        # 1. Convert SVG to JSX
        temp_jsx = os.path.join(os.getcwd(), "temp", "reconstruct_ps.jsx")
        
        try:
            converter = SVGToPhotoshopJSX(self.temp_svg_path)
            converter.parse()
            converter.generate_jsx(temp_jsx)
            logger.info(f"  JSX Script Generated: {temp_jsx}")
        except Exception as e:
            logger.error(f"  JSX Generation Failed: {e}")
            return

        # 2. Execute via API
        url = "http://localhost:8000/api/photoshop/execute-jsx-file"
        try:
            params = {"path": temp_jsx}
            resp = requests.post(url, params=params)
            
            if resp.status_code == 200:
                logger.info("✅ Photoshop Native Import Triggered.")
            else:
                logger.error(f"❌ API Error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            logger.error(f"❌ Connection Error: {e}. Is ONI Server running?")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniversalBridge")

class UniversalBridge:
    """
    The 'One-Click' Orchestrator. 
    Connects the Vectorizer Engine directly to the Host Application (Corel, PS, AI, Blender, Maya, AutoCAD, AE).
    """
    
    def __init__(self):
        self.vectorizer = VectorizerService()
        self.temp_svg_path = os.path.join(os.getcwd(), "temp", "universal_vector.svg")
        
        # Ensure temp dir
        os.makedirs(os.path.dirname(self.temp_svg_path), exist_ok=True)

    def _auto_detect_target(self) -> str:
        """
        Intelligently detects the user's intent based on Active Window or Running Processes.
        Priority:
        1. Focused Window (if supported app)
        2. Running Process (if only one supported app is running)
        3. Default to COREL (if ambiguous)
        """
        logger.info("🔍 Auto-Detecting Target Application...")
        
        app_signatures = [
            ("CorelDRW", "CorelDRAW", "COREL"),
            ("Photoshop", "Photoshop", "PS"),
            ("Illustrator", "Illustrator", "AI"),
            ("blender", "Blender", "BLENDER"),
            ("maya", "Maya", "MAYA"),
            ("acad", "AutoCAD", "AUTOCAD"),
            ("AfterFX", "After Effects", "AE")
        ]
        
        # 1. Check Active Window (Best context)
        if gw:
            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    title = active_window.title
                    logger.info(f"  Active Window: '{title}'")
                    for proc_sig, title_sig, code in app_signatures:
                        if title_sig.lower() in title.lower():
                            logger.info(f"  👉 Context Match: {code}")
                            return code
            except Exception as e:
                logger.warning(f"  Active Window Check Failed: {e}")

        # 2. Check Running Processes (Fallback)
        running_targets = []
        for proc in psutil.process_iter(['name']):
            try:
                p_name = proc.info['name']
                for proc_sig, _, code in app_signatures:
                    if proc_sig.lower() in p_name.lower():
                        if code not in running_targets:
                            running_targets.append(code)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if len(running_targets) == 1:
            logger.info(f"  👉 Single Supported App Running: {running_targets[0]}")
            return running_targets[0]
        elif len(running_targets) > 1:
            logger.warning(f"  ⚠️ Multiple Apps Running: {running_targets}. Defaulting to COREL (Primary).")
            return "COREL"
        
        logger.error("  ❌ No supported apps found running.")
        return None

    def process_and_inject(self, image_path: str, target_app: str = None, n_colors: int = 8):
        """
        Main Pipeline: Image -> Vector -> App
        """
        # Auto-detect if not specified
        if not target_app or target_app.upper() == "AUTO":
            detected = self._auto_detect_target()
            if detected:
                target_app = detected
            else:
                logger.error("❌ Could not auto-detect target. Please specify.")
                return

        target_app = target_app.upper()
        
        # 1. Vectorize
        logger.info(f"🎨 Phase 1: Vectorizing {os.path.basename(image_path)}...")
        self.vectorizer.convert_image_to_svg(image_path, self.temp_svg_path, n_colors)
        
        if not os.path.exists(self.temp_svg_path):
            logger.error("❌ Vectorization failed. SVG not found.")
            return

        # 2. Inject
        logger.info(f"🚀 Phase 2: Injecting into {target_app}...")
        
        if target_app == "COREL":
            self._inject_corel()
        elif target_app in ["PS", "PHOTOSHOP"]:
            self._inject_photoshop()
        elif target_app in ["AI", "ILLUSTRATOR"]:
            self._inject_illustrator()
        elif target_app == "BLENDER":
            self._inject_blender()
        elif target_app == "MAYA":
            self._inject_maya()
        elif target_app == "AUTOCAD":
            self._inject_autocad()
        elif target_app in ["AE", "AFTER", "AFTEREFFECTS"]:
            self._inject_after_effects()
        else:
            logger.error(f"❌ Unknown target app: {target_app}")

    def _inject_corel(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "corel_import.ps1")
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", adapter_path, "-SvgPath", self.temp_svg_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0: logger.info("✅ CorelDRAW Import Successful.")
            else: logger.error(f"❌ CorelDRAW Import Failed: {result.stderr}")
        except Exception as e: logger.error(f"❌ Execution Error: {e}")

    def _inject_photoshop(self):
        svg_path_js = self.temp_svg_path.replace("\\", "/")
        jsx_payload = f"""
        var oni_svg_path = "{svg_path_js}";
        function importUniversalSVG(svgPath) {{
            if (!app.documents.length) app.documents.add();
            var fileRef = new File(svgPath);
            if (!fileRef.exists) return;
            try {{
                var idPlc = charIDToTypeID("Plc ");
                var desc2 = new ActionDescriptor();
                var idnull = charIDToTypeID("null");
                desc2.putPath(idnull, fileRef);
                var idFTcs = charIDToTypeID("FTcs");
                var idQCSt = charIDToTypeID("QCSt");
                var idQcsa = charIDToTypeID("Qcsa");
                desc2.putEnumerated(idFTcs, idQCSt, idQcsa);
                executeAction(idPlc, desc2, DialogModes.NO);
            }} catch(e) {{ alert("Import failed: " + e); }}
        }}
        importUniversalSVG(oni_svg_path);
        """
        temp_jsx = os.path.join(os.getcwd(), "temp", "inject_ps.jsx")
        with open(temp_jsx, "w") as f: f.write(jsx_payload)
        url = "http://localhost:8000/api/photoshop/execute-jsx-file"
        try:
            requests.post(url, params={"path": temp_jsx})
            logger.info("✅ Photoshop Import Triggered via API.")
        except Exception as e: logger.error(f"❌ Error: {e}")

    def _inject_illustrator(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "illustrator_import.jsx")
        svg_path_js = self.temp_svg_path.replace("\\", "/")
        adapter_path_js = adapter_path.replace("\\", "/")
        wrapper_jsx = os.path.join(os.getcwd(), "temp", "inject_ai.jsx")
        payload = f"""var oni_svg_path = "{svg_path_js}";\n$.evalFile("{adapter_path_js}");"""
        with open(wrapper_jsx, "w") as f: f.write(payload)
        ps_script = f"""try {{ $app = New-Object -ComObject Illustrator.Application; $app.DoJavaScriptFile("{wrapper_jsx}"); Write-Host "✅ Done"; }} catch {{ exit 1 }}"""
        ps_file = os.path.join(os.getcwd(), "temp", "run_ai.ps1")
        with open(ps_file, "w") as f: f.write(ps_script)
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file]
        try: subprocess.run(cmd)
        except: pass

    def _inject_blender(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "blender_import.py")
        cmd = ["blender", "--python", adapter_path, "--", self.temp_svg_path]
        try: subprocess.Popen(cmd); logger.info("✅ Blender Launched.")
        except: logger.error("❌ Blender not found.")

    def _inject_maya(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "maya_import.py")
        os.environ["ONI_SVG_PATH"] = self.temp_svg_path
        try:
            subprocess.Popen(["maya", "-command", f"python(\"exec(open('{adapter_path.replace(os.sep, '/')}').read())\")"])
            logger.info("✅ Maya Launched.")
        except: logger.error("❌ Maya not found.")

    def _inject_autocad(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "autocad_import.ps1")
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", adapter_path, "-SvgPath", self.temp_svg_path]
        try: subprocess.run(cmd); logger.info("✅ AutoCAD Attempted.")
        except: pass

    def _inject_after_effects(self):
        adapter_path = os.path.join(os.getcwd(), "Modules", "Universal_Vectorizer", "Adapters", "after_effects_import.jsx")
        svg_path_js = self.temp_svg_path.replace("\\", "/")
        adapter_path_js = adapter_path.replace("\\", "/")
        wrapper_jsx = os.path.join(os.getcwd(), "temp", "inject_ae.jsx")
        payload = f"""var oni_svg_path = "{svg_path_js}";\n$.evalFile("{adapter_path_js}");"""
        with open(wrapper_jsx, "w") as f: f.write(payload)
        try: subprocess.Popen(["AfterFX.exe", "-r", wrapper_jsx]); logger.info("✅ AE Script Triggered.")
        except: logger.error("❌ AfterFX not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python universal_bridge.py <image_path> [target_app] [n_colors]")
        sys.exit(1)
    img = sys.argv[1]
    app_target = sys.argv[2] if len(sys.argv) > 2 else "AUTO"
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    bridge = UniversalBridge()
    bridge.process_and_inject(img, app_target, cols)
