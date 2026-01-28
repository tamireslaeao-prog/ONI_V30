# Windows Automation Master Secrets
**Context:** Desktop interaction via PowerShell & Win32 API.

## 1. The Gateway: P/Invoke (`Add-Type`)
PowerShell's `SendKeys` is for amateurs. The Master accesses the Kernel.
**The Fix:** Compile C# on the fly to call `user32.dll`.
```powershell
$sig = @"
[DllImport("user32.dll")]
public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
"@
Add-Type -MemberDefinition $sig -Name Win32 -Namespace ONI
[ONI.Win32]::SetWindowPos($hwnd, 0, 0, 0, 1920, 1080, 0x0040)
```
*   **Power:** Move, Resize, Hide, Show, Flash any window instantly.

## 2. Input: `SendInput` vs `PostMessage`
*   `PostMessage`: Good for background clicks (sometimes), but "Ghostly". Apps often ignore it.
*   `SendInput`: The Gold Standard. Simulates hardware driver events.
*   **Secret:** Updates keyboard state (Shift/Ctrl/Alt) correctly, unlike `PostMessage`.

## 3. The "Focus" Lie
Many automation fails happen because a window "thinks" it has focus but doesn't.
**The Fix:**
1.  `SetForegroundWindow(hwnd)`
2.  `AttachThreadInput` (The "Mind Meld" trick to force focus attachment).
3.  Check `GetForegroundWindow()` in a loop until it matches.

## 4. UI Automation (UIA)
Use `.NET` reflection to see what the eye cannot.
```powershell
Add-Type -AssemblyName UIAutomationClient
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Submit")
$btn = $root.FindFirst("Descendants", $cond)
$btn.Invoke()
```
*   **Precision:** Click buttons by Name, ID, or Type, not X,Y coordinates.

## 5. High DPI Hell
Coordinates (1920x1080) lie on 4K screens with 150% scaling.
**The Fix:**
*   Always mark the automation process as "DPI Aware" via manifest or API.
*   Or rely on `UIAutomation` which handles scaling natively.
