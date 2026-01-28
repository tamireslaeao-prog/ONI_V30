from PIL import Image
import os

def create_valid_dummy_png():
    width = 1920
    height = 1080
    color = (0, 0, 0) # Black
    
    output_dir = r"c:\Users\user\Desktop\ONI V24\temp\render_neon"
    os.makedirs(output_dir, exist_ok=True)
    
    img_path = os.path.join(output_dir, "frame_0001.png")
    
    img = Image.new('RGB', (width, height), color)
    img.save(img_path)
    print(f"Created valid PNG at: {img_path}")

if __name__ == "__main__":
    create_valid_dummy_png()
