
import cv2
import numpy as np
import logging
from typing import List, Tuple

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TraceReactor")

class TraceReactor:
    """
    Converts binary masks into vector paths (SVG d-strings).
    Uses OpenCV findContours and Ramer-Douglas-Peucker simplification.
    """
    
    def __init__(self, epsilon_factor: float = 0.001):
        """
        Args:
            epsilon_factor: Multiplier for approxPolyDP (lower = more detail, higher = smoother/less points).
                            Standard range 0.001 - 0.005.
        """
        self.epsilon_factor = epsilon_factor

    def mask_to_paths(self, mask: np.ndarray) -> List[str]:
        """
        Extracts SVG path strings from a binary mask.
        Returns a list of 'd' attributes (e.g., "M 10 10 L 20 20 Z").
        """
        # Ensure mask is binary uint8
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)
            
        # Find contours
        # RETR_CCOMP retrieves both outer and inner contours (holes)
        # CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
            
        svg_paths = []
        
        # Iterate through contours
        for i, contour in enumerate(contours):
            # Simplify contour
            epsilon = self.epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) < 3:
                continue
                
            # Convert to SVG path string
            # approx has shape (N, 1, 2) -> [[x,y], [x,y]...]
            points = approx[:, 0, :]
            
            # Build path string: M x0 y0 L x1 y1 L ... Z
            # Using join for performance
            path_data = ["M", str(points[0][0]), str(points[0][1])]
            
            for p in points[1:]:
                path_data.extend(["L", str(p[0]), str(p[1])])
                
            path_data.append("Z")
            svg_paths.append(" ".join(path_data))
            
        logger.info(f"Extracted {len(svg_paths)} paths from mask.")
        return svg_paths

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        mask = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            tr = TraceReactor()
            paths = tr.mask_to_paths(mask)
            print(f"Generated {len(paths)} SVG paths.")
            if paths:
                print("First path sample:", paths[0][:50] + "...")
