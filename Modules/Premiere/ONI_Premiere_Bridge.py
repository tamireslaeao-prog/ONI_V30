
import subprocess
import os
import json
import time

class PremiereBridge:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "Config", "premiere_config.json")
        self.premiere_path = r"C:\Program Files\Adobe\Adobe Premiere Pro 2025\Adobe Premiere Pro.exe"
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    if "premiere_path" in data:
                        self.premiere_path = data["premiere_path"]
            except Exception as e:
                print(f"Warning: Could not load config: {e}")

    def check_health(self):
        """Checks if Premiere Pro executable exists"""
        if not os.path.exists(self.premiere_path):
            return "MISSING_BINARY", False
            
        return "READY", True

    def run_script(self, script_path):
        """
        Executes a JSX script in Premiere Pro.
        Note: Premiere Pro receives scripts via command line argument, 
        but it usually just opens the app. Automation often requires 
        socket connection (CEP) or OS-level dispatch.
        For V1, we try standard command line launch.
        """
        if not os.path.exists(self.premiere_path):
             return False, "Premiere Pro binary missing"
        
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_path}"

        # Standard Windows Command for Adobe Scripts often involves just passing the file
        # provided Open With is set, OR passing it as argument:
        # "Adobe Premiere Pro.exe" "C:\path\to\script.jsx"
        cmd = [self.premiere_path, "/Script", script_path]
        
        try:
            # Non-blocking launch
            subprocess.Popen(cmd)
            return True, f"Launched Script: {os.path.basename(script_path)}"
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    bridge = PremiereBridge()
    status, ok = bridge.check_health()
    print(f"Premiere Bridge Status: {status} (Operational: {ok})")
    
    # Test script path
    script = os.path.join(os.path.dirname(__file__), "Scripts", "oni_premiere_test.jsx")
    if os.path.exists(script):
        print(f"Found test script: {script}")
    else:
        print("Test script not found yet.")
