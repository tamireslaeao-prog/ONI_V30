# SKILL: AUTOCAD UNIVERSAL CONTROL (GOD MODE)
> **Protocol:** DUAL INJECTION STRATEGY
> **Status:** ACTIVE & VERIFIED

## 1. The Concept
To achieve "God Mode" in AutoCAD, we bypass the UI ribbon and standard slow typing. We inject a custom "Neural Network" of shortcuts directly into the host's configuration.

## 2. The Mechanism (Dual Injection)
We use two vectors to gain control:

### Vector A: The PGP Hack (Speed)
**Target:** `acad.pgp` (Program Parameters)
**Action:** We inject `ONI_*` aliases pointing to standard commands.
**Benefit:**
*   `ONI_L` -> `LINE` (Instant, no ambiguity)
*   `ONI_TR` -> `TRIM`
*   `ONI_PU` -> `PURGE`
**Script:** `app/scripts/Inject-AutoCAD-Keys.ps1`

### Vector B: The LISP Kernel (Logic)
**Target:** `oni_kernel.lsp` loaded via `acaddoc.lsp`
**Action:** We load custom functions on startup.
**Benefit:** Allows logic that simple aliases can't do.
*   `ONI_CLEAN` -> Runs a sequence of Purge + Audit + Zoom Extents.
*   `ONI_GET_BOUNDS` -> Returns drawing geometry to the Agent.

## 3. Installation Flow
1.  **Locate:** Find `acad.pgp` (via LISP `(findfile "acad.pgp")` or File Search).
2.  **Backup:** Always create `acad.pgp.bak`.
3.  **Inject:** Append `ONI_*` block.
4.  **Hook:** Create `acaddoc.lsp` in the same folder to load `oni_kernel.lsp`.
5.  **Restart:** Restart AutoCAD to load the new brain.

## 4. Usage Rules
*   **Always use `ONI_*` aliases** instead of standard commands. They are guaranteed to exist and behave as expected.
*   **Verification:** Type `ONI_STATUS` to confirm the Kernel is alive.
*   **Latency:** Wait 500ms after sending an Alias command to allow the command prompt to catch up.

## 5. File Manifest
*   `Inject-AutoCAD-Keys.ps1` -> The Installer.
*   `oni_kernel.lsp` -> The Brain.
*   `oni_autoloader.lsp` / `acaddoc.lsp` -> The Hook.
