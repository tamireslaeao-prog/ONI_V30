
import win32com.client
import os
import time
import psutil
import requests
import json
from multiprocessing import Process
from typing import Optional

# =========================================================================================
# ONI UNIVERSAL PHOTOSHOP BRIDGE (V11 ENGINE)
# =========================================================================================

class PhotoshopUniversal:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.app = None
        self.log_callback = print

    def set_logger(self, callback):
        self.log_callback = callback

    def log(self, msg):
        self.log_callback(f"[ONI-PSD-V11] {msg}")

    def _kill_photoshop(self):
        self.log("🔪 Killing Photoshop instances...")
        for proc in psutil.process_iter():
            if "photoshop" in proc.name().lower():
                try:
                    proc.kill()
                except:
                    pass
        time.sleep(2)

    def _dialog_sentinel(self, duration=180):
        """Runs in a separate process to smash dialogs."""
        print("[SENTINEL] 👀 Watching for Dialogs...")
        start = time.time()
        while time.time() - start < duration:
            try:
                # Fast Enter
                requests.get(f"{self.base_url}/api/keys", params={"keys": "enter"})
                
                # Vision Check
                resp = requests.get(f"{self.base_url}/api/hybrid-vision/desktop", params={"nocache": str(time.time())})
                if resp.status_code == 200:
                    data = resp.json()
                    for el in data.get("elements", []):
                        name = el.get("name", "").lower()
                        # Keywords for blocking dialogs
                        if any(x in name for x in ["substituir", "resolver", "ok", "update", "cancelar", "fechar", "sim", "não", "rasterizar", "continue"]):
                            cx = el.get("rect", {}).get("center_x")
                            cy = el.get("rect", {}).get("center_y")
                            if cx and cy:
                                print(f"[SENTINEL] 🔨 SMASHING '{name}' at {cx},{cy}")
                                requests.get(f"{self.base_url}/api/click", params={"x": str(cx), "y": str(cy)})
                time.sleep(2)
            except:
                pass

    def run_automation(self, file_path: str, new_text: str = "ONI", keep_open: bool = True):
        """
        Executes the blind V11 automation on a specific file.
        """
        if not os.path.exists(file_path):
            self.log(f"❌ File not found: {file_path}")
            return False

        # Start Sentinel
        sentinel = Process(target=self._dialog_sentinel, args=(180,))
        sentinel.start()

        try:
            self._kill_photoshop()
            
            self.app = win32com.client.Dispatch("Photoshop.Application")
            self.log(f"✅ Photoshop {self.app.Version} Running.")
            
            try: self.app.DisplayDialogs = 3 # NO DIALOGS
            except: pass

            self.log(f"📂 Opening: {file_path}")
            self.app.Open(file_path)

            # JSX PAYLOAD (The Brains)
            jsx_script = self._get_jsx_payload(new_text)
            
            self.log("🧠 Executing V11 Logic...")
            result = self.app.DoJavaScript(jsx_script)
            self.log(f"📝 REPORT: {result}")
            
            if result and "Updated" in str(result):
                self.log("💾 Saving changes...")
                self.app.ActiveDocument.Save()
                
            return True

        except Exception as e:
            self.log(f"🔥 CRITICAL ERROR: {e}")
            return False
            
        finally:
            self.log("🏁 Stopping Sentinel...")
            sentinel.terminate()

    def _get_jsx_payload(self, text: str) -> str:
        return f"""
        app.displayDialogs = DialogModes.NO;
        var targetText = "{text}";
        var report = [];
        var editCount = 0;
        
        function log(m) {{ report.push(m); }}
        
        function unlockLayer(l) {{
            try {{ if (l.allLocked) l.allLocked = false; }} catch(e) {{}}
        }}

        // ---------------------------------------------------------
        // 1. FULL SPECTRUM CLEANUP
        // ---------------------------------------------------------
        function cleanupLayers(doc) {{
            for (var i = doc.layers.length - 1; i >= 0; i--) {{
                var l = doc.layers[i];
                var name = l.name.toLowerCase();
                var isTrash = false;
                
                // TEXT LAYERS
                if (l.kind == LayerKind.TEXT) {{
                    var content = "";
                    try {{ content = l.textItem.contents.toLowerCase(); }} catch(e){{}}
                    
                    if (content.indexOf("text styles") != -1 || 
                        content.indexOf("rate it") != -1 ||
                        content.indexOf("medesigner") != -1 ||
                        content.indexOf("psd") != -1 || 
                        content.indexOf("preview") != -1 ||
                        content.indexOf("instructions") != -1 ||
                        content.indexOf("premium") != -1 ||
                        content.indexOf("text effect") != -1 ||
                        content.indexOf("editable") != -1 ||
                        content.indexOf("high resolution") != -1 ||
                        content.indexOf("change this") != -1) {{
                        isTrash = true;    
                    }}
                }}
                
                // SMART OBJECTS (Trash Detection)
                if (l.kind == LayerKind.SMARTOBJECT) {{
                    if (name.indexOf("title") != -1 || 
                        name.indexOf("additional") != -1 ||
                        name.indexOf("info") != -1 ||
                        name.indexOf("preview") != -1) {{
                        isTrash = true;
                    }}
                }}
                
                // GROUPS/FOLDERS (Trash Detection)
                if (l.typename == "LayerSet") {{
                    if (name.indexOf("additional") != -1 || 
                        name.indexOf("info") != -1 || 
                        name.indexOf("help") != -1) {{
                        isTrash = true;
                    }}
                }}

                if (isTrash) {{
                    unlockLayer(l);
                    try {{
                        l.remove();
                        log("🗑️ Deleting Trash: " + l.name + " (" + l.typename + ")");
                    }} catch(e) {{
                        try {{
                            l.visible = false;
                            log("⚠️ Hide Trash: " + l.name);
                        }} catch(e2)  {{ log("❌ Fail: " + l.name); }}
                    }}
                }}
                else if (l.typename == "LayerSet") {{
                     cleanupLayers(l);
                }}
            }}
        }}

        function replaceTextInDoc(doc, txt) {{
            var count = 0;
            for (var i = 0; i < doc.layers.length; i++) {{
                var l = doc.layers[i];
                unlockLayer(l);
                if (l.kind == LayerKind.TEXT) {{
                     try {{ l.textItem.contents = txt; count++; }} catch(e) {{
                        try {{ l.textItem.font = "Arial-BoldMT"; l.textItem.contents = txt; count++; }} catch(e2) {{}}
                     }}
                }}
                if (l.typename == "LayerSet") count += replaceTextInDoc(l, txt);
            }}
            return count;
        }}

        function processSmartObjects(layer) {{
            unlockLayer(layer);
            if (layer.kind == LayerKind.SMARTOBJECT) {{
                var name = layer.name.toLowerCase();
                // EDIT Keywords (Whitelist)
                if (name.indexOf("edit") != -1 || name.indexOf("text") != -1 || name.indexOf("mockup") != -1 || name.indexOf("place") != -1 || name.indexOf("smart") != -1 || name.indexOf("object") != -1) {{
                    if (name.indexOf("title") == -1) {{
                        app.activeDocument.activeLayer = layer;
                        try {{
                            var idplacedLayerEditContents = stringIDToTypeID("placedLayerEditContents");
                            executeAction(idplacedLayerEditContents, undefined, DialogModes.NO);
                            
                            var replaced = replaceTextInDoc(app.activeDocument, targetText);
                            if (replaced > 0) {{
                                app.activeDocument.close(SaveOptions.SAVECHANGES);
                                log("  -> [SO] Updated " + replaced + " layers in " + layer.name);
                                editCount++;
                            }} else {{
                                app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
                            }}
                        }} catch(e) {{}}
                    }}
                }}
            }} else if (layer.typename == "LayerSet") {{
                for (var i = 0; i < layer.layers.length; i++) {{
                    processSmartObjects(layer.layers[i]);
                }}
            }}
        }}

        function processDirectText(layer) {{
            unlockLayer(layer);
            if (layer.kind == LayerKind.TEXT) {{
                try {{
                    layer.textItem.contents = targetText;
                    log("  -> [Text] Updated " + layer.name);
                    editCount++;
                }} catch(e) {{
                    try {{
                       layer.textItem.font = "Arial-BoldMT";
                       layer.textItem.contents = targetText;
                       editCount++;
                    }} catch(e2) {{}}
                }}
            }} else if (layer.typename == "LayerSet") {{
                for (var i = 0; i < layer.layers.length; i++) {{
                    processDirectText(layer.layers[i]);
                }}
            }}
        }}

        var mainDoc = app.activeDocument;
        log("🧹 Phase 1: Full Spectrum Cleanup...");
        cleanupLayers(mainDoc);
        
        log("🔍 Phase 2: Smart Objects...");
        for (var i = 0; i < mainDoc.layers.length; i++) processSmartObjects(mainDoc.layers[i]);
        
        if (editCount == 0) {{
             log("⚠️ Phase 3: Direct Text Edit (Fallback)...");
             for (var i = 0; i < mainDoc.layers.length; i++) processDirectText(mainDoc.layers[i]);
        }}

        report.join(" | ");
        """

if __name__ == "__main__":
    # Test block
    bridge = PhotoshopUniversal()
    # bridge.run_automation(r"Path")
