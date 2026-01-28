# 🎬 ONI SYSTEM FOR ADOBE AFTER EFFECTS

## Complete Motion Graphics Automation Framework

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Usage Examples](#usage-examples)
6. [Style System](#style-system)
7. [Automation Workflows](#automation-workflows)
8. [Advanced Techniques](#advanced-techniques)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 SYSTEM OVERVIEW

O **ONI System for After Effects** é uma framework completa de automação para criação de motion graphics, inspirado no sistema ONI original para Photoshop/CorelDRAW.

### Features Principais

- ✅ **Automação Completa**: Scripts ExtendScript (JSX) para controle total do AE
- ✅ **PowerShell Bridge**: Execução de comandos AE via linha de comando
- ✅ **Style Database**: Sistema de estilos procedurais (Cyberpunk, Corporate, Synthwave)
- ✅ **Batch Processing**: Geração em massa de títulos, lower thirds, etc
- ✅ **Animation Presets**: Biblioteca de animações reutilizáveis
- ✅ **Expression Library**: Expressões prontas para movimento procedural

### Arquitetura do Sistema

```
ONI-AfterEffects/
├── oni_lib_aftereffects.jsx        # Core library (ExtendScript)
├── ae_styles_db.json               # Style database
├── ONI.AfterEffects.Automation.ps1 # PowerShell automation
├── templates/
│   ├── cyberpunk_title.aep
│   ├── lower_third.aep
│   └── tech_hud.aep
└── docs/
    └── ONI_AfterEffects_Documentation.md
```

---

## 🔧 INSTALLATION

### Prerequisites

1. **Adobe After Effects** 2024 or 2025
2. **Windows PowerShell** 5.1 or later
3. **ExtendScript Toolkit** (optional, for debugging)

### Step 1: Copy Files

```powershell
# Create ONI directory
New-Item -ItemType Directory -Path "C:\ONI\AfterEffects"

# Copy files
Copy-Item oni_lib_aftereffects.jsx "C:\ONI\AfterEffects\"
Copy-Item ae_styles_db.json "C:\ONI\AfterEffects\"
Copy-Item ONI.AfterEffects.Automation.ps1 "C:\ONI\AfterEffects\"
```

### Step 2: Enable Scripts in After Effects

1. Open After Effects
2. Go to: **Edit > Preferences > Scripting & Expressions**
3. Enable: **Allow Scripts to Write Files and Access Network**
4. Restart After Effects

### Step 3: Load PowerShell Module

```powershell
Import-Module "C:\ONI\AfterEffects\ONI.AfterEffects.Automation.ps1"
```

### Step 4: Verify Installation

```powershell
$ae = Connect-AfterEffects
Get-AEInfo -AE $ae
```

---

## 🚀 QUICK START

### Example 1: Create Cyberpunk Title

```powershell
# Connect to After Effects
$ae = Connect-AfterEffects

# Generate cyberpunk title
New-CyberpunkTitle -AE $ae `
    -Text "NEURAL LINK" `
    -Color "cyan" `
    -FontSize 140 `
    -Duration 6 `
    -OutputPath "C:\renders\neural_link.mov"

# Render
Start-AERender -AE $ae
```

### Example 2: Create Lower Third

```powershell
New-LowerThird -AE $ae `
    -Name "DR. SARAH CHEN" `
    -Title "CHIEF NEUROSCIENTIST" `
    -Style "cyberpunk" `
    -Duration 8
```

### Example 3: Batch Process Titles

```csv
# titles.csv
ID,Text,Color,FontSize,Duration
1,CYBERPUNK 2077,cyan,120,5
2,NEURAL LINK,magenta,140,6
3,GHOST PROTOCOL,purple,130,5
```

```powershell
New-BatchTitles -AE $ae `
    -CSVPath "C:\data\titles.csv" `
    -OutputFolder "C:\renders\batch"
```

---

## 🧩 CORE COMPONENTS

### 1. ONI.Core Module

Funções fundamentais para manipulação de composições.

```javascript
// Get or create composition
var comp = ONI.Core.GetOrCreateComp("MyComp", 1920, 1080, 30, 10);

// Color helper (converts RGB 0-255 to AE 0-1)
var cyanColor = ONI.Core.Color(0, 240, 255);

// Center layer
ONI.Core.CenterLayer(textLayer, comp);

// Apply expression
ONI.Core.ApplyExpression(layer.position, "wiggle(2, 50)");
```

### 2. ONI.Shapes Module

Criação de shape layers procedurais.

```javascript
// Rectangle
var rect = ONI.Shapes.CreateRect(
    comp,           // composition
    "MyRect",       // name
    960, 540,       // x, y position
    400, 200,       // width, height
    [0, 0.941, 1],  // fill color (cyan)
    [1, 0, 0],      // stroke color (red)
    3               // stroke width
);

// Circle
var circle = ONI.Shapes.CreateCircle(
    comp, "MyCircle", 960, 540, 100, [1, 0, 0.333]
);

// Polygon (hexagon)
var hexagon = ONI.Shapes.CreatePolygon(
    comp, "Hexagon", 960, 540, 80, 6, [0.690, 0.149, 1.0]
);
```

### 3. ONI.Text Module

Sistema de texto com animações.

```javascript
// Create text
var titleText = ONI.Text.CreateText(
    comp,
    "CYBERPUNK 2077",
    960, 540,          // position
    120,               // font size
    "Orbitron-Bold",   // font
    [0, 0.941, 1.0]    // color (cyan)
);

// Animate text in (character by character)
ONI.Text.AnimateTextIn(titleText, 1.0, 2.0);
```

### 4. ONI.FX Module

Aplicação de efeitos visuais.

```javascript
// Glow effect
ONI.FX.ApplyGlow(layer, 100, 50, 50);

// Drop shadow
ONI.FX.ApplyDropShadow(layer, 10, 20, 135, 0.75);

// Stroke
ONI.FX.ApplyStroke(layer, 3, [0, 0.941, 1.0], 2);

// Noise/grain
ONI.FX.ApplyNoise(layer, 25);

// Light burst (requires CC plugin)
ONI.FX.ApplyLightBurst(layer, 50, 100);
```

### 5. ONI.Animate Module

Presets de animação.

```javascript
// Fade in
ONI.Animate.FadeIn(layer, 0.5, 1.0);

// Fade out
ONI.Animate.FadeOut(layer, 8.0, 0.8);

// Bounce in
ONI.Animate.BounceIn(layer, 0.5, 1.5);

// Slide in
ONI.Animate.SlideIn(layer, comp, 1.0, 0.8, "left");

// Wiggle expression
ONI.Animate.AddWiggle(layer.position, 2, 50);

// Loop expression
ONI.Animate.AddLoop(layer.rotation, "cycle");
```

### 6. ONI.Generate Module

Geração procedural de elementos.

```javascript
// Tech grid background
var grid = ONI.Generate.CreateTechGrid(comp, 50, 1, [0, 0.941, 1.0]);

// Random particles
var particles = ONI.Generate.CreateParticles(comp, 50, [1, 0, 0.333]);

// Scanlines overlay
var scanlines = ONI.Generate.CreateScanlines(comp, 4, 15);
```

---

## 🎨 STYLE SYSTEM

### Available Styles

1. **Cyberpunk Motion** (`cyberpunk_motion_v1`)
   - Neon glows, glitches, tech elements
   - Best for: Title sequences, lower thirds, HUD interfaces

2. **Minimal Corporate** (`minimal_corporate_v1`)
   - Clean, professional animations
   - Best for: Business presentations, explainer videos

3. **Synthwave Retro** (`synthwave_motion_v1`)
   - 80s inspired gradients and grids
   - Best for: Music videos, retro content

4. **Glitch Art** (`glitch_art_v1`)
   - Data corruption aesthetics
   - Best for: Transitions, creative effects

5. **Kinetic Typography** (`kinetic_typography_v1`)
   - Dynamic text animations
   - Best for: Lyric videos, quotes

6. **Infographic Motion** (`infographic_motion_v1`)
   - Data visualization
   - Best for: Stats, charts, educational content

### Loading Styles

```javascript
// Load style database
var stylesFile = new File("C:/ONI/AfterEffects/ae_styles_db.json");
stylesFile.open("r");
var stylesJSON = stylesFile.read();
stylesFile.close();
var styleDb = JSON.parse(stylesJSON);

// Get specific style
var cyberpunkStyle = null;
for (var i = 0; i < styleDb.styles.length; i++) {
    if (styleDb.styles[i].style_id === "cyberpunk_motion_v1") {
        cyberpunkStyle = styleDb.styles[i];
        break;
    }
}

// Apply style colors
var primaryColor = cyberpunkStyle.color_system.primary[0].ae_rgb;
```

---

## 💼 USAGE EXAMPLES

### Example 1: Complete Title Sequence

```javascript
$.evalFile("C:/ONI/AfterEffects/oni_lib_aftereffects.jsx");

// Create composition
var comp = ONI.Presets.CreateCyberpunkComp("Title_Sequence", 1920, 1080);
comp.duration = 8;

// Main title
var mainTitle = ONI.Text.CreateText(
    comp, "NEURAL INTERFACE", 
    960, 400, 140, "Orbitron-Bold", 
    [0, 0.941, 1.0]
);
ONI.Core.CenterLayer(mainTitle, comp);
ONI.FX.ApplyGlow(mainTitle, 100, 50, 50);
ONI.FX.ApplyStroke(mainTitle, 3, [0, 0.941, 1.0], 2);
ONI.Animate.BounceIn(mainTitle, 0.5, 1.5);

// Subtitle
var subtitle = ONI.Text.CreateText(
    comp, "SYSTEM INITIALIZATION", 
    960, 550, 48, "Roboto-Regular", 
    [1.0, 1.0, 1.0]
);
ONI.Core.CenterLayer(subtitle, comp);
ONI.Animate.FadeIn(subtitle, 1.5, 1.0);

// Background elements
var particles = ONI.Generate.CreateParticles(comp, 30, [0, 0.941, 1.0, 0.3]);
var scanlines = ONI.Generate.CreateScanlines(comp, 4, 10);

// Animate out
ONI.Animate.FadeOut(mainTitle, 6.5, 1.0);
ONI.Animate.FadeOut(subtitle, 6.8, 0.8);
```

### Example 2: Animated Lower Third

```javascript
// Create composition
var comp = ONI.Core.GetOrCreateComp("Lower_Third", 1920, 1080, 30, 8);

// Background bar
var bgBar = ONI.Shapes.CreateRect(
    comp, "BG_Bar",
    400, comp.height - 150,
    600, 100,
    [0.039, 0.039, 0.059, 0.9],
    [0, 0.941, 1.0, 1.0],
    2
);

// Accent line
var accentLine = ONI.Shapes.CreateRect(
    comp, "Accent",
    350, comp.height - 150,
    10, 100,
    [0, 0.941, 1.0, 1.0],
    null, 0
);

// Name
var nameText = ONI.Text.CreateText(
    comp, "DR. SARAH CHEN",
    450, comp.height - 170,
    48, "Orbitron-Bold",
    [0, 0.941, 1.0]
);

// Title
var titleText = ONI.Text.CreateText(
    comp, "CHIEF NEUROSCIENTIST",
    450, comp.height - 130,
    24, "Roboto-Regular",
    [1.0, 1.0, 1.0]
);

// Animations
ONI.Animate.SlideIn(bgBar, comp, 0.5, 0.8, "left");
ONI.Animate.SlideIn(accentLine, comp, 0.6, 0.7, "left");
ONI.Animate.SlideIn(nameText, comp, 0.8, 0.6, "left");
ONI.Animate.SlideIn(titleText, comp, 1.0, 0.6, "left");

// Hold and exit
ONI.Animate.FadeOut(bgBar, 6.5, 0.8);
ONI.Animate.FadeOut(nameText, 6.7, 0.6);
ONI.Animate.FadeOut(titleText, 6.8, 0.5);
```

### Example 3: Tech HUD Overlay

```javascript
var comp = ONI.Core.GetOrCreateComp("HUD_Overlay", 1920, 1080, 30, 10);

// Corner brackets (4 corners)
var cornerPositions = [
    [100, 100, 0],
    [comp.width - 100, 100, 90],
    [comp.width - 100, comp.height - 100, 180],
    [100, comp.height - 100, 270]
];

for (var i = 0; i < cornerPositions.length; i++) {
    var pos = cornerPositions[i];
    
    // L-shaped bracket
    var bracket = ONI.Shapes.CreateRect(
        comp, "Corner_" + i,
        pos[0], pos[1],
        80, 80,
        [0, 0, 0, 0],
        [0, 0.941, 1.0, 1.0],
        3
    );
    
    bracket.property("ADBE Transform Group").property("ADBE Rotate Z").setValue(pos[2]);
    
    // Pulse animation
    ONI.Animate.AddLoop(bracket.property("ADBE Transform Group").property("ADBE Opacity"), "pingpong");
}

// Center crosshair
var crosshairH = ONI.Shapes.CreateRect(
    comp, "Crosshair_H",
    comp.width / 2, comp.height / 2,
    40, 2,
    [0, 0.941, 1.0, 1.0],
    null, 0
);

var crosshairV = ONI.Shapes.CreateRect(
    comp, "Crosshair_V",
    comp.width / 2, comp.height / 2,
    2, 40,
    [0, 0.941, 1.0, 1.0],
    null, 0
);

// Scanlines
ONI.Generate.CreateScanlines(comp, 4, 8);

// Random tech elements
for (var j = 0; j < 15; j++) {
    var x = Math.random() * comp.width;
    var y = Math.random() * comp.height;
    var size = Math.random() * 20 + 5;
    
    var element = ONI.Shapes.CreateCircle(
        comp, "Element_" + j,
        x, y, size,
        [0, 0.941, 1.0, 0.3]
    );
    
    ONI.Animate.AddWiggle(element.property("ADBE Transform Group").property("ADBE Opacity"), 1, 30);
}
```

---

## 🤖 AUTOMATION WORKFLOWS

### Workflow 1: Batch Title Generation

```powershell
# titles.csv
# ID,Text,Color,FontSize,Duration
# 1,EPISODE 01,cyan,120,5
# 2,EPISODE 02,magenta,120,5
# 3,EPISODE 03,purple,120,5

$ae = Connect-AfterEffects

New-BatchTitles -AE $ae `
    -CSVPath "C:\projects\episodes\titles.csv" `
    -OutputFolder "C:\renders\episodes"
```

### Workflow 2: Project Setup Automation

```powershell
# Create new project with ONI structure
New-AEProject -AE $ae -ProjectPath "C:\projects\new_project.aep"

# Create compositions
New-AEComposition -AE $ae -Name "Title_Sequence" -Duration 8
New-AEComposition -AE $ae -Name "Lower_Third" -Duration 6
New-AEComposition -AE $ae -Name "Outro" -Duration 5
```

### Workflow 3: Style Variations

```powershell
$styles = @("cyan", "magenta", "purple", "green")

foreach ($style in $styles) {
    New-CyberpunkTitle -AE $ae `
        -Text "NEURAL LINK" `
        -Color $style `
        -OutputPath "C:\renders\title_$style.mov"
}
```

---

## 🔬 ADVANCED TECHNIQUES

### Custom Expressions

```javascript
// Smooth wiggle
layer.position.expression = @"
freq = 2;
amp = 50;
smooth = 5;
wiggle(freq, amp).smooth(smooth)
"@

// Bounce with decay
layer.scale.expression = @"
amp = .1;
freq = 2.0;
decay = 5.0;
n = 0;
if (numKeys > 0){
    n = nearestKey(time).index;
    if (key(n).time > time){n--;}
}
if (n == 0){ t = 0;}
else {t = time - key(n).time;}
if (n > 0){
    v = velocityAtTime(key(n).time - thisComp.frameDuration/10);
    value + v*amp*Math.sin(freq*t*2*Math.PI)/Math.exp(decay*t);
}else{
    value
}
"@

// Looping animation
layer.rotation.expression = "loopOut('cycle')"
```

### Dynamic Text from JSON

```javascript
// Load data from JSON
var dataFile = new File("C:/data/names.json");
dataFile.open("r");
var data = JSON.parse(dataFile.read());
dataFile.close();

// Create text for each entry
for (var i = 0; i < data.names.length; i++) {
    var name = data.names[i];
    
    var textLayer = ONI.Text.CreateText(
        comp, name.text,
        960, 200 + (i * 100),
        48, "Roboto-Bold",
        [1, 1, 1]
    );
    
    ONI.Animate.FadeIn(textLayer, i * 0.5, 0.5);
}
```

---

## 🛠️ TROUBLESHOOTING

### Issue 1: "Allow Scripts to Write Files" Error

**Solution:**
1. Edit > Preferences > Scripting & Expressions
2. Enable: **Allow Scripts to Write Files and Access Network**
3. Restart After Effects

### Issue 2: PowerShell Can't Connect to AE

**Solution:**
```powershell
# Check if AE is running
Get-Process | Where-Object {$_.ProcessName -like "*AfterFX*"}

# If not, launch manually then reconnect
$ae = Connect-AfterEffects
```

### Issue 3: Fonts Not Found

**Solution:**
```javascript
// Always use try-catch for fonts
try {
    textDoc.font = "Orbitron-Bold";
} catch(e) {
    textDoc.font = "Arial-BoldMT"; // Fallback
}
```

### Issue 4: Script Execution Timeout

**Solution:**
```powershell
# Break large operations into smaller chunks
# Use progress indicators
Write-Host "Processing... (1/10)" -ForegroundColor Yellow
```

---

## 📚 ADDITIONAL RESOURCES

### Expression Reference

- [Adobe Expression Language Reference](https://ae-expressions.docsforadobe.dev/)
- [Motion Script Expressions](https://www.motionscript.com/)

### ExtendScript Documentation

- [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/)
- [ExtendScript Toolkit](https://extendscript.docsforadobe.dev/)

### Community

- [Creative COW Forums](https://creativecow.net/forums/forum/adobe-after-effects/)
- [AE Scripting Reddit](https://www.reddit.com/r/AfterEffects/)

---

## 📄 LICENSE

ONI System for After Effects
© 2026 - MIT License

---

## 🤝 CONTRIBUTING

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch de feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📞 SUPPORT

Para suporte:
- Email: oni-support@example.com
- Discord: ONI Community
- GitHub Issues

---

**Version:** 1.0  
**Last Updated:** 2026-01-04  
**Compatible with:** Adobe After Effects 2024/2025
