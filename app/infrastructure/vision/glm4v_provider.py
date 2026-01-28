"""
ONI v9.0 - GLM-4.5V Visual Grounding Provider
Alternative VLM provider using Chinese GLM-4.5V model.

Supports normalized coordinates (0-999) and explicit action space.
Use as fallback when other providers fail.
"""

import re
import base64
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("litellm not available for GLM-4.5V")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class GLMGroundingResult:
    """Result from GLM-4.5V grounding."""
    x: int
    y: int
    action: str
    confidence: float = 0.8
    raw_response: str = ""


# GLM-4.5V Action Space definition
GLM_ACTION_SPACE = """
### Available Actions:
- left_click(start_box='[x,y]') - Click at coordinates
- right_click(start_box='[x,y]') - Right-click
- left_double_click(start_box='[x,y]') - Double-click
- left_drag(start_box='[x1,y1]', end_box='[x2,y2]') - Drag
- hover(start_box='[x,y]') - Move mouse
- key(keys='...') - Press keys
- type(content='...') - Type text
- scroll(start_box='[x,y]', direction='up|down') - Scroll
- WAIT() - Wait 5 seconds
- DONE() - Task complete
"""


class GLM4VProvider:
    """
    GLM-4.5V Visual Grounding Provider.
    
    Uses normalized coordinates (0-999) which get converted to pixels.
    Good alternative to UI-TARS for fallback scenarios.
    
    Requires litellm with GLM-4.5V model access.
    """
    
    def __init__(
        self, 
        model: str = "glm-4.5v",
        screen_width: int = 1920,
        screen_height: int = 1080
    ):
        """
        Initialize GLM-4.5V provider.
        
        Args:
            model: Model name for litellm
            screen_width: Screen width for coordinate conversion
            screen_height: Screen height for coordinate conversion
        """
        self.model = model
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    @property
    def is_available(self) -> bool:
        """Check if provider is available."""
        return LITELLM_AVAILABLE
    
    def _normalize_to_pixels(self, norm_x: int, norm_y: int) -> Tuple[int, int]:
        """Convert normalized coords (0-999) to pixel coords."""
        pixel_x = int((norm_x / 999.0) * self.screen_width)
        pixel_y = int((norm_y / 999.0) * self.screen_height)
        return pixel_x, pixel_y
    
    def _parse_action_response(self, response: str) -> Optional[GLMGroundingResult]:
        """
        Parse GLM-4.5V response to extract action and coordinates.
        
        Looks for patterns like:
        - left_click(start_box='[500,300]')
        - type(content='hello')
        """
        # Try to find click actions with coordinates
        click_pattern = r"(left_click|right_click|left_double_click|hover)\(start_box='\[(\d+),\s*(\d+)\]'\)"
        match = re.search(click_pattern, response)
        
        if match:
            action = match.group(1)
            norm_x = int(match.group(2))
            norm_y = int(match.group(3))
            pixel_x, pixel_y = self._normalize_to_pixels(norm_x, norm_y)
            
            return GLMGroundingResult(
                x=pixel_x,
                y=pixel_y,
                action=action,
                raw_response=response
            )
        
        # Try drag pattern
        drag_pattern = r"left_drag\(start_box='\[(\d+),\s*(\d+)\]',\s*end_box='\[(\d+),\s*(\d+)\]'\)"
        drag_match = re.search(drag_pattern, response)
        
        if drag_match:
            start_x = int(drag_match.group(1))
            start_y = int(drag_match.group(2))
            end_x = int(drag_match.group(3))
            end_y = int(drag_match.group(4))
            
            pixel_start = self._normalize_to_pixels(start_x, start_y)
            
            return GLMGroundingResult(
                x=pixel_start[0],
                y=pixel_start[1],
                action="drag",
                raw_response=response
            )
        
        return None
    
    async def find_element(
        self,
        screenshot_b64: str,
        description: str,
        screen_size: Optional[Tuple[int, int]] = None
    ) -> Optional[GLMGroundingResult]:
        """
        Find element on screen by description.
        
        Args:
            screenshot_b64: Base64 encoded screenshot
            description: Text description of element to find
            screen_size: Optional (width, height) override
            
        Returns:
            GLMGroundingResult with coordinates, or None
        """
        if not self.is_available:
            logger.warning("GLM-4.5V not available")
            return None
        
        if screen_size:
            self.screen_width, self.screen_height = screen_size
        
        try:
            # Build prompt
            system_prompt = f"""You are a GUI automation assistant.
Given a screenshot and an instruction, output the action to perform.
Use normalized coordinates (0-999).

{GLM_ACTION_SPACE}

Output ONLY the action call, nothing else."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}
                        },
                        {"type": "text", "text": f"Task: {description}"}
                    ]
                }
            ]
            
            # Call model
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            result = self._parse_action_response(content)
            
            if result:
                logger.info(
                    "GLM-4.5V found element",
                    description=description,
                    x=result.x,
                    y=result.y,
                    action=result.action
                )
            
            return result
            
        except Exception as e:
            logger.error("GLM-4.5V failed", error=str(e))
            return None
    
    async def predict_click(
        self,
        screenshot_b64: str,
        instruction: str
    ) -> Optional[Tuple[int, int]]:
        """
        Simple interface: get click coordinates for instruction.
        
        Args:
            screenshot_b64: Base64 screenshot
            instruction: What to click
            
        Returns:
            (x, y) pixel coordinates or None
        """
        result = await self.find_element(screenshot_b64, instruction)
        if result:
            return (result.x, result.y)
        return None


# Global singleton
_glm4v_provider: Optional[GLM4VProvider] = None


def get_glm4v_provider() -> GLM4VProvider:
    """Get or create GLM-4.5V provider singleton."""
    global _glm4v_provider
    if _glm4v_provider is None:
        _glm4v_provider = GLM4VProvider()
    return _glm4v_provider
