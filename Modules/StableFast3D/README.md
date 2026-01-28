# 🔮 ONI StableFast3D Module

> **Engine:** `stabilityai/stable-fast-3d`
> **Local Path:** `temp/3D2/stable-fast-3d-main`
> **Status:** ✅ OPERATIONAL (CUDA 12.1)

## 🏗️ Architecture
This module provides a local bridge to the `stable-fast-3d` inference engine. It bypasses cloud restrictions by running directly on the user's NVIDIA GPU.

### Prerequisites (CRITICAL)
This module requires a specifically crafted environment to compile `tiny-cuda-nn`:
1.  **Visual Studio 2022 Community**: With "Desktop Development with C++" workload.
2.  **CUDA Toolkit 12.1**: Exact version mismatch causes `nvcc` errors.
3.  **PyTorch cu121**: Matched to the Toolkit.

## 🚀 Usage

```python
from Modules.StableFast3D import sf3d_adapter

# Run Inference
model_path = sf3d_adapter.run_sf3d_inference(
    image_path="path/to/image.png",
    output_dir="path/to/output"
)
```

## 🛠️ Internal Logic
1.  **Background Removal:** Uses `rembg` to isolate the subject.
2.  **Preprocessing:** Resizes and centers the subject (Ratio 0.85).
3.  **Inference:**
    -   Loads `model.safetensors` (Automated download from HF Hub).
    -   Executes mesh reconstruction (0.5s on RTX 3060+).
    -   Optimizes mesh topology (`remesh="triangle"`).
4.  **Export:** Saves as `.glb` (GLTF Binary) with embedded textures.

## ⚠️ Troubleshooting
-   **Error:** `gated repo` -> You must log in via `huggingface-cli login` once.
-   **Error:** `ninja: build stopped` -> Reinstall Visual Studio 2022.
-   **Error:** `No module named sf3d` -> Check `sys.path.append` in adapter.
