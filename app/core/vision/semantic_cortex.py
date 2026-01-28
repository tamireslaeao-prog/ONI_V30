"""
ONI V23 - Semantic Visual Cortex
The brain that understands UI meaning, not just pixels.

Capabilities:
- "Find the login button" -> Returns clickable coordinates
- "Is there a loading spinner?" -> Returns boolean
- "What is the primary action on this screen?" -> Returns element
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import structlog
import numpy as np
from PIL import Image

from app.core.vision.yolo_ui_adapter import YoloUIAdapter, UIElement, yolo_adapter

logger = structlog.get_logger(__name__)


@dataclass
class SemanticQuery:
    """Parsed semantic query."""
    intent: str  # "find", "check", "count", "describe"
    target_type: Optional[str]  # "button", "input", "icon", "text"
    target_descriptor: Optional[str]  # "red", "login", "close", "primary"
    raw_query: str


@dataclass
class SemanticResult:
    """Result of a semantic query."""
    success: bool
    element: Optional[UIElement]
    elements: List[UIElement]
    confidence: float
    explanation: str


class SemanticCortex:
    """
    High-level semantic understanding of UI.
    
    Combines:
    - YOLO object detection
    - OCR text recognition
    - Color analysis
    - Geometry heuristics
    - Natural language query parsing
    """
    
    def __init__(self):
        self.yolo = yolo_adapter
        self._color_keywords = {
            "red": [(180, 0, 0), (255, 100, 100)],
            "green": [(0, 150, 0), (100, 255, 100)],
            "blue": [(0, 0, 180), (100, 100, 255)],
            "yellow": [(200, 200, 0), (255, 255, 100)],
            "orange": [(255, 100, 0), (255, 180, 50)],
            "purple": [(100, 0, 100), (200, 100, 200)],
            "white": [(240, 240, 240), (255, 255, 255)],
            "black": [(0, 0, 0), (30, 30, 30)],
            "gray": [(100, 100, 100), (180, 180, 180)],
            "grey": [(100, 100, 100), (180, 180, 180)],
        }
        self._action_keywords = {
            "primary": ["submit", "ok", "save", "confirm", "continue", "next", "login", "sign in"],
            "cancel": ["cancel", "close", "back", "no", "exit", "dismiss"],
            "danger": ["delete", "remove", "clear", "logout", "sign out"],
        }
    
    def parse_query(self, query: str) -> SemanticQuery:
        """
        Parse natural language query into structured intent.
        
        Examples:
        - "find the red button" -> (find, button, red)
        - "click on login" -> (find, button, login)
        - "is there a spinner" -> (check, spinner, None)
        """
        query_lower = query.lower().strip()
        
        # Detect intent
        if any(q in query_lower for q in ["find", "locate", "where", "click", "press"]):
            intent = "find"
        elif any(q in query_lower for q in ["is there", "check", "exists", "has"]):
            intent = "check"
        elif any(q in query_lower for q in ["count", "how many"]):
            intent = "count"
        else:
            intent = "find"  # Default
        
        # Detect target type
        target_type = None
        type_keywords = {
            "button": ["button", "btn", "botão"],
            "input": ["input", "field", "textbox", "text box", "campo"],
            "icon": ["icon", "ícone", "image", "imagem"],
            "link": ["link", "anchor", "href"],
            "checkbox": ["checkbox", "check box", "toggle"],
            "dropdown": ["dropdown", "select", "combo"],
            "menu": ["menu", "menubar"],
            "spinner": ["spinner", "loading", "carregando"],
            "close": ["close", "x", "fechar"],
        }
        
        for t_type, keywords in type_keywords.items():
            if any(kw in query_lower for kw in keywords):
                target_type = t_type
                break
        
        # Detect descriptor (color, label, position)
        target_descriptor = None
        
        # Check for color
        for color in self._color_keywords:
            if color in query_lower:
                target_descriptor = f"color:{color}"
                break
        
        # Check for action keywords
        if target_descriptor is None:
            for action, keywords in self._action_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    target_descriptor = f"action:{action}"
                    break
        
        # Extract quoted text as literal label
        quoted = re.findall(r'"([^"]+)"', query)
        if quoted:
            target_descriptor = f"label:{quoted[0]}"
        
        # Extract specific words as potential labels
        if target_descriptor is None:
            words = query_lower.split()
            possible_labels = [w for w in words if len(w) > 2 and w not in [
                "find", "the", "button", "click", "press", "locate", "where", "is", "a", "an"
            ]]
            if possible_labels:
                target_descriptor = f"text:{possible_labels[-1]}"  # Use last word as likely label
        
        return SemanticQuery(
            intent=intent,
            target_type=target_type,
            target_descriptor=target_descriptor,
            raw_query=query
        )
    
    async def find_element(
        self, 
        image: Image.Image, 
        query: str,
        ocr_results: Optional[List[Dict]] = None
    ) -> SemanticResult:
        """
        Find UI element matching a natural language query.
        
        Args:
            image: Screenshot to analyze
            query: Natural language query (e.g., "red button", "login")
            ocr_results: Pre-computed OCR results (optional)
        
        Returns:
            SemanticResult with matched element(s)
        """
        parsed = self.parse_query(query)
        logger.info("semantic_query_parsed", 
                   intent=parsed.intent, 
                   target_type=parsed.target_type,
                   descriptor=parsed.target_descriptor)
        
        # Collect candidates from multiple sources
        candidates: List[UIElement] = []
        
        # 1. YOLO detection
        yolo_elements = self.yolo.detect_objects(image, confidence=0.3)
        candidates.extend(yolo_elements)
        
        # 2. Geometry heuristics for buttons
        if parsed.target_type in ["button", None]:
            button_candidates = self.yolo.detect_buttons_heuristic(image)
            candidates.extend(button_candidates)
        
        # 3. OCR-based elements (if provided)
        if ocr_results:
            for ocr in ocr_results:
                text = ocr.get("text", "")
                bbox = ocr.get("bbox", [0, 0, 0, 0])
                if len(bbox) >= 4:
                    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                    candidates.append(UIElement(
                        element_type="text",
                        label=text,
                        confidence=ocr.get("confidence", 0.5),
                        bbox=(x1, y1, x2, y2),
                        center=((x1 + x2) // 2, (y1 + y2) // 2),
                        metadata={"source": "ocr"}
                    ))
        
        # 4. Filter and rank candidates
        matched = self._filter_candidates(candidates, parsed, image)
        
        if not matched:
            return SemanticResult(
                success=False,
                element=None,
                elements=[],
                confidence=0.0,
                explanation=f"No element found matching: {query}"
            )
        
        # Sort by confidence
        matched.sort(key=lambda e: e.confidence, reverse=True)
        best = matched[0]
        
        return SemanticResult(
            success=True,
            element=best,
            elements=matched[:5],  # Top 5 matches
            confidence=best.confidence,
            explanation=f"Found {len(matched)} candidates. Best match: {best.element_type} at {best.center}"
        )
    
    def _filter_candidates(
        self, 
        candidates: List[UIElement], 
        query: SemanticQuery,
        image: Image.Image
    ) -> List[UIElement]:
        """Filter and score candidates based on query."""
        filtered = []
        
        for elem in candidates:
            score = elem.confidence
            
            # Type matching boost
            if query.target_type:
                if query.target_type in elem.element_type:
                    score += 0.2
                elif elem.element_type == "button_candidate" and query.target_type == "button":
                    score += 0.1
            
            # Descriptor matching
            if query.target_descriptor:
                if query.target_descriptor.startswith("color:"):
                    color = query.target_descriptor.split(":")[1]
                    if self._check_color_match(image, elem.bbox, color):
                        score += 0.3
                
                elif query.target_descriptor.startswith("label:"):
                    label = query.target_descriptor.split(":")[1].lower()
                    if elem.label and label in elem.label.lower():
                        score += 0.4
                
                elif query.target_descriptor.startswith("text:"):
                    text = query.target_descriptor.split(":")[1].lower()
                    if elem.label and text in elem.label.lower():
                        score += 0.3
                
                elif query.target_descriptor.startswith("action:"):
                    action = query.target_descriptor.split(":")[1]
                    keywords = self._action_keywords.get(action, [])
                    if elem.label and any(kw in elem.label.lower() for kw in keywords):
                        score += 0.35
            
            # Store updated score
            elem.confidence = min(score, 1.0)
            
            # Only include reasonable matches
            if elem.confidence > 0.2:
                filtered.append(elem)
        
        return filtered
    
    def _check_color_match(
        self, 
        image: Image.Image, 
        bbox: Tuple[int, int, int, int], 
        color_name: str
    ) -> bool:
        """Check if region has the specified color."""
        try:
            x1, y1, x2, y2 = bbox
            region = image.crop((x1, y1, x2, y2))
            
            # Get dominant color
            pixels = np.array(region)
            if len(pixels.shape) < 3:
                return False
            
            avg_color = pixels.mean(axis=(0, 1))[:3]  # RGB average
            
            # Check against color range
            color_range = self._color_keywords.get(color_name)
            if color_range:
                low, high = color_range
                return all(low[i] <= avg_color[i] <= high[i] for i in range(3))
            
            return False
        except Exception:
            return False
    
    async def get_clickable_point(self, query: str, image: Image.Image) -> Optional[Tuple[int, int]]:
        """
        Convenience method: Get coordinates to click for a query.
        
        Args:
            query: What to find (e.g., "OK button", "close icon")
            image: Current screenshot
        
        Returns:
            (x, y) coordinates or None
        """
        result = await self.find_element(image, query)
        if result.success and result.element:
            return result.element.center
        return None


# Singleton instance
semantic_cortex = SemanticCortex()
