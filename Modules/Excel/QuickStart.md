# 🚀 ONI EXCEL - 15-MINUTE QUICK START

> **Get ONI running in Excel in 15 minutes or less**

---

## ⏱️ TIMELINE

```
00:00 - 05:00  →  Setup folders and install modules
05:00 - 10:00  →  Choose your method (VBA, PowerShell, or Python)
10:00 - 12:00  →  Generate first badge
12:00 - 15:00  →  Test and export
```

---

## 📋 REQUIREMENTS

✓ **Microsoft Excel 2016 or higher** (Office 365 recommended)
✓ **Windows 10/11** (for PowerShell method)
✓ **Python 3.8+** (for Python method - optional)
✓ **Basic Excel knowledge**

---

## 🎯 CHOOSE YOUR METHOD

### **Method 1: VBA (Pure Excel)** ⭐ RECOMMENDED FOR BEGINNERS
- ✅ Works entirely in Excel
- ✅ No external dependencies
- ✅ Visual Basic Editor built-in
- ❌ Manual code import

### **Method 2: PowerShell (Automation)**
- ✅ Script external automation
- ✅ Batch processing
- ✅ Windows native
- ❌ Requires PowerShell knowledge

### **Method 3: Python (No Excel Required!)**
- ✅ Works without Excel installed
- ✅ Cross-platform (Windows/Mac/Linux)
- ✅ Uses openpyxl library
- ❌ Requires Python installation

---

## 🔧 METHOD 1: VBA INSTALLATION (5 min)

### STEP 1: Enable Developer Tab

1. **Open Excel**
2. **File → Options → Customize Ribbon**
3. **Check "Developer" checkbox**
4. **Click OK**

### STEP 2: Import ONI Modules

1. **Press Alt+F11** (opens VBA Editor)
2. **Insert → Module** (creates new module)
3. **Copy contents of `ONI.Gen.bas`**
4. **Paste into module**
5. **Repeat for `ONI.ExcelAutomation.bas`**

### STEP 3: Test Installation

1. **In VBA Editor, press F5** (Run)
2. **Select `TestONIRandomness`**
3. **Click Run**
4. **Check Immediate Window (Ctrl+G)** for output

Expected output:
```
=== ONI Randomness Test ===
Iterations: 10000
Mean: 0.5012 (expected: 0.5000)
Std Dev: 0.2891 (expected: ~0.2887)
```

**If you see this: ✅ VBA Installation Complete!**

---

## 🔧 METHOD 2: POWERSHELL INSTALLATION (5 min)

### STEP 1: Create Project Folder

```powershell
# Open PowerShell
cd C:\
mkdir ONI-Excel
cd ONI-Excel

# Create subfolders
mkdir data, scripts, output
```

### STEP 2: Copy Files

```
Download and place:
✓ ONI.Gen.ps1 → C:\ONI-Excel\
✓ ONI.ExcelAutomation.ps1 → C:\ONI-Excel\
```

### STEP 3: Set Execution Policy

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass
```

### STEP 4: Test Installation

```powershell
cd C:\ONI-Excel
Import-Module .\ONI.Gen.ps1
Import-Module .\ONI.ExcelAutomation.ps1

# Test
$seed = New-ONISeed -StylePrefix "TEST"
Write-Host "Seed: $seed"
```

**If seed appears: ✅ PowerShell Installation Complete!**

---

## 🔧 METHOD 3: PYTHON INSTALLATION (5 min)

### STEP 1: Install Python

Download from: https://www.python.org/downloads/
- ✓ Check "Add Python to PATH" during installation

### STEP 2: Install Dependencies

```bash
# Open Command Prompt or Terminal
pip install openpyxl Pillow
```

### STEP 3: Download ONI Script

```
Save ONI_Excel.py to your projects folder
```

### STEP 4: Test Installation

```bash
python ONI_Excel.py
```

Expected output:
```
=== ONI Excel Badge Generator ===
✓ Cyberpunk badge generated!
  Name: ALEX MERCER
  Title: CYBER SECURITY
  ID: CS-4729
  Seed: ONI-CYB-20260104-XXXX
