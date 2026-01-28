
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ColorQuantizer")

@dataclass
class QuantizedLayer:
    """Represents a single color layer extracted from the image."""
    color_rgb: Tuple[int, int, int]
    color_hex: str
    mask: np.ndarray  # Binary mask (255=foreground, 0=background)
    area_percent: float

class ColorQuantizer:
    """
    Reduces an image to a fixed palette of dominant colors and extracts binary masks.
    Uses MiniBatchKMeans for speed and LAB color space for perceptual accuracy.
    """
    
    def __init__(self, n_colors: int = 8, blur_kernel: int = 3):
        self.n_colors = n_colors
        self.blur_kernel = blur_kernel
        
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

    def quantize(self, image_path: str) -> List[QuantizedLayer]:
        """
        Main pipeline: Load -> Preprocess -> K-Means -> Extract Masks
        """
        # 1. Load Image
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Could not open image: {image_path}")
            
        # 2. Preprocessing
        # Bilateral filter preserves edges better than Gaussian
        img_blur = cv2.bilateralFilter(img_bgr, 9, 75, 75)
        
        # Convert to LAB for better perceptual color clustering
        img_lab = cv2.cvtColor(img_blur, cv2.COLOR_BGR2Lab)
        
        # Reshape for Scikit-Learn (h*w, 3)
        h, w = img_lab.shape[:2]
        image_array = img_lab.reshape((h * w, 3))
        
        # 3. K-Means Clustering
        logger.info(f"Clustering into {self.n_colors} colors...")
        clf = MiniBatchKMeans(n_clusters=self.n_colors, batch_size=4096, n_init=3)
        labels = clf.fit_predict(image_array)
        quantized_centers = clf.cluster_centers_.astype("uint8")
        
        # 4. Extract Layers
        layers = []
        unique_labels, counts = np.unique(labels, return_counts=True)
        total_pixels = h * w
        
        # Sort by luminance (approximation in LAB: L channel is index 0)
        # Note: Center array is (L, A, B)
        sorted_indices = np.argsort(quantized_centers[:, 0])
        
        for i in sorted_indices:
            if i not in unique_labels:
                continue
                
            # Create Mask
            # Reshape labels back to image dimensions
            label_mask = labels.reshape((h, w))
            binary_mask = np.where(label_mask == i, 255, 0).astype("uint8")
            
            # Get Color (Convert back to RGB)
            center_lab = quantized_centers[i].reshape(1, 1, 3)
            center_rgb = cv2.cvtColor(center_lab, cv2.COLOR_Lab2RGB)[0, 0]
            color_tuple = tuple(center_rgb)
            
            # Simple morphological cleanup on mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            cleaned_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
            
            # Calculate area
            count = counts[np.where(unique_labels == i)[0][0]]
            
            layer = QuantizedLayer(
                color_rgb=color_tuple,
                color_hex=self._rgb_to_hex(color_tuple),
                mask=cleaned_mask,
                area_percent=(count / total_pixels) * 100
            )
            layers.append(layer)
            
            logger.info(f"Layer {i}: {layer.color_hex} ({layer.area_percent:.1f}%)")
            
        return layers

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        q = ColorQuantizer(n_colors=5)
        res = q.quantize(sys.argv[1])
        print(f"Quantized into {len(res)} layers.")
