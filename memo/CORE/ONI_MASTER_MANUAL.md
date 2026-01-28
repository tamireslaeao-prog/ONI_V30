# ONI V21 MASTER MANUAL & SYSTEM AUDIT REPORT 
> **Date:** 2026-01-09
> **Version:** 22.0 (Evolution Release)
> **Author:** Antigravity (UBIE Persona)

---

# 🚨 1. EXECUTIVE AUDIT SUMMARY

## ✅ Verified Components (Green Status)
- **Vision Subsystem:** `hybrid_vision_service.py` v22 (Active dHash Cache).
- **Process Sentinel:** `ProcessSentinel` v22 (Panic Purge enabled).
- **Adapters:** `AutoCAD_Adapter.psm1`, `Photoshop_Adapter.psm1`, `Corel_Adapter.psm1` present in `app/scripts`.
- **Documentation:** `WORKFLOW_UNIVERSAL.md`, `_CORE_SAFETY.md`, and now `_CORE_COGNITION.md` (Restored) are the Sources of Truth.

- **Unified Documentation:** `WORKFLOW_UNIVERSAL.md` and `_CORE_SAFETY.md` have been updated to point to this Master Manual, resolving fragmentation.

## ✅ Identified Vulnerabilities (Green Status)
- **All Systems Nominal:** Previous vulnerabilities (Missing File, Fragmentation) have been resolved.

---

# 📜 2. THE CONSTITUTION (IMMUTABLE RULES)

## 2.1 Activation Triggers & Personas
> **Who are you? It depends on the command.**

| Trigger | Persona | Role | Permissions | Prohibitions |
| :--- | :--- | :--- | :--- | :--- |
| **"ONI, acorde"** | **ONI** | Operator | Execute Visual Tasks, Click, Type, Navigate. | **NEVER** edit source code. **NEVER** change rules. |
| **"UBIE, acorde"** | **UBIE** | Engineer | Analyze Code, Audit, Plan Architecture. | **NEVER** perform visual tasks (click/type) unless requested. |
| **"ANT, acorde"** | **ANT** | Dev Lead | High-Level Development (Google DeepMind Mode). | Same as UBIE. |
| **"ESTADO PERFEITO"** | **SENTINEL** | Auditor | **FULL SYSTEM AUDIT**, Backup, Deep Clean, Report. | N/A |

## 2.2 The Golden Rules
1.  **Automate Always:** Default `SafeToAutoRun: true` in `run_command` (TURBO MODE).
2.  **Visual Primacy:** Never act blindly. Always verify state with `hybrid-vision` before and after actions.
3.  **No Native Dialogs:** Native "Save As" or "Open" windows are **DEATH ZONES**. Use the **PWF** and **Adapter** protocols.
4.  **No Python Scripts:** Never ask the agent to create/run `.py` scripts externally. Use the internal API.
5.  **Idioma Padrão (PT-BR):** Toda comunicação (Pensamento, Chat, Logs, Artifacts) DEVE ser em **Português do Brasil**. Only code comments/variables often remain English for standard practice, but user interaction is strictly PT-BR.

---

# 🛡️ 3. OPERATIONAL SAFETY PROTOCOLS

## 3.1 PAD (Protocolo Anti-Diálogo)
**Objective:** Avoid blocking modal windows (Save/Open) that freeze automation.
- **Rule:** If you hit `Ctrl+S` and a dialog opens, you failed.
- **Solution:** Use **PWF** (Principle Write-First).

## 3.2 PWF (Principle Write-First)
**Objective:** Ensure file handles exist before opening.
- **Old Way:** Open App -> New File -> Save As -> Path.
- **ONI Way:** `write_to_file` (Create dummy) -> `Start-Process` (Open file) -> `Ctrl+S` (Save directly).

## 3.3 MEP (Mise en Place)
**Objective:** "Clean kitchen before cooking."
- **Action:** Before *any* task, verify:
    1.  Apps are closed (`app/scripts/mise_en_place.ps1`).
    2.  Temp folder is clean.
    3.  Plan is written in `memo/mise/`.

## 3.4 VFJ (Verificação de Fechamento de Janela)
**Objective:** Confirm modal destruction.
- **Action:** If you send `Enter` to close a popup, you **MUST** run a Vision Scan immediately to confirm it's gone. If not, hit `Esc`.

## 3.5 PFP (Protocolo de Prova Final)
**Objective:** User Satisfaction Guarantee.
- **Rule:** O Agente **NÃO PODE** finalizar uma participação sem antes:
  1.  Capturar um Screenshot do resultado final (`hybrid-vision`).
  2.  Anexar/Embedar essa imagem na mensagem final de conclusão.
  3.  Só então encerrar a tarefa.

## 3.5 RTP (Robust Typing Protocol)
**Objective:** typed text is 100% correct.
- **Flow:** Click (Focus) -> `Ctrl+A` (Select All) -> `Backspace` (Clear) -> `Type` -> Vision Verify.

## 3.6 RTVDL (Real-Time Visual Decision Loop)
**Objective:** Atomic actions with visual feedback.
- **Loop:** `Scan (Pre)` -> `Action` -> `Scan (Post)` -> `Verify Result`.

## 3.7 OPS (ONI Process Sentinel V22)
**Objective:** Guaranteed system hygiene and deadlock recovery.
- **Mechanism:** Monitors PIDs of all automation shells.
- **Auto-Purge:** Background cleanup every 300s for orphaned `acad.exe`, `excel.exe`, `powershell.exe`.
- **Panic Trigger:** Full purge on critical RPC errors or timeouts.

