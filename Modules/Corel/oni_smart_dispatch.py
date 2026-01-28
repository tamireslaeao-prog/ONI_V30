"""
ONI SMART DISPATCH - COREL VECTORIZATION
Intelligent router for 'oni_vector_corel' trigger.

Logic:
1. Input is File Path? -> Send to Corel Bridge (Vectorize)
2. Input is Text?      -> Send to NanoBanana (Generate) -> Then to Corel Bridge (Vectorize)
"""

import sys
import os
import subprocess
import argparse

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Modules
PROJECT_ROOT = os.path.dirname(BASE_DIR)
NANO_SCRIPT = os.path.join(BASE_DIR, "Photoshop", "VectorFactory", "nanobanana_gen.py")
COREL_BRIDGE = os.path.join(BASE_DIR, "Corel", "ONI_Corel_Bridge.py")

def is_file_path(input_str):
    # Check if looks like a path or exists
    if os.path.exists(input_str):
        return True
    
    # Check extensions
    valid_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']
    if any(input_str.lower().endswith(ext) for ext in valid_exts):
        # It's intended as a file, even if missing (let bridge handle error)
        return True
        
    return False

def generate_image(prompt):
    print(f"[DISPATCH] Detected Prompt: '{prompt}'")
    print(f"[DISPATCH] Routing to NanoBanana (Stability AI)...")
    
    cmd = ["python", NANO_SCRIPT, prompt]
    try:
        # Capture output to find the generated file path
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"[ERROR] Generation Failed: {result.stderr}")
            return None
            
        # Parse output for "Image saved to: "
        for line in result.stdout.splitlines():
            if "Image saved to:" in line:
                rel_path = line.split("Image saved to:")[1].strip()
                # NanoBanana uses relative path from PROJECT_ROOT
                abs_path = os.path.join(PROJECT_ROOT, rel_path)
                if os.path.exists(abs_path):
                    return abs_path
                # Fallback: try as absolute
                if os.path.exists(rel_path):
                    return rel_path
                
    except Exception as e:
        print(f"[ERROR] NanoBanana Execution Failed: {e}")
        return None
        
    return None

def vectorize_image(image_path):
    print(f"[DISPATCH] Routing to Corel Bridge: {image_path}")
    
    cmd = ["python", COREL_BRIDGE, "--trace", image_path]
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Corel Bridge Failed: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: oni_smart_dispatch.py <input>")
        sys.exit(1)
        
    # Join all args to handle spaces in prompts without quotes if passed loosely
    # But batch file usually passes "%~1" or "%*"
    # Let's assume sys.argv[1] is the primary payload if quoted
    
    input_arg = " ".join(sys.argv[1:]).strip('"').strip()
    
    # DECISION MATRIX
    target_image = None
    
    if is_file_path(input_arg):
        print(f"[DISPATCH] Mode: DIRECT FILE")
        target_image = input_arg
    else:
        print(f"[DISPATCH] Mode: TEXT PROMPT")
        target_image = generate_image(input_arg)
        
    if target_image:
        if os.path.exists(target_image):
            vectorize_image(target_image)
        else:
            print(f"[ERROR] Target image not found: {target_image}")
            sys.exit(1)
    else:
        print("[ERROR] Could not resolve input to an image.")
        sys.exit(1)

if __name__ == "__main__":
    main()
