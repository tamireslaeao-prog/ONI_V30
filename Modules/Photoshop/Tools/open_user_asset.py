import sys
import os

# Add parent directory to sys.path to allow importing ONI_Photoshop_Bridge
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ONI_Photoshop_Bridge import PhotoshopBridge

bridge = PhotoshopBridge()
target_file = r"D:\DESIGN\psd_sources\37749682_ramadan_text_effect.psd"
# JS requires forward slashes or escaped backslashes
target_file_js = target_file.replace("\\", "/")

print(f"🚀 Opening User Asset: {target_file}")
bridge.execute_code(f'app.open(new File("{target_file_js}"));')
print("✅ Command sent to Photoshop.")
