from ONI_Photoshop_Bridge import PhotoshopBridge
import time

bridge = PhotoshopBridge()

# 1. Create Canvas
print("Creating Canvas...")
bridge.canvas.create(1000, 1000, "Gold_Texture_Base")

# 2. Fill Gold
print("Applying Gold Base...")
bridge.execute_code('ONI_PS.Canvas.FillBackground(ONI_PS.Core.HexColor("D4AF37"));')

# 3. Add Noise (Texture)
print("Adding Texture (Noise)...")
# Using the Library's AddNoise function directly
bridge.execute_code('ONI_PS.Effects.AddNoise(15, NoiseDistribution.GAUSSIAN, true);')

# 4. Add a subtle pattern (Scanlines via Pattern Overlay workaround or just simple Filter)
# Adding a second layer with clouds would be better but let's stick to simple Noise for "Texture"
# Let's add a "Highlight" gradient
bridge.layers.create("Highlight", 50)
bridge.execute_code('''
var doc = app.activeDocument;
var selBounds = [[0,0], [1000,0], [1000,500], [0,500]];
doc.selection.select(selBounds);
doc.selection.fill(ONI_PS.Core.HexColor("FFFFDD"));
doc.selection.deselect();
ONI_PS.Effects.GaussianBlur(100);
doc.activeLayer.blendMode = BlendMode.OVERLAY;
''')

print("Gold Asset Ready.")
