import subprocess
import os
import urllib.parse

# ONI AE RUNNER - SOURCE INJECTION MODE V3 (URI ENCODED)
# Bypasses CLI syntax errors by wrapping code in eval(decodeURIComponent(...))

AE_PATH = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
TARGET_SCRIPT = r"c:\Users\user\Desktop\ONIV24\app\scripts\ae\project_neon_sphere_3d.jsx"

def run_injection_v3():
    if not os.path.exists(TARGET_SCRIPT):
        print("Script missing")
        return

    with open(TARGET_SCRIPT, 'r', encoding='utf-8') as f:
        code = f.read()

    # Encode to URI Component (handles newlines, quotes, special chars)
    # quote() by default quotes everything except letters, numbers and '_.-'
    encoded_code = urllib.parse.quote(code)
    
    # Construct the payload
    # We need to be careful with the outer quotes for the CLI.
    # The command will be: AfterFX.exe -s "eval(decodeURIComponent('ENCODED_STRING'))"
    # We need to ensure the ENCODED_STRING doesn't contain single quotes that break the JS string.
    # urllib.parse.quote DOES escape single quotes to %27, so we are safe!
    
    payload = f"eval(decodeURIComponent('{encoded_code}'));"
    
    # Write payload to debugging file just in case
    with open(r"c:\Users\user\Desktop\ONIV24\logs\payload_v3.txt", "w") as f:
        f.write(payload)

    print(f"Injecting V3 Payload ({len(payload)} chars)...")
    
    cmd = [AE_PATH, "-nosplash", "-s", payload]
    
    subprocess.Popen(cmd)
    print("Sent. This should be Syntax-Error free.")

if __name__ == "__main__":
    run_injection_v3()
