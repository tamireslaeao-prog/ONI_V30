"""
Optimized UI Analyzer for Monitor 2
Focus on key interactive elements with clean annotations
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple
import structlog

logger = structlog.get_logger(__name__)


class OptimizedUIAnalyzer:
    """
    Lightweight UI analyzer focused on actionable elements.
    Optimized for single monitor analysis with minimal visual pollution.
    """
    
    def __init__(
        self, 
        image_path: str,
        max_buttons: int = 15,
        max_texts: int = 30,
        min_confidence: float = 0.7
    ):
        self.image_path = image_path
        self.max_buttons = max_buttons
        self.max_texts = max_texts
        self.min_confidence = min_confidence
        
        # Load image
        self.img = cv2.imread(image_path)
        self.img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.height, self.width = self.img.shape[:2]
        
        # Results storage
        self.ui_data = {
            'image_dimensions': {'width': self.width, 'height': self.height},
            'monitor_offset_x': 0,
            'total_elements': 0,
            'key_buttons': [],
            'text_labels': [],
            'interactive_areas': []
        }
    
    def detect_key_buttons(self) -> List[Dict]:
        """Detect prominent interactive buttons."""
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Morphological operations to enhance button-like shapes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by size (typical button range)
            if not (500 < area < 50000):
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (button-like)
            aspect_ratio = w / float(h) if h > 0 else 0
            if not (0.3 < aspect_ratio < 8):
                continue
            
            # Calculate confidence based on shape regularity
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            # Rectangular buttons have lower circularity (0.3-0.8)
            if circularity < 0.2 or circularity > 0.95:
                continue
            
            confidence = min(0.95, 0.5 + circularity * 0.5)
            
            if confidence < self.min_confidence:
                continue
            
            # Check if region has text (more likely a button)
            roi = self.img_rgb[y:y+h, x:x+w]
            has_text = self._quick_text_check(roi)
            
            if has_text:
                confidence = min(0.98, confidence + 0.15)
            
            button = {
                'id': f'btn_{len(buttons)}',
                'type': 'button',
                'coordinates': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2),
                    'bbox': [int(x), int(y), int(x+w), int(y+h)]
                },
                'confidence': round(float(confidence), 2),
                'has_text': bool(has_text)
            }
            
            buttons.append(button)
            
            # Stop if we hit the limit
            if len(buttons) >= self.max_buttons:
                break
        
        # Sort by confidence and size
        buttons.sort(key=lambda b: (b['confidence'], b['coordinates']['width'] * b['coordinates']['height']), 
                    reverse=True)
        
        return buttons[:self.max_buttons]
    
    def detect_text_labels(self) -> List[Dict]:
        """Extract prominent text labels using OCR with improved accuracy."""
        
        # Pre-process image for better OCR
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast with CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Slight sharpening
        kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        # Convert back to RGB for Tesseract (keep grayscale tones, don't binarize)
        processed = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        # Configure Tesseract for sparse text (UI elements scattered)
        # PSM 11 = Sparse text. Find as much text as possible in no particular order.
        # PSM 3 = Fully automatic page segmentation, but no OSD
        custom_config = r'--oem 3 --psm 11 -l por+eng'
        
        try:
            ocr_data = pytesseract.image_to_data(
                processed, 
                config=custom_config, 
                output_type=pytesseract.Output.DICT
            )
        except Exception as e:
            logger.warning("ocr_failed", error=str(e))
            return []
        
        text_labels = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Lower confidence threshold to capture more UI text
            if not text or conf < 40 or len(text) < 2:
                continue
            
            # Skip common OCR garbage
            if text in ['|', '||', '-', '--', '...', '__', '==', '<<', '>>', '[', ']', '(', ')']:
                continue
            
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            
            # Filter tiny text
            if w < 15 or h < 8:
                continue
            
            label = {
                'id': f'txt_{len(text_labels)}',
                'text': text,
                'coordinates': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2),
                    'bbox': [int(x), int(y), int(x+w), int(y+h)]
                },
                'confidence': round(float(conf) / 100, 2)
            }
            
            text_labels.append(label)
            
            if len(text_labels) >= self.max_texts:
                break
        
        # Sort by confidence
        text_labels.sort(key=lambda t: t['confidence'], reverse=True)
        
        return text_labels[:self.max_texts]
    
    def detect_interactive_areas(self) -> List[Dict]:
        """Detect large interactive areas (windows, panels, canvases)."""
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        # Adaptive threshold for better edge detection
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        areas = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only large areas (windows, panels)
            if area < self.width * self.height * 0.05:  # At least 5% of screen
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (window-like)
            aspect_ratio = w / float(h) if h > 0 else 0
            if not (0.5 < aspect_ratio < 3):
                continue
            
            # Calculate fill ratio
            extent = area / float(w * h) if (w * h) > 0 else 0
            
            if extent < 0.6:  # Too sparse
                continue
            
            confidence = min(0.95, 0.6 + extent * 0.35)
            
            area_elem = {
                'id': f'area_{len(areas)}',
                'type': 'interactive_area',
                'coordinates': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2),
                    'bbox': [int(x), int(y), int(x+w), int(y+h)]
                },
                'confidence': round(float(confidence), 2),
                'area_pixels': int(area)
            }
            
            areas.append(area_elem)
            
            # Limit to top 5 largest areas
            if len(areas) >= 5:
                break
        
        # Sort by size
        areas.sort(key=lambda a: a['area_pixels'], reverse=True)
        
        return areas[:5]
    
    def _quick_text_check(self, roi: np.ndarray) -> bool:
        """Quick check if ROI contains text."""
        if roi.size == 0:
            return False
        
        # Convert to grayscale
        if len(roi.shape) == 3:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        else:
            gray_roi = roi
        
        # Check for text-like patterns (horizontal edges)
        edges = cv2.Canny(gray_roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Text typically has 5-20% edge density
        return 0.05 < edge_density < 0.20
    
    def analyze(self) -> Dict:
        """Run complete UI analysis."""
        logger.info("ui_analysis_started", dimensions=f"{self.width}x{self.height}")
        
        # Detect buttons
        logger.info("detecting_buttons", max_count=self.max_buttons)
        buttons = self.detect_key_buttons()
        self.ui_data['key_buttons'] = buttons
        
        # Detect text
        logger.info("detecting_text", max_count=self.max_texts)
        texts = self.detect_text_labels()
        self.ui_data['text_labels'] = texts
        
        # Detect interactive areas
        logger.info("detecting_areas")
        areas = self.detect_interactive_areas()
        self.ui_data['interactive_areas'] = areas
        
        self.ui_data['total_elements'] = len(buttons) + len(texts) + len(areas)
        
        logger.info(
            "ui_analysis_completed",
            buttons=len(buttons),
            texts=len(texts),
            areas=len(areas),
            total=self.ui_data['total_elements']
        )
        
        return self.ui_data
    
    def create_clean_annotation(self, output_path: str, mouse_pos: tuple = None):
        """Create minimally annotated image with original colors and mouse cursor."""
        logger.info("creating_annotation", output=output_path)
        
        # Use original RGB image
        pil_img = Image.fromarray(self.img_rgb)
        draw = ImageDraw.Draw(pil_img, 'RGBA')
        
        # Load font
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
            font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 9)
        except Exception:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
            except Exception:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Draw interactive areas (subtle background)
        for area in self.ui_data['interactive_areas']:
            c = area['coordinates']
            draw.rectangle(
                [c['x'], c['y'], c['x'] + c['width'], c['y'] + c['height']],
                outline=(100, 100, 255, 180),
                width=2
            )
        
        # Draw mouse cursor if provided
        if mouse_pos:
            mx, my = mouse_pos
            # Draw red crosshair/circle
            r = 5
            # Outer glow
            draw.ellipse((mx-r-2, my-r-2, mx+r+2, my+r+2), outline=(255, 255, 255, 200), width=2)
            # Inner red circle
            draw.ellipse((mx-r, my-r, mx+r, my+r), outline=(255, 0, 0, 255), width=2)
            # Center point
            draw.ellipse((mx-1, my-1, mx+1, my+1), fill=(255, 0, 0, 255))
            
            # Label coords
            coord_text = f"({int(mx)}, {int(my)})"
            draw.text((mx + 10, my + 10), coord_text, font=font, fill=(255, 0, 0, 255), stroke_width=2, stroke_fill=(255,255,255,255))
        
        # Draw buttons (green outlines)
        for btn in self.ui_data['key_buttons']:
            c = btn['coordinates']
            
            # Semi-transparent green box
            draw.rectangle(
                [c['x'], c['y'], c['x'] + c['width'], c['y'] + c['height']],
                outline=(0, 255, 0, 220),
                width=2
            )
            
            # Center crosshair
            cx, cy = c['center_x'], c['center_y']
            crosshair_size = 8
            draw.line(
                [(cx - crosshair_size, cy), (cx + crosshair_size, cy)],
                fill=(0, 255, 0, 255),
                width=2
            )
            draw.line(
                [(cx, cy - crosshair_size), (cx, cy + crosshair_size)],
                fill=(0, 255, 0, 255),
                width=2
            )
            
            # Coordinates label (compact)
            label = f"({cx},{cy})"
            label_x = c['x'] + 4
            label_y = c['y'] - 14
            
            # Background for readability
            draw.rectangle(
                [label_x - 2, label_y - 2, label_x + 70, label_y + 12],
                fill=(0, 0, 0, 180)
            )
            draw.text((label_x, label_y), label, fill=(0, 255, 0, 255), font=font_small)
        
        # Draw text labels (yellow boxes)
        for txt in self.ui_data['text_labels']:
            c = txt['coordinates']
            
            # Thin yellow outline
            draw.rectangle(
                [c['x'], c['y'], c['x'] + c['width'], c['y'] + c['height']],
                outline=(255, 255, 0, 200),
                width=1
            )
            
            # Text preview (truncated)
            text_preview = txt['text'][:15]
            text_x = c['x'] + 2
            text_y = c['y'] - 12
            
            # Only show if not overlapping with button
            overlap = any(
                self._boxes_overlap(c['bbox'], btn['coordinates']['bbox'])
                for btn in self.ui_data['key_buttons']
            )
            
            if not overlap:
                draw.rectangle(
                    [text_x - 2, text_y - 2, text_x + len(text_preview) * 6, text_y + 12],
                    fill=(0, 0, 0, 160)
                )
                draw.text((text_x, text_y), text_preview, fill=(255, 255, 0, 255), font=font_small)
        
        # Save annotated image
        pil_img.save(output_path)
        logger.info("annotation_saved", path=output_path)
    
    def _boxes_overlap(self, box1: List[int], box2: List[int]) -> bool:
        """Check if two bounding boxes overlap."""
        # box format: [x1, y1, x2, y2]
        return not (box1[2] < box2[0] or box1[0] > box2[2] or 
                   box1[3] < box2[1] or box1[1] > box2[3])


# Standalone usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ui_analyzer_optimized.py <screenshot_path>")
        sys.exit(1)
    
    screenshot_path = sys.argv[1]
    
    print(f"Analyzing: {screenshot_path}")
    
    analyzer = OptimizedUIAnalyzer(screenshot_path)
    ui_data = analyzer.analyze()
    
    # Save JSON
    import json
    json_path = "ui_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(ui_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Data saved: {json_path}")
    
    # Create annotation
    annotated_path = "ui_annotated.png"
    analyzer.create_clean_annotation(annotated_path)
    
    print(f"✓ Annotated image: {annotated_path}")
    print(f"\nSummary:")
    print(f"  Buttons: {len(ui_data['key_buttons'])}")
    print(f"  Text Labels: {len(ui_data['text_labels'])}")
    print(f"  Interactive Areas: {len(ui_data['interactive_areas'])}")
    print(f"  Total Elements: {ui_data['total_elements']}")