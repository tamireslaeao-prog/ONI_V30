# Greebles Vector Library - Creation Guide
# Target System: Callisto CorelDRAW Automation

> **Definition:** "Greebles" are fine detailed technical or ornamental parts added to the surface of a larger object to make it appear more complex and visually interesting. In the ONI system, these are modular vector assets used by the generative engine.

---

## 1. Library Structure

The Greebles library is organized into categories. All assets must be vector objects (curves), grouped, and scalable.

### Master File
*   **Path:** `[ONIROOT]\Modules\Corel\Library\Greebles_Master_v1.cdr`
*   **Pages:** One page per Category.

### Categories
1.  **Technical_Hardware** (Screws, vents, panels, rivets)
2.  **UI_Labels** (Warning signs, arrows, barcodes, data blocks)
3.  **Ornamental_Geo** (Geometric primitive clusters, fractals)
4.  **Japanese_Trad** (Seals, kamon crests, brush strokes)
5.  **Cyber_Glitch** (Distorted lines, pixel fragments, noise patterns)

---

## 2. Asset Specifications

### General Rules
*   **Format:** Native CorelDRAW vectors (Curves).
*   **Color:** Single color (Black `C0 M0 Y0 K100` or RGB `#000000`) unless specified. The script handles coloring.
*   **Grouping:** Each individual greeble MUST be a single Group object.
*   **Naming:** Use object data/naming in Object Manager: `greeble_[category]_[id]` (e.g., `greeble_tech_042`).
*   **Size:** Built within a 100mm x 100mm bounding box for consistency.

### Category Details

#### A. Technical_Hardware
*   **Style:** Industrial, mechanical.
*   **Elements:**
    *   *Screw Heads*: Phillips, Torx, Hex (Top down view).
    *   *Vent Grills*: Parallel rounded rectangles.
    *   *Access Panels*: Rectangles with "cut corners" and rivets.
*   **Complexity:** Low to Medium.

#### B. UI_Labels
*   **Style:** HUD, Military, Sci-Fi interface.
*   **Elements:**
    *   "DANGER", "CAUTION", "HIGH VOLTAGE" in tiny technical font (converted to keylines).
    *   Directional arrows and chevrons.
    *   Fake barcodes / QR codes (stylized).
    *   Targeting reticles and crosshairs.

#### C. Ornamental_Geo
*   **Style:** Abstract, Memphis, Bauhaus.
*   **Elements:**
    *   Circle clusters.
    *   Triangle tessellations.
    *   Squiggles and wavy lines.
    *   Dot grids (halftones).

#### D. Japanese_Trad
*   **Style:** Cultural, organic yet structured.
*   **Elements:**
    *   *Kamon*: stylized family crests (flower, wave symbols).
    *   *Hanko*: Square seal shapes with faux-kanji.
    *   *Enso*: Circular brush strokes.

#### E. Cyber_Glitch
*   **Style:** Digital decay, datamosh.
*   **Elements:**
    *   Horizontal line tears.
    *   Randomized pixel blocks.
    *   "Signal Lost" static noise patterns.

---

## 3. Creation Workflow

1.  **Drafting**: Use `Grid` view in CorelDRAW. Draw shape using `Pen` or `Rectangle/Ellipse` tools.
2.  **Cleanup**:
    *   `Object > Convert to Curves` (Ctrl+Q).
    *   `Weld` distinct shapes into one curve object where possible.
    *   Remove invisible nodes or cleanup rough paths.
3.  **Grouping**: Group the object (`Ctrl+G`).
4.  **Metadata**: Open `Object Data Manager`. Assign the name tag.
5.  **Storage**: Drag and drop into the "Symbol Manager" or save on the Master Layout page.

---

## 4. Export for Automation

For the script to access these, they can be exported as individual .CDR or .SVG files, or kept in the Master CDR.

**Recommended Structure for Files:**
`[ONIROOT]\Modules\Corel\Library\Assets\`
  `\Tech\`
    `tech_001.svg`
    `tech_002.svg`
  `\UI\`
    `ui_warn_01.svg`

**SVG Export Settings:**
*   **Version:** 1.1
*   **Styling:** Internal CSS
*   **Text:** Convert to curves (Critical!)
*   **Precision:** 3 decimals

---

## 5. Quick "Greeble" Generator Script (Mini-Idea)
*Use the 'ApplyRandomGreebles' macro to test these assets.*

The macro logic loops through this folder, picks a random SVG, imports it, scales it, tints it, and places it in a non-colliding layout position.

---
**End of Specification**
