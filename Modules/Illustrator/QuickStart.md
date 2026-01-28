# 🚀 ONI + ADOBE ILLUSTRATOR COMPLETE INTEGRATION GUIDE

> **Status:** Sistema completo para Adobe Illustrator - Scripts, PowerShell, Templates!

---

## 📦 WHAT YOU HAVE NOW

### ✅ 1. Adobe Illustrator Template Specifications (.AIT)
**Location:** Artifact "Adobe Illustrator Template Specifications"
- 6 complete template specs (Cyberpunk, Print Badge, Certificate, Japanese, Synthwave, Infographic)
- Layer organization, color swatches, guides
- Step-by-step creation workflow
- Export settings for each template type

### ✅ 2. ExtendScript Macros (ONI.Macros.jsx)
**Location:** Artifact "Adobe Illustrator ExtendScript Macros"
- 10 automation scripts ready to install
- Cyberpunk effects, badge creation, greebles, gradients
- Print-safe CMYK conversion, batch export
- Scanlines, tech borders, Japanese vertical text

### ✅ 3. PowerShell Automation (ONI.IllustratorAutomation.ps1)
**Location:** Artifact "ONI.IllustratorAutomation.ps1"
- Full COM automation bridge
- Document creation, shape generation, text handling
- Style application from styles_db.json
- Batch badge generation from CSV
- Export to PDF/PNG/SVG

### ✅ 4. Greebles Vector Library (Reusable)
Use the same guide from CorelDRAW version - save as .AI format instead of .CDR

---

## 🎯 QUICK START: 3 USAGE SCENARIOS

### SCENARIO 1: Manual Design with Templates & Scripts

```powershell
# STEP 1: Install ExtendScript
1. Save ONI.Macros.jsx to:
   Mac: /Applications/Adobe Illustrator [VERSION]/Presets/en_US/Scripts/
   Win: C:\Program Files\Adobe\Adobe Illustrator [VERSION]\Presets\en_US\Scripts\

2. Restart Illustrator

# STEP 2: Create template
1. Open Illustrator
2. Follow "Adobe Illustrator Template Specifications" guide
3. Create "Cyberpunk Badge" template
4. File > Save as Template
5. Save as: ONI_Cyberpunk_Badge.ait

# STEP 3: Use template
1. File > New from Template
2. Select ONI_Cyberpunk_Badge.ait
3. Replace placeholders ([NAME], [PHOTO])

# STEP 4: Apply effects with scripts
1. Select text object
2. File > Scripts > ONI.Macros
3. Choose option 1 (Apply Cyberpunk Neon Effect)
4. Script applies glow, stroke, colors

# STEP 5: Add greebles
1. File > Scripts > ONI.Macros
2. Choose option 3 (Apply Random Tech Greebles)
3. 10-20 random decorative elements added

# STEP 6: Export
1. File > Scripts > ONI.Macros
2. Choose option 7 (Batch Export)
3. Creates PDF, PNG (300 DPI), SVG
```

---

### SCENARIO 2: Semi-Automated with PowerShell

```powershell
# STEP 1: Setup modules
cd C:\ONI
Import-Module .\ONI.Gen.ps1
Import-Module .\ONI.IllustratorAutomation.ps1

# STEP 2: Connect to Illustrator
$ai = Connect-Illustrator
# Illustrator opens automatically if not running

# STEP 3: Generate single badge
New-CyberpunkBadge -AI $ai `
    -Name "ALEX MERCER" `
    -Title "SECURITY OFFICER" `
    -ID "SEC-2847" `
    -OutputPath "C:\badges\alex_mercer.ai"

# Result: Complete badge created with randomized greebles

# STEP 4: View and adjust
# Badge opens in Illustrator, ready for manual tweaks

# STEP 5: Export
Export-IllustratorToPDF -Document $ai.ActiveDocument `
    -OutputPath "C:\badges\alex_mercer.pdf"

Export-IllustratorToPNG -Document $ai.ActiveDocument `
    -OutputPath "C:\badges\alex_mercer.png" -DPI 300

# STEP 6: Disconnect
Disconnect-Illustrator -AI $ai
```

---

### SCENARIO 3: Full Automation (Batch Processing)

