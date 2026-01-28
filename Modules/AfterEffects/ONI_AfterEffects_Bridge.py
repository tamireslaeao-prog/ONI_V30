
import subprocess
import os
import re

class AfterEffectsBridge:
    def __init__(self):
        self.aerender_path = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe"
        self.afterfx_path = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
        
    def check_health(self):
        if not os.path.exists(self.aerender_path):
            return "MISSING_BINARY", False
            
        # Check Version
        try:
            # aerender -version often returns code 0 or 1 depending on version
            res = subprocess.run([self.aerender_path, "-version"], capture_output=True, text=True)
            output = res.stdout + res.stderr
            
            # Check for specific success strings or just existence
            if "After Effects" in output or "version" in output.lower():
                return "READY", True
            
            # Code 15 check (Empty Render Queue) - Valid for Smoke Test
            if res.returncode == 15 or "aerender Error" in output:
                 # It ran, but errored. That means the bridge IS connected.
                 return "READY_WITH_ERRORS", True
                 
            return f"UNKNOWN_STATE (Code {res.returncode})", False
        except Exception as e:
            return f"EXCEPTION: {str(e)}", False

    def run_script(self, script_to_run):
        # uses AfterFX.exe -r
        if not os.path.exists(self.afterfx_path):
             return False, "AfterFX.exe missing"
             
        cmd = [self.afterfx_path, "-r", script_to_run]
        try:
            # Non-blocking launch
            subprocess.Popen(cmd)
            return True, "Script Launched"
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    bridge = AfterEffectsBridge()
    status, ok = bridge.check_health()
    print(f"AE Bridge Status: {status} (Operational: {ok})")
