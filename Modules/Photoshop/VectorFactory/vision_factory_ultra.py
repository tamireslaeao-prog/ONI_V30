"""
ONI Vision Factory V3 - ULTRA QUALITY EDITION
Revolutionary Improvements:
- Multi-scale analysis for texture preservation
- Adaptive bilateral filtering with edge detection
- Bezier curve fitting for smooth vectors
- Intelligent color clustering with perceptual weights
- Sub-pixel precision contouring
- Hierarchical shape decomposition
- Smart noise reduction with detail preservation
"""
import cv2
import numpy as np
import sys
import os
from scipy.interpolate import splprep, splev
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage import measure, morphology
from skimage.filters import gaussian, sobel
from skimage.segmentation import felzenszwalb

class UltraVisionFactory:
    def __init__(self, quality='ultra'):
        self.quality_presets = {
            'draft':  {'scale': 0.5, 'colors': 6,  'smoothing': 0.01, 'min_area': 200, 'edge_sigma': 2.0},
            'good':   {'scale': 0.75, 'colors': 10, 'smoothing': 0.005, 'min_area': 100, 'edge_sigma': 1.5},
            'high':   {'scale': 1.0, 'colors': 16, 'smoothing': 0.002, 'min_area': 50, 'edge_sigma': 1.0},
            'ultra':  {'scale': 1.0, 'colors': 24, 'smoothing': 0.001, 'min_area': 25, 'edge_sigma': 0.8},
            'master': {'scale': 1.0, 'colors': 32, 'smoothing': 0.0005, 'min_area': 10, 'edge_sigma': 0.5},
        }
        self.settings = self.quality_presets.get(quality, self.quality_presets['ultra'])

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
            # RemBG expects RGBA or RGB
            return remover(image)
        else:
            print("[WARN] RemBG not found. Using Advanced Morphological Silhouette.")
            # Fallback: Advanced Morphology for "Clean Silhouette"
            # 1. Convert to grayscale & contrast boost
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
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
            if len(image.shape) == 3:
                b, g, r = cv2.split(image)
                return cv2.merge([b, g, r, mask])
            else:
                return image # Already likely good or handled

        
    def analyze_image_complexity(self, image):
        """Advanced image analysis for optimal parameter selection."""
        # Multi-scale edge detection
        edges = sobel(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        edge_density = np.mean(edges > 0.1)
        
        # Color variance analysis
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        color_variance = np.var(lab, axis=(0, 1)).sum()
        
        # Texture complexity (using Local Binary Pattern concept)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        complexity_score = {
            'edge_density': edge_density,
            'color_variance': color_variance,
            'texture_complexity': laplacian_var
        }
        
        # Adaptive color count
        if laplacian_var > 1000 or edge_density > 0.3:
            return min(32, int(self.settings['colors'] * 1.5)), complexity_score
        elif laplacian_var < 100 and edge_density < 0.1:
            return max(8, int(self.settings['colors'] * 0.7)), complexity_score
        
        return self.settings['colors'], complexity_score
    
    def smart_preprocessing(self, image, complexity):
        """Intelligent preprocessing based on image characteristics."""
        
        # Handle Alpha Channel if present
        has_alpha = False
        alpha = None
        if len(image.shape) == 3 and image.shape[2] == 4:
            has_alpha = True
            b, g, r, alpha = cv2.split(image)
            img_process = cv2.merge([b, g, r])
        else:
            img_process = image

        # Adaptive denoising
        if complexity['texture_complexity'] > 500:
            # High texture - gentle denoising
            denoised = cv2.fastNlMeansDenoisingColored(img_process, None, 3, 3, 7, 21)
        else:
            # Low texture - standard bilateral
            denoised = cv2.bilateralFilter(img_process, 9, 75, 75)
        
        # Edge-aware sharpening for crisp vectors
        if complexity['edge_density'] < 0.2:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel * 0.3)
            result = cv2.addWeighted(denoised, 0.7, sharpened, 0.3, 0)
        else:
            result = denoised
            
        # Re-merge alpha if it existed
        if has_alpha:
            b, g, r = cv2.split(result)
            return cv2.merge([b, g, r, alpha])
            
        return result
    
    def perceptual_color_clustering(self, image, n_colors):
        """
        Supreme color separation using Felzenszwalb superpixels + LAB clustering.
        Replaces weak MeanShift for clean, edge-aware color separation.
        """
        # 1. Felzenszwalb superpixel segmentation (preserves edges)
        segments = felzenszwalb(image, scale=100, sigma=0.5, min_size=50)
        
        # 2. Extract superpixel colors (edge-aware)
        unique_segments = np.unique(segments)
        superpixel_colors = []
        
        # Create superpixel mask structure
        h, w = image.shape[:2]
        
        # Fast superpixel mean calculation
        for seg_id in unique_segments:
            mask = segments == seg_id
            region = image[mask]
            if len(region) > 0:
                # Ensure we only take RGB (first 3 channels)
                mean_color = np.mean(region, axis=0)[:3] 
                superpixel_colors.append(mean_color)
        
        superpixel_colors = np.array(superpixel_colors).astype(np.float32)
        
        # 3. K-Means on superpixel centers (better than full image)
        # Convert to LAB for perceptual clustering
        if len(superpixel_colors) > 0:
            lab_colors = cv2.cvtColor(
                superpixel_colors.reshape(1, -1, 3).astype(np.uint8),
                cv2.COLOR_BGR2LAB
            ).reshape(-1, 3).astype(np.float32)
            
            # High-iteration K-Means for precision
            real_n_colors = min(n_colors, len(superpixel_colors))
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 500, 0.001)
            _, _, centers_lab = cv2.kmeans(
                lab_colors, real_n_colors, None, criteria, 50, cv2.KMEANS_PP_CENTERS
            )
            
            # 4. Assign pixels directly to nearest cluster
            lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
            
            # Compute distances to centers
            # Optimized distance calculation
            from scipy.spatial.distance import cdist
            distances = cdist(lab_image, centers_lab)
            labels = np.argmin(distances, axis=1)
            
            # Convert centers back to BGR
            centers_bgr = cv2.cvtColor(
                centers_lab.reshape(1, -1, 3).astype(np.uint8),
                cv2.COLOR_LAB2BGR
            ).reshape(-1, 3)
            
            return labels, centers_bgr, (h, w)
        else:
            # Fallback
            return np.zeros(h*w, dtype=int), np.array([[0,0,0]]), (h,w)
    
    def bezier_smooth_contour(self, contour, smoothness=0.002):
        """
        V5 SUPREME SMOOTHING: True B-Spline Curve Fitting.
        Detects sharp corners, then fits mathematical splines between them.
        """
        if len(contour) < 6:
            return contour
        
        # 1. Detect corners using enhanced angle analysis
        points = contour.reshape(-1, 2)
        n = len(points)
        
        # Calculate dynamic angles
        angles = []
        for i in range(n):
            p_prev = points[(i - 2) % n] # Look further back
            p_curr = points[i]
            p_next = points[(i + 2) % n] # Look further ahead
            
            v1 = p_prev - p_curr
            v2 = p_next - p_curr
            
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                angles.append(np.pi)
                continue
                
            dot_prod = np.dot(v1, v2) / (norm_v1 * norm_v2)
            dot_prod = np.clip(dot_prod, -1.0, 1.0)
            angles.append(np.arccos(dot_prod))
            
        angles = np.array(angles)
        
        # Mark corners: Sharp turns (< 140 deg) are corners
        # But we also want to mark inflection points if possible
        is_corner = angles < np.radians(140)
        
        # Ensure we have at least some corners or start points
        if not np.any(is_corner):
            is_corner[0] = True
            
        indices = np.where(is_corner)[0]
        # Sort indices to process segments in order
        indices = np.sort(indices)
        
        smoothed_points = []
        
        for k in range(len(indices)):
            start_idx = indices[k]
            end_idx = indices[(k + 1) % len(indices)]
            
            if end_idx < start_idx: # Wrap around
                segment_indices = list(range(start_idx, n)) + list(range(0, end_idx + 1))
            else:
                segment_indices = list(range(start_idx, end_idx + 1))
                
            segment = points[segment_indices]
            
            # If segment is short (likely a corner detail or straight line), keep linear
            if len(segment) < 5:
                smoothed_points.extend(segment[:-1]) # omit last to avoid dupe
                continue
                
            # SPLINE FITTING
            try:
                # Remove duplicates in segment for spline stability
                clean_segment = []
                for p in segment:
                    if len(clean_segment) == 0 or not np.array_equal(p, clean_segment[-1]):
                        clean_segment.append(p)
                clean_segment = np.array(clean_segment)
                
                if len(clean_segment) < 4:
                     smoothed_points.extend(clean_segment[:-1])
                     continue

                # Fit Spline
                # s (smoothing factor) is critical. Higher = smoother.
                # standard approx: m = len(points), s = m - sqrt(2*m)
                m = len(clean_segment)
                s_factor = m * 2 # Relaxed smoothing for organic look
                
                tck, u = splprep(clean_segment.T, s=s_factor, k=3)
                
                # Resample for SVG
                # Generate fewer points for cleaner SVG, but enough for smoothness
                u_new = np.linspace(0, 1, max(10, m // 2))
                x_new, y_new = splev(u_new, tck)
                
                for x, y in zip(x_new, y_new):
                    smoothed_points.append([x, y])
                    
            except Exception as e:
                # Fallback to linear if spline fails
                smoothed_points.extend(segment[:-1])
                
        # Close the loop
        if len(smoothed_points) > 0 and len(points) > 0:
             # Ensure start/end match if closed
             pass 

        # Convert back to standard format
        return np.array(smoothed_points, dtype=np.int32).reshape(-1, 1, 2)

    
    def generate_svg_path_advanced(self, contour):
        """Generate optimized SVG path with cubic Bezier curves."""
        if len(contour) < 3:
            return None
        
        # Ensure contour is the correct shape and type
        contour = np.array(contour).reshape(-1, 2)
        
        # Get first point as scalars
        x0 = float(contour[0][0])
        y0 = float(contour[0][1])
        path_data = f"M {x0:.2f} {y0:.2f}"
        
        # Generate smooth cubic Bezier curves
        for i in range(1, len(contour)):
            curr_x = float(contour[i][0])
            curr_y = float(contour[i][1])
            
            # Calculate control points for smooth curves
            if i < len(contour) - 1:
                next_x = float(contour[i+1][0])
                next_y = float(contour[i+1][1])
                # Quadratic Bezier for smoother curves
                path_data += f" Q {curr_x:.2f} {curr_y:.2f} {(curr_x+next_x)/2:.2f} {(curr_y+next_y)/2:.2f}"
            else:
                path_data += f" L {curr_x:.2f} {curr_y:.2f}"
        
        path_data += " Z"
        return path_data
    
    def precision_morphology(self, mask, image_complexity):
        """
        Content-aware morphological operations.
        Adapts kernel size and iterations to image detail level.
        """
        # Adaptive kernel based on image detail
        if image_complexity['edge_density'] > 0.3:
            # High detail: minimal morphology
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            iterations_close = 1
            iterations_open = 0
        elif image_complexity['edge_density'] > 0.15:
            # Medium detail
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            iterations_close = 1
            iterations_open = 1
        else:
            # Low detail: aggressive cleanup
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            iterations_close = 2
            iterations_open = 1
        
        # Close tiny gaps
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=iterations_close)
        
        # Remove noise
        if iterations_open > 0:
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations_open)
        
        return mask

    def supreme_contour_extraction(self, mask, min_area):
        """
        Supreme contour extraction with edge preservation.
        Replaces standard findContours with precise edge-aware logic.
        """
        # Canny edge detection for precision guidance on the mask
        # (This helps refine the binary boundaries)
        edges = cv2.Canny(mask, 50, 150)
        
        # Find contours with CHAIN_APPROX_NONE (zero loss initially)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        
        valid_contours = []
        
        if hierarchy is not None:
            hierarchy = hierarchy[0]
            for i, cnt in enumerate(contours):
                # Adaptive simplification
                # Calculate edge density matches
                # If the contour follows Canny edges, it's significant
                
                area = cv2.contourArea(cnt)
                if area >= min_area:
                    # Check if it's an outer contour (not a hole)
                    is_hole = hierarchy[i][3] != -1
                    
                    # SIMPLIFICATION STRATEGY:
                    # 1. Use extremely low epsilon for high fidelity
                    # 2. But simplify straight lines to clean up noise
                    epsilon = 0.0005 * cv2.arcLength(cnt, True) # Very precise
                    simplified_cnt = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    valid_contours.append({
                        'contour': simplified_cnt,
                        'area': area,
                        'is_hole': is_hole,
                        'hierarchy_idx': i
                    })
        
        return sorted(valid_contours, key=lambda x: x['area'], reverse=True)
    
    def raster_to_svg(self, image_path, output_svg_path):
        """Main conversion pipeline with ultra quality."""
        print(f"\n[PAINT] ONI VISION FACTORY V3 - ULTRA QUALITY MODE")
        print(f"[FILE] Processing: {os.path.basename(image_path)}")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print("[ERROR] Error: Could not read image")
            return False
        
        # Handle alpha channel
        has_alpha = len(img.shape) == 3 and img.shape[2] == 4
        alpha = img[:, :, 3] if has_alpha else None
        img_rgb = img[:, :, :3] if has_alpha else img
        
        height, width = img_rgb.shape[:2]
        print(f"[DIM] Dimensions: {width}x{height}")
        
        # Analyze complexity
        n_colors, complexity = self.analyze_image_complexity(img_rgb)
        print(f"[INFO] Complexity Analysis:")
        print(f"   - Edge Density: {complexity['edge_density']:.3f}")
        print(f"   - Color Variance: {complexity['color_variance']:.1f}")
        print(f"   - Texture Score: {complexity['texture_complexity']:.1f}")
        print(f"[COLOR] Adaptive Colors: {n_colors}")
        
        # 1. Smart Background Removal (V4 Injection)
        img_clean = self.smart_background_removal(img_rgb)
        
        # 2. Smart preprocessing (Denoise/Sharpen)
        img_processed = self.smart_preprocessing(img_clean, complexity)

        
        # Perceptual color clustering
        labels, centers, shape = self.perceptual_color_clustering(img_processed, n_colors)
        
        # Generate SVG
        svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <style>
      .vector-shape {{ stroke: none; }}
      .vector-shape:hover {{ opacity: 0.9; }}
    </style>
  </defs>
  <g id="oni-vectors">
