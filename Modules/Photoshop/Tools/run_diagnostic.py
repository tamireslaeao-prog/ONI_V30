import sys
import os
# Fix Path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ONI_Photoshop_Bridge import PhotoshopBridge

bridge = PhotoshopBridge()
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
INSPECTOR = os.path.join(TOOLS_DIR, "oni_layer_inspector.jsx")

print("🔍 RUNNING DIAGNOSTIC...")
bridge.execute_jsx(INSPECTOR)