Saved: badge_cyberpunk.xlsx
```

**If files created: ✅ Python Installation Complete!**

---

## 🎨 GENERATE YOUR FIRST BADGE

### Method 1: VBA

1. **Open Excel** (new workbook)
2. **Alt+F11** (VBA Editor)
3. **Insert → Module**
4. **Paste this code:**

```vba
Sub QuickBadge()
    GenerateCyberpunkBadge ActiveSheet, 2, 2, "YOUR NAME", "YOUR TITLE", "ID-001"
End Sub
```

5. **Press F5** to run
6. **Switch to Excel** → Badge appears!

### Method 2: PowerShell

```powershell
cd C:\ONI-Excel
Import-Module .\ONI.ExcelAutomation.ps1

$excel = Connect-Excel
New-CyberpunkBadge -Excel $excel `
    -Name "YOUR NAME" `
    -Title "YOUR TITLE" `
    -ID "ID-001"
```

### Method 3: Python

```python
from ONI_Excel import ONIBadgeGenerator

generator = ONIBadgeGenerator()
wb, seed = generator.create_cyberpunk_badge(
    name="YOUR NAME",
    title="YOUR TITLE",
    badge_id="ID-001"
)
wb.save("my_badge.xlsx")
print(f"Badge created with seed: {seed}")
```

---

## ✅ VERIFICATION CHECKLIST

```
☐ Excel installed (or Python for Method 3)
☐ ONI modules imported/installed
☐ Test script runs without errors
☐ First badge generated successfully
☐ Badge displays in Excel
☐ Seed visible in output
```

**All checked? You're ready! 🎉**

---

## 🎯 QUICK EXAMPLES

### Example 1: Cyberpunk Badge (VBA)

```vba
Sub Example1()
    GenerateCyberpunkBadge ActiveSheet, 2, 2, _
        "ALEX MERCER", "CYBER SECURITY", "CS-4729"
End Sub
```

### Example 2: Minimal Badge (VBA)

```vba
Sub Example2()
    GenerateMinimalBadge ActiveSheet, 15, 2, _
        "JOHN SMITH", "PROJECT MANAGER", "PM-001"
End Sub
```

### Example 3: Batch from CSV (PowerShell)

```powershell
# Create employees.csv first:
# Name,Title,ID
# John Smith,Manager,EMP-001
# Jane Doe,Engineer,EMP-002

New-BatchBadges -Excel $excel `
    -CSVPath "employees.csv" `
    -Style "cyberpunk"
```

### Example 4: Multiple Styles (Python)

```python
generator = ONIBadgeGenerator()

# Cyberpunk
wb1, _ = generator.create_cyberpunk_badge("Agent Alpha", "Operative", "OP-001")
wb1.save("badge_cyber.xlsx")

# Minimal
wb2, _ = generator.create_minimal_badge("Agent Beta", "Support", "SP-002")
wb2.save("badge_minimal.xlsx")
```

---

## 🛠️ TROUBLESHOOTING

### Problem: "Macro security warning"

**Solution:**
```
1. File → Options → Trust Center
2. Trust Center Settings
3. Macro Settings
4. Select "Enable all macros"
5. Restart Excel
```

### Problem: "Module not found" (PowerShell)

**Solution:**
```powershell
# Check if in correct directory
Get-Location  # Should show C:\ONI-Excel

# Use full path
Import-Module "C:\ONI-Excel\ONI.Gen.ps1" -Force
```

### Problem: "ModuleNotFoundError: openpyxl" (Python)

**Solution:**
```bash
# Reinstall with pip
pip install --upgrade openpyxl Pillow

# Verify installation
pip list | grep openpyxl
```

### Problem: "Badge looks wrong"

**Solution:**
```
VBA: Check column widths are auto-adjusted
PowerShell: Ensure COM connection is active
Python: Verify openpyxl version (3.0+)
```

### Problem: "Colors not showing"

**Solution:**
```
- Excel must be in "Normal" view (not Page Layout)
- Check Fill color is applied (not just font color)
- Verify RGB values are correct (not BGR)
```

---

## 📊 COMPARISON: WHICH METHOD?