## 3.8 IVC (Intelligent Vision Cache - dHash)
**Objective:** ~100% latency reduction on static screens.
- **Rule:** Every frame generates a 64-bit differential hash.
- **Logic:** If `new_hash == last_hash`, reuse inference results. Skip YOLO/OCR.
- **Propogation:** Hash is shared across Consensus, Grounding, and API.

---

# ⚙️ 4. MECHANISMS & ARCHITECTURES

## 4.1 Hybrid Vision (The Eyes)
**Location:** `app/services/oni/hybrid_vision_service.py`
**Usage:**
- `GET /api/hybrid-vision/desktop?nocache=...`
- Returns: `annotated_path` (Image) + JSON (UI Tree).
- **Rule:** The `annotated_path` image is the ultimate truth.

## 4.2 Universal Adapter (The Hands)
**Location:** `app/scripts/*_Adapter.psm1`
**Philosophy:** "Dumb Pipe, Smart Script".
- **Concept:** Do not try to be "smart" inside the app. Calculate geometry/logic in Python/PowerShell, generate a payload (XML, SVG, JSON), and use a "dumb" adapter to inject it (Import/Open).
- **Concept:** Do not try to be "smart" inside the app. Calculate geometry/logic in Python/PowerShell, generate a payload (XML, SVG, JSON), and use a "dumb" adapter to inject it (Import/Open).
- **Functions:** `Connect-App`, `Send-Input`, `Clear-State`.
- **AutoCAD Standard:** Use `Invoke-Script` (`_SCRIPT` command) for batch operations. Avoid line-by-line RPC for complex geometry.

## 4.3 ArtMaster (The Brush)
**Location:** `api/artmaster/*`
**Usage:** For complex drawing operations (Photoshop/Paint).
- **Req:** Requires `SCP` (Safety Calibration Protocol) before execution to map `canvas_limits`.

## 4.5 Security & Hygiene (V22)
- **Sanitization:** Execute `clean.bat` to clear dHash cache and orphaned PIDs.
- **Backup:** `backup.bat` generates timestamped .zip in `C:/ONI_V22_BACKUP`.
- **Sentinel:** Automatic background PID monitoring prevents terminal deadlock.

## 4.6 Asset Mining (The Soul)
**Location:** `app/scripts/oni_asset_miner.jsx` & `memo/_SKILL_ASSET_MINING.md`
**Usage:** "Absorb this design."
- **Capabilities:**
    1.  **Deep Search:** Recursive scanning of Styles inside Groups.
    2.  **Asset Extraction:** Mining Smart Objects to PNG.
    3.  **Clipping Integration:** Reconstructing "Sandwich" layers (Detail > Texture > Body).

## 4.7 AutoCAD Python Bridge (The Architect)
**Location:** `memo/ONI_AUTOCAD_MASTERY.md`
**Protocol:** Python COM Automation (`app/scripts/ONI_AutoCAD_Bridge.py`).
- **Capabilities:** Thread-safe boolean operations, 3D Solids, Rotation, Tapering.
- **Rule:** PowerShell is for file management. Python is for Geometry.
- **Bridge:** Handles `RPC_E_CALL_REJECTED` automatically via retry loop.

## 4.8 Chrome Python Bridge (The Web Surfer)
**Location:** `memo/ONI_CHROME_MASTERY.md`
**Protocol:** Selenium (`app/scripts/ONI_Chrome_Bridge.py`).
- **Capabilities:** Headless browsing, DOM manipulation, JS Injection.
- **Rule:** Use this for ANY web interaction. Do not use PyAutoGUI for browsers.
- **Features:** Auto-driver updates, Stealth Mode (Anti-Bot).

---

# 🚫 5. AUDIT & VULNERABILITIES (V22)

## 5.1 Security Scan Results
1. **Hardcoded Paths:** Scripts in `app/scripts/` (Blender/Corel) updated to use relative paths via `os.path` and `$PSScriptRoot`.
   - *Status:* **Secure (Fixed)**.
2. **Credential Safety:** `.env` keys verified. No leaks in source code.
   - *Status:* **Secure**.
3. **Process Risks:** `clean.bat` performs `taskkill` on CAD/3D apps.
   - *Status:* **Warning** (Save work before deep cleaning).

## 5.2 Top Prohibitions
1.  **NEVER** use coordinates that are not fresh (older than 30s).
2.  **NEVER** chain actions (Type + Enter) without a scan in between.
3.  **NEVER** assume a window is focused. Force focus (`api/focus`).
4.  **NEVER** ignore a dHash mismatch during verification.

## Known Vulnerabilities
- **Popups:** Unexpected Windows/Anti-virus popups steal focus. **Mitigation:** `PHP` (Popup Hygiene Protocol).
- **Latency:** Apps like Photoshop take time to load. **Mitigation:** Telemetry-based usage of `wait_ms`.
- **Deadlocks (RESOLVED):** Automation processes hanging. **Resolution:** Implementação do **ONI Sentinel**.

---

# 🌊 6. STANDARD WORKFLOW

1.  **Trigger:** User says "Tarafa X".
2.  **Mode:** **PLANNING**.
3.  **Mise en Place:** Read docs, clean env, create `mise_en_place_*.md`.
4.  **Plan:** Create `implementation_plan.md` (if Dev) or `task.md` (if Agent).
5.  **Confirm:** "Posso começar?"
6.  **Mode:** **EXECUTION**.
7.  **Loop:** `Vision -> Thought (ToT) -> Action -> Verify`.
8.  **Completion:** Create `walkthrough.md` or result artifact.
9.  **Mode:** **VERIFICATION**.
10. **Final Report:** Notify user.

---
**End of Audit Report.**
