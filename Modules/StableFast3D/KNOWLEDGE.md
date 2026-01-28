# 🔮 STABLE FAST 3D KNOWLEDGE BASE

> **Módulo:** Modules/StableFast3D
> **Versão:** V1.0 (Local GPU)
> **Status:** ⚡ Operational (CUDA 12.1)

---

## 🎯 Quick Commands

### Python Execution
```python
from Modules.StableFast3D import sf3d_adapter

# Generate 3D Model
glb_path = sf3d_adapter.run_sf3d_inference(
    input_image_path="path/to/image.png"
)
print(f"Model saved to: {glb_path}")
```

---

## 🏗️ Architecture

### Arquivos
- `sf3d_adapter.py`: Wrapper principal para a engine.
- `temp/3D2/stable-fast-3d-main`: Codigo fonte da Stability AI.

### Requirements (V30 Specific)
- **Visual Studio 2022:** C++ Desktop Workload (Required for Ninja/NVCC).
- **CUDA 12.1:** Strict version requirement.
- **PyTorch:** `cu121` build.

---

## 💡 Engine Details

- **Input:** Image (RGBA preferred, auto-removes background).
- **Process:** Single-view reconstruction (Tri-plane Gaussian Splatting -> Mesh).
- **Output:** `.glb` (Textured Mesh).
- **Time:** ~0.5s per model.

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| `Ninja: build stopped` | Reinstalar VS2022 + C++ CMake Tools |
| `HuggingFace 401` | Rodar `huggingface-cli login` |
| `Torch not compiled with CUDA` | Reinstalar Torch com `--index-url https://download.pytorch.org/whl/cu121` |