| Feature | VBA | PowerShell | Python |
|---------|-----|------------|--------|
| **Setup Time** | 5 min | 5 min | 5 min |
| **Excel Required** | ✓ Yes | ✓ Yes | ✗ No |
| **External Deps** | ✗ None | ✗ None | ✓ pip packages |
| **Automation** | Manual | ✓ Scripts | ✓✓ Best |
| **Cross-Platform** | ✗ Windows | ✗ Windows | ✓✓ All |
| **Learning Curve** | Low | Medium | Medium |
| **Speed** | Fast | Fast | Very Fast |
| **Best For** | Excel users | Automation | Developers |

**Recommendation:**
- **Beginner:** VBA
- **Windows Power User:** PowerShell
- **Developer/Multi-platform:** Python

---

## 🚀 NEXT STEPS

### Week 1: Basics
- [ ] Generate 5 different badges
- [ ] Try both Cyberpunk and Minimal styles
- [ ] Experiment with colors
- [ ] Create custom seed values
- [ ] Export as PDF

### Week 2: Customization
- [ ] Modify badge dimensions
- [ ] Add custom fields
- [ ] Create new color palettes
- [ ] Design custom layouts
- [ ] Add company logo

### Week 3: Automation
- [ ] Batch generate from CSV
- [ ] Create templates
- [ ] Set up scheduled generation
- [ ] Integrate with databases
- [ ] Build custom UI (VBA UserForm)

---

## 📚 RESOURCES

**Official Documentation:**
- Excel VBA: https://docs.microsoft.com/en-us/office/vba/api/overview/excel
- openpyxl: https://openpyxl.readthedocs.io/
- PowerShell: https://docs.microsoft.com/en-us/powershell/

**ONI Documentation:**
- Complete Guide: `oni_excel_complete_guide.md`
- VBA Reference: `ONI.Gen.bas` + `ONI.ExcelAutomation.bas`
- Python Reference: `ONI_Excel.py`
- PowerShell Reference: `ONI.ExcelAutomation.ps1`

---

## 🎯 COMMON COMMANDS

### VBA Quick Commands

```vba
' Generate badge
GenerateCyberpunkBadge ActiveSheet, 2, 2, "Name", "Title", "ID"

' Generate seed
Dim seed As String
seed = GenerateONISeed("CYB")
Debug.Print seed

' Random color
Dim color As Long
color = GetRandomColorFromPalette("cyberpunk_v1", "primary")
```

### PowerShell Quick Commands

```powershell
# Connect
$excel = Connect-Excel

# Generate
New-CyberpunkBadge -Excel $excel -Name "Name" -Title "Title" -ID "ID"

# Batch
New-BatchBadges -Excel $excel -CSVPath "file.csv" -Style "cyberpunk"

# Disconnect
Disconnect-Excel -Excel $excel
```

### Python Quick Commands

```python
# Quick badge
from ONI_Excel import ONIBadgeGenerator
gen = ONIBadgeGenerator()
wb, seed = gen.create_cyberpunk_badge("Name", "Title", "ID")
wb.save("output.xlsx")

# Batch
batch_generate_badges("employees.csv", "output", "cyberpunk")
```

---

## 💡 TIPS & TRICKS

1. **Save seeds** for reproducibility
2. **Use CSV** for batch processing
3. **Test with small batches** first
4. **Backup your templates**
5. **Document custom colors**
6. **Version control** your code (Git)
7. **Use named ranges** in Excel
8. **Freeze panes** for easier editing

---

## 🎉 YOU'RE READY!

**What you can do now:**

✅ Generate badges in 3 different methods
✅ Customize colors and layouts
✅ Batch process from CSV
✅ Export to Excel, PDF, PNG
✅ Automate with scripts
✅ Create reproducible designs with seeds

**Time invested:** 15 minutes
**Badges you can generate:** Unlimited
**Methods available:** 3 (VBA, PowerShell, Python)

---

## 📞 NEED HELP?

**Quick Checks:**
1. Method 1 (VBA): Alt+F11 → Immediate Window (Ctrl+G) for errors
2. Method 2 (PowerShell): Check `$Error[0]` for last error
3. Method 3 (Python): Run with `python -v ONI_Excel.py` for verbose output

**Still Stuck?**
- Re-read installation steps for your method
- Check file paths are correct
- Verify Excel/Python version
- Try a different method

---

**🚀 FROM ZERO TO EXCEL BADGE IN 15 MINUTES!**

```
"The easiest way to create professional badges in Excel."
```

**Ready? Choose your method and let's create! 🎨✨**
