# 🧠 Blender Procedural Patterns (Learned from Perfect Eye/Ear)

> **Data:** 2026-01-19
> **Context:** Modeling organic stylized parts (Eye, Ear) via Python API.

## 🌟 1. Silhouette-First Modeling (The "Anti-Primitive" Pattern)
**Context:** Creating complex organic shapes (like Ears) by deforming primitives (Cylinders) failed ("Clam Shape").
**The Fix:**
Instead of starting with a volume, start with a **2D Outline (Loop)**.
1.  Define coordinates for the profile loop manually.
2.  Fill Face (`bm.faces.new`).
3.  Extrude to create volume.
4.  Modulators (Subsurf) handle the smoothing.
**Why:** Guarantees the fundamental shape (Silhouette) is correct before topology gets messy.

## 🌟 2. Robust Extrude-Scale (Replacing Inset)
**Context:** `bmesh.ops.inset_region` is physically accurate but fragile. It fails/overlaps on acute angles (like Tragus notch) or small scales.
**The Fix:**
Use **Extrude -> Translate -> Scale** sequence instead.
1. `bmesh.ops.extrude_face_region` (Creates new faces).
2. `bmesh.ops.translate` (+Y Thickness).
3. `bmesh.ops.scale` (Simulation of Inset).
**Why:** Never fails on bad geometry. Scale reduces the loop size regardless of angles.

## 🌟 3. The "Deep Hollow" Principle
**Context:** Texture maps or slight depressions failed to look like an Ear Canal or Pupil.
**The Fix:**
**Physical Depth > Visual Trick.**
-   Push vertices SIGNIFICANTLY into the mesh (+/- axis).
-   If needed, push them "through" the back (if clipped).
**Why:** SSS (Subsurface Scattering) needs thickness variation to work. Physical depth creates real shadows in Cycles.

## 🌟 4. Studio World Override (Shadow Control)
**Context:** Default Blender "Forest.exr" HDRI ruins procedural reflection testing.
**The Fix:**
Programmatically create a **World Shader Node Tree** in the script.
-   `ShaderNodeBackground` (Dark Blue/Grey).
-   Disconnect default world.
**Why:** Ensures the code output looks identical on any user machine, independent of their local Blender startup file.

## 🌟 5. Cycles Switch (Glass Fix)
**Context:** Eevee (especially 4.2) struggles with nested refraction (Cornea -> Iris).
**The Fix:**
Force `scene.render.engine = 'CYCLES'` in the script setup.
**Why:** Eevee requires complex "Screen Space Refraction" settings that break between versions. Cycles works OOTB for Glass.