```powershell
# STEP 1: Prepare CSV file
# employees.csv:
# Name,Title,ID
# John Smith,Manager,EMP-001
# Jane Doe,Engineer,EMP-002
# Mike Johnson,Designer,EMP-003

# STEP 2: Run batch generation
$ai = Connect-Illustrator

New-BatchBadges -AI $ai `
    -CSVPath "C:\data\employees.csv" `
    -Style "cyberpunk" `
    -OutputFolder "C:\badges\batch_output"

# Result: 
# - 3 .AI files created
# - Each with unique randomized design
# - All following same Cyberpunk style

# STEP 3: Batch export (optional)
Get-ChildItem "C:\badges\batch_output\*.ai" | ForEach-Object {
    $doc = $ai.Open($_.FullName)
    
    $pdfPath = $_.FullName -replace '\.ai$','.pdf'
    Export-IllustratorToPDF -Document $doc -OutputPath $pdfPath
    
    $pngPath = $_.FullName -replace '\.ai$','.png'
    Export-IllustratorToPNG -Document $doc -OutputPath $pngPath -DPI 300
    
    $doc.Close(2) # Don't save changes
}

Disconnect-Illustrator -AI $ai
```

---

## 🛠️ INSTALLATION WALKTHROUGH

### PHASE 1: Setup File Structure (5 minutes)

```powershell
# Create folder structure
New-Item -ItemType Directory -Path "C:\ONI" -Force
New-Item -ItemType Directory -Path "C:\ONI\data" -Force
New-Item -ItemType Directory -Path "C:\ONI\assets" -Force
New-Item -ItemType Directory -Path "C:\ONI\assets\greebles" -Force
New-Item -ItemType Directory -Path "C:\ONI\templates" -Force
New-Item -ItemType Directory -Path "C:\ONI\scripts" -Force

# Copy files
# - Save styles_db.json to C:\ONI\data\
# - Save corel_styles_db.json to C:\ONI\data\ (works for AI too)
# - Save ONI.Gen.ps1 to C:\ONI\
# - Save ONI.IllustratorAutomation.ps1 to C:\ONI\
# - Save ONI.Macros.jsx to C:\ONI\scripts\
```

### PHASE 2: Install ExtendScript Macros (10 minutes)

```powershell
# Find Illustrator Scripts folder
$aiVersion = "2024" # or your version
$scriptPath = "C:\Program Files\Adobe\Adobe Illustrator $aiVersion\Presets\en_US\Scripts\"

# Copy script
Copy-Item "C:\ONI\scripts\ONI.Macros.jsx" $scriptPath

# Restart Illustrator
```

**TEST:**
```
1. Open Adobe Illustrator
2. File > Scripts > ONI.Macros
3. Should see menu with 10 options
4. Create test document (Cmd/Ctrl + N)
5. Draw rectangle
6. File > Scripts > ONI.Macros > Option 1
7. Rectangle should get cyan neon glow effect
```

### PHASE 3: Create First Template (30 minutes)

```
Follow "Adobe Illustrator Template Specifications" document:
1. Start with "Cyberpunk Badge Template"
2. File > New
   - Width: 90mm, Height: 140mm
   - Color Mode: RGB
   - Raster Effects: 300 PPI
3. Create 7 layers as specified
4. Add color swatches (Window > Swatches)
5. Create guides (View > Guides)
6. Add placeholder objects (rectangles, text)
7. Apply graphic styles
8. File > Save as Template
9. Name: ONI_Cyberpunk_Badge.ait

TEST:
1. File > New from Template
2. Select ONI_Cyberpunk_Badge.ait
3. Should open with all layers, swatches, guides ready
4. All placeholders should be editable
```

### PHASE 4: Build Greebles Library (Optional, 2-4 hours)

```
Same as CorelDRAW guide, but save as .AI format:

Week 1: 20 Technical greebles
- Create in Illustrator
- Use basic shapes (rectangles, circles, polygons)
- Save as: C:\ONI\assets\greebles\technical\screw_hex_10mm.ai

Week 2: 15 Labels
Week 3: 15 Ornamental

Export formats:
- Native: .AI (Illustrator format)
- Vector: .SVG (for web)
- Raster: .PNG (300 DPI, transparent background)
```

### PHASE 5: Test PowerShell Automation (15 minutes)

```powershell
# Open PowerShell as Administrator
cd C:\ONI

# Test ONI.Gen module
Import-Module .\ONI.Gen.ps1 -Force
Test-ONIRandomness
# Should show random distribution tests

