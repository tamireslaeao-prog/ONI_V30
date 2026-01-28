# 🚀 ONI BLENDER - 15-MINUTE QUICK START

> **Get ONI running in Blender in 15 minutes or less**

---

## ⏱️ TIMELINE

```
00:00 - 05:00  →  Setup folders and install add-on
05:00 - 10:00  →  Test installation in Blender
10:00 - 12:00  →  Generate first badge
12:00 - 15:00  →  Render and export
```

---

## 📋 REQUIREMENTS

✓ **Blender 3.0 or higher** (Download: https://www.blender.org)
✓ **Python 3.9+** (included with Blender)
✓ **2GB free disk space**
✓ **Basic Blender knowledge** (optional)

---

## 🔧 INSTALLATION

### STEP 1: Download ONI Files (2 min)

Create project folder:

**Windows:**
```powershell
cd C:\
mkdir ONI-Blender
cd ONI-Blender
```

**macOS/Linux:**
```bash
cd ~
mkdir ONI-Blender
cd ONI-Blender
```

Download these files:
```
✓ ONI_Gen.py                    → Root folder
✓ ONI_BlenderAutomation.py      → Root folder
✓ blender_styles_db.json        → data/ folder
✓ oni_addon/ (entire folder)    → Blender add-ons folder
```

Your structure:
```
ONI-Blender/
├── ONI_Gen.py
├── ONI_BlenderAutomation.py
├── data/
│   └── blender_styles_db.json
├── scripts/
└── output/
```

---

### STEP 2: Install Blender Add-on (3 min)

**Method A: Zip Installation (Recommended)**

1. **Zip the add-on folder:**
   ```
   Select: oni_addon/ folder
   Right-click → Send to → Compressed (zipped) folder
   Rename: oni_addon.zip
   ```

2. **Install in Blender:**
   ```
   Open Blender
   Edit → Preferences (Ctrl+Alt+U)
   Add-ons tab
   Click "Install..." button
   Navigate to oni_addon.zip
   Click "Install Add-on"
   ```

3. **Enable the add-on:**
   ```
   Search: "ONI"
   Check the box next to "3D View: ONI Creativity Engine"
   Click "Save Preferences"
   ```

**Method B: Manual Installation**

1. **Find Blender scripts folder:**
   ```
   Windows: C:\Users\[YourName]\AppData\Roaming\Blender Foundation\Blender\3.x\scripts\addons\
   macOS: ~/Library/Application Support/Blender/3.x/scripts/addons/
   Linux: ~/.config/blender/3.x/scripts/addons/
   ```

2. **Copy oni_addon folder:**
   ```
   Copy entire oni_addon/ folder
   Paste into addons/ folder
   ```

3. **Enable in Blender:**
   ```
   Edit → Preferences → Add-ons
   Search "ONI" → Enable
   ```

---

### STEP 3: Configure Python Path (2 min)

Add ONI modules to Blender's Python:

1. **Open Blender Text Editor:**
   ```
   Top menu: Select "Scripting" workspace
   Click "+ New" in Text Editor
   ```

2. **Paste this code:**
   ```python
   import sys
   import bpy
   
   # Add ONI path (CHANGE THIS TO YOUR PATH)
   oni_path = r"C:\ONI-Blender"  # Windows
   # oni_path = "/Users/yourname/ONI-Blender"  # macOS
   # oni_path = "/home/yourname/ONI-Blender"  # Linux
   
   if oni_path not in sys.path:
       sys.path.append(oni_path)
   
   # Test import
   try:
       import ONI_Gen
       import ONI_BlenderAutomation
       print("✓ ONI modules loaded successfully!")
   except ImportError as e:
       print(f"✗ Error loading ONI modules: {e}")
   ```

3. **Run the script:**
   ```
   Click "Run Script" button or press Alt+P
   Check System Console for output (Window → Toggle System Console)
   ```

4. **Save as startup script (optional):**
   ```
   File → Save Copy (in Text Editor)
   Save as: startup_oni.py
   ```

---

### STEP 4: Test Installation (3 min)

1. **Open 3D Viewport:**
   ```
   Press 'N' to open sidebar
   Look for "ONI" tab
   ```

2. **If ONI tab appears: ✅ Installation successful!**

3. **Test badge generation:**
   ```
   In ONI panel:
   - Name: "TEST USER"
   - Title: "DEVELOPER"
   - ID: "DEV-001"
   - Click "Generate Badge"
   ```

4. **Expected result:**
   ```
   - Badge appears in 3D viewport
   - Camera and lights created
   - Objects in "ONI_Badge" collection
   - System console shows: "Badge generated successfully!"
   ```

**If badge appears: 🎉 SUCCESS!**

---

## 🎯 FIRST BADGE (5 min)

### Complete Workflow:

```python
# In Blender Text Editor, paste and run:

import bpy
import sys

# Add ONI path
sys.path.append(r"C:\ONI-Blender")  # Change to your path

# Import ONI
from ONI_BlenderAutomation import quick_badge

# Generate badge
result = quick_badge(
    name="JOHN SMITH",
    title="SECURITY OFFICER",
    badge_id="SEC-2847"
)

print(f"Badge created with seed: {result['seed']}")
```

**Or use the UI:**

1. Open ONI sidebar (press N → ONI tab)
2. Enter your details:
   - Name: Your name
   - Title: Your title
   - ID: Any ID
3. Click "Generate Badge"
4. Wait 2-5 seconds
5. Badge appears!

---

## 📸 RENDER YOUR BADGE (3 min)

1. **Check camera position:**
   ```
   Press Numpad 0 (camera view)
   If camera not visible: ONI panel → "Setup Camera"
   ```

2. **Render preview:**
   ```
   Press F12 (render image)
   Or: ONI panel → "Export & Render" → "Render Badge"
   ```

3. **Save render:**
   ```
   Image → Save As
   Choose location
   Format: PNG (recommended)
   Click "Save Image"
   ```

4. **Export 3D model:**
   ```
   ONI panel → "Export & Render" section
   Export Path: Choose location
   Format: glTF/GLB
   Click "Export Badge"
   ```

---

## ✅ VERIFICATION CHECKLIST

```
☐ Blender 3.0+ installed
☐ ONI files downloaded
☐ Add-on installed and enabled
☐ ONI tab visible in sidebar
☐ Python path configured
☐ Test badge generated successfully
☐ Camera and lighting setup
☐ Badge renders without errors
☐ Export to glTF works
```

**All checked? You're ready to create! 🚀**

---

## 🎨 QUICK CUSTOMIZATION

### Change Colors:

```python
# In ONI panel
Style Palette: Choose different style
- Cyberpunk Neon
- Minimal Corporate
- Vaporwave
- Japanese Tech
etc.
```

### Change Materials:

1. Select badge object
2. Shader Editor (top menu)
3. Modify material nodes
4. ONI panel → "Apply Style" to reapply

### Add More Greebles:

```
ONI panel → "Style & Colors"
Greebles section:
- Count: 30 (more details)
- Min Size: 0.03
- Max Size: 0.2
Click "Generate Greebles"
```

---

## 🛠️ TROUBLESHOOTING

### Problem: "ONI tab not visible"

**Solution:**
```
1. Edit → Preferences → Add-ons
2. Search: "ONI"
3. Ensure checkbox is CHECKED
4. If not found: Reinstall add-on
5. Restart Blender
```

### Problem: "Module not found" error

**Solution:**
```
1. Check Python path is correct in startup script
2. Verify ONI_Gen.py and ONI_BlenderAutomation.py exist
3. Run startup script again (Alt+P)
4. Check System Console for errors (Window → Toggle System Console)
```

### Problem: "Badge generates but looks wrong"

**Solution:**
```
1. Switch to Solid shading (Z key → Solid)
2. Check Viewport Shading is set to Material Preview
3. Ensure Cycles or Eevee is selected (not Workbench)
4. ONI panel → "Setup Lighting" to reset lights
```

### Problem: "Render is black"

**Solution:**
```
1. Check camera is active (Numpad 0)
2. ONI panel → "Setup Lighting"
3. Render Properties → Set engine to Cycles
4. Increase light power in properties
```

### Problem: "Export fails"

**Solution:**
```
1. Ensure path is valid (no special characters)
2. Select badge objects before export
3. Try different export format (FBX instead of glTF)
4. Check file permissions in output folder
```

---

## 📚 NEXT STEPS

### Week 1: Basics
- [ ] Generate 5 different badges
- [ ] Try all style palettes
- [ ] Adjust camera angles
- [ ] Change lighting styles
- [ ] Export as images and 3D files

### Week 2: Customization
- [ ] Modify materials in Shader Editor
- [ ] Create custom greeble patterns
- [ ] Adjust badge dimensions
- [ ] Create variations with different seeds
- [ ] Batch generate from CSV

### Week 3: Advanced
- [ ] Create custom styles in JSON
- [ ] Write Python scripts for automation
- [ ] Integrate with external tools
- [ ] Create animation sequences
- [ ] Build custom add-on features

---

## 🔗 RESOURCES

**Official Blender Documentation:**
- Python API: https://docs.blender.org/api/current/
- Add-ons: https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html

**ONI Documentation:**
- Complete Guide: See `blender_oni_complete_guide.md`
- Python Scripts: See `helper_scripts/`
- Style Database: See `data/blender_styles_db.json`

**Community:**
- Blender Stack Exchange: https://blender.stackexchange.com
- Blender Discord: https://discord.gg/blender
- ONI GitHub: (your repository URL)

---

## 🎯 COMMON COMMANDS

**Blender Shortcuts:**
```
N                    → Toggle sidebar (ONI panel)
F12                  → Render image
Numpad 0            → Camera view
Z                    → Shading mode
Shift+A             → Add object
X                    → Delete
G                    → Move (Grab)
R                    → Rotate
S                    → Scale
Ctrl+Z              → Undo
```

**ONI Operations:**
```
Generate Badge      → Alt+P (run script) or UI button
New Seed            → ONI panel → "New Seed" button
Apply Style         → Select objects → "Apply Style"
Setup Scene         → "Setup Camera" + "Setup Lighting"
Render              → F12 or "Render Badge" button
Export              → "Export Badge" button
```

---

## 💡 TIPS & TRICKS

1. **Always work in metric units** (Scene Properties → Units → Metric)
2. **Use Material Preview shading** for accurate colors (Z → Material Preview)
3. **Save often** (Ctrl+S)
4. **Name your objects** for easier management
5. **Use collections** to organize badges
6. **Backup your seeds** for reproducibility
7. **Test render at low samples first** (64 samples)
8. **Use Eevee for fast previews**, Cycles for final renders

---

## 🎉 YOU'RE READY!

**What you can do now:**

✅ Generate 3D badges instantly
✅ Customize with 8+ style presets
✅ Render high-quality images
✅ Export to game engines (Unity, Unreal, Godot)
✅ Automate with Python scripts
✅ Create variations with seeds
✅ Batch process designs

**Time to create:** 15 minutes
**Possibilities:** Unlimited

---

## 📞 NEED HELP?

**Quick checks:**
1. System Console (Window → Toggle System Console)
2. Info Editor (shows recent operations)
3. Python Console (for testing commands)

**Test command:**
```python
import bpy
print("Blender version:", bpy.app.version_string)
print("Python version:", sys.version)
```

**Still stuck?**
- Re-read installation steps
- Check file paths are correct
- Restart Blender
- Reinstall add-on
- Check Blender version (must be 3.0+)

---

**🚀 FROM ZERO TO 3D BADGE IN 15 MINUTES!**

```
"The fastest way to create professional 3D badges."
```

**Ready? Let's create! 🎨✨**
