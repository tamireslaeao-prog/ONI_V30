# 🧊 INSTANTMESH KNOWLEDGE BASE

> **Módulo:** Modules/InstantMesh
> **Versão:** V1.0 (TencentARC)
> **Status:** ⚡ Operational (Base Model)

---

## 🎯 Quick Commands

### Python Execution
```python
from Modules.InstantMesh import instantmesh_adapter

instantmesh_adapter.run_instantmesh(
    input_image="path/to/image.png"
)
```

---

## 🏗️ Architecture

### Arquivos
- `instantmesh_adapter.py`: Wrapper de subprocesso.
- `temp/3D2/InstantMesh`: Repositório clonado.
- `temp/instantmesh_output`: Destino dos modelos.

### Requirements (V30 Specific)
- **Repo:** `TencentARC/InstantMesh` cloned locally.
- **Weights:** `facebook/dino-vitb16`, `stabilityai/sd-turbo` (Auto-download).
- **VRAM:** Minimum 4GB (Optimized).

---

## 💡 Capabilities

- **Input:** Single Image (RGB).
- **Process:** Multi-view diffusion -> Sparse Reconstruction.
- **Output:** OBJ, GLB, USDZ.
- **Quality:** High geometry detail, slightly lower texture resolution than SF3D.

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| `CUDA OOM` | Fechar Chrome/Photoshop. Usar `max_split_size_mb:64`. |
| `ImportError: src` | Sempre rodar com `cwd=INSTANTMESH_DIR`. |
| `TypedStorage Warning` | Ignorar (Aviso do PyTorch antigo). |
