
import os
import sys
import logging
import cv2
from pathlib import Path

# Add project root to path if needed
current_dir = Path(os.getcwd())
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from Modules.Universal_Vectorizer.quantizer import ColorQuantizer
from Modules.Universal_Vectorizer.trace_reactor import TraceReactor
from Modules.Universal_Vectorizer.svg_composer import SVGComposer

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VectorFactoryV2")

class VectorizerService:
    """
    Orchestrator for the Universal Vectorizer pipeline.
    """
    
    def __init__(self):
        self.quantizer = ColorQuantizer(n_colors=8)
        self.tracer = TraceReactor(epsilon_factor=0.002) # Adjusted for balance
        
    def convert_image_to_svg(self, input_path: str, output_path: str, n_colors: int = 8):
        """
        Converts a raster image to a universal SVG.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # 1. Quantize
        logger.info(f"Step 1: Quantizing {input_path} to {n_colors} colors...")
        self.quantizer.n_colors = n_colors
        layers = self.quantizer.quantize(input_path)
        
        # Get dimensions from first layer mask
        if not layers:
            raise ValueError("No layers generated.")
        
        height, width = layers[0].mask.shape
        
        # 2. Initialize Composer
        composer = SVGComposer(width, height)
        
        # 3. Trace & Compose
        logger.info("Step 2: Tracing layers...")
        for i, layer in enumerate(layers):
            logger.info(f"  Tracing Layer {i} ({layer.color_hex})...")
            
            # Trace
            paths = self.tracer.mask_to_paths(layer.mask)
            
            # Add to composer
            if paths:
                composer.add_layer(layer, paths)
                
        # 4. Save
        logger.info(f"Step 3: Saving to {output_path}...")
        composer.save(output_path)
        logger.info("✅ Vectorization Complete.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python vectorizer_service.py <input_image> <output_svg> [n_colors]")
        sys.exit(1)
        
    input_img = sys.argv[1]
    output_svg = sys.argv[2]
    colors = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    service = VectorizerService()
    try:
        service.convert_image_to_svg(input_img, output_svg, colors)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