# Test seed system
$seed = New-ONISeed -StylePrefix "TEST"
Write-Host "Seed: $seed"
# Should output: ONI-TEST-20260104-XXXX

# Test color generation
$color = Get-RandomColor -FromPalette "cyberpunk_v1" -Category "primary"
Write-Host "Random Cyberpunk color: $color"
# Should output hex color from palette

# Test Illustrator connection
Import-Module .\ONI.IllustratorAutomation.ps1 -Force
$ai = Connect-Illustrator
# Illustrator should launch

# Test document creation
$doc = New-IllustratorDocument -AI $ai -Width 100 -Height 100 -Unit "mm"
# Should create 100x100mm document

# Test shape creation
$rect = New-IllustratorRectangle -Document $doc -X 10 -Y 10 `
    -Width 50 -Height 30 -FillColor "#FF0000"
# Should create red rectangle

# Cleanup
Disconnect-Illustrator -AI $ai
```

---

## 💡 ADVANCED WORKFLOWS

### WORKFLOW 1: Style Variations

```powershell
# Generate 5 variations of same badge with different seeds

$ai = Connect-Illustrator

1..5 | ForEach-Object {
    $seed = New-ONISeed -StylePrefix "CYB"
    
    New-CyberpunkBadge -AI $ai `
        -Name "ALEX MERCER" `
        -Title "SECURITY" `
        -ID "SEC-2847" `
        -OutputPath "C:\badges\variation_$_.ai"
    
    # Close document
    $ai.ActiveDocument.Close(2) # aiDoNotSaveChanges
    
    # Each badge will have different:
    # - Random color selections from palette
    # - Random greeble placements
    # - Random element sizes (within style bounds)
}

# Review all 5, pick best one
```

### WORKFLOW 2: Cross-Style Breeding

```powershell
# Manually create hybrid styles in Illustrator

# EXAMPLE: Cyberpunk + Japanese
1. Create Cyberpunk badge (template)
2. File > Scripts > ONI.Macros > Option 9 (Vertical Japanese Text)
3. Input Japanese text: "電子バッジ"
4. Apply both style colors:
   - Cyberpunk neon outlines
   - Japanese red accent elements
5. Arrange vertically on right side
6. Result: "Cyber-Tokyo" hybrid badge

# Save as new template: File > Save as Template
# Name: ONI_CyberTokyo_Badge.ait
```

### WORKFLOW 3: Dynamic Data Integration

```powershell
# Connect to database, generate badges on-the-fly

# employees.csv with photos
# Name,Title,ID,PhotoPath
# John Smith,Manager,001,C:\photos\john.jpg

$ai = Connect-Illustrator
$employees = Import-Csv "employees.csv"

foreach ($emp in $employees) {
    # Generate badge
    New-CyberpunkBadge -AI $ai `
        -Name $emp.Name `
        -Title $emp.Title `
        -ID $emp.ID `
        -OutputPath "C:\badges\$($emp.ID).ai"
    
    $doc = $ai.ActiveDocument
    
    # Import photo
    if (Test-Path $emp.PhotoPath) {
        # Place photo
        $placedItem = $doc.PlacedItems.Add()
        $placedItem.File = $emp.PhotoPath
        
        # Position in photo container (15mm from top-left)
        $placedItem.Top = $doc.Height - (15 * 2.834645669)
        $placedItem.Left = 15 * 2.834645669
        
        # Scale to fit container (60x80mm)
        $placedItem.Width = 60 * 2.834645669
        $placedItem.Height = 80 * 2.834645669
    }
    
    # Export
    Export-IllustratorToPDF -Document $doc -OutputPath "C:\badges\$($emp.ID).pdf"
    
    # Close
    $doc.Close(2)
}

Disconnect-Illustrator -AI $ai
```

---

## 🎨 CREATIVE TIPS

### TIP 1: Layered Randomness
```
Don't randomize everything equally:
- Text: Low variation (legibility)
- Greebles: High variation (visual interest)
- Colors: Medium variation (brand consistency)

In ONI.Gen.ps1:
$textVariation = 0.1  # 10% variation
$greebleVariation = 0.8  # 80% variation
$colorVariation = 0.4  # 40% variation
```

