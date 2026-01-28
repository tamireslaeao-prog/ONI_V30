import subprocess
import os
import sys

# ONI AE RUNNER - SOURCE INJECTION MODE
# Bypasses "-r file.jsx" issues by injecting code directly via "-s"

AE_PATH = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"

def run_jsx_as_source(jsx_path):
    if not os.path.exists(jsx_path):
        print(f"Error: JSX not found at {jsx_path}")
        return

    try:
        with open(jsx_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Minify/Clean to be safe for CLI
        # 1. Remove // comments (basic) - dangerous if URL contains //, but usually fine for simple code
        # 2. Flatten lines? No, JS needs newlines or semicolons.
        
        # Escape for PowerShell/CMD
        # The most robust way is to just wrap in double quotes and escape internal double quotes.
        # But for -s, we can just pass the string.
        
        # SANITIZATION
        code_escaped = code.replace('"', "'") # Replace double quotes with single where possible? 
        # Actually proper escaping for PowerShell argument is hard.
        # Best bet: Remove newlines, ensure semicolons, and pass as one robust string.
        
        lines = code.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('//'): continue
            if not line: continue
            clean_lines.append(line)
        
        flat_code = " ".join(clean_lines)
        
        # Double quote escaping for CLI
        flat_code_arg = flat_code.replace('"', '\\"')
        
        cmd = [AE_PATH, "-nosplash", "-s", flat_code]
        
        print(f"Executing Source Injection ({len(flat_code)} chars)...")
        subprocess.Popen(cmd)
        print("Sent to AE.")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_jsx_as_source(sys.argv[1])
    else:
        # Default target
        run_jsx_as_source(r"c:\Users\user\Desktop\ONIV24\app\scripts\ae\project_neon_sphere_3d.jsx")
