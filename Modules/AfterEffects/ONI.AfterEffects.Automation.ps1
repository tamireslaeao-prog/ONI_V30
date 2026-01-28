# ============================================================================
# ONI.AfterEffects.Automation.ps1
# Version: 1.0
# Description: PowerShell automation for Adobe After Effects using ExtendScript
# ============================================================================

<#
.SYNOPSIS
Complete automation system for After Effects motion graphics generation

.DESCRIPTION
This module provides functions to:
- Launch After Effects projects
- Execute JSX scripts programmatically
- Generate cyberpunk motion graphics
- Batch process compositions
- Automated rendering

.EXAMPLE
$ae = Connect-AfterEffects
New-CyberpunkTitle -AE $ae -Text "NEURAL LINK" -Output "C:\renders\title.mov"
#>

# ============================================================================
# AFTER EFFECTS CONNECTION
# ============================================================================

function Connect-AfterEffects {
    <#
    .SYNOPSIS
    Establishes connection to After Effects via COM
    #>
    
    try {
        # Try to get running instance
        $ae = [Runtime.InteropServices.Marshal]::GetActiveObject("AfterEffects.Application")
        Write-Host "✓ Connected to running After Effects instance" -ForegroundColor Green
    }
    catch {
        # Launch new instance
        try {
            Write-Host "Launching After Effects..." -ForegroundColor Yellow
            $ae = New-Object -ComObject AfterEffects.Application
            Start-Sleep -Seconds 5
            Write-Host "✓ After Effects launched" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to After Effects. Ensure it's installed."
            return $null
        }
    }
    
    return $ae
}

function Disconnect-AfterEffects {
    param($AE)
    
    if ($AE) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($AE) | Out-Null
        [System.GC]::Collect()
        Write-Host "✓ Disconnected from After Effects" -ForegroundColor Green
    }
}

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

function Invoke-AEScript {
    <#
    .SYNOPSIS
    Executes JSX script in After Effects
    
    .PARAMETER ScriptContent
    The ExtendScript code to execute
    
    .PARAMETER ScriptFile
    Path to .jsx file to execute
    #>
    param(
        [Parameter(Mandatory=$true, ParameterSetName='Content')]
        [string]$ScriptContent,
        
        [Parameter(Mandatory=$true, ParameterSetName='File')]
        [string]$ScriptFile,
        
        $AE
    )
    
    if (-not $AE) {
        $AE = Connect-AfterEffects
    }
    
    try {
        if ($ScriptFile) {
            if (-not (Test-Path $ScriptFile)) {
                Write-Error "Script file not found: $ScriptFile"
                return $null
            }
            $ScriptContent = Get-Content $ScriptFile -Raw
        }
        
        # Execute script
        $result = $AE.DoScript($ScriptContent)
        
        Write-Host "✓ Script executed successfully" -ForegroundColor Green
        return $result
    }
    catch {
        Write-Error "Script execution failed: $_"
        return $null
    }
}

# ============================================================================
# COMPOSITION CREATION
# ============================================================================

function New-AEComposition {
    <#
    .SYNOPSIS
    Creates new composition
    #>
    param(
        $AE,
        [string]$Name = "New_Comp",
        [int]$Width = 1920,
        [int]$Height = 1080,
        [double]$Duration = 10,
        [int]$FrameRate = 30
    )
    
    $script = @"
var comp = app.project.items.addComp('$Name', $Width, $Height, 1.0, $Duration, $FrameRate);
comp.name;
"@
    
    $result = Invoke-AEScript -AE $AE -ScriptContent $script
    
    Write-Host "✓ Composition created: $Name ($Width x $Height, $($FrameRate)fps)" -ForegroundColor Green
    
    return $result
}

# ============================================================================
# CYBERPUNK TITLE GENERATOR
# ============================================================================

