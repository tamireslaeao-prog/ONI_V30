import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.photoshop.composer_service import PhotoshopComposer

def process_file_detailed(file_path, colors):
    print(f"🔌 Connecting to Photoshop for DETAILED vectorization...")
    composer = PhotoshopComposer()
    composer._ensure_connection()
    
    if not composer.app:
        print("❌ Photoshop unavailable.")
        return

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f"❌ File not found: {abs_path}")
        return

    print(f"📂 Opening: {abs_path}")
    # Check if open
    try:
        composer.app.Open(abs_path)
    except:
        pass

    print(f"🎨 Running Detailed Vectorization (Max Colors: {colors})...")
    print("⏳ This may take 10-20 seconds scanning pixels...")
    
    result = composer.vectorize_detailed_active_layer(max_colors=colors, tolerance=1.0)
    print(f"📊 Result: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to image file")
    parser.add_argument("--colors", type=int, default=16, help="Max colors to posterize")
    args = parser.parse_args()
    
    process_file_detailed(args.file, args.colors)
