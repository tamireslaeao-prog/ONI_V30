# ONI GOLDEN STANDARD: THE UNIVERSAL ADAPTER PROTOCOL
> **Version:** 1.0 (The "AutoCAD/Corel" Breakthrough)
> **Date:** 2026-01-06
> **Objective:** To automate ANY desktop software with 100% reliability.

## 1. The Core Philosophy: "Dumb Pipe, Smart Script"

The greatest mistake in automation is trying to make the *Connection* smart (e.g., complex COM objects, fragile Python libraries, deeply nested API calls).
The **Golden Standard** inverts this:

- **The Adapter (The Pipe):** Must be dumb, slow, and purely mechanical. It mimics a patient human user.
- **The Script (The Brain):** Must be brilliant. It calculates everything (geometry, paths, logic) *outside* the application and prepares a "package" for the application to digest.

## 2. The Universal Formula

To automate Software X (be it AutoCAD, Photoshop, Excel, or Blender), you need three components:

### A. The Adapter (`App_Adapter.psm1`)
A PowerShell module that handles the "Physical Layer". It has only 3 responsibilities:
1.  **Connect:** Find the Process ID and force the Window to Focus (`AppActivate`).
2.  **Type:** Send keystrokes with a heartbeat (`300ms` delay). Never flood the buffer.
3.  **Reset:** A "Panic Key" sequence (e.g., `Esc, Esc, Esc` or `Ctrl+.`) to return to a neutral state.

### B. The Payload (The "Smart" Part)
Do not try to "draw a line" by dragging the mouse.
Instead, **Generate an Asset** that the software naturally understands:
- **AutoCAD:** Generate a `.scr` (Script) or send CLI commands.
- **Corel:** Generate a `.svg` or `.cdr` (XML).
- **Photoshop:** Generate a `.jsx` (ExtendScript) or `.svg`.
- **Excel:** Generate a `.csv` or `.xml`.

### C. The Injection (The Bridge)
The Adapter simply tells the Software to "Ingest the Payload".
- *AutoCAD:* Type `_SCRIPT` + Path + Enter.
- *Corel:* Type `Ctrl+I` + Path + Enter.
- *Photoshop:* Type `File > Scripts > Browse` keys.

---

## 3. How to Implement in ANY Software

### Step 1: Build the Adapter
Copy the standard template:
```powershell
function Connect-App {
    # 1. Get-Process
    # 2. WScript.Shell.AppActivate(Title)
    # 3. Wait 500ms
}

function Send-Input {
    # 1. Focus
    # 2. SendKeys(Text)
    # 3. Sleep 300ms (ESSENTIAL!)
}
```

### Step 2: Define the "Ingestion Path"
Find the keyboard shortcut that allows the software to load external data.
- Does it have `Import` (`Ctrl+I`)?
- Does it have a Console/CLI?
- Does it support Drag & Drop (simulated)?

### Step 3: Write the Generator
Write a script (PowerShell/Python) that creates the file the software expects.
- Don't draw a circle in the app. **Write a file that contains a circle.**

### Step 4: Execute
1. Script generates File `x`.
2. Adapter focuses App.
3. Adapter types "Import `x`".

---

## 4. Why This Works
1.  **Decoupling:** If the App crashes, your script logic is safe.
2.  **Speed:** Generating a file is instant. Formatting UI commands is slow.
3.  **Precision:** Math calculated in code is perfect. Mouse drags are not.
4.  **Universal:** Every software can open/import *something*.

## 5. Case Studies
- **AutoCAD:** We stopped clicking buttons. We typed commands into the CLI.
- **CorelDRAW:** We stopped using COM. We generated SVGs and imported them via Keyboard.
- **Photoshop (Next):** We will stop simulating brushes. We will generate `.jsx` or `.svg` and inject them.
