# Workflow: Open Photoshop & Create New Document

**Status:** Verified Working
**Date:** 2025-12-27

## Objective
Successfully open Adobe Photoshop and initialize a new blank canvas using keyboard shortcuts via ONI API.

## Sequence of Actions

### 1. Launch Photoshop
*   **Action:** Open Start Menu
    *   `GET /api/keys?keys=win&delay=1.0`
*   **Action:** Search for Application
    *   `GET /api/type?text=Photoshop`
*   **Action:** Launch Application
    *   `GET /api/keys?keys=enter&delay=5.0`
    *   *Note:* Wait 5 seconds for the application to load completely.

### 2. Create New Document
*   **Action:** Open "New Document" Dialog
    *   `GET /api/keys?keys=ctrl,n&delay=2.0`
*   **Action:** Confirm Default Settings (Create Canvas)
    *   `GET /api/keys?keys=enter&delay=2.0`

## Visual Analysis Protocol (Post-Action)
After executing this sequence, always perform:
1.  `GET /api/active-window` to confirm Photoshop is focused.
2.  `GET /api/screenshot-enhanced` to verify the white canvas is visible.
