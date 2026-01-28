# 📡 ONI API REGISTRY
> **Versão:** 25.0  
> **Data:** 2026-01-21  
> **Base URL:** `http://localhost:8000`  
> **IMPORTANTE:** Este documento DEVE ser lido no startup "ONI, acorde"

---

## ⚡ QUICK REFERENCE

| Módulo | Prefix | Descrição |
|--------|--------|-----------|
| **Core** | `/api` | Endpoints principais (vision, mouse, keyboard) |
| **Photoshop** | `/api/photoshop` | COM Bridge para Adobe Photoshop |
| **Blender** | `/api/blender` | Python Bridge para Blender |
| **Agent** | `/api/v1/agent` | Agente Híbrido |
| **Onihand** | `/api/v1/onihand` | Gestos e Arte |
| **Segmentation** | `/api/segment` | Análise Visual (scikit-image) |

---

## 🎛️ CORE ENDPOINTS (`/api`)

### Vision & Perception
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/hybrid-vision/desktop` | GET | Scan completo da tela (UI + Screenshot + Annotated) |
| `/api/hybrid-vision/web` | GET | Scan de páginas web |
| `/api/screenshot` | GET | Captura de tela simples |

### Mouse Control
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/click` | GET | `x`, `y`, `button=left`, `clicks=1` | Clique simples |
| `/api/mouse/double-click` | GET | `x`, `y` | Double-click |
| `/api/mouse/safe-drag` | GET | `start_x`, `start_y`, `end_x`, `end_y` | Drag seguro |

### Keyboard Control
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/keys` | GET | `keys` (ex: `ctrl,s`) | Pressionar teclas |
| `/api/type` | GET | `text` | Digitar texto |

### Window Management
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/focus` | GET | `title` | Focar janela por título |
| `/api/open` | GET | `name`, `wait=2` | Abrir aplicativo |
| `/api/windows` | GET | - | Listar janelas abertas |

---

## 🎨 PHOTOSHOP ENDPOINTS (`/api/photoshop`)

> **Tecnologia:** win32com (COM Automation) + JavaScript (DoJavaScript)  
> **Requer:** Photoshop rodando

### Conexão
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/photoshop/connect` | POST | Estabelece conexão COM com Photoshop |
| `/api/photoshop/open` | POST | Abre documento (param: `path`) |

### Comandos Genéricos
| Endpoint | Método | Body | Descrição |
|----------|--------|------|-----------|
| `/api/photoshop/command` | POST | `{"action": "create_doc", "params": {...}}` | Comando genérico |

**Actions suportadas:**
- `create_doc`: Cria documento (`width`, `height`, `name`)
- `set_color`: Define cor foreground (`r`, `g`, `b`)
- `select_tool`: Seleciona ferramenta (`tool_name`)

### Desenho
| Endpoint | Método | Body | Descrição |
|----------|--------|------|-----------|
| `POST /api/photoshop/draw/stroke` | `points=[[x,y]...]`, `tool=brush` | Draw smooth stroke (no jitter). |

### 2.6. Composition & Asset Management (New V12)

| Endpoint | Parameters | Description |
|---|---|---|
| `POST /api/photoshop/compose` | `assets=[{path, label, y_offset}]`, `dark_mode=true` | **Auto-Composer:** Creates a new master document and composes multiple PSD assets into it, handling layout, scaling, and visibility fixes (Dark Mode). |

### 🆕 Layers (V2 - 2026-01-21)
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/photoshop/layers` | GET | - | Lista TODAS as layers (nome, tipo, visibilidade) |
| `/api/photoshop/layers/select` | POST | `name` ou `index` | Seleciona layer por nome ou índice |

### 🆕 Smart Objects (V2)
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/photoshop/smart-object/open` | POST | - | Abre Smart Object selecionado (.psb) |
| `/api/photoshop/smart-object/close` | POST | `save=true` | Fecha Smart Object e retorna ao documento pai |

### 🆕 Text (V2)
| Endpoint | Método | Params | Descrição |
|----------|--------|--------|-----------|
| `/api/photoshop/text/replace` | POST | `new_text`, `layer_name` (opcional) | Substitui texto em layer TEXT |

### 🆕 Document (V2)
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/photoshop/document/info` | GET | Info do documento (nome, size, path, saved) |
| `/api/photoshop/document/save` | POST | Salva documento (Ctrl+S) |

### 🆕 JSX (V2)
| Endpoint | Método | Body | Descrição |
|----------|--------|------|-----------|
| `/api/photoshop/execute-jsx` | POST | `{"script": "..."}` | Executa JavaScript arbitrário no Photoshop |

---

## 🧊 BLENDER ENDPOINTS (`/api/blender`)


| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/blender/execute` | POST | Executa Python no Blender |
| `/api/blender/render` | POST | Renderiza cena |

---

## 🔬 SEGMENTATION ENDPOINTS (`/api/segment`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/segment/analyze` | POST | Análise de imagem (regiões, contornos) |

---

## 🤖 AGENT ENDPOINTS (`/api/v1/agent`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/agent/execute` | POST | Executa task via agente |
| `/api/v1/agent/status` | GET | Status do agente |

---

## ✋ ONIHAND ENDPOINTS (`/api/v1/onihand`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/onihand/draw` | POST | Desenho assistido |

---

## 🔧 UTILITY ENDPOINTS

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/autonomous/startup` | GET | Status do servidor ONI |
| `/api/v1/health` | GET | Health check |

---

## 📝 NOTAS DE USO

### Padrão de Chamada (Agente)
```python
# Usar read_url_content para GET
read_url_content("http://localhost:8000/api/keys?keys=ctrl,s")

# Usar run_command + curl para POST
curl -X POST http://localhost:8000/api/photoshop/command -H "Content-Type: application/json" -d '{"action":"create_doc"}'
```

### Verificação pós-ação
Sempre verificar resultado com:
```
GET /api/hybrid-vision/desktop?nocache=[timestamp]
```

---

**ATUALIZADO:** 2026-01-21 por ANT (Fixing Memory Gap)
