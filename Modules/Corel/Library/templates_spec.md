# CorelDRAW Template Specification
# Version: 1.0 (ONI System)

> **Note:** These specifications define the structure for .CDT (CorelDRAW Template) files used by the ONI system. When creating these templates manually, follow these guidelines strictly to ensure compatibility with the automation scripts.

---

## 1. System Overview

The **ONI CorelDRAW Template System** relies on a standardized set of layers, styles, and page properties. Each template serves as a base container for the generative design algorithms.

### File Location
All master templates should be saved to: `[ONIROOT]\Modules\Corel\Templates\`

### Naming Convention
`[Category]_[Style]_[Variant].cdt`
*   Example: `Badge_Cyberpunk_v1.cdt`
*   Example: `Poster_Japanese_Vertical.cdt`

---

## 2. Universal Template Structure

All ONI templates must share these common characteristics:

### Color Management
*   **Primary Mode:** RGB (for digital/screen) or CMYK (for print)
*   **Rendering Intent:** Relative Colorimetric
*   **Color Profile:** sRGB IEC61966-2.1 (RGB) / Coated FOGRA39 (CMYK)

### Page Properties
*   **Bleed:** 3.0mm (standard)
*   **Resolution:** 300 DPI (minimum)
*   **Ruler Origin:** Top-Left (0,0)

### Layer Hierarchy (Bottom to Top)
1.  **Background** (Locked, Non-printable guides)
2.  **Base_Layer** (Main backgrounds and fills)
3.  **Data_Merge** (Placeholder zones for variable data)
4.  **Design_Elements** (Static graphical elements)
5.  **Greebles_Container** (Zone for generative details)
6.  **Text_Overlay** (Editable text fields)
7.  **Effects_Overlay** (Post-processing, gradients, glows)
8.  **Output_Info** (Non-printing registration marks, die lines)

---

## 3. Template Definitions

### A. Cyberpunk Identity Badge
*   **Filename:** `Badge_Cyberpunk_v1.cdt`
*   **Size:** 90mm x 140mm (Portrait)
*   **Color Mode:** RGB
*   **Key Features:**
    *   Dark background (`#0A0A0F`)
    *   Neon accent spots (Cyan/Magenta)
    *   Holographic texture overlay layer (Transformation mode: Screen)

#### Layer Specifics:
*   `Data_Merge`: Rectangle (60x80mm) for photo placeholder.
*   `Text_Overlay`: Paragraph text boxes for NAME, RANK, ID. Font: *Orbitron*.
*   `Effects_Overlay`: "Scanlines" pattern fill (transparency 80%).

---

### B. Print-Ready Conference Badge
*   **Filename:** `Badge_Print_Standard.cdt`
*   **Size:** 85.6mm x 53.98mm (standard ID-1/Credit Card)
*   **Color Mode:** CMYK
*   **Key Features:**
    *   High contrast for readability.
    *   Optimized for PVC card printing.
    *   Rich Black (`C60 M40 Y40 K100`) enabled.

#### Layer Specifics:
*   `Output_Info`: Die cut line (Spot Color: "CutContour") 0.25mm outline.
*   `Data_Merge`: QR Code zone (20x20mm) and Barcode zone (bottom edge).

---

### C. Formal Certificate of Achievement
*   **Filename:** `Certificate_Formal_A4.cdt`
*   **Size:** A4 (297mm x 210mm) - Landscape
*   **Color Mode:** CMYK
*   **Key Features:**
    *   Guilloche border pattern (complex vector curves).
    *   Gold foil stamp placeholder (Spot Color: "PANTONE 871 C").

#### Layer Specifics:
*   `Design_Elements`: Vector rosette background pattern (5% opacity).
*   `Text_Overlay`: "Certificate of Achievement" in *Trajan Pro*.
*   `Data_Merge`: Recipient Name field (Center aligned).

---

### D. Japanese Typography Poster
*   **Filename:** `Poster_Japanese_A3.cdt`
*   **Size:** A3 (297mm x 420mm) - Portrait
*   **Color Mode:** CMYK
*   **Key Features:**
    *   Vertical text support.
    *   "Tatami" style grid layout.
    *   Circle "Seal" elements.

#### Layer Specifics:
*   `Text_Overlay`: Vertical text frames (Right-to-Left flow). Font: *Noto Sans JP*.
*   `Design_Elements`: Asanoha (Hemp leaf) pattern background.

---

### E. Synthwave Music Poster
*   **Filename:** `Poster_Synthwave_1080p.cdt`
*   **Size:** 1920px x 1080px (Screen)
*   **Color Mode:** RGB
*   **Key Features:**
    *   Retro 80s sun graphic on horizon.
    *   Perspective grid floor.
    *   Chrome text effects.

#### Layer Specifics:
*   `Effects_Overlay`: Noise grain texture (5% opacity).
*   `Text_Overlay`: Title text with multi-step contour (Chrome effect).

---

### F. Modern Infographic Layout
*   **Filename:** `Infographic_Vertical_Long.cdt`
*   **Size:** 800px x 2000px (Web)
*   **Color Mode:** RGB
*   **Key Features:**
    *   Modular grid system (100px blocks).
    *   Flat icon style.

#### Layer Specifics:
*   `Data_Merge`: Pre-defined chart containers (Pie, Bar, Line placeholders).
*   `Design_Elements`: Connector lines and flow arrows.
*   `Text_Overlay`: Header and body text pairs.

---

## 4. Template Creation Workflow (Manual)

To create a new template for ONI:

1.  **Initialize**: Open CorelDRAW, `File > New`. Set parameters (Size, Color Mode).
2.  **Layers**: Open `Object Manager` docker (`Window > Dockers > Objects`). Create the standard layer hierarchy defined in Section 2.
3.  **Placeholders**: Draw shapes for variable data (Images, Text). Use generic colors (Gray). Name these objects in the Object Manager (e.g., `placeholder_photo`, `text_name`).
4.  **Save**: `File > Save As Template...`. Choose `.CDT` format. Save to `C:\ONI\Corel\Templates`.

## 5. Maintenance Checklist

*   [ ] Check color profiles match production printer requirements.
*   [ ] Verify all text fields are "Artistic Text" or "Paragraph Text" as per requirement.
*   [ ] Ensure "Output_Info" layer is set to non-printing.
*   [ ] Confirm all linked images are embedded, not externally linked.
*   [ ] Test file size (keep under 50MB for performance).

---
**End of Specification**
