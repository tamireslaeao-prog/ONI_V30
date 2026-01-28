import sys
import os

# Add project root to path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.photoshop.composer_service import PhotoshopComposer

def test_vectorizer():
    print("🧪 Starting Vectorizer Integration Test...")
    
    composer = PhotoshopComposer()
    composer._ensure_connection()
    
    if not composer.app:
        print("❌ Could not connect to Photoshop. Is it open?")
        return

    # Create a test document if none exists
    if composer.app.Documents.Count == 0:
        print("📝 Creating Test Document...")
        composer.app.Documents.Add(500, 500, 72, "Vector_Test", 2, 1, 1) # Mode 2=RGB

    # Create a test raster layer (Circle)
    print("🎨 Creating Raster Circle...")
    jsx_create = """
    var doc = app.activeDocument;
    var layer = doc.artLayers.add();
    layer.name = "Raster_Circle";
    
    // Select Circle
    var selRegion = Array(Array(100,100), Array(400,100), Array(400,400), Array(100,400));
    doc.selection.select(selRegion);
    
    // Fill Red
    var color = new SolidColor(); color.rgb.red=255; color.rgb.green=0; color.rgb.blue=0;
    doc.selection.fill(color);
    doc.selection.deselect();
    """
    composer.app.DoJavaScript(jsx_create)

    # TEST VECTORIZATION
    print("🚀 Invoking Vectorize Service...")
    result = composer.vectorize_active_layer(tolerance=1.5)
    print(f"📊 Service Result: {result}")

    # Verify
    verify_jsx = """
    var doc = app.activeDocument;
    var l = doc.activeLayer;
    if (l.name.indexOf("VECTOR_") != -1 && l.kind == LayerKind.SOLIDFILL) {
        "Verified";
    } else {
        "Failed: " + l.name + " (" + l.kind + ")";
    }
    """
    verification = composer.app.DoJavaScript(verify_jsx)
    
    if verification == "Verified":
        print("✅ TEST PASSED: Vector layer created and verified.")
    else:
        print(f"❌ TEST FAILED: {verification}")

if __name__ == "__main__":
    test_vectorizer()
