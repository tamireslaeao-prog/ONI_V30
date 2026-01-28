# 🧊 ONI InstantMesh Module

> **Engine:** `TencentARC/InstantMesh`
> **Local Path:** `temp/3D2/InstantMesh`
> **Status:** ✅ OPERATIONAL (4GB GPU Optimized)

## 🏗️ Architecture
State-of-the-art Single Image to 3D generation based on LGM (Large Gaussian Model).
This ONI implementation employs **aggressive VRAM optimization** to run on consumer GPUs (GTX 1650 / 4GB).

### Optimizations Applied
- `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64`: Prevents fragmentation.
- **Base Config:** Uses `instant-mesh-base.yaml` instead of large.
- **Subprocess Isolation:** Runs in a separate process to release VRAM immediately after generation.

## 🚀 Usage

```python
from Modules.InstantMesh import instantmesh_adapter

# Generate 3D Model
instantmesh_adapter.run_instantmesh(
    input_image="path/to/logo.png"
)
```

## 🛠️ Output
Files are saved to `temp/instantmesh_output`:
- `*.obj`: Mesh file.
- `*.glb`: Binary GLTF (Web/AR ready).
- `*.mp4`: Turntable animation.
