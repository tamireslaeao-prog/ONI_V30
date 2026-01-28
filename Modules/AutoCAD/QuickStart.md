# AutoCAD Module - QuickStart Guide

## Prerequisites

1. **AutoCAD 2022+** installed
2. **Python 3.11+** with `pywin32`
3. **PowerShell 5.1+**

## Installation

```powershell
# Install Python COM library
pip install pywin32
```

## Python Usage

### Basic Example

```python
from ONI_AutoCAD_Bridge import AutoCADBridge

# Connect to AutoCAD
cad = AutoCADBridge()
cad.connect()

# Draw shapes
cad.draw_rectangle(0, 0, 100, 50)
cad.draw_circle(150, 25, 25)
cad.draw_line(0, 60, 200, 60)

# Add text
cad.add_text("ONI AutoCAD Test", 10, 70, 5)

# Zoom to see all
cad.zoom_extents()

# Save
cad.save("C:\\output\\test.dwg")
```

### Working with Layers

```python
cad.connect()

# Create layers
cad.create_layer("CUTS", color=1)      # Red
cad.create_layer("FOLDS", color=3)     # Green
cad.create_layer("TEXT", color=7)      # White

# Set active layer
cad.set_layer("CUTS")
cad.draw_rectangle(0, 0, 100, 50)

cad.set_layer("FOLDS")
cad.draw_line(50, 0, 50, 50)

cad.set_layer("TEXT")
cad.add_text("Part A", 10, 25, 3)
```

### Dimensions

```python
cad.connect()

# Draw shape
cad.draw_rectangle(0, 0, 100, 50)

# Add dimensions
cad.add_dimension_linear(0, 0, 100, 0, -10)   # Width
cad.add_dimension_linear(0, 0, 0, 50, -10)    # Height
```

## PowerShell Usage

### Basic Example

```powershell
# Import module
Import-Module .\Modules\AutoCAD\AutoCAD_Adapter.psm1

# Connect
Connect-AutoCAD -CreateNewDoc

# Draw
New-CADRectangle -X 0 -Y 0 -Width 100 -Height 50
New-CADCircle -CenterX 150 -CenterY 25 -Radius 25
New-CADText -Text "ONI Test" -X 10 -Y 60 -Height 5

# Zoom
Invoke-CADZoomExtents

# Save
Save-CADDrawing -Path "C:\output\test.dwg"

# Disconnect
Disconnect-AutoCAD
```

### Layer Management

```powershell
Connect-AutoCAD -CreateNewDoc

# Create layers
New-CADLayer -Name "CUTS" -Color 1
New-CADLayer -Name "FOLDS" -Color 3

# Draw on specific layer
Set-CADLayer -Name "CUTS"
New-CADRectangle -X 0 -Y 0 -Width 100 -Height 50

Set-CADLayer -Name "FOLDS"
New-CADLine -X1 50 -Y1 0 -X2 50 -Y2 50

Save-CADDrawing -Path "C:\output\layered.dwg"
Disconnect-AutoCAD
```

## Common Patterns

### Box Mold Template

```python
cad = AutoCADBridge()
cad.connect()

# Create layers
cad.create_layer("CUTS", 1)   # Red - cuts
cad.create_layer("FOLDS", 3)  # Green - folds
cad.create_layer("DIMS", 4)   # Cyan - dimensions

# Draw outer boundary
cad.set_layer("CUTS")
cad.draw_rectangle(0, 0, 200, 150)

# Draw fold lines
cad.set_layer("FOLDS")
cad.draw_line(20, 0, 20, 150)
cad.draw_line(180, 0, 180, 150)
cad.draw_line(0, 20, 200, 20)
cad.draw_line(0, 130, 200, 130)

# Add dimensions
cad.set_layer("DIMS")
cad.add_dimension_linear(0, 0, 200, 0, -10)

cad.zoom_extents()
cad.save("C:\\output\\box_mold.dwg")
```

## Troubleshooting

### "AutoCAD.Application" not found

- Ensure AutoCAD is installed
- Try running as Administrator
- Check AutoCAD version compatibility

### RPC_E_CALL_REJECTED

- AutoCAD is busy, add retry logic:

```python
import time

for attempt in range(3):
    try:
        cad.connect()
        break
    except:
        time.sleep(2)
```

### Objects not visible

- Call `zoom_extents()` after drawing
- Check layer visibility

## API Reference

### Python (ONI_AutoCAD_Bridge)

| Method | Description |
|--------|-------------|
| `connect()` | Connect to AutoCAD |
| `draw_line(x1,y1,x2,y2)` | Draw line |
| `draw_circle(cx,cy,r)` | Draw circle |
| `draw_rectangle(x,y,w,h)` | Draw rectangle |
| `draw_polyline(points)` | Draw polyline |
| `add_text(text,x,y,h)` | Add text |
| `create_layer(name,color)` | Create layer |
| `set_layer(name)` | Set active layer |
| `save(path)` | Save drawing |
| `close()` | Close document |
| `zoom_extents()` | Zoom to fit |

### PowerShell (AutoCAD_Adapter)

| Command | Description |
|---------|-------------|
| `Connect-AutoCAD` | Connect |
| `New-CADLine` | Draw line |
| `New-CADCircle` | Draw circle |
| `New-CADRectangle` | Draw rectangle |
| `New-CADText` | Add text |
| `New-CADLayer` | Create layer |
| `Set-CADLayer` | Set active layer |
| `Save-CADDrawing` | Save |
| `Close-CADDrawing` | Close |

---

**Version:** 1.0.0  
**Updated:** 2026-01-14
