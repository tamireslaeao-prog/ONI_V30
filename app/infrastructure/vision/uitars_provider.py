"""
ONI v4.0 - UI-TARS Visual Grounding Provider
Uses UI-TARS model for precise GUI element detection.
"""

import base64
import io
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, List

import httpx
import structlog
from PIL import Image, ImageDraw, ImageFont

logger = structlog.get_logger()

# Constants
DEFAULT_SCREEN_SIZE = (1920, 1080)
DEFAULT_MAX_TOKENS = 50
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TIMEOUT = 30.0
MARKER_RADIUS = 12
MARKER_FONT_SIZE = 14
MARKER_COLOR_FILL = "red"
MARKER_COLOR_OUTLINE = "white"
TEXT_COLOR = "white"


@dataclass
class GroundingResult:
    """Result from visual grounding."""
    x: int
    y: int
    confidence: float
    element_type: str
    description: str
    
    @property
    def coords(self) -> Tuple[int, int]:
        """Get coordinates as tuple."""
        return (self.x, self.y)


class UITarsProvider:
    """
    Visual grounding using UI-TARS model.
    
    UI-TARS is specialized for GUI element detection.
    Input: screenshot + description
    Output: precise (x, y) coordinates
    
    Supports:
    - HuggingFace Inference API
    - Local model via vLLM/Transformers
    - CUA VLM Router (cloud)
    """
    
    MODELS = {
        "ui-tars-7b": "ByteDance-Seed/UI-TARS-1.5-7B",
        "ui-tars-2": "cua/bytedance/ui-tars-2",
        "moondream3": "moondream/moondream3-preview",
    }
    
    def __init__(
        self,
        model: str = "ui-tars-7b",
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize UI-TARS provider.
        
        Args:
            model: Model to use (ui-tars-7b, ui-tars-2, moondream3)
            api_key: HuggingFace or CUA API key
            endpoint_url: Custom endpoint URL
        """
        self._model = model
        self._model_id = self.MODELS.get(model, model)
        
        # Load API key from parameter or environment
        self._api_key = (
            api_key 
            or os.getenv("HUGGINGFACE_API_KEY") 
            or os.getenv("CUA_API_KEY")
        )
        
        # Determine endpoint
        if endpoint_url:
            self._endpoint = endpoint_url
        elif "cua/" in self._model_id:
            self._endpoint = "https://api.cua.ai/vlm/v1/chat/completions"
        else:
            self._endpoint = f"https://api-inference.huggingface.co/models/{self._model_id}"
        
        logger.info("uitars_provider_init", model=self._model_id, has_key=bool(self._api_key))
    
    @property
    def is_available(self) -> bool:
        """Check if provider has required API key."""
        return bool(self._api_key)
    
    def _build_prompt(self, description: str) -> str:
        """Build prompt for UI element finding."""
        return f"""You are a GUI grounding model. Find the element described and return its center coordinates.

Element to find: {description}

Return ONLY the coordinates in format: (x, y)
Where x and y are pixel coordinates relative to the image.
If element is not found, return: NOT_FOUND
"""
    
    def _encode_screenshot(self, screenshot: bytes) -> str:
        """Encode screenshot bytes to base64."""
        return base64.b64encode(screenshot).decode('utf-8')
    
    def _build_payload(self, prompt: str, img_base64: str) -> dict:
        """Build API request payload."""
        return {
            "model": self._model_id,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                    }
                ]
            }],
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
        }
    
    async def find_element(
        self,
        screenshot: bytes,
        description: str,
        screen_size: Tuple[int, int] = DEFAULT_SCREEN_SIZE,
    ) -> Optional[GroundingResult]:
        """
        Find element on screen by description.
        
        Args:
            screenshot: Screenshot as bytes (PNG)
            description: Text description of element to find
            screen_size: Screen dimensions for coordinate scaling
            
        Returns:
            GroundingResult with coordinates, or None if not found
        """
        if not self._api_key:
            logger.warning("uitars_no_api_key")
            return None
        
        if not screenshot:
            logger.error("uitars_empty_screenshot")
            return None
        
        try:
            img_base64 = self._encode_screenshot(screenshot)
            prompt = self._build_prompt(description)
            payload = self._build_payload(prompt, img_base64)
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    self._endpoint,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse response
            text = self._extract_text_from_response(data)
            logger.debug("uitars_response", text=text)
            
            # Extract coordinates
            coords = self._parse_coordinates(text, screen_size)
            
            if coords:
                return GroundingResult(
                    x=coords[0],
                    y=coords[1],
                    confidence=0.9,
                    element_type="unknown",
                    description=description,
                )
            
            return None
            
        except httpx.HTTPStatusError as e:
            logger.error("uitars_http_error", status=e.response.status_code, error=str(e))
            return None
        except Exception as e:
            logger.error("uitars_error", error=str(e), exc_info=True)
            return None
    
    def _extract_text_from_response(self, data: dict) -> str:
        """Extract text from API response."""
        if isinstance(data, list):
            return data[0].get("generated_text", "")
        
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        
        return ""
    
    def _parse_coordinates(
        self,
        text: str,
        screen_size: Tuple[int, int],
    ) -> Optional[Tuple[int, int]]:
        """
        Parse coordinates from model response.
        
        Supports multiple formats:
        - (x, y)
        - x=123, y=456
        - 123 456 or 123, 456
        - 0.5, 0.3 (normalized)
        """
        text = text.strip()
        
        if "NOT_FOUND" in text.upper():
            return None
        
        # Format: (x, y)
        match = re.search(r'\((\d+),\s*(\d+)\)', text)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # Format: x=123, y=456
        match = re.search(r'x\s*=\s*(\d+).*?y\s*=\s*(\d+)', text, re.IGNORECASE)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # Format: 123 456 or 123, 456
        match = re.search(r'(\d+)[,\s]+(\d+)', text)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # Format: normalized 0.5, 0.3
        match = re.search(r'(0\.\d+)[,\s]+(0\.\d+)', text)
        if match:
            x = int(float(match.group(1)) * screen_size[0])
            y = int(float(match.group(2)) * screen_size[1])
            return (x, y)
        
        return None
    
    async def find_all_elements(
        self,
        screenshot: bytes,
        screen_size: Tuple[int, int] = DEFAULT_SCREEN_SIZE,
    ) -> List[GroundingResult]:
        """
        Find ALL clickable elements on screen.
        
        Note: Not fully implemented yet.
        """
        logger.info("uitars_find_all_not_implemented")
        return []


class SetOfMark:
    """
    Set-of-Mark (SOM) visual annotation system.
    
    Overlays numbered labels on detected elements,
    making it easier for LLMs to reference specific elements.
    
    Example: "Click on element [3]" instead of "Click on the OK button"
    """
    
    def __init__(self, grounder: Optional[UITarsProvider] = None):
        """
        Initialize Set-of-Mark annotator.
        
        Args:
            grounder: Optional UI-TARS provider for element detection
        """
        self._grounder = grounder
        self._elements: List[GroundingResult] = []
    
    def _load_font(self) -> ImageFont.FreeTypeFont:
        """Load font for markers."""
        try:
            return ImageFont.truetype("arial.ttf", MARKER_FONT_SIZE)
        except OSError:
            return ImageFont.load_default()
    
    def _draw_marker(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        number: int,
        font: ImageFont.FreeTypeFont
    ) -> None:
        """Draw numbered marker at position."""
        # Draw circle
        draw.ellipse(
            [
                x - MARKER_RADIUS, 
                y - MARKER_RADIUS, 
                x + MARKER_RADIUS, 
                y + MARKER_RADIUS
            ],
            fill=MARKER_COLOR_FILL,
            outline=MARKER_COLOR_OUTLINE,
        )
        
        # Draw number
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        draw.text(
            (x - text_w // 2, y - text_h // 2),
            text,
            fill=TEXT_COLOR,
            font=font,
        )
    
    async def annotate_screenshot(
        self,
        screenshot: bytes,
    ) -> Tuple[bytes, List[GroundingResult]]:
        """
        Annotate screenshot with numbered markers.
        
        Args:
            screenshot: Screenshot bytes
            
        Returns:
            Tuple of (annotated_screenshot_bytes, list of elements)
        """
        # Load screenshot
        img = Image.open(io.BytesIO(screenshot))
        draw = ImageDraw.Draw(img)
        font = self._load_font()
        
        # Find all elements if grounder available
        if self._grounder:
            self._elements = await self._grounder.find_all_elements(screenshot)
        
        # Draw numbered markers
        for i, elem in enumerate(self._elements, 1):
            self._draw_marker(draw, elem.x, elem.y, i, font)
        
        # Save annotated image
        output = io.BytesIO()
        img.save(output, format="PNG")
        
        return output.getvalue(), self._elements
    
    def get_element_by_number(self, number: int) -> Optional[GroundingResult]:
        """
        Get element by its marker number.
        
        Args:
            number: Marker number (1-indexed)
        """
        if 1 <= number <= len(self._elements):
            return self._elements[number - 1]
        return None


def get_uitars_provider(
    model: str = "ui-tars-7b",
    api_key: Optional[str] = None
) -> UITarsProvider:
    """
    Get configured UI-TARS provider.
    
    Args:
        model: Model to use
        api_key: Optional API key
    """
    return UITarsProvider(model=model, api_key=api_key)
