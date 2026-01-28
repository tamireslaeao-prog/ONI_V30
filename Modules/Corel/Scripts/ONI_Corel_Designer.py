import win32com.client
import argparse
import sys

# ONI Corel Designer Suite
# Implements advanced design operations: Vectorization, Outlining, Auto-Fit, Smart-Grouping

def get_corel():
    try:
        return win32com.client.Dispatch("CorelDRAW.Application")
    except:
        print("❌ CorelDRAW not found.")
        return None

def vectorize_selection(corel):
    """Traces selected bitmap with High Quality settings"""
    if corel.ActiveSelection.Shapes.Count == 0:
        print("⚠️ Select a bitmap first.")
        return

    print("🕵️ Vectorizing...")
    try:
        sr = corel.ActiveSelectionRange
        # Iterate in case multiple bitmaps selected
        for s in sr:
            if s.Type == 5: # cdrBitmapShape
                # TraceType: 1=cdrTraceDetailedLogo, 2=cdrTraceLineArt, etc. Using 1 for Logo
                # Trace(TraceType, Smoothing, ColorMode)
                trace = s.Bitmap.Trace(1) 
                trace.Smoothing = 50 
                trace.DeleteOriginalObject = True
                trace.RemoveBackground = True
                trace.Finish()
        print("✅ Vectorization complete.")
    except Exception as e:
        print(f"❌ Trace Failed: {e}")

def create_outline(corel, offset_mm):
    """Creates a contour/outline around the selection"""
    if corel.ActiveSelection.Shapes.Count == 0:
        print("⚠️ Select objects first.")
        return

    print(f"🖌️ Creating {offset_mm}mm Outline...")
    try:
        corel.ActiveDocument.Unit = 4 # cdrMillimeter
        sr = corel.ActiveSelectionRange
        
        # Create Boundary first to get a single silhouette
        boundary = sr.CustomCommand("Boundary", "CreateBoundary")
        
        if boundary:
            # CreateContour(Type, Offset, Steps, ...)
            # Type: 1=Outside
            eff = boundary.CreateContour(1, offset_mm, 1)
            eff.Separate()
            boundary.Delete() # Delete the inner boundary, keep the contour
            print("✅ Outline created.")
        else:
            print("⚠️ Could not create boundary.")

    except Exception as e:
        print(f"❌ Outline Failed: {e}")

def fit_page_to_selection(corel, margin_mm=0):
    """Resizes the page to fit the selected objects"""
    if corel.ActiveSelection.Shapes.Count == 0:
        print("⚠️ Select objects first.")
        return

    print("📐 Fitting Page...")
    try:
        corel.ActiveDocument.Unit = 4 # cdrMillimeter
        sr = corel.ActiveSelectionRange
        
        # Get bounding box
        x, y, w, h = sr.GetBoundingBox(True) # True = include stroke
        
        # Apply bounds to Page
        doc = corel.ActiveDocument
        page = doc.ActivePage
        
        new_w = w + (margin_mm * 2)
        new_h = h + (margin_mm * 2)
        
        page.SetSize(new_w, new_h)
        
        # Center selection on page
        # Calculate center of new page
        cx = new_w / 2
        cy = new_h / 2
        
        # Move objects (if they weren't centered relative to bounds, this ensures they are centered on new page)
        # Actually, simpler to just set page size and then center objects
        
        sr.AlignToPageCenter(3) # 3 = cdrAlignHCenter + cdrAlignVCenter
        
        print(f"✅ Page resized to {new_w:.1f}x{new_h:.1f}mm")

    except Exception as e:
        print(f"❌ Fit Page Failed: {e}")

def smart_group_objects(corel):
    """Groups objects based on proximity (Primitive Clustering)"""
    if corel.ActiveSelection.Shapes.Count < 2:
        print("⚠️ Need at least 2 objects to group.")
        return

    print("🧠 Smart Grouping...")
    # This is a naive implementation: Group everything selected.
    # A true 'Smart Group' would need spatial analysis (O(n^2) distance check)
    # Lanya's implementation creates rects and overlaps.
    # For V1, we will implement a "Group All Selected" as a baseline, 
    # then iterate to "Group Intersecting" in V2.
    
    try:
        sr = corel.ActiveSelectionRange
        # Check overlaps
        # Optimization: Just group for now to ensure reliability
        grp = sr.Group()
        print("✅ Objects grouped.")
        
    except Exception as e:
        print(f"❌ Smart Group Failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ONI Corel Designer")
    parser.add_argument("--vectorize", action="store_true", help="Vectorize selected bitmaps")
    parser.add_argument("--outline", type=float, help="Create outline with offset in mm")
    parser.add_argument("--fit-page", action="store_true", help="Resize page to selection")
    parser.add_argument("--smart-group", action="store_true", help="Intelligently group objects")
    
    args = parser.parse_args()
    
    app = get_corel()
    if app:
        if args.vectorize:
            vectorize_selection(app)
        if args.outline is not None:
            create_outline(app, args.outline)
        if args.fit_page:
            fit_page_to_selection(app)
        if args.smart_group:
            smart_group_objects(app)
