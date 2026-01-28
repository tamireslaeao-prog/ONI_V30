import subprocess
import os
import urllib.parse
import time

# ONI AE RUNNER - SOURCE INJECTION MODE V4
# Fixes single-quote issue in V3

AE_PATH = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
TARGET_SCRIPT = r"c:\Users\user\Desktop\ONIV24\app\scripts\ae\project_3d_cube.jsx"

def run_injection_v4():
    if not os.path.exists(TARGET_SCRIPT):
        print("Script missing")
        return

    with open(TARGET_SCRIPT, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Encode via standard URI (preserves single quotes usually)
    encoded_code = urllib.parse.quote(code)
    
    # 2. MANUALLY ESCAPE SINGLE QUOTES
    # This is critical because we wrap the string in '...'
    encoded_code = encoded_code.replace("'", "%27")
    
    # Payload wrapper
    payload = f"eval(decodeURIComponent('{encoded_code}'));"
    
    print(f"Injecting V4 Payload ({len(payload)} chars). Quotes are safe.")
    
    cmd = [AE_PATH, "-nosplash", "-s", payload]
    
    subprocess.Popen(cmd)
    print("Sent.")

if __name__ == "__main__":
    run_injection_v4()