### TIP 2: Constrained Chaos
```
Use "forbidden zones" for greebles:
- Never place over text
- Never place over photo
- Never place over QR codes

In PowerShell:
$safeZones = @(
    @{X=15; Y=15; Width=60; Height=80},  # Photo
    @{X=10; Y=100; Width=70; Height=30}  # Text area
)

# When generating greebles, check if point is in safe zone
# Skip if inside
```

### TIP 3: Seed Collections
```
Keep a library of favorite seeds:

CYBERPUNK-FAVORITES.txt:
ONI-CYB-20260104-A3F7  # Aggressive, high contrast
ONI-CYB-20260104-B8K2  # Balanced, professional
ONI-CYB-20260104-C1M9  # Subtle, elegant

To reproduce:
Set-ONISeed -Seed "ONI-CYB-20260104-A3F7"
# All subsequent random calls will match that design
```

### TIP 4: Illustrator-Specific Features

```jsx
// Use Illustrator's built-in features in scripts

// 1. Blend Tool for smooth transitions
var blend = doc.blends.add();
blend.blendOptions.steps = 256;
blend.blendOptions.smoothColor = true;

// 2. Live Effects (non-destructive)
var outerGlow = object.liveEffects.add("Adobe Outer Glow");
// Remains editable in Appearance panel

// 3. Graphic Styles for instant application
var graphicStyle = doc.graphicStyles.getByName("Cyber Frame");
graphicStyle.applyTo(object);

// 4. Symbols for reusable elements
var symbol = doc.symbols.add(greeble);
var symbolInstance = doc.symbolItems.add(symbol);
```

---

## 📊 PERFORMANCE BENCHMARKS

### Manual Design (Traditional)
- Setup: 5 min
- Single badge: 30-45 min
- Variations: 30 min each
- **Total for 10 badges: 5+ hours**

### Semi-Automated (Templates + Scripts)
- Setup: 10 min (one-time)
- Single badge: 10-15 min
- Variations: 5 min each
- **Total for 10 badges: 2 hours**

### Fully Automated (PowerShell)
- Setup: 30 min (one-time)
- Single badge: 8-12 seconds
- Variations: 8-12 seconds each
- **Total for 10 badges: 2 minutes**

*Note: Illustrator may be slightly slower than CorelDRAW for COM automation*

---

## 🚨 TROUBLESHOOTING

### Issue: "Cannot connect to Illustrator"
```powershell
# Solution 1: Ensure Illustrator is installed
Get-ItemProperty "HKLM:\SOFTWARE\Adobe\Illustrator\*" | Select-Object DisplayName

# Solution 2: Run PowerShell as Administrator
# Right-click PowerShell > Run as Administrator

# Solution 3: Enable scripting in Illustrator
# Edit > Preferences > General > Scripting & Automation
# Check "Enable JavaScript"
```

### Issue: "Script not found"
```
Solution:
1. Verify script location:
   File > Scripts > Other Script... > Browse to ONI.Macros.jsx
2. If works, move to Scripts folder for permanent access
3. Check file extension is .jsx (not .txt)
4. Restart Illustrator
```

### Issue: "Style colors not applying"
```powershell
# Verify path to styles database
Test-Path "C:\ONI\data\styles_db.json"

# If false, fix path in ONI.IllustratorAutomation.ps1:
# Line ~XXX: $StylePath = "C:\ONI\data\styles_db.json"
```

### Issue: "COM object not responding"
```powershell
# Illustrator COM can be finicky

# Solution 1: Close all Illustrator instances
Get-Process -Name "Illustrator" | Stop-Process -Force

# Solution 2: Clear COM cache (Windows)
Remove-Item "HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify" -Recurse -Force

# Solution 3: Use direct script execution instead
$ai = Connect-Illustrator
Run-IllustratorScript -AI $ai -ScriptPath "C:\ONI\scripts\ONI.Macros.jsx"
```

### Issue: "Fonts not found"
```
Solution:
1. Install required fonts:
   - Arial (default, usually installed)
   - Courier New (default)
   - Orbitron (download from Google Fonts)
   - Noto Sans JP (download from Google Fonts)

2. Or edit scripts to use fallback fonts:
   In ONI.Macros.jsx, change:
   textFrame.textRange.characterAttributes.textFont = "Arial";
```

---

## 🎯 ROADMAP: Next Steps

