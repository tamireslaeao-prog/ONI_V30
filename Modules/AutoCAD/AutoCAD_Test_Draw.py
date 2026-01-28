"""
AutoCAD Test Draw - Validation Script
Verifies AutoCAD Bridge functionality

Usage:
    python AutoCAD_Test_Draw.py
"""

from ONI_AutoCAD_Bridge import AutoCADBridge
import sys


def test_basic_drawing():
    """Test basic drawing operations."""
    print("=" * 60)
    print("ONI AutoCAD Bridge - Test Suite")
    print("=" * 60)
    
    cad = AutoCADBridge()
    
    # Test 1: Connection
    print("\n[TEST 1] Connecting to AutoCAD...")
    if not cad.connect():
        print("[FAIL] Could not connect to AutoCAD")
        return False
    print("[PASS] Connected successfully")
    
    # Test 2: Get Info
    print("\n[TEST 2] Getting AutoCAD info...")
    info = cad.get_info()
    print(f"  Version: {info.get('version', 'Unknown')}")
    print(f"  Document: {info.get('document', 'Unknown')}")
    print("[PASS] Info retrieved")
    
    # Test 3: Draw Line
    print("\n[TEST 3] Drawing line...")
    try:
        line = cad.draw_line(0, 0, 100, 0)
        print(f"  Line created: {line}")
        print("[PASS] Line drawn")
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    
    # Test 4: Draw Circle
    print("\n[TEST 4] Drawing circle...")
    try:
        circle = cad.draw_circle(50, 50, 25)
        print(f"  Circle created: {circle}")
        print("[PASS] Circle drawn")
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    
    # Test 5: Draw Rectangle
    print("\n[TEST 5] Drawing rectangle...")
    try:
        rect = cad.draw_rectangle(0, 80, 100, 40)
        print(f"  Rectangle created: {rect}")
        print("[PASS] Rectangle drawn")
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    
    # Test 6: Add Text
    print("\n[TEST 6] Adding text...")
    try:
        text = cad.add_text("ONI AutoCAD Test", 0, 130, 5)
        print(f"  Text created: {text}")
        print("[PASS] Text added")
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    
    # Test 7: Layer Management
    print("\n[TEST 7] Creating layer...")
    try:
        result = cad.create_layer("ONI_TEST", color=1)
        if result:
            print("[PASS] Layer created")
        else:
            print("[WARN] Layer may already exist")
    except Exception as e:
        print(f"[FAIL] {e}")
    
    # Test 8: Zoom Extents
    print("\n[TEST 8] Zooming to extents...")
    try:
        cad.zoom_extents()
        print("[PASS] Zoom applied")
    except Exception as e:
        print(f"[FAIL] {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE - Check AutoCAD window for results")
    print("=" * 60)
    print("\nExpected elements:")
    print("  - Horizontal line at Y=0")
    print("  - Circle at (50, 50) with radius 25")
    print("  - Rectangle at (0, 80) with size 100x40")
    print("  - Text 'ONI AutoCAD Test' at (0, 130)")
    print("  - Layer 'ONI_TEST' in red (color 1)")
    
    return True


def test_polyline():
    """Test polyline drawing."""
    print("\n[BONUS TEST] Drawing polyline...")
    cad = AutoCADBridge()
    
    if not cad.connect(create_new_doc=False):
        print("[SKIP] Could not connect")
        return
    
    # Draw a star-like polyline
    points = [
        150, 0,
        175, 50,
        225, 50,
        185, 80,
        200, 130,
        150, 100,
        100, 130,
        115, 80,
        75, 50,
        125, 50
    ]
    
    try:
        pline = cad.draw_polyline(points, closed=True)
        print(f"  Polyline created: {pline}")
        print("[PASS] Polyline drawn")
        cad.zoom_extents()
    except Exception as e:
        print(f"[FAIL] {e}")


if __name__ == "__main__":
    try:
        success = test_basic_drawing()
        if success:
            test_polyline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        sys.exit(1)
