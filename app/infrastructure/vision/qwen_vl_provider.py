"""
ONI v11.0 - Qwen2.5-VL Provider
Visual grounding using Alibaba's Qwen2.5-VL model.

Features:
- Precise object grounding with bounding boxes and points
- JSON coordinate output
- Local and API deployment support
"""

import base64
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import structlog
import httpx

logger = structlog.get_logger(__name__)


@dataclass
class QwenGroundingResult:
    """Result from Qwen-VL grounding."""
    x: int
    y: int
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]] = None  # x1, y1, x2, y2
    description: str = ""


class QwenVLProvider:
    """
    Qwen2.5-VL Visual Grounding Provider.
    
    Uses OpenRouter (recommended) for Qwen2.5-VL access.
    DashScope is NOT available internationally.
    
    Features:
    - Precise bbox + point-based localization
    - JSON coordinate output format
    - OpenRouter integration (free tier: qwen/qwen2.5-vl-72b-instruct:free)
    
    Example:
        provider = QwenVLProvider()  # Uses OpenRouter by default
        result = await provider.find_element(screenshot, "Save button")
        click(result.x, result.y)
    """
    
    # Coordinate extraction patterns
    COORD_PATTERNS = [
        r'\[?\(?\s*(\d+)\s*,\s*(\d+)\s*\]?\)?',  # (x, y) or [x, y]
        r'x\s*[:=]\s*(\d+).*?y\s*[:=]\s*(\d+)',   # x: 100, y: 200
        r'(\d+)\s*[xX×]\s*(\d+)',                  # 100x200
    ]
    
    def __init__(
        self,
        mode: str = "openrouter",
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        model_name: str = "qwen/qwen2.5-vl-72b-instruct:free",
    ):
        """
        Initialize Qwen-VL provider.
        
        Args:
            mode: "openrouter" (recommended), "huggingface", or "local"
            api_key: API key (auto-detects from env)
            endpoint_url: Custom endpoint URL
            model_name: Model identifier
        """
        self._mode = mode
        
        # Auto-detect API key based on mode
        if mode == "openrouter":
            self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            self._endpoint = "https://openrouter.ai/api/v1/chat/completions"
            self._model_name = model_name
        else:
            self._api_key = api_key or os.getenv("QWEN_API_KEY") or os.getenv("HF_TOKEN")
            self._endpoint = endpoint_url or "https://api-inference.huggingface.co/models/"
            self._model_name = "Qwen/Qwen2.5-VL-7B-Instruct"
        
        self._client = httpx.AsyncClient(timeout=30.0)
        
        # Local model (lazy loaded)
        self._local_model = None
        self._local_processor = None
        
        logger.info(
            "qwen_vl_provider_init",
            mode=mode,
            model=self._model_name,
            has_api_key=bool(self._api_key)
        )
    
    @property
    def is_available(self) -> bool:
        """Check if provider is available."""
        if self._mode in ("openrouter", "huggingface"):
            return bool(self._api_key)
        else:
            return self._local_model is not None
    
    async def find_element(
        self,
        screenshot: bytes,
        description: str,
        screen_size: Tuple[int, int] = (1920, 1080),
    ) -> Optional[QwenGroundingResult]:
        """
        Find element by natural language description.
        
        Args:
            screenshot: PNG screenshot bytes
            description: Text description of element to find
            screen_size: Screen dimensions for coordinate scaling
            
        Returns:
            QwenGroundingResult with coordinates, or None if not found
        """
        if self._mode == "openrouter":
            return await self._find_via_openrouter(screenshot, description, screen_size)
        elif self._mode == "huggingface":
            return await self._find_via_api(screenshot, description, screen_size)
        else:
            return await self._find_via_local(screenshot, description, screen_size)
    
    async def _find_via_openrouter(
        self,
        screenshot: bytes,
        description: str,
        screen_size: Tuple[int, int],
    ) -> Optional[QwenGroundingResult]:
        """Find element using OpenRouter API."""
        if not self._api_key:
            logger.warning("openrouter_api_key_missing")
            return None
        
        try:
            b64_image = base64.b64encode(screenshot).decode()
            
            prompt = f"""Look at this screenshot and find the UI element: "{description}"

Return ONLY the center coordinates in JSON format:
{{"x": <number>, "y": <number>, "confidence": <0.0-1.0>}}

If not found, return: {{"x": 0, "y": 0, "confidence": 0}}"""

            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "ONI Visual Grounding",
            }
            
            payload = {
                "model": self._model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 100,
            }
            
            response = await self._client.post(
                self._endpoint,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return self._parse_text_response(text, screen_size)
            else:
                logger.warning(
                    "openrouter_api_error",
                    status=response.status_code,
                    text=response.text[:200]
                )
                return None
                
        except Exception as e:
            logger.error("openrouter_api_exception", error=str(e))
            return None
    
    async def _find_via_api(
        self,
        screenshot: bytes,
        description: str,
        screen_size: Tuple[int, int],
    ) -> Optional[QwenGroundingResult]:
        """Find element using API."""
        if not self._api_key:
            logger.warning("qwen_api_key_missing")
            return None
        
        try:
            # Encode image
            b64_image = base64.b64encode(screenshot).decode()
            
            # Prepare prompt for coordinate extraction
            prompt = f"""Look at this screenshot and find the UI element matching this description: "{description}"

Return ONLY the center coordinates of the element in this exact JSON format:
{{"x": <number>, "y": <number>, "confidence": <0-1>}}

If the element is not found, return: {{"x": 0, "y": 0, "confidence": 0}}"""

            # Call API (HuggingFace Inference API format)
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "inputs": {
                    "image": b64_image,
                    "text": prompt,
                },
                "parameters": {
                    "max_new_tokens": 100,
                }
            }
            
            url = f"{self._endpoint}{self._model_name}"
            response = await self._client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result, screen_size)
            else:
                logger.warning(
                    "qwen_api_error",
                    status=response.status_code,
                    text=response.text[:200]
                )
                return None
                
        except Exception as e:
            logger.error("qwen_api_exception", error=str(e))
            return None
    
    async def _find_via_local(
        self,
        screenshot: bytes,
        description: str,
        screen_size: Tuple[int, int],
    ) -> Optional[QwenGroundingResult]:
        """Find element using local model."""
        # Load model if needed
        if self._local_model is None:
            try:
                await self._load_local_model()
            except Exception as e:
                logger.error("qwen_local_load_failed", error=str(e))
                return None
        
        try:
            from PIL import Image
            import io
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(screenshot))
            
            # Prepare prompt
            prompt = f"""<|im_start|>user
<image>
Find the UI element: "{description}"
Return coordinates as JSON: {{"x": number, "y": number}}<|im_end|>
<|im_start|>assistant
"""
            
            # Run inference
            inputs = self._local_processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            ).to(self._local_model.device)
            
            outputs = self._local_model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
            )
            
            response_text = self._local_processor.decode(
                outputs[0], skip_special_tokens=True
            )
            
            return self._parse_text_response(response_text, screen_size)
            
        except Exception as e:
            logger.error("qwen_local_inference_failed", error=str(e))
            return None
    
    async def _load_local_model(self):
        """Load local Qwen-VL model."""
        logger.info("loading_qwen_local_model", model=self._model_name)
        
        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            import torch
            
            self._local_processor = AutoProcessor.from_pretrained(self._model_name)
            self._local_model = Qwen2VLForConditionalGeneration.from_pretrained(
                self._model_name,
                torch_dtype=torch.float16,
                device_map="auto",
            )
            
            logger.info("qwen_local_model_loaded")
            
        except ImportError:
            raise RuntimeError(
                "transformers package required for local mode. "
                "Install with: pip install transformers accelerate"
            )
    
    def _parse_response(
        self,
        response: Dict,
        screen_size: Tuple[int, int],
    ) -> Optional[QwenGroundingResult]:
        """Parse API response to extract coordinates."""
        try:
            # HuggingFace returns list of generated text
            if isinstance(response, list) and response:
                text = response[0].get("generated_text", "")
            elif isinstance(response, dict):
                text = response.get("generated_text", str(response))
            else:
                text = str(response)
            
            return self._parse_text_response(text, screen_size)
            
        except Exception as e:
            logger.error("qwen_parse_failed", error=str(e))
            return None
    
    def _parse_text_response(
        self,
        text: str,
        screen_size: Tuple[int, int],
    ) -> Optional[QwenGroundingResult]:
        """Parse text response to extract coordinates."""
        import json
        
        # Try JSON parsing first
        try:
            # Find JSON-like content
            json_match = re.search(r'\{[^}]+\}', text)
            if json_match:
                data = json.loads(json_match.group())
                x = int(data.get("x", 0))
                y = int(data.get("y", 0))
                confidence = float(data.get("confidence", 0.5))
                
                if x > 0 and y > 0:
                    # Scale if coordinates seem normalized (0-1)
                    if x <= 1 and y <= 1:
                        x = int(x * screen_size[0])
                        y = int(y * screen_size[1])
                    
                    return QwenGroundingResult(
                        x=x,
                        y=y,
                        confidence=confidence
                    )
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback to regex patterns
        for pattern in self.COORD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                
                if x > 0 and y > 0:
                    # Scale if needed
                    if x <= 1 and y <= 1:
                        x = int(x * screen_size[0])
                        y = int(y * screen_size[1])
                    
                    return QwenGroundingResult(
                        x=x,
                        y=y,
                        confidence=0.6
                    )
        
        logger.warning("qwen_coords_not_found", text=text[:200])
        return None
    
    async def find_all_elements(
        self,
        screenshot: bytes,
        screen_size: Tuple[int, int] = (1920, 1080),
    ) -> List[QwenGroundingResult]:
        """
        Find all interactive elements on screen.
        
        Returns list of all detected elements with their coordinates.
        """
        # For full element detection, we prompt for a list
        elements = []
        
        try:
            b64_image = base64.b64encode(screenshot).decode()
            
            prompt = """List all interactive UI elements (buttons, inputs, links, menus) visible in this screenshot.
For each element, provide: name and center coordinates.
Format as JSON array: [{"name": "...", "x": number, "y": number}, ...]"""

            if self._mode == "api" and self._api_key:
                headers = {"Authorization": f"Bearer {self._api_key}"}
                payload = {
                    "inputs": {"image": b64_image, "text": prompt},
                    "parameters": {"max_new_tokens": 500}
                }
                
                url = f"{self._endpoint}{self._model_name}"
                response = await self._client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    import json
                    result = response.json()
                    text = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
                    
                    # Parse JSON array
                    array_match = re.search(r'\[.*\]', text, re.DOTALL)
                    if array_match:
                        data = json.loads(array_match.group())
                        for item in data:
                            if "x" in item and "y" in item:
                                elements.append(QwenGroundingResult(
                                    x=int(item["x"]),
                                    y=int(item["y"]),
                                    confidence=0.7,
                                    description=item.get("name", "")
                                ))
                                
        except Exception as e:
            logger.error("qwen_find_all_failed", error=str(e))
        
        return elements
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()


# Global singleton
_qwen_provider: Optional[QwenVLProvider] = None


def get_qwen_vl_provider() -> QwenVLProvider:
    """Get or create Qwen-VL provider singleton."""
    global _qwen_provider
    if _qwen_provider is None:
        _qwen_provider = QwenVLProvider()
    return _qwen_provider
