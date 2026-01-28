"""
ONI V23 - YOLO UI Adapter
Wraps Ultralytics YOLO for UI element detection.

Since we don't have a custom UI-trained model yet, this adapter:
1. Uses base YOLO for general object detection
2. Combines with OCR for text element identification
3. Uses color/geometry heuristics for button/input detection
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import structlog
import numpy as np
from PIL import Image

logger = structlog.get_logger(__name__)


@dataclass
class UIElement:
    """Represents a detected UI element."""
    element_type: str  # "button", "input", "icon", "text", "image", "unknown"
    label: Optional[str]  # OCR text or inferred label
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: Tuple[int, int]
    metadata: Dict[str, Any]


class YoloUIAdapter:
    """
    Adapter for YOLO-based UI element detection.
    
    V1: Uses base YOLO + heuristics
    V2 (Future): Custom-trained UI model
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if YoloUIAdapter._model is not None:
            return  # Already initialized
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model (lazy initialization)."""
        try:
            from ultralytics import YOLO
            
            # Check for custom UI model first, fallback to base
            model_paths = [
                Path("models/yolo_ui_v1.pt"),  # Custom (future)
                Path("yolov8n.pt"),  # Base model in project root
                Path.home() / ".cache" / "ultralytics" / "yolov8n.pt",  # Cache
            ]
            
            model_path = None
            for p in model_paths:
                if p.exists():
                    model_path = p
                    break
            
            if model_path is None:
                # Download base model
                logger.info("yolo_downloading_base_model")
                YoloUIAdapter._model = YOLO("yolov8n.pt")
            else:
                logger.info("yolo_loading_model", path=str(model_path))
                YoloUIAdapter._model = YOLO(str(model_path))
            
            logger.info("yolo_model_loaded", classes=len(YoloUIAdapter._model.names))
            
        except Exception as e:
            logger.error("yolo_load_failed", error=str(e))
            YoloUIAdapter._model = None
    
    def detect_objects(self, image: Image.Image, confidence: float = 0.5) -> List[UIElement]:
        """
        Run YOLO detection on an image.
        
        Args:
            image: PIL Image to analyze
            confidence: Minimum confidence threshold
            
        Returns:
            List of detected UIElements
        """
        if YoloUIAdapter._model is None:
            logger.warning("yolo_model_not_loaded")
            return []
        
        try:
            # Convert PIL to numpy if needed
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            else:
                img_array = image
            
            # Run inference
            results = YoloUIAdapter._model(img_array, conf=confidence, verbose=False)
            
            elements = []
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = YoloUIAdapter._model.names[cls_id]
                    
                    # Map YOLO classes to UI element types
                    element_type = self._map_class_to_ui_type(cls_name)
                    
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    elements.append(UIElement(
                        element_type=element_type,
                        label=cls_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=(center_x, center_y),
                        metadata={"yolo_class_id": cls_id, "yolo_class_name": cls_name}
                    ))
            
            logger.info("yolo_detection_complete", count=len(elements))
            return elements
            
        except Exception as e:
            logger.error("yolo_detection_failed", error=str(e))
            return []
    
    def _map_class_to_ui_type(self, yolo_class: str) -> str:
        """
        Map YOLO COCO classes to UI element types.
        
        Note: Base YOLO is trained on COCO, not UI elements.
        This is a heuristic mapping for V1.
        """
        # COCO classes that might appear in screenshots
        button_like = ["cell phone", "remote", "keyboard"]
        text_like = ["book", "clock"]
        icon_like = ["sports ball", "apple", "orange"]
        
        yolo_lower = yolo_class.lower()
        
        if yolo_lower in button_like:
            return "button"
        elif yolo_lower in text_like:
            return "text"
        elif yolo_lower in icon_like:
            return "icon"
        elif yolo_lower == "person":
            return "avatar"
        elif yolo_lower == "tv" or yolo_lower == "laptop":
            return "screen"
        else:
            return "object"
    
    def detect_buttons_heuristic(self, image: Image.Image) -> List[UIElement]:
        """
        Use color/geometry heuristics to find button-like regions.
        
        Buttons typically:
        - Have uniform background color
        - Have centered text
        - Have rounded or rectangular shape
        - Have distinct border or shadow
        """
        import cv2
        
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (potential button boundaries)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (buttons are usually wide, not tall)
                aspect = w / max(h, 1)
                if 0.5 < aspect < 10 and w > 40 and h > 15 and h < 100:
                    # Likely a button candidate
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    elements.append(UIElement(
                        element_type="button_candidate",
                        label=None,
                        confidence=0.5,  # Low confidence for heuristic
                        bbox=(x, y, x + w, y + h),
                        center=(center_x, center_y),
                        metadata={"source": "geometry_heuristic", "aspect_ratio": aspect}
                    ))
            
            # Sort by area (larger = more likely primary button)
            elements.sort(key=lambda e: (e.bbox[2] - e.bbox[0]) * (e.bbox[3] - e.bbox[1]), reverse=True)
            
            return elements[:20]  # Limit to top 20 candidates
            
        except Exception as e:
            logger.error("button_heuristic_failed", error=str(e))
            return []


# Singleton instance
yolo_adapter = YoloUIAdapter()