function New-CyberpunkTitle {
    <#
    .SYNOPSIS
    Generates cyberpunk style animated title
    
    .EXAMPLE
    New-CyberpunkTitle -AE $ae -Text "NEURAL LINK" -Color "cyan" -OutputPath "C:\output\title.mov"
    #>
    param(
        $AE,
        [string]$Text = "CYBERPUNK 2077",
        [string]$Color = "cyan", # cyan, magenta, purple, green
        [int]$FontSize = 120,
        [string]$OutputPath = "$env:USERPROFILE\Desktop\cyberpunk_title.mov",
        [double]$Duration = 5
    )
    
    Write-Host "`n=== CYBERPUNK TITLE GENERATOR ===" -ForegroundColor Cyan
    Write-Host "Text: $Text" -ForegroundColor Yellow
    Write-Host "Color: $Color" -ForegroundColor Yellow
    
    # Load ONI library path
    $libPath = Join-Path $PSScriptRoot "oni_lib_aftereffects.jsx"
    if (-not (Test-Path $libPath)) {
        Write-Error "ONI Library not found: $libPath"
        return
    }
    
    # Color mapping
    $colorMap = @{
        "cyan" = "[0, 0.941, 1.0]"
        "magenta" = "[1.0, 0, 0.333]"
        "purple" = "[0.690, 0.149, 1.0]"
        "green" = "[0.224, 1.0, 0.078]"
    }
    
    $aeColor = $colorMap[$Color]
    if (-not $aeColor) { $aeColor = $colorMap["cyan"] }
    
    # Build script
    $script = @"
// Load ONI Library
$.evalFile('$($libPath.Replace('\','\\'))');

// Create composition
var comp = ONI.Presets.CreateCyberpunkComp('Cyberpunk_Title', 1920, 1080);
comp.duration = $Duration;

// Add title text
var titleLayer = ONI.Text.CreateText(
    comp, 
    '$Text',
    comp.width / 2,
    comp.height / 2,
    $FontSize,
    'Orbitron-Bold',
    $aeColor
);

// Center text
ONI.Core.CenterLayer(titleLayer, comp);

// Apply glow effect
ONI.FX.ApplyGlow(titleLayer, 100, 50, 50, $aeColor);

// Apply stroke
ONI.FX.ApplyStroke(titleLayer, 3, $aeColor, 2);

// Animate in
ONI.Animate.FadeIn(titleLayer, 0.5, 1.0);
ONI.Animate.BounceIn(titleLayer, 0.5, 1.5);

// Animate out
ONI.Animate.FadeOut(titleLayer, comp.duration - 1, 0.8);

// Add scanlines
var scanlines = ONI.Generate.CreateScanlines(comp, 4, 15);

// Add random greebles
for (var i = 0; i < 20; i++) {
    var x = Math.random() * comp.width;
    var y = Math.random() * comp.height;
    var size = Math.random() * 20 + 5;
    
    var greeble = ONI.Shapes.CreateCircle(
        comp, 
        'Greeble_' + i, 
        x, y, size, 
        $aeColor
    );
    
    greeble.opacity.setValue(Math.random() * 50 + 10);
    ONI.Animate.AddWiggle(greeble.position, 0.5, 20);
}

comp.name;
"@
    
    Write-Host "Executing title generation script..." -ForegroundColor Yellow
    
    $compName = Invoke-AEScript -AE $AE -ScriptContent $script
    
    if ($compName) {
        Write-Host "✓ Title composition created: $compName" -ForegroundColor Green
        
        # Add to render queue
        Write-Host "Adding to render queue..." -ForegroundColor Yellow
        
        $renderScript = @"
var comp = null;
for (var i = 1; i <= app.project.numItems; i++) {
    if (app.project.item(i).name === '$compName') {
        comp = app.project.item(i);
        break;
    }
}

if (comp) {
    var renderQueue = app.project.renderQueue;
    var item = renderQueue.items.add(comp);
    item.outputModules[1].file = new File('$($OutputPath.Replace('\','\\'))');
    'Render queued';
} else {
    'Composition not found';
}
"@
        
        $result = Invoke-AEScript -AE $AE -ScriptContent $renderScript
        
        Write-Host "`n✓ CYBERPUNK TITLE COMPLETE" -ForegroundColor Green
        Write-Host "  Composition: $compName" -ForegroundColor Cyan
        Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
        Write-Host "  Duration: $Duration seconds" -ForegroundColor Cyan
        Write-Host "`n  To render: File > Export > Add to Render Queue" -ForegroundColor Yellow
    }
}

# ============================================================================
# LOWER THIRD GENERATOR
# ============================================================================

