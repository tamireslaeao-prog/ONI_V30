import subprocess
import os
import sys
import re

# ONI AE RUNNER - SOURCE INJECTION MODE V2
# Bypasses "-r file.jsx" by injecting sanitized code via "-s"

AE_PATH = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
TARGET_SCRIPT = r"c:\Users\user\Desktop\ONIV24\app\scripts\ae\project_neon_sphere_3d.jsx"

def sanitize_jsx(path):
    if not os.path.exists(path):
        print(f"Error: File not found {path}")
        return ""
        
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    sanitized = []
    for line in lines:
        # Strip whitespace
        line = line.strip()
        # Remove single line comments
        if line.startswith("//"): continue
        if not line: continue
        
        # Remove inline comments (naive)
        if "//" in line:
            line = line.split("//")[0].strip()
            
        # Ensure semicolon at end if generic statement (simple heuristic)
        if not line.endswith(";") and not line.endswith("{") and not line.endswith("}"):
            line += ";"
            
        sanitized.append(line)
        
    # Join into one massive string
    # Replace double quotes with escaped double quotes? 
    # Actually Python subprocess handles arg quoting, but AE -s receives the string.
    # AE might choke on unescaped quotes inside the string if they conflict with outer shell quotes.
    # Safe bet: Use single quotes in JS where possible, or escape double quotes.
    
    full_code = " ".join(sanitized)
    return full_code

def run_injection():
    print(f"Reading {TARGET_SCRIPT}...")
    code = sanitize_jsx(TARGET_SCRIPT)
    if not code: return

    print(f"Injecting {len(code)} bytes payload to AE...")
    
    # Check if AE path exists
    if not os.path.exists(AE_PATH):
        print("AE Executable not found!")
        return

    # Subprocess call
    # We pass the code as a single argument to -s
    try:
        # Using shell=False is safer and handles args better usually, 
        # but for extremely long strings Windows CreateProcess has a limit (32k chars).
        # Our script should be small enough (<32k).
        cmd = [AE_PATH, "-nosplash", "-s", code]
        
        subprocess.Popen(cmd)
        print("Payload sent. Check AE.")
        
    except Exception as e:
        print(f"Injection Failed: {e}")

if __name__ == "__main__":
    run_injection()
