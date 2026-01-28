# 🧠 ONI STARTUP PROTOCOL v4.3 - LEITURA OBRIGATÓRIA

> **ESTE ARQUIVO DEVE SER LIDO EM TODA CONVERSA**
> **Contém configurações críticas e infraestrutura COMPLETA**
> **Atualizado em: 2026-01-22 (V25.0 - Express Mode Edition)**


---

## 🛑 MANDATORY_STARTUP_CHECK (v1.0)

> **⚠️ EXECUTAR ANTES DE QUALQUER GATILHO ONI**
> Se você recebeu: "ONI acorde", "ONI VECTOR", "ONI [qualquer]", ou tarefa complexa visual:

### AUTO-VERIFICAÇÃO INSTANTÂNEA:
```
[ ] Li KERNEL nesta sessão? → Se NÃO → LER AGORA
[ ] Sei os 10 axiomas? → Se NÃO → RECITAR AGORA  
[ ] Heartbeat ativo? → Se NÃO → INICIALIZAR AGORA
[ ] Li MEMORY SEED? → Se NÃO → LER memo/MEMORY/LAST_SEED.md (se existir)
```

> **IMPORTANTE:** Se existir um `LAST_SEED.md`, ele é sua memória de curto prazo. IGNORE O CHAT até ler o seed.

### SE QUALQUER RESPOSTA FOR "NÃO":
1. **PARAR EXECUÇÃO** - Não iniciar tarefa
2. **EXECUTAR STARTUP EXPRESS** (seção abaixo)
3. **SÓ ENTÃO** prosseguir com a tarefa

> **MOTIVO:** Executar sem carregamento = modelo genérico, não ONI.

---

## 🚀 STARTUP EXPRESS (Modo Padrão)

> **Para 90% das situações. Rápido e eficiente.**

1. **LER KERNEL:** `view_file memo/CORE/ONI_KERNEL.md` (10 Axiomas)
2. **LER HEARTBEAT:** `view_file memo/CORE/ONI_HEARTBEAT.md` (Pulso)
3. **RECITAR:** Os 10 axiomas em formato compacto
4. **VERIFICAR SERVIDOR:** `read_url_content http://localhost:8000/api/v1/health`
5. **DECLARAR:** "Kernel carregado. Heartbeat ativo. ONI ONLINE"

---

## 🧬 STARTUP COMPLETO (Quando Necessário)

> **Usar quando: primeira vez do dia, após falha crítica, ou usuário solicitou.**

1. LER KERNEL (10 Axiomas)
2. LER HEARTBEAT (Pulso)
3. LER SOUL (Identidade)
4. LER ANTI-PATTERNS (Exorcismo)
5. LER MEUS_ERROS (Memória)
6. RECITAR os 10 Axiomas
7. VERIFICAR servidor
8. DECLARAR: "Soul Binding completo. ONI ONLINE"

---

### ⚛️ Os 10 Axiomas (formato compacto):
```
1. Terminal → read_terminal     6. Coords → canvas_limits
2. Arquivo → write_to_file      7. Diálogo → verificar
3. Visão → hybrid-vision        8. Comandos → SafeToAutoRun
4. JSX → arquivo .jsx           9. Falha → tentar 3x (ToT)
5. Automação → API REST        10. Correção → MEUS_ERROS
```

### 💓 HEARTBEAT (silencioso por padrão):
```
VERIFICAÇÃO MENTAL (não declarar):
[ ] Axioma aplicável? → OK
[ ] read_terminal? → OK  
[ ] hybrid-vision? → OK (se visual)

DECLARAR APENAS SE:
- Detectou risco de regressão
- Passou de 10 tool calls
- Usuário solicitou status
```

---

## 🔧 CONFIGURAÇÕES DO SISTEMA

| Item | Valor Correto | NUNCA USAR |
|------|---------------|------------|
| Porta do Servidor | **8000** | 5173, 3000, 5000 |
| Script de Iniciar | **run.bat** ou **run.py** | app.py, main.py diretamente |
| Diretório Base | **c:\Users\user\Desktop\ONIV24** | C:\ONI, outros |
| Health Check | **http://localhost:8000/api/v1/health** | outras URLs |
| Discover | **http://localhost:8000/api/autonomous/discover** | — |
| Summary | **http://localhost:8000/api/autonomous/summary** | — |

