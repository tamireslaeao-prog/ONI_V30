"""
ONI Vision Utilities.
"""
from typing import Any
import hashlib
from PIL import Image
import io
import numpy as np

def compute_dhash(image_bytes: bytes, hash_size: int = 8) -> str:
    """
    Compute Perceptual Difference Hash (dHash).
    Used for efficient frame caching in Vision 2.0.
    """
    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # 1. Resize to (hash_size + 1, hash_size)
        # Antialias is better for quality, but LANCZOS/BILINEAR is faster for hashing
        img = img.convert("L").resize(
            (hash_size + 1, hash_size), 
            Image.Resampling.LANCZOS
        )
        
        pixels = list(img.getdata())
        
        # 2. Compare adjacent pixels
        diff = []
        for row in range(hash_size):
            for col in range(hash_size):
                left_pixel_index = row * (hash_size + 1) + col
                pixel_left = pixels[left_pixel_index]
                pixel_right = pixels[left_pixel_index + 1]
                diff.append(pixel_left > pixel_right)
        
        # 3. Convert binary array to hex string
        decimal_value = 0
        hex_string = []
        for index, value in enumerate(diff):
            if value:
                decimal_value += 2**(index % 8)
            if (index % 8) == 7:
                hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
                decimal_value = 0
                
        return "".join(hex_string)
        
    except Exception:
        # Fallback to simple md5 if image invalid
        return hashlib.md5(image_bytes).hexdigest()

def compute_dhash_bytes(image: bytes) -> str:
    """Alias for consistency."""
    return compute_dhash(image)
