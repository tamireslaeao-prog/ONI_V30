import asyncio
import base64
import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from PIL import Image

try:
    import easyocr
    from ultralytics import YOLO
    import supervision as sv
except ImportError:
    # These will be handled by the check in __init__
    pass

from app.utils.visualization import BoxAnnotator
from app.services.vision.vision_cache import get_vision_cache

logger = logging.getLogger(__name__)

class DetectionProcessor:
    """Processor for object detection using YOLO."""

    def __init__(
        self,
        model_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        force_device: Optional[str] = None,
    ):
        self.model_path = model_path
        self.cache_dir = cache_dir
        self.device = force_device
        self.model = None
        # self._load_model() # Lazy loading enabled in Phase 4

    def _load_model(self):
        """Load the YOLO model."""
        if not self.model_path:
            # Default to a standard icon detection model if not specified
            # In a real scenario, this should download/load a specific weights file
            model_name = "yolov8n.pt" 
            # Ideally we want a specific trained model for UI elements "icon_detect/model.pt"
            # For now we will use standard yolov8n as placeholder or rely on user providing path
            logger.warning("No specific model path provided for DetectionProcessor. Using 'yolov8n.pt' as fallback. This may not detect UI icons correctly.")
            self.model_path = model_name

        try:
            logger.info(f"Loading YOLO model from {self.model_path}")
            self.model = YOLO(str(self.model_path))
            if self.device:
                self.model.to(self.device)
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def detect(
        self, image: Image.Image, conf_threshold: float = 0.2, iou_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Run detection on an image."""
        if not self.model:
             self._load_model()
             
        if not self.model:
            logger.warning("Model not loaded, skipping detection")
            return []

        try:
            results = self.model(
                image, 
                conf=conf_threshold, 
                iou=iou_threshold,
                verbose=False
            )
            
            detections = []
            for result in results:
                # Process detections using Supervision for consistency if desired, 
                # or manually extract from YOLO Result object
                for box in result.boxes:
                    # box.xyxy is [x1, y1, x2, y2]
                    # box.xyxyn is normalized [x1, y1, x2, y2]
                    coords = box.xyxyn[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = self.model.names[cls] if self.model.names else str(cls)
                    
                    detections.append({
                        "id": None, # assigned later
                        "type": "icon",
                        "bbox": coords, # normalized
                        "confidence": conf,
                        "label": label,
                        "text": None
                    })
            return detections
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []


class OCRProcessor:
    """Processor for Optical Character Recognition using EasyOCR."""

    def __init__(self, languages: List[str] = ["en"], gpu: bool = True):
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self._init_reader()

    def _init_reader(self):
        """Initialize the EasyOCR reader."""
        try:
            logger.info(f"Initializing EasyOCR with languages {self.languages}")
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.reader = None

    def detect_text(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect text in an image."""
        if not self.reader:
            logger.warning("OCR reader not loaded, skipping text detection")
            return []

        try:
            import numpy as np
            # Convert PIL to numpy array for EasyOCR
            if image.mode != "RGB":
                image = image.convert("RGB")
            img_np = np.array(image)
            
            results = self.reader.readtext(img_np)
            
            detections = []
            width, height = image.size
            
            for bbox, text, conf in results:
                # bbox is [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                # Extract min/max for bounding box
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                x1, x2 = min(x_coords), max(x_coords)
                y1, y2 = min(y_coords), max(y_coords)
                
                # Normalize
                norm_bbox = [x1 / width, y1 / height, x2 / width, y2 / height]
                
                detections.append({
                    "id": None,
                    "type": "text",
                    "bbox": norm_bbox,
                    "confidence": float(conf),
                    "label": "text",
                    "text": text
                })
                
            return detections
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return []


class OmniParserService:
    """Service for parsing screen content using computer vision."""

    def __init__(
        self,
        yolo_model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        self.detection_processor = DetectionProcessor(
            model_path=Path(yolo_model_path) if yolo_model_path else None,
            force_device=device
        )
        self.ocr_processor = OCRProcessor()
        self.annotator = BoxAnnotator()
        
        # Caching (Phase 4)
        self._cache: Dict[str, Any] = {}
        self._cache_times: Dict[str, float] = {}
        
    def _nms(self, detections: List[Dict[str, Any]], iou_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Apply Non-Maximum Suppression to merge overlapping boxes."""
        if not detections:
            return []
            
        # Basic NMS implementation
        # For production, use torch.ops.torchvision.nms or similar optimized ops
        
        # Sort by confidence
        sorted_dets = sorted(detections, key=lambda x: x["confidence"], reverse=True)
        keep = []
        
        while sorted_dets:
            current = sorted_dets.pop(0)
            keep.append(current)
            
            # Remove highly overlapping boxes
            remaining = []
            for other in sorted_dets:
                iou = self._calculate_iou(current["bbox"], other["bbox"])
                if iou < iou_threshold:
                    remaining.append(other)
            sorted_dets = remaining
            
        return keep

    def _calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union."""
        # box format: [x1, y1, x2, y2]
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
            
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        union_area = box1_area + box2_area - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0

    async def parse_screen(
        self, 
        image_data: Union[bytes, str, Image.Image],
        confidence_threshold: float = 0.2,
        frame_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse the screen image to detect UI elements in parallel with caching.
        Phase 4: Optimization (Caching enabled).
        
        Returns:
            Dict containing 'annotated_image' (PIL Image) and 'elements' (List[Dict])
        """
        # 1. Check Cache
        import time
        from app.core.config import settings
        
        cached_elements = None
        if settings.vision.caching_enabled and frame_hash:
            if frame_hash in self._cache:
                age = time.time() - self._cache_times.get(frame_hash, 0)
                if age < settings.vision.cache_ttl:
                    logger.debug("vision_cache_hit", hash=frame_hash[:8], age=f"{age:.2f}s")
                    cached_elements = self._cache[frame_hash]
                    
        # 2. Load Image (needed for annotation even if cache hit)
        image = image_data
        if not isinstance(image, Image.Image):
            try:
                if isinstance(image, bytes):
                    image = Image.open(io.BytesIO(image))
                elif isinstance(image, str) and (image.startswith("/") or image.startswith("C:")):
                    image = Image.open(image)
                elif isinstance(image, str):
                    import base64
                    image = Image.open(io.BytesIO(base64.b64decode(image)))
            except Exception as e:
                logger.error(f"Failed to load image for parsing: {e}")
                return {"annotated_image": None, "elements": []}

        # 3. Running Detectors (only if no cache)
        if cached_elements is not None:
            filtered_detections = cached_elements
        else:
            # Parallel Detection
            icon_task = asyncio.to_thread(self.detection_processor.detect, image, conf_threshold=confidence_threshold)
            text_task = asyncio.to_thread(self.ocr_processor.detect_text, image)
            
            icon_detections, text_detections = await asyncio.gather(icon_task, text_task)
            
            # Merge and Filter (NMS)
            all_detections = icon_detections + text_detections
            filtered_detections = self._nms(all_detections)
            
            # Assign structural IDs
            for idx, det in enumerate(filtered_detections):
                det["id"] = idx
            
            # Update Cache
            if frame_hash and settings.vision.caching_enabled:
                self._cache[frame_hash] = filtered_detections
                self._cache_times[frame_hash] = time.time()
            
        # 4. Annotate Image
        annotated_image = image.copy()
        if filtered_detections:
            annotated_image = self.annotator.draw_boxes(annotated_image, filtered_detections, {})
            
        return {
            "annotated_image": annotated_image,
            "elements": filtered_detections
        }