### PHASE 1: Master the Basics (Week 1)
- [ ] Install all components
- [ ] Create 1 template (Cyberpunk)
- [ ] Test all 10 ExtendScript macros
- [ ] Generate 5 badges manually
- [ ] Generate 5 badges with PowerShell

### PHASE 2: Build Library (Weeks 2-3)
- [ ] Create 20 technical greebles (.AI format)
- [ ] Create 10 label greebles
- [ ] Create 10 ornamental greebles
- [ ] Save as Symbols in Illustrator
- [ ] Create Symbols Library (.AI with symbols)

### PHASE 3: Automate Workflows (Week 4)
- [ ] Setup batch CSV processing
- [ ] Create 50 badges from data
- [ ] Export all to PDF/PNG/SVG
- [ ] Measure time savings vs manual

### PHASE 4: Expand Styles (Ongoing)
- [ ] Create Print Badge template
- [ ] Create Certificate template
- [ ] Create Japanese Poster template
- [ ] Develop custom hybrid styles
- [ ] Share with team via Creative Cloud Libraries

### PHASE 5: Advanced Features (Ongoing)
- [ ] Integrate with Adobe Creative Cloud APIs
- [ ] Use Illustrator Actions for repetitive tasks
- [ ] Create custom panels with CEP (Common Extensibility Platform)
- [ ] Build web interface for badge generation

---

## 📚 QUICK REFERENCE

### File Locations
```
C:\ONI\
├── ONI.Gen.ps1 (Random generation engine)
├── ONI.IllustratorAutomation.ps1 (PowerShell bridge)
├── scripts\
│   └── ONI.Macros.jsx (ExtendScript macros)
├── data\
│   ├── styles_db.json (Main style database)
│   └── corel_styles_db.json (Also works for AI)
├── assets\
│   └── greebles\ (Vector library, .AI format)
└── templates\
    └── *.ait (Illustrator templates)

Adobe Illustrator Scripts:
C:\Program Files\Adobe\Adobe Illustrator [VERSION]\Presets\en_US\Scripts\

User Templates:
C:\Users\[USER]\AppData\Roaming\Adobe\Adobe Illustrator [VERSION]\en_US\Templates\
```

### Key Commands
```powershell
# PowerShell
Import-Module .\ONI.Gen.ps1
Import-Module .\ONI.IllustratorAutomation.ps1
$ai = Connect-Illustrator
New-CyberpunkBadge -AI $ai -Name "X" -Title "Y"
Disconnect-Illustrator -AI $ai

# Illustrator
Cmd/Ctrl + N         → New Document
Cmd/Ctrl + Shift + S → Save as Template
Cmd/Ctrl + Shift + O → Outline Text
F7                   → Layers Panel
Cmd/Ctrl + R         → Show Rulers
File > Scripts       → Run Scripts
```

### Illustrator Scripting Reference
- ExtendScript Toolkit: Installed with Creative Cloud
- Illustrator Scripting Guide: https://ai-scripting.docsforadobe.dev/
- JavaScript Tools Guide: https://extendscript.docsforadobe.dev/

---

## 🎉 CONGRATULATIONS!

You now have a **complete generative design system** for Adobe Illustrator that bridges:
- ✅ **Style DNA** (JSON databases)
- ✅ **Templates** (Illustrator .AIT)
- ✅ **Scripts** (ExtendScript automation)
- ✅ **Vector Library** (Greebles in .AI format)
- ✅ **PowerShell Engine** (COM bridge)

**From concept to final design in seconds, not hours.** 🚀

### Key Differences from CorelDRAW Version:
1. **Scripts:** ExtendScript (.jsx) instead of VBA
2. **Templates:** .AIT instead of .CDT
3. **Units:** Points internally (converted from mm)
4. **Effects:** Live Effects (non-destructive)
5. **Integration:** Works with Creative Cloud ecosystem

### Unique Illustrator Advantages:
- **Creative Cloud Libraries:** Share swatches, symbols across apps
- **Better SVG Export:** Industry-standard web graphics
- **Adobe Integration:** Works with Photoshop, InDesign, XD
- **CEP Panels:** Can build custom UI panels
- **Scriptographer/Astute Graphics:** Extended scripting capabilities

---

**"ONI não executa comandos. ONI cria arte."** 🎨

*Now in both CorelDRAW AND Adobe Illustrator!*