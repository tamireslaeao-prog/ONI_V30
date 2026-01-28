# ONI Premiere Module

## Overview
This module provides a bridge between ONI and Adobe Premiere Pro.

## Structure
- **ONI_Premiere_Bridge.py**: Main controller. Checks for binary existence and launches scripts.
- **Scripts/**: Contains JSX/ExtendScript files for automation.
- **Config/**: JSON configuration files.

## Usage
```python
from ONI_Premiere_Bridge import PremiereBridge

bridge = PremiereBridge()
status, ok = bridge.check_health()
if ok:
    bridge.run_script("your_script.jsx")
```

## Known Limitations
- Premiere Pro automation is primarily done via ExtendScript (JSX).
- Command line arguments are limited; complex data transfer usually requires writing to an intermediate JSON file that the JSX reads.