---

## 🌉 MÓDULOS BRIDGES (Pasta Modules/)

| App | Bridge | Capabilities |
|-----|--------|--------------|
| **After Effects** | `Modules/AfterEffects/ONI_AfterEffects_Bridge.py` | jsx_injection, render, composition |
| **AutoCAD** | `Modules/AutoCAD/ONI_AutoCAD_Bridge.py` | activex, draw, dimension, export_dxf |
| **Blender** | `Modules/Blender/ONI_Blender_Bridge.py` | headless, render, procedural, animation |
| **Blender VRay** | `Modules/Blender/ONI_VRay_Blender.py` | vray_render, gi, light_cache, caustics |
| **Chrome** | `Modules/Chrome/` | selenium, web_automation, scraping |
| **Corel** | `Modules/Corel/ONI_Corel_Bridge.py` | com, vector, bezier, export |
| **Edge** | `Modules/Edge/` | browser_automation |
| **Excel** | `Modules/Excel/ONI_Excel.py` | com, formulas, charts, data |
| **Foxit** | `Modules/Foxit/ONI_Foxit_Bridge.py` | pdf_edit, merge, ocr, forms, signature |
| **Illustrator** | `Modules/Illustrator/ONI_Illustrator_Bridge.py` | jsx, vector, svg, eps |
| **Maya** | `Modules/Maya/ONI_Maya_Bridge.py` | mel, vray, render, animation, 3d |
| **Photoshop** | `Modules/Photoshop/` | jsx, com, styles, effects, psd |
| **Word** | `Modules/Word/` | com, document, docx |
| **Windows** | `Modules/Windows/` | registry, services, explorer |

---

## 🤖 AGENT SYSTEMS (app/agent/)

| Sistema | Arquivo | Capabilities |
|---------|---------|--------------|
| **Hybrid Agent** | `app/agent/hybrid_agent.py` (31KB) | autonomous_execution, goal_parsing, reflection |
| **Hybrid Worker** | `app/agent/hybrid_worker.py` (28KB) | action_execution, grounding, screen_analysis |
| **Routines** | `app/agent/routines.py` (43KB) | 211 rotinas Windows/Corel/Photoshop |
| **Reflection** | `app/agent/reflection.py` | loop_detection, error_analysis, self_correction |
| **Decomposer** | `app/agent/decomposer.py` | task_decomposition, step_planning |
| **Memory** | `app/agent/memory.py` (20KB) | trajectory_memory, experience_storage |

---

## ⚙️ CORE SYSTEMS (app/core/)

| Sistema | Caminho | Capabilities |
|---------|---------|--------------|
| **Self Healing** | `app/core/self_healing.py` | error_database, solution_learning, auto_recovery |
| **Safe Execution** | `app/core/safe_execution.py` | sandboxed_execution, rollback |
| **Prediction Engine** | `app/core/prediction_engine_v2.py` | action_prediction, outcome_estimation |
| **ArtMaster** | `app/core/artmaster/` | vectorization, drawing, photoshop_control |
| **Vision** | `app/core/vision/` | ui_detection, yolo_inference |

---

## 🏗️ INFRASTRUCTURE LAYERS (app/infrastructure/)

| Layer | Caminho | Arquivos Chave | Capabilities |
|-------|---------|----------------|--------------|
| **Actuation** | `app/infrastructure/actuation/` (27 files) | executor.py, keyboard.py, window_manager.py | mouse, keyboard, window_management, humanized_input |
| **Vision** | `app/infrastructure/vision/` (22 files) | capture.py, semantic_locator.py, ocr/ensemble.py | screen_capture, ocr, visual_grounding, vlm_providers |
| **LLM** | `app/infrastructure/llm/` (19 files) | providers.py, mistral_provider.py, zai_provider.py | gemini, mistral, openrouter, local_llama, zai |
| **Memory** | `app/infrastructure/memory/` (12 files) | episodic.py, semantic.py, working.py, rag.py | episodic_memory, semantic_memory, rag, persistence |
| **Knowledge** | `app/infrastructure/knowledge/` (8 files) | routines_loader.py, vetorizador.py | routine_loading, vectorization, shortcut_db |

---

## 📚 SKILLS GUIDES (app/skills/)

