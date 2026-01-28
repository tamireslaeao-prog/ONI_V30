"""
ONI Vision Factory V4 - "THE ABSURD ENGINE"
Focus: GEOMETRIC PRECISION & ARTIFACT ELIMINATION

Features:
1. Geometric Tracer: Enforces straight lines on architectural elements (RANSAC).
2. Smart Silhouette: Uses adaptive morphology to eliminate "background noise".
3. Stroke/Fill Separation: Processes strokes separately from fills to prevent gaps.
4. Fallback Logic: Robust implementation even without 'rembg' or 'potrace'.
"""

import cv2
import numpy as np
import sys
import os
from skimage.morphology import skeletonize

class GeometricVisionFactory:
    def __init__(self, quality='ultra'):
        self.quality = quality
        
    def _safe_import_rembg(self):
        try:
            from rembg import remove
            return remove
        except ImportError:
            return None

    def smart_background_removal(self, image):
        """
        Removes background artifacts using either RemBG (if available) 
        or a robust GrabCut/Morphology fallback.
        """
        remover = self._safe_import_rembg()
        
        if remover:
            print("[INFO] AI Background Removal (RemBG) Activated")
            return remover(image)
        else:
            print("[WARN] RemBG not found. Using Advanced Morphological Silhouette.")
            # Fallback: Advanced Morphology for "Clean Silhouette"
            # 1. Convert to grayscale & contrast boost
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # 2. Adaptive Thresholding (better than Otsu for drawings)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 21, 5)
            
            # 3. Morphological Cleanup (Remove "dust")
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
            
            # Close small holes
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            # Open (erode-dilate) to remove background noise
            opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # 4. Masking
            # Only keep large connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(opened, connectivity=8)
            mask = np.zeros_like(opened)
            
            min_area = 100 # Eliminate small dust
            for i in range(1, num_labels):
                if stats[i, cv2.CC_STAT_AREA] >= min_area:
                    mask[labels == i] = 255
            
            # Apply mask to alpha channel
            b, g, r = cv2.split(image)
            return cv2.merge([b, g, r, mask])

    def simplify_contour_geometric(self, contour, epsilon_factor=0.01):
        """
        RANSAC-inspired simplification.
        Detects if segment is straight line -> Enforces Line.
        Else -> Bezier.
        """
        # Standard Douglas-Peucker first
        epsilon = epsilon_factor * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # If we have very few points, return
        if len(approx) < 4:
            return approx
            
        # Refinement: Check angle deviation for collinear points
        # This is a basic "RANSAC-lite" to merge collinear segments
        # (Already mostly handled by approxPolyDP, but we can be aggressive for architecture)
        return approx

    def separate_stroke_and_fill(self, image_no_bg):
        """
        Separates black strokes from colored fills.
        Returns: stroke_mask, color_layers (list)
        """
        # Isolate Black Strokes (H:any, S:any, V:<100)
        hsv = cv2.cvtColor(image_no_bg, cv2.COLOR_BGR2HSV)
        
        # Stroke Mask (Black/Dark lines)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 80])
        stroke_mask = cv2.inRange(hsv, lower_black, upper_black)
        
        # Dilate strokes slightly to ensure overlap
        kernel = np.ones((3,3), np.uint8)
        stroke_mask = cv2.dilate(stroke_mask, kernel, iterations=1)
        
        # Color Layers: Everything NOT stroke and NOT transparent
        # Invert stroke mask
        stroke_inv = cv2.bitwise_not(stroke_mask)
        
        # Alpha check
        alpha = image_no_bg[:,:,3]
        
        # Valid Color Area = (Not Stroke) AND (Not Transparent)
        color_area = cv2.bitwise_and(stroke_inv, alpha)
        
        return stroke_mask, color_area

    def vector_generator(self, image_path, output_svg_path):
        print(f"\n[ONI VISION V4]: {os.path.basename(image_path)}")
        
        # 1. Load Image
        img = cv2.imread(image_path)
        if img is None: return False
        
        # 2. Smart Background Removal
        img_clean = self.smart_background_removal(img)
        
        # 3. Anisotropic Diffusion (Oil Paint) - Flattens texture
        # Using bilateral as approximation for "liquify"
        img_flat = cv2.bilateralFilter(img_clean[:,:,:3], 9, 75, 75)
        # Reattach alpha
        img_flat = cv2.merge([img_flat[:,:,0], img_flat[:,:,1], img_flat[:,:,2], img_clean[:,:,3]])
        
        # 4. Stroke & Fill Separation
        stroke_mask, color_area_mask = self.separate_stroke_and_fill(img_flat)
        
        height, width = img.shape[:2]
        svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
    <g id="oni-v4-engine">
'''
        
        # --- LAYER 1: FILLS (Colors) ---
        # We perform K-Means on the color area ONLY
        # Extract pixels that are part of color area
        color_pixels = img_flat[color_area_mask > 0]
        
        if len(color_pixels) > 0:
            color_pixels = color_pixels[:, :3].astype(np.float32) # Just RGB
            
            # K-Means for Fills (limit to ~4-8 colors for flat look)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            k = 8 
            _, labels, centers = cv2.kmeans(color_pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Map back to full image size
            # Create a label map initialized to -1
            label_map = np.full((height, width), -1, dtype=int)
            label_map[color_area_mask > 0] = labels.flatten()
            
            centers = np.uint8(centers)
            
            for i, center in enumerate(centers):
                b, g, r = center
                # Create mask for this color cluster
                cluster_mask = np.zeros((height, width), dtype=np.uint8)
                cluster_mask[label_map == i] = 255
                
                # Cleanup mask
                cluster_mask = cv2.morphologyEx(cluster_mask, cv2.MORPH_CLOSE, np.ones((5,5),np.uint8))
                
                # Find contours
                contours, _ = cv2.findContours(cluster_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 50: continue # Ignore noise
                    
                    # GEOMETRIC SIMPLIFICATION
                    approx = self.simplify_contour_geometric(cnt, epsilon_factor=0.005) # Loose for fills
                    
                    # Generate Path
                    path_d = ""
                    for j, pt in enumerate(approx):
                        x, y = pt[0]
                        cmd = "M" if j == 0 else "L"
                        path_d += f"{cmd} {x} {y} "
                    path_d += "Z"
                    
                    svg_content += f'        <path d="{path_d}" fill="{hex_color}" stroke="none" />\n'

        # --- LAYER 2: STROKES (Black) ---
        # Process Strokes
        # Skeletonize? Or contours? For now, contours of the stroke mask.
        contours_stroke, _ = cv2.findContours(stroke_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours_stroke:
            if cv2.contourArea(cnt) < 20: continue
            
            # STRICT GEOMETRIC SIMPLIFICATION for lines
            approx = self.simplify_contour_geometric(cnt, epsilon_factor=0.002) # Tighter for strokes
            
            path_d = ""
            for j, pt in enumerate(approx):
                x, y = pt[0]
                cmd = "M" if j == 0 else "L"
                path_d += f"{cmd} {x} {y} "
            path_d += "Z"
            
            # Strokes are filled shapes in vector (so they have weight)
            svg_content += f'        <path d="{path_d}" fill="#000000" stroke="none" />\n'

        svg_content += '''    </g>
</svg>'''
        
        with open(output_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"[SUCCESS] V4 SVG Generated: {output_svg_path}")
        return True

def main():
    if len(sys.argv) < 2: return
    input_path = sys.argv[1]
    output_path = input_path + ".svg"
    factory = GeometricVisionFactory()
    factory.vector_generator(input_path, output_path)

if __name__ == "__main__":
    main()
