# ONI Neuro-Integration Protocol (CorelDRAW Shortcuts)

> **Version:** 1.0
> **Component:** CorelDRAW Neural Interface
> **Status:** Active Feature

## Overview
The **Neuro-Integration Protocol** allows ONI to programmatically inject custom keyboard shortcuts into CorelDRAW workspaces. This bypasses the need for manual configuration or VBA "SendKeys" limitations, effectively creating a dedicated communication channel between the Agent and the Application.

## Architecture

### 1. Configuration (`app/config/corel_shortcuts.json`)
Defines the mapping between human-readable names, CorelDRAW GUIDs, and desired Key Sequences.

```json
{
    "name": "Quick Trace - Detailed Logo",
    "guid": "21129FEE-F5C2-41bc-9B04-CB5D39CB3974",
    "keys": "Ctrl+Shift+D"
}
```

### 2. Injection Engine (`app/setup/Install-CorelShortcuts.ps1`)
A robust PowerShell engine that:
1.  **Detects:** Finds the active CorelDRAW installation in `%AppData%`.
2.  **Targets:** Locates the current active workspace (defaulting to `_default.cdws`).
3.  **Injects:** Unpacks the specific XML structure, modifies the `<uiConfig>`, and injects `<keySequence>` nodes.
4.  **Deploys:** Repacks and generates `ONI_Neural_v1.cdws`.

## Usage
### Deployment
To enable ONI shortcuts on a new environment:
```powershell
.\app\setup\Install-CorelShortcuts.ps1
```

### Activation
Currently, CorelDRAW requires a one-time manual import or script restart to switch workspaces:
1.  **Manual:** *Tools > Options > Workspace > Import > Select `ONI_Neural_v1.cdws`*.
2.  **Automatic (Planned):** Modifying `settings.ini` to point to the new workspace file during boot.

## Supported Commands
| Command | Shortcut | GUID |
| :--- | :--- | :--- |
| **Quick Trace (Detailed)** | `Ctrl+Shift+D` | `21129FEE...` |
| **Convert to Bitmap** | `Ctrl+Shift+B` | `2962cd49...` |

## Adding New Shortcuts
1.  Find the Command GUID (Use `DrawUI.xml` or CSV map).
2.  Add entry to `app/config/corel_shortcuts.json`.
3.  Run `Install-CorelShortcuts.ps1`.