function New-LowerThird {
    <#
    .SYNOPSIS
    Creates animated lower third (name/title bar)
    #>
    param(
        $AE,
        [string]$Name = "JOHN SMITH",
        [string]$Title = "CHIEF TECHNOLOGY OFFICER",
        [string]$Style = "cyberpunk", # cyberpunk, minimal, corporate
        [double]$Duration = 8
    )
    
    Write-Host "`n=== LOWER THIRD GENERATOR ===" -ForegroundColor Cyan
    
    $libPath = Join-Path $PSScriptRoot "oni_lib_aftereffects.jsx"
    
    $script = @"
$.evalFile('$($libPath.Replace('\','\\'))');

var comp = ONI.Core.GetOrCreateComp('LowerThird', 1920, 1080, 30, $Duration);

// Background bar
var bgBar = ONI.Shapes.CreateRect(
    comp,
    'BG_Bar',
    400, comp.height - 150,
    600, 100,
    [0.039, 0.039, 0.059, 0.9],
    [0, 0.941, 1.0, 1.0],
    2
);

// Name text
var nameText = ONI.Text.CreateText(
    comp,
    '$Name',
    450, comp.height - 170,
    48,
    'Orbitron-Bold',
    [0, 0.941, 1.0]
);

// Title text
var titleText = ONI.Text.CreateText(
    comp,
    '$Title',
    450, comp.height - 130,
    24,
    'Roboto-Regular',
    [1.0, 1.0, 1.0]
);

// Animate in
ONI.Animate.SlideIn(bgBar, comp, 0.5, 0.8, 'left');
ONI.Animate.SlideIn(nameText, comp, 0.8, 0.6, 'left');
ONI.Animate.SlideIn(titleText, comp, 1.0, 0.6, 'left');

// Animate out
ONI.Animate.SlideOut(bgBar, comp, comp.duration - 1, 0.6, 'left');
ONI.Animate.SlideOut(nameText, comp, comp.duration - 0.8, 0.5, 'left');
ONI.Animate.SlideOut(titleText, comp, comp.duration - 0.6, 0.5, 'left');

comp.name;
"@
    
    $compName = Invoke-AEScript -AE $AE -ScriptContent $script
    
    Write-Host "✓ Lower third created: $compName" -ForegroundColor Green
}

# ============================================================================
# TECH HUD OVERLAY
# ============================================================================

function New-TechHUD {
    <#
    .SYNOPSIS
    Creates futuristic HUD overlay elements
    #>
    param(
        $AE,
        [int]$ElementCount = 15,
        [double]$Duration = 10
    )
    
    Write-Host "`n=== TECH HUD GENERATOR ===" -ForegroundColor Cyan
    
    $libPath = Join-Path $PSScriptRoot "oni_lib_aftereffects.jsx"
    
    $script = @"
$.evalFile('$($libPath.Replace('\','\\'))');

var comp = ONI.Core.GetOrCreateComp('Tech_HUD', 1920, 1080, 30, $Duration);

// Corner brackets
for (var corner = 0; corner < 4; corner++) {
    var x, y, rotation;
    
    switch(corner) {
        case 0: x = 100; y = 100; rotation = 0; break;
        case 1: x = comp.width - 100; y = 100; rotation = 90; break;
        case 2: x = comp.width - 100; y = comp.height - 100; rotation = 180; break;
        case 3: x = 100; y = comp.height - 100; rotation = 270; break;
    }
    
    var bracket = ONI.Shapes.CreateRect(
        comp,
        'Corner_' + corner,
        x, y,
        80, 80,
        [0, 0, 0, 0],
        [0, 0.941, 1.0, 1.0],
        3
    );
    
    bracket.rotation.setValue(rotation);
}

// Random tech elements
for (var i = 0; i < $ElementCount; i++) {
    var x = Math.random() * comp.width;
    var y = Math.random() * comp.height;
    var size = Math.random() * 40 + 10;
    
    var element = ONI.Shapes.CreateCircle(
        comp,
        'Element_' + i,
        x, y, size,
        [0, 0.941, 1.0, 0.3]
    );
    
    ONI.Animate.AddWiggle(element.opacity, 2, 30);
}

// Scanlines
ONI.Generate.CreateScanlines(comp, 4, 10);

comp.name;
"@
    
    $compName = Invoke-AEScript -AE $AE -ScriptContent $script
    
    Write-Host "✓ Tech HUD created: $compName" -ForegroundColor Green
}

# ============================================================================
# BATCH PROCESSING
# ============================================================================