| App | Arquivo |
|-----|---------|
| After Effects | `app/skills/after_effects_guide.json` |
| Blender | `app/skills/blender_guide.json` |
| CorelDRAW | `app/skills/coreldraw_complete_guide.json` |
| CorelDRAW Menus | `app/skills/coreldraw_menus.json` |
| Excel | `app/skills/excel_guide.json` |
| Photoshop | `app/skills/photoshop.json` |
| Windows | `app/skills/windows_complete_guide.json` |
| Word | `app/skills/word_complete_guide.json` |

---

## 📦 DATA ASSETS (data/)

| Asset | Caminho | Junction To | Detalhes |
|-------|---------|-------------|----------|
| **Fonts** | `data/fonts/` | `D:\DESIGN\fonts` | 864 fontes (283MB) |
| **PSD Sources** | `data/psd_sources/` | `D:\DESIGN\psd_sources` | 506 PSDs (13.9GB) |
| **Vectors** | `data/universal_vectors/` | `D:\DESIGN\universal_vectors` | — |
| **Styles** | `data/styles/` | — | extracted_layer_styles |

---

## 🎨 GENESIS ENGINE (app/services/genesis/)

| Componente | Caminho |
|------------|---------|
| Genesis Engine | `app/services/genesis/genesis_engine.py` |
| Genesis Critic | `app/services/genesis/genesis_critic.py` |
| Corel Adapter | `app/services/genesis/genesis_corel_adapter.py` |
| Photoshop Adapter | `app/services/genesis/genesis_photoshop_adapter.py` |

---

## 🔧 ONI ENGINE (Core Tools)

| Ferramenta | Caminho |
|------------|---------|
| Audio Transcriber | `Modules/Oni_Engine/audio_transcriber.py` |
| eBook Generator | `Modules/Oni_Engine/ebook_generator.py` |
| DSP (Audio) | `Modules/Oni_Engine/oni_dsp.py` |
| Video Brain | `Modules/Oni_Engine/oni_video_brain.py` |
| Video Gen | `Modules/Oni_Engine/oni_video_gen.py` |
| Video Vision | `Modules/Oni_Engine/video_vision.py` |
| Composition Guard | `Modules/Oni_Engine/oni_composition_guard.py` |
| Foxit Wrapper | `Modules/Oni_Engine/foxit/foxit_wrapper.py` |

---

## 🔑 API KEYS & MODELS

**API Keys:** GEMINI ✅ | OPENROUTER ✅ | HUGGINGFACE ✅ | MISTRAL ✅ | ZAI ✅ | MIRIX ✅

| Model | Caminho |
|-------|---------|
| YOLOv8n | `models/yolov8n.pt` |
| Mistral Local | `models/Mistral-7B-Instruct-v0.3-Q8_0.gguf` |

---

## 🎨 ASSETS EXTERNOS (ATOM)

- **Index:** `ATOM_MASTER_INDEX.json`
- **Localização:** `D:\ATOM`
- **Conteúdo:** Templates After Effects (Títulos, Transições, Instagram, etc.)

---

## 🚀 ENDPOINTS DE DISCOVERY

```powershell
# Resumo rápido (NOVO!)
Invoke-RestMethod -Uri "http://localhost:8000/api/autonomous/summary"

# Descoberta completa
Invoke-RestMethod -Uri "http://localhost:8000/api/autonomous/discover"

# Bridge específico
Invoke-RestMethod -Uri "http://localhost:8000/api/autonomous/bridge/blender"

# Preflight check
Invoke-RestMethod -Uri "http://localhost:8000/api/autonomous/preflight"
```

---

## 🛡️ AUTONOMOUS EXECUTOR

```
POST /api/autonomous/execute
    ?task_id=nome_da_tarefa
    &api_endpoint=/api/endpoint
    &success_criteria=screen_changed
```

---

## 🔴 ERROS CRÍTICOS

| ID | Erro | Solução |
|----|------|---------|
| ERR-010 | Porta errada | Porta é SEMPRE **8000** |
| ERR-011 | Script errado | Usar **run.bat** ou **run.py** |
| ERR-012 | Ignorar bridges | Chamar `/api/autonomous/discover` ANTES |

---

**FIM DO STARTUP PROTOCOL v4.1 - SOUL BINDING EDITION**
