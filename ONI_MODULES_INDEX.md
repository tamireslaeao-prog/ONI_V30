# 🧠 ONI V30 MODULE INDEX

> **System Status:** ONLINE
> **Last Update:** 2026-01-25

## 📦 Active Modules (Local Capabilities)

### 🔮 Generative 3D (New!)
| Module | Engine | Status | Path |
|--------|--------|--------|------|
| **InstantMesh** | TencentARC | ✅ Optimized (4GB) | `Modules/InstantMesh` |
| **StableFast3D** | StabilityAI | 🔐 Gated (Requires Login) | `Modules/StableFast3D` |

### 🌉 Bridges (DCC)
| Module | App | Status |
|--------|-----|--------|
| **Maya** | Autodesk Maya 2026 | ✅ Connected (Port 7001) |
| **Blender** | Blender 4.x | ✅ Scripting Ready |

## 🚀 How to Load
To use these modules in a new session, run:
```python
# Generic Loader
import sys
sys.path.append(r"C:\Users\user\Desktop\ONI_V30")

# 3D Generation
from Modules.InstantMesh import instantmesh_adapter
from Modules.StableFast3D import sf3d_adapter
```