function New-BatchTitles {
    <#
    .SYNOPSIS
    Generates multiple title sequences from CSV
    #>
    param(
        $AE,
        [string]$CSVPath,
        [string]$OutputFolder = "$env:USERPROFILE\Desktop\titles"
    )
    
    if (-not (Test-Path $CSVPath)) {
        Write-Error "CSV file not found: $CSVPath"
        return
    }
    
    # Create output folder
    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder | Out-Null
    }
    
    # Load CSV
    $titles = Import-Csv -Path $CSVPath
    
    Write-Host "`n=== BATCH TITLE GENERATION ===" -ForegroundColor Cyan
    Write-Host "Total titles: $($titles.Count)" -ForegroundColor Yellow
    
    foreach ($title in $titles) {
        $outputPath = Join-Path $OutputFolder "$($title.ID)_$($title.Text -replace ' ','_').mov"
        
        Write-Host "`nProcessing: $($title.Text)" -ForegroundColor Yellow
        
        New-CyberpunkTitle -AE $AE `
            -Text $title.Text `
            -Color $title.Color `
            -FontSize $title.FontSize `
            -OutputPath $outputPath `
            -Duration $title.Duration
        
        Write-Host "  ✓ Queued: $($title.Text)" -ForegroundColor Green
    }
    
    Write-Host "`n✓ BATCH COMPLETE" -ForegroundColor Green
    Write-Host "  Total: $($titles.Count)" -ForegroundColor Cyan
    Write-Host "  Output: $OutputFolder" -ForegroundColor Cyan
}

# ============================================================================
# PROJECT MANAGEMENT
# ============================================================================

function New-AEProject {
    <#
    .SYNOPSIS
    Creates new After Effects project with ONI structure
    #>
    param(
        $AE,
        [string]$ProjectPath
    )
    
    $script = @"
// Create new project
app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
var newProj = app.newProject();

// Create folder structure
var assetsFolder = app.project.items.addFolder('Assets');
var compsFolder = app.project.items.addFolder('Compositions');
var rendersFolder = app.project.items.addFolder('Renders');

'Project created';
"@
    
    $result = Invoke-AEScript -AE $AE -ScriptContent $script
    
    if ($ProjectPath) {
        $saveScript = "app.project.save(new File('$($ProjectPath.Replace('\','\\'))'));"
        Invoke-AEScript -AE $AE -ScriptContent $saveScript
    }
    
    Write-Host "✓ Project created with ONI structure" -ForegroundColor Green
}

# ============================================================================
# RENDER MANAGEMENT
# ============================================================================

function Start-AERender {
    <#
    .SYNOPSIS
    Starts After Effects render queue
    #>
    param($AE)
    
    $script = @"
var renderQueue = app.project.renderQueue;
renderQueue.render();
'Rendering started';
"@
    
    Invoke-AEScript -AE $AE -ScriptContent $script
    
    Write-Host "✓ Render started" -ForegroundColor Green
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Get-AEInfo {
    <#
    .SYNOPSIS
    Gets After Effects version and project info
    #>
    param($AE)
    
    $script = @"
var info = {
    version: app.version,
    buildName: app.buildName,
    projectName: app.project.file ? app.project.file.name : 'Untitled',
    numItems: app.project.numItems,
    numComps: 0
};

for (var i = 1; i <= app.project.numItems; i++) {
    if (app.project.item(i) instanceof CompItem) {
        info.numComps++;
    }
}

JSON.stringify(info);
"@
    
    $result = Invoke-AEScript -AE $AE -ScriptContent $script
    
    if ($result) {
        $info = $result | ConvertFrom-Json
        
        Write-Host "`n=== AFTER EFFECTS INFO ===" -ForegroundColor Cyan
        Write-Host "Version: $($info.version)" -ForegroundColor Yellow
        Write-Host "Build: $($info.buildName)" -ForegroundColor Yellow
        Write-Host "Project: $($info.projectName)" -ForegroundColor Yellow
        Write-Host "Total Items: $($info.numItems)" -ForegroundColor Yellow
        Write-Host "Compositions: $($info.numComps)" -ForegroundColor Yellow
    }
}

# ============================================================================
# EXPORT MODULE
# ============================================================================

Export-ModuleMember -Function @(
    'Connect-AfterEffects',
    'Disconnect-AfterEffects',
    'Invoke-AEScript',
    'New-AEComposition',
    'New-CyberpunkTitle',
    'New-LowerThird',
    'New-TechHUD',
    'New-BatchTitles',
    'New-AEProject',
    'Start-AERender',
    'Get-AEInfo'
)

Write-Host "ONI.AfterEffects.Automation module loaded" -ForegroundColor Green
Write-Host "Use: Get-Command -Module ONI.AfterEffects.Automation" -ForegroundColor Yellow
