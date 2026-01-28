import cv2
import numpy as np
import sys
import json

class OniLogoTracer:
    def __init__(self):
        # Preset palettes for known entities
        self.palettes = {
            'vegan_v1': {
                'green': {'lower': np.array([35, 50, 50]), 'upper': np.array([85, 255, 255]), 'hex': '#6B8E23'},
                'red': {'lower': np.array([0, 50, 50]), 'upper': np.array([10, 255, 255]), 'hex': '#B22222'},
                'red2': {'lower': np.array([170, 50, 50]), 'upper': np.array([180, 255, 255]), 'hex': '#B22222'}
            }
        }

    def process_image(self, img_path: str, out_path: str, palette_name: str = 'auto', smoothness: float = 0.001, blur: int = 0, upscale: int = 1):
        """
        Ultimate Vectorization Engine V2 (Stroke Quality Focused).
        upscale: Internal processing multiplier.
        blur: If > 0, applies Bilateral Filter (Edge-Preserving) instead of Gaussian.
        """
        print(f"DTO-TRACER: Processing {img_path}...")
        print(f"  > Params: Upscale={upscale}x, Bilateral={blur}, Smoothness={smoothness}")
        
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {img_path}")

        # Store original dims
        orig_h, orig_w = img.shape[:2]

        # 1. SUPER-RESOLUTION UP (Bicubic)
        if upscale > 1:
            print(f"  > Upscaling internally to {img.shape[1]*upscale}x{img.shape[0]*upscale}...")
            img = cv2.resize(img, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)

        # 2. EDGE-PRESERVING FILTER (Bilateral)
        # Replacing simple Blur with Bilateral to keep corners sharp but surfaces smooth
        if blur > 0:
            print(f"  > Applying BilateralFilter (d={blur})...")
            # d=blur, sigmaColor=75, sigmaSpace=75 (standard strong smoothie)
            img = cv2.bilateralFilter(img, blur, 75, 75)

        h, w = img.shape[:2]
        
        # Start SVG - Use ORIGINAL dimensions in header, we will scale points back down
        svg_content = [f'<svg width="{orig_w}" height="{orig_h}" viewBox="0 0 {orig_w} {orig_h}" xmlns="http://www.w3.org/2000/svg">']
        
        if palette_name == 'auto':
            self._process_auto(img, svg_content, smoothness=smoothness, scale_down=upscale)
        else:
            self._process_preset(img, palette_name, svg_content, smoothness=smoothness, scale_down=upscale)

        svg_content.append('</svg>')
        
        with open(out_path, 'w') as f:
            f.write("".join(svg_content))
            
        print(f"DTO-TRACER: Success! Saved to {out_path}")

    def _process_auto(self, img, svg_content, n_colors=5, smoothness=0.001, scale_down=1):
        print("  > Running K-Means...")
        data = img.reshape((-1, 3))
        data = np.float32(data)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        labels = labels.flatten()
        total_pixels = img.shape[0] * img.shape[1]
        
        for i, color in enumerate(centers):
            if np.mean(color) > 240: continue # ignore white

            count = np.sum(labels == i)
            percentage = count / total_pixels
            if percentage < 0.005: continue # Lower threshold (0.5%) to catch accents
                
            mask = (labels == i).reshape(img.shape[:2]).astype(np.uint8) * 255
            
            # Morphological Cleanup
            kernel = np.ones((3,3), np.uint8) # Smaller kernel to preserve sharp corners
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[2], color[1], color[0]) 
            print(f"  > Dominant: {hex_color} ({percentage:.1%})")
            
            self._append_contours_to_svg(mask, hex_color, svg_content, smoothness, scale_down)

    def _process_preset(self, img, palette_name, svg_content, smoothness=0.001, scale_down=1):
        # Stub for preset compatibility
        pass 

    def _append_contours_to_svg(self, mask, color_hex, svg_list, smoothness=0.001, scale_down=1):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            if cv2.contourArea(cnt) < (50 * scale_down): continue 
            
            # RDP Simplification
            epsilon = smoothness * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            if len(approx) < 3: continue
            
            # SCALE BACK DOWN to Original Coords
            # We divide every coordinate by the upscale factor
            points_str = " ".join([f"{p[0][0]/scale_down:.3f},{p[0][1]/scale_down:.3f}" for p in approx])
            
            path_str = f'  <path fill="{color_hex}" stroke="none" d="M{points_str} Z" />\n'
            svg_list.append(path_str)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        tracer = OniLogoTracer()
        img_in = sys.argv[1]
        svg_out = sys.argv[2]
        palette = sys.argv[3] if len(sys.argv) > 3 else 'auto'
        
        smooth = 0.001
        if len(sys.argv) > 4:
            try: smooth = float(sys.argv[4])
            except Exception: pass
            
        blur_val = 0
        if len(sys.argv) > 5:
            try: blur_val = int(sys.argv[5])
            except Exception: pass
            
        upscale_val = 1
        if len(sys.argv) > 6:
            try: upscale_val = int(sys.argv[6])
            except Exception: pass

        tracer.process_image(img_in, svg_out, palette, smoothness=smooth, blur=blur_val, upscale=upscale_val)
    else:
        print("Usage: python oni_logo_tracer.py <input> <output_svg> [palette] [smooth] [blur] [upscale]")