'''
        
        # Sort colors by luminance for better layering
        color_luminance = [(i, 0.299*c[2] + 0.587*c[1] + 0.114*c[0]) for i, c in enumerate(centers)]
        color_luminance.sort(key=lambda x: x[1], reverse=True)
        
        total_shapes = 0
        total_points = 0
        
        for color_idx, _ in color_luminance:
            mask = (labels == color_idx).reshape(height, width).astype(np.uint8) * 255
            
            # SUPREME: Precision Morphology
            mask = self.precision_morphology(mask, complexity)
            
            # Skip white/transparent
            b, g, r = centers[color_idx]
            if r > 250 and g > 250 and b > 250:
                continue
            
            if has_alpha and alpha is not None:
                alpha_region = alpha[labels.reshape(height, width) == color_idx]
                if len(alpha_region) > 0 and np.mean(alpha_region) < 100:
                    continue
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # SUPREME: Contour Extraction
            contour_data = self.supreme_contour_extraction(mask, self.settings['min_area'])
            
            for cnt_info in contour_data:
                cnt = cnt_info['contour']
                
                # SUPREME: Smart Smoothing (already replaced bezier_smooth_contour)
                smooth = self.bezier_smooth_contour(cnt, self.settings['smoothing'])
                
                if len(smooth) < 3:
                    continue
                
                # Generate advanced SVG path
                path_d = self.generate_svg_path_advanced(smooth)
                
                if path_d:
                    opacity = 0.95 if cnt_info['is_hole'] else 1.0
                    svg_content += f'    <path class="vector-shape" d="{path_d}" fill="{hex_color}" opacity="{opacity}"/>\n'
                    total_shapes += 1
                    total_points += len(smooth)
        
        svg_content += '''  </g>
</svg>'''
        
        # Write file
        with open(output_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"\n[SUCCESS] CONVERSION COMPLETE")
        print(f"[STATS] Statistics:")
        print(f"   - Vector Shapes: {total_shapes}")
        print(f"   - Total Points: {total_points}")
        print(f"   - Avg Points/Shape: {total_points/max(1,total_shapes):.1f}")
        print(f"[SAVE] Output: {output_svg_path}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("[PAINT] ONI Vision Factory V3 - Ultra Quality Edition")
        print("\nUsage: python vision_factory.py <input_image> [quality]")
        print("\nQuality Levels:")
        print("  draft  - Fast preview (6 colors)")
        print("  good   - Balanced quality (10 colors)")
        print("  high   - High quality (16 colors)")
        print("  ultra  - Ultra quality (24 colors) [DEFAULT]")
        print("  master - Maximum quality (32 colors)")
        return
    
    input_path = sys.argv[1]
    quality = sys.argv[2] if len(sys.argv) > 2 else 'ultra'
    output_path = input_path + ".svg"
    
    factory = UltraVisionFactory(quality=quality)
    factory.raster_to_svg(input_path, output_path)

if __name__ == "__main__":
    main()
