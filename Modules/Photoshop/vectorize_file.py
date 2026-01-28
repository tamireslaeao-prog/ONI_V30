import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.photoshop.composer_service import PhotoshopComposer

def process_file(file_path):
    print(f"🔌 Connecting to Photoshop...")
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
    try:
        composer.app.Open(abs_path)
    except Exception as e:
        print(f"❌ Failed to open file: {e}")
        return

    print("🎨 Vectorizing active layer...")
    # Optional: Unlock background if needed? 
    # The vectorizer relies on "Load Selection Transparency". 
    # If the image is flat/locked background, we might need to unlock it or select subject.
    # Updated to use auto_subject=True (Select Subject)
    
    result = composer.vectorize_active_layer(tolerance=1.0, auto_subject=True)
    print(f"📊 Result: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to image file")
    args = parser.parse_args()
    
    process_file(args.file)
