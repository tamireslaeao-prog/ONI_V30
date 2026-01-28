import os
import sys
import torch
from PIL import Image
import numpy as np

# --- CONFIG ---
# Resolve paths relative to the project root (assuming Oni V30 structure)
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(MODULE_DIR)) # Up 2 levels (Modules -> Root)
SF3D_ROOT = os.path.join(PROJECT_ROOT, "temp", "3D2", "stable-fast-3d-main")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "temp", "sf3d_output")

# Add SF3D to path
sys.path.append(SF3D_ROOT)

try:
    from sf3d.system import SF3D
    from sf3d.utils import remove_background, resize_foreground
    import rembg
except ImportError as e:
    print(f"CRITICAL: Could not import SF3D modules. Ensure requirements are installed in {SF3D_ROOT}")
    print(f"Error: {e}")
    sys.exit(1)

def run_sf3d_inference(input_image_path):
    print("--- ONI LOCAL SF3D AGENT ---")
    print(f"Device: {torch.cuda.get_device_name(0)}")
    
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found: {input_image_path}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Load Model
    print("Loading Model (stabilityai/stable-fast-3d)...")
    model = SF3D.from_pretrained(
        "stabilityai/stable-fast-3d",
        config_name="config.yaml",
        weight_name="model.safetensors",
    )
    model.cuda()
    model.eval()
    
    # 2. Process Image
    print(f"Processing Image: {input_image_path}")
    rembg_session = rembg.new_session()
    
    raw_img = Image.open(input_image_path).convert("RGBA")
    
    # Auto-Remove Background
    print("Removing Background...")
    nobg_img = remove_background(raw_img, rembg_session)
    input_img = resize_foreground(nobg_img, 0.85)
    
    # Save processed input for debug
    input_img.save(os.path.join(OUTPUT_DIR, "debug_input.png"))
    
    # 3. Generate 3D
    print("Generating 3D Mesh (0.5s)...")
    with torch.no_grad():
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            mesh, glob_dict = model.run_image(
                [input_img],
                bake_resolution=1024,
                remesh="triangle", # Optimization
                vertex_count=-1
            )
    
    # 4. Export
    out_path = os.path.join(OUTPUT_DIR, "rick_sf3d.glb")
    mesh[0].export(out_path, include_normals=True)
    
    print(f"SUCCESS! Model saved to: {out_path}")
    return out_path

if __name__ == "__main__":
    print("This is a library module. Usage:")
    print("from Modules.StableFast3D import sf3d_adapter")
    print("sf3d_adapter.run_sf3d_inference('path/to/img.png')")
