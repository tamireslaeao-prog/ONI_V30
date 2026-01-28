# 🎓 ONI: Photoshop Mastery Profile (V22)
**Status:** Combat Ready (Level 10/10)
**Date:** 2026-01-10
**Architecture:** COM Interop + Action Manager (Hybrid)

---

## 🏗️ 1. The Skill Tree
Our capabilities are structured into three distinct tiers of complexity, moving from basic manipulation to "God Mode".

### Tier 1: The Foundation (Infrastructure)
*   **Connection Protocol:** Robust handling of `RPC_E_SERVERCALL_RETRYLATER` (0x8001010A) with retry loops.
*   **Units:** Strict enforcement of Pixels (`Preferences.RulerUnits = 1`) at script start.
*   **Canvas Logic:** Precision control of Document creation, Resize, and Canvas Size.
*   **Layer Management:** Creating, naming, ordering, opacity control, and locking.

### Tier 2: The Chemistry (Depth & FX)
*   **Filters:** Type-safe application of Gaussian Blur, Add Noise, and Unsharp Mask.
*   **Blending Modes:** Mastery of `psMultiply` (Darken), `psScreen` (Lighten), `psOverlay` (Contrast) via Enum constants.
*   **Procedural FX:**
    *   *Manual Shadow:* Duplicate -> Fill Black -> Blur -> Multiply -> Offset.
    *   *Vignette:* Ellipse Selection -> Invert -> Feather -> Fill Black -> Multiply.
*   **Selection Dynamics:** Feathering, Inverting, and Expanding/Contracting selections for organic masks.

### Tier 3: The Architecture (Precision & Code)
*   **Hybrid Vector Engine:** Generating perfect Bezier Curves (Heart, Star) using **JSX Payloads** to bypass PowerShell's Array marshalling limitations.
    *   *Method:* `DoJavaScript( "doc.pathItems.add(...)" )` with `PointKind.SMOOTHPOINT`.
*   **Smart Automation:** Using the **Action Manager** (`executeAction`) for tasks inaccessible via COM:
    *   Select All Layers.
    *   Convert Layer/Group to Smart Object.
    *   Complex Alignments.
*   **Clipping Logic:** Programmatic Clipping Masks using `Layer.Group = true`.

---

## ⚡ 2. Master Techniques (The Secrets)

### Performance: `suspendHistory`
Direct DOM commands update the UI/History for *every step* (slow).
*   **The Fix:** Wrap operations in `doc.suspendHistory(Name, CodeString)`.
*   **Speedup:** 10x faster execution for complex sequences.

### Action Manager: The "Nuclear Option"
When COM fails (e.g., "Convert to Smart Object"), we use the internal event engine.
*   **Pattern:** `ActionDescriptor` (Params) -> `ActionReference` (Target) -> `executeAction`.
*   **Tools:** Use `stringIDToTypeID` (Readable) over `charIDToTypeID` (Cryptic).

### The "New Document" Quirk (2026 UI)
*   **Problem:** The 2026 "New Document" dialog has a non-standard UI where the "Create" button is hidden from automation.
*   **Solution:**
    1.  Prefer `Ctrl+O` (Open existing) over `Ctrl+N`.
    2.  If creating new, use `app.documents.add()` via Script, bypassing the UI entirely.

### Hybrid Arrays
PowerShell cannot natively marshal complex structures like `PathPointInfo[]` to COM.
*   **Solution:** Construct the array entirely inside a JavaScript string and execute via `DoJavaScript`.

---

## 📚 3. Portfolio (Verified Scripts)
*Scripts located in `app/scripts/` serving as proof of capability.*

| Script | Capability Demonstrated |
|--------|-------------------------|
| `ps_v8_final.ps1` | **Magnum Opus:** Generating 6 distinct ONI Brand Signatures. |
| `ps_class2_fx_fixed.ps1` | Robust Rasterization, Blur, and Manual FX. |
| `ps_class3_smart_clip.ps1` | Action Manager V3 (Select -> Group -> Smart Object). |
| `ps_master_vectors.ps1` | Drawing Smooth Bezier Paths via JSON/JSX. |
| `ps_master_speed.ps1` | Benchmarking `suspendHistory`. |

---

## 📖 4. Core Knowledge (Sources)
*   **Official:** Adobe Photoshop Scripting Guide (2020).
*   **Community:** Scripting Listener Plugin (Action Manager IDs).
*   **Empirical:**
    *   *Fill vs Recolor:* `Layer.Fill` fails on Text; use `TextItem.Color` instead.
    *   *Rasterize:* `Rasterize(5)` (Type) vs `Rasterize(1)` (Layer) - distinct enums.
