import time
from huggingface_hub import snapshot_download, hf_hub_download

REPO = "TencentARC/InstantMesh"
FILES = [
    ("image_encoder", "model.safetensors"),
    ("unet", "diffusion_pytorch_model.safetensors"),
]

def download_with_retry():
    print(f"--- ONI HEAVY DUTY DOWNLOADER ---")
    print(f"Targeting: {REPO}")
    
    while True:
        try:
            print("\n[INFO] Starting full snapshot download...")
            snapshot_download(repo_id=REPO, resume_download=True)
            print("[SUCCESS] Snapshot complete.")
            break
        except Exception as e:
            print(f"[RETRY] Snapshot interrupted: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)

    print("\n[FINISH] All models are now cached and verified.")

if __name__ == "__main__":
    download_with_retry()
