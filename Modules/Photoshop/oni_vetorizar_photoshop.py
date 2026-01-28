import os
import sys
import cv2
import numpy as np
import win32com.client

# 1. SETUP PATHS
BASE_DIR = r"c:\Users\user\Desktop\oni v41\Modules\Photoshop\VectorFactory"
sys.path.append(BASE_DIR)

try:
    from vision_factory_ultra import UltraVisionFactory
    from vector_factory_ultra import UltraVectorCompiler
except ImportError as e:
    print(f"❌ Error importing Vector Factory: {e}")
    sys.exit(1)

def upscale_image(image_path, scale_factor=4):
    """Upscales image for better vector detail."""
    print(f"🔍 Upscaling image by {scale_factor}x...")
    img = cv2.imread(image_path)
    if img is None: return None
    
    h, w = img.shape[:2]
    new_dim = (w * scale_factor, h * scale_factor)
    
    # 1. Upscale with Lanczos (High Quality)
    upscaled = cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)
    
    # 2. Denoise slightly to remove JPEG artifacts amplified by upscale
    upscaled = cv2.fastNlMeansDenoisingColored(upscaled, None, 5, 5, 7, 21)
    
    # 3. Sharpening to recover edges
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    upscaled = cv2.filter2D(upscaled, -1, kernel)
    
    # Save temporary upscaled file
    temp_path = image_path.replace(".png", "_upscaled.png")
    cv2.imwrite(temp_path, upscaled)
    return temp_path

def run_ultra_vectorization(image_path):
    print(f"🚀 Starting ULTRA Vectorization (High Definition)...")
    
    if not os.path.exists(image_path):
        print("❌ Image file not found.")
        return

    # STEP 0: UPSCALE
    hq_image_path = upscale_image(image_path, scale_factor=4)
    if not hq_image_path:
        print("❌ Upscaling failed.")
        return

    # STEP 1: RASTER TO SVG
    # We use 'master' quality for maximum segments
    # But we override settings for FACE PRECISION:
    # - Lower smoothing (more erratic but precise)
    # - Lower min_area (capture eyes/pupils)
    svg_path = hq_image_path + ".svg"
    
    print(f"🎨 Phase 1: Calculating High-Fidelity Bezier Curves...")
    vision = UltraVisionFactory(quality='master') 
    
    # OVERRIDE SETTINGS FOR FACIAL DETAIL
    vision.settings['min_area'] = 5      # Capture tiny details (eyes)
    vision.settings['smoothing'] = 0.0002 # Minimal smoothing for accuracy
    vision.settings['colors'] = 48       # More colors for better gradients
    
    success = vision.raster_to_svg(hq_image_path, svg_path)
    
    if not success:
        print("❌ Vision Factory failed.")
        return

    # STEP 2: SVG TO JSX
    print(f"🔧 Phase 2: Generating Procedural JSX...")
    compiler = UltraVectorCompiler()
    
    # Refinement: Add Title
    config = {
        "text": "HD RENDER", 
        "subtext": "Procedural Pen V2",
        "color": "FFFFFF"
    } 
    jsx_path = compiler.compile_to_jsx(svg_path, config)
    
    if not jsx_path:
        print("❌ JSX Compilation failed.")
        return

    # STEP 3: EXECUTE
    print(f"▶️ Phase 3: Executing in Photoshop...")
    try:
        ps = win32com.client.Dispatch("Photoshop.Application")
        ps.DoJavaScriptFile(jsx_path)
        print("✅ Success! Check Photoshop.")
    except Exception as e:
        print(f"❌ Photoshop Execution Error: {e}")

if __name__ == "__main__":
    # TARGET IMAGE
    target_image = r"C:/Users/user/.gemini/antigravity/brain/a33a3cb8-327f-43b6-bc74-398aca80898d/uploaded_media_1769616607520.png"
    run_ultra_vectorization(target_image)
