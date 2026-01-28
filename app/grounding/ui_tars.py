"""
ONI v3.0 - UI-TARS Visual Grounding
Uses UI-TARS model to convert element descriptions into screen coordinates.
Supports HuggingFace Inference Endpoints and vLLM local deployment.
"""
import asyncio
import base64
import re
import logging
from dataclasses import dataclass
from typing import Any, Literal

import httpx
import structlog

logger = structlog.get_logger()


@dataclass
class GroundingResult:
    """Result from grounding operation."""
    x: int
    y: int
    confidence: float
    method: str  # "ui_tars", "ocr", "fallback"
    raw_response: str = ""


class UITarsGrounding:
    """
    Visual grounding using UI-TARS model.
    
    UI-TARS is a vision-language model specialized in GUI understanding.
    It takes a screenshot and description, outputs normalized coordinates.
    
    Recommended models:
    - UI-TARS-1.5-7B (1920x1080 output resolution)
    - UI-TARS-72B (1000x1000 output resolution)
    
    Example:
        grounding = UITarsGrounding(
            endpoint_url="https://your-endpoint.endpoints.huggingface.cloud",
            api_key="hf_xxx",
            grounding_width=1920,
            grounding_height=1080,
        )
        result = await grounding.locate("the blue submit button", screenshot_bytes)
        print(f"Click at ({result.x}, {result.y})")
    """
    
    def __init__(
        self,
        endpoint_url: str,
        api_key: str | None = None,
        model: str = "ui-tars-1.5-7b",
        grounding_width: int = 1920,
        grounding_height: int = 1080,
        screen_width: int = 1920,
        screen_height: int = 1080,
        timeout: float = 30.0,
        provider: Literal["huggingface", "vllm", "openai"] = "huggingface",
    ) -> None:
        """
        Initialize UI-TARS grounding.
        
        Args:
            endpoint_url: URL of the grounding model endpoint
            api_key: API key for authentication
            model: Model name
            grounding_width: Output coordinate resolution width from model
            grounding_height: Output coordinate resolution height from model
            screen_width: Actual screen width for scaling
            screen_height: Actual screen height for scaling
            timeout: Request timeout in seconds
            provider: API provider type
        """
        self._endpoint_url = endpoint_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._grounding_width = grounding_width
        self._grounding_height = grounding_height
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._timeout = timeout
        self._provider = provider
        
        self._client = httpx.AsyncClient(timeout=timeout)
        self._initialized = False
    
    @property
    def is_available(self) -> bool:
        """Check if grounding is configured."""
        return bool(self._endpoint_url)
    
    async def initialize(self) -> bool:
        """
        Test connection to grounding endpoint.
        
        Returns:
            True if endpoint is reachable
        """
        if not self._endpoint_url:
            logger.warning("ui_tars_not_configured", reason="no endpoint URL")
            return False
        
        try:
            headers = self._get_headers()
            response = await self._client.get(
                f"{self._endpoint_url}/health",
                headers=headers,
            )
            self._initialized = response.status_code == 200
            logger.info("ui_tars_initialized", status=self._initialized)
            return self._initialized
        except Exception as e:
            logger.warning("ui_tars_init_failed", error=str(e))
            return False
    
    async def locate(
        self,
        description: str,
        screenshot: bytes,
    ) -> GroundingResult:
        """
        Locate element on screen by description.
        
        Args:
            description: Natural language description of element
            screenshot: PNG screenshot as bytes
            
        Returns:
            GroundingResult with coordinates
            
        Raises:
            GroundingError: If grounding fails
        """
        if not self._endpoint_url:
            raise GroundingError("UI-TARS endpoint not configured")
        
        # Encode screenshot to base64
        b64_image = base64.b64encode(screenshot).decode("utf-8")
        
        # Build prompt for UI-TARS
        prompt = f"Query:{description}\nOutput only the coordinate of one point in your response.\n"
        
        try:
            response = await self._call_model(prompt, b64_image)
            x, y = self._parse_coordinates(response)
            
            # Scale coordinates from model resolution to screen resolution
            scaled_x = round(x * self._screen_width / self._grounding_width)
            scaled_y = round(y * self._screen_height / self._grounding_height)
            
            logger.info(
                "ui_tars_located",
                description=description[:50],
                raw_coords=(x, y),
                scaled_coords=(scaled_x, scaled_y),
            )
            
            return GroundingResult(
                x=scaled_x,
                y=scaled_y,
                confidence=0.9,  # UI-TARS doesn't provide confidence
                method="ui_tars",
                raw_response=response,
            )
            
        except Exception as e:
            logger.error("ui_tars_locate_failed", error=str(e), description=description[:50])
            raise GroundingError(f"UI-TARS grounding failed: {e}") from e
    
    async def _call_model(self, prompt: str, b64_image: str) -> str:
        """Call the grounding model API."""
        headers = self._get_headers()
        
        if self._provider == "huggingface":
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.1,
                },
                "image": b64_image,
            }
            url = f"{self._endpoint_url}/generate"
            
        elif self._provider == "vllm":
            payload = {
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.1,
            }
            url = f"{self._endpoint_url}/v1/chat/completions"
            
        else:  # OpenAI-compatible
            payload = {
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.1,
            }
            url = f"{self._endpoint_url}/v1/chat/completions"
        
        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract text based on provider
        if self._provider == "huggingface":
            return data.get("generated_text", "")
        else:
            return data["choices"][0]["message"]["content"]
    
    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers
    
    def _parse_coordinates(self, response: str) -> tuple[int, int]:
        """
        Parse coordinates from model response.
        
        UI-TARS typically outputs: "Point: (523, 147)" or just "523, 147"
        """
        # Find all numbers in response
        numbers = re.findall(r"\d+", response)
        
        if len(numbers) < 2:
            raise GroundingError(f"Could not parse coordinates from: {response}")
        
        # Take first two numbers as x, y
        x = int(numbers[0])
        y = int(numbers[1])
        
        return x, y
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()


class GroundingError(Exception):
    """Raised when grounding operation fails."""
    pass
