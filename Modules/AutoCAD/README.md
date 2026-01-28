# ONI AutoCAD Module

Python COM Bridge for AutoCAD automation via ActiveX.

## Quick Start

```python
from ONI_AutoCAD_Bridge import AutoCADBridge

# Connect
cad = AutoCADBridge()
cad.connect()

# Draw rectangle
cad.draw_rectangle(0, 0, 100, 50)

# Save
cad.save("C:\\output\\drawing.dwg")
```

## Files

- `ONI_AutoCAD_Bridge.py` - Main Python COM interface
- `AutoCAD_Adapter.psm1` - PowerShell wrapper
- `AutoCAD_Test_Draw.py` - Validation script
- `docs/ONI_AutoCAD_Documentation.md` - Full documentation

## Requirements

- AutoCAD 2022+ installed
- Python 3.11+ with `pywin32`
- PowerShell 5.1+

## Installation

```powershell
pip install pywin32
```

## Version

- **Version:** 1.0.0
- **Updated:** 2026-01-14
- **Author:** ONI Team
