# ⛏️ SKILL: DEEP ASSET MINING (PHOTOSHOP)

> **Module:** ONI_ASSET_MINER
> **Version:** 1.0
> **Status:** BATTLE TESTED (Project 422)

## 1. The Philosophy
Standard usage of `psd-tools` or basic JSX only scratches the surface. To replicate a "Premium" design, we must mine the **Assets** (Textures/Images) and the **Deep Styles** (Stacks).

## 2. Protocols

### A. Recursive Style Scanning (The "Deep Search")
Standard tools miss effects inside Groups (`LayerSet`).
**Solution:** Recursive Loop.
```javascript
function findAllStylesRecursive(layers, results) {
    if (layer.typename == "LayerSet") recurse(layer.layers);
    else extract(layer.lefx);
}
```
**Outcome:** We found that "Metal" styles are often split:
- Layer A (Top): Satin/Sheen
- Layer B (Bottom): Gradient/Body

### B. Smart Object Mining (The "Drill")
We can enter Smart Objects to steal the raw assets.
**Command:** `stringIDToTypeID("placedLayerEditContents")`
**Workflow:**
1. Open Host PSD.
2. Iterate layers looking for `LayerKind.SMARTOBJECT`.
3. Execute "Edit Contents" -> Opens child `.psb`.
4. `ExportOptionsSaveForWeb` (PNG) -> Save to `data/textures/extracted/`.
5. Close `.psb` without saving.

### C. Pixel Layer Extraction (The "Surface Mine")
Sometimes the texture is just a raster layer, not a Smart Object.
**Workflow:**
1. Identify target layer (e.g., "Texture").
2. `layer.duplicate()` to a `new Document`.
3. `doc.trim(TrimType.TRANSPARENT)`.
4. Save PNG.

### D. The "Integration Sandwich" (Reconstruction)
To re-assemble, we must respect the Z-Order and Clipping Masks.
**Formula:**
1. **BASE:** Text Layer (with Body Styling).
2. **TEXTURE:** Placed above Base. **Clipped** (`grouped = true`).
3. **DETAIL:** Duplicated Text Layer (Fill 0%) above Texture. (Top Shine).

## 3. Key Scripts (Consolidated)
- `oni_deep_scan.jsx`: Extracts Styles (Recursive).
- `oni_asset_miner.jsx`: Extracts Images (SO + Pixel).
- `oni_apply_stack.jsx`: Rebuilds the Sandwich.

## 4. Usage
When user says "Absorb this", run **Scan** + **Mine**.
When user says "Replicate this", run **Apply Stack**.
