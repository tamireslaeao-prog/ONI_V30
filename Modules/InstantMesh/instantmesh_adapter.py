import subprocess
import os
import sys

# --- CONFIG ---
# Resolve paths relative to the project root (assuming Oni V30 structure)
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(MODULE_DIR)) # Up 2 levels (Modules -> Root)
INSTANTMESH_DIR = os.path.join(PROJECT_ROOT, "temp", "3D2", "InstantMesh")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "temp", "instantmesh_output")
CONFIG_PATH = "configs/instant-mesh-base.yaml" # CHANGED FROM LARGE TO BASE

# --- OPTIMIZATION ---
# Aggressive memory management for 4GB GPUs
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"

def run_instantmesh(input_image_path):
    print(f"--- ONI INSTANTMESH AGENT ---")
    print(f"Input: {input_image_path}")
    print(f"Output: {OUTPUT_DIR}")
    
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found: {input_image_path}")
    
    # Ensure output exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # --- PERMANENCE PROTOCOL ---
    # Restore optimized run.py if lost (e.g. temp cleaned)
    PATCH_FILE = os.path.join(MODULE_DIR, "patches", "run_optimized.py")
    TARGET_RUN = os.path.join(INSTANTMESH_DIR, "run.py")
    
    if os.path.exists(PATCH_FILE):
        print(f"[MEMORY] Applying Permanent Optimization Patch to {TARGET_RUN}...")
        import shutil
        try:
            shutil.copy2(PATCH_FILE, TARGET_RUN)
        except Exception as e:
            print(f"[WARNING] Failed to apply patch: {e}")
    # ---------------------------

    # Construct Command
    # python run.py configs/instant-mesh-large.yaml <image> --output_path <dir> --export_texmap
    cmd = [
        sys.executable,
        "run.py",
        CONFIG_PATH,
        input_image_path,
        "--output_path", OUTPUT_DIR,
        "--export_texmap",
        "--save_video"
    ]
    
    print("Launching Subprocess...")
    # Critical: Run inside the repo directory so relative imports (src.*) work
    result = subprocess.run(cmd, cwd=INSTANTMESH_DIR)
    
    if result.returncode == 0:
        print(f"\n[SUCCESS] Model generated in: {OUTPUT_DIR}")
        print("Look for the .obj/.glb in the 'meshes' subdirectory.")
    else:
        print(f"\n[FAILURE] Process exited with code {result.returncode}")

if __name__ == "__main__":
    print("This is a library module. Usage:")
    print("from Modules.InstantMesh import instantmesh_adapter")
    print("instantmesh_adapter.run_instantmesh('path/to/img.png')")
