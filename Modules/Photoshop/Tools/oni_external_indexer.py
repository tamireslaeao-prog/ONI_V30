import os
import json
import time

TARGET_ROOT = r"D:\DESIGN"
OUTPUT_FILE = r"c:\Users\user\Desktop\ONIV25\memo\EXTERNAL_ASSET_CATALOG.json"

catalog = {
    "metadata": {
        "scanned_at": time.ctime(),
        "root": TARGET_ROOT
    },
    "psd_sources": [],
    "styles": [],
    "brushes": [],
    "fonts": [],
    "vectors": []
}

def scan_directory(path, extensions):
    results = []
    try:
        if not os.path.exists(path):
            return []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    full_path = os.path.join(root, file)
                    results.append({
                        "name": file,
                        "path": full_path,
                        "size_mb": round(os.path.getsize(full_path) / (1024*1024), 2)
                    })
    except Exception as e:
        print(f"Error scanning {path}: {e}")
    return results

print("🚀 Starting Deep Scan of D:/DESIGN...")

# 1. PSD Sources
print("Scanning PSD Sources...")
catalog["psd_sources"] = scan_directory(os.path.join(TARGET_ROOT, "psd_sources"), [".psd", ".psb"])

# 2. Styles & Brushes
print("Scanning Extras...")
catalog["styles"] = scan_directory(os.path.join(TARGET_ROOT, "photoshop_extras"), [".asl"])
catalog["brushes"] = scan_directory(os.path.join(TARGET_ROOT, "photoshop_extras"), [".abr"])

# 3. Fonts
print("Scanning Fonts...")
catalog["fonts"] = scan_directory(os.path.join(TARGET_ROOT, "fonts"), [".ttf", ".otf"])

# 4. Vectors
print("Scanning Vectors...")
catalog["vectors"] = scan_directory(os.path.join(TARGET_ROOT, "universal_vectors"), [".ai", ".eps", ".svg"])

# Save
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"✅ Catalog Saved: {OUTPUT_FILE}")
print(f"   - PSDs: {len(catalog['psd_sources'])}")
print(f"   - Styles: {len(catalog['styles'])}")
print(f"   - Fonts: {len(catalog['fonts'])}")
