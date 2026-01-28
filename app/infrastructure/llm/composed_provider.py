"""
ONI v4.0 - Composed LLM Provider
Combines visual grounding model with planning model.

Architecture:
1. Grounding Model (UI-TARS, Moondream) → finds elements on screen
2. Planning Model (Mistral, Gemini, GPT) → decides what action to take
3. ONI orchestrates both and executes

Based on CUA framework's model composition pattern.
"""

import asyncio
from typing import Any, Optional, Tuple, List
from dataclasses import dataclass

import structlog

from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from app.infrastructure.vision.uitars_provider import UITarsProvider, GroundingResult

logger = structlog.get_logger()


@dataclass
class ComposedAction:
    """Action with grounding information."""
    action_type: str
    params: dict
    grounded_coords: Optional[Tuple[int, int]] = None
    confidence: float = 0.8
    reasoning: str = ""


class ComposedProvider:
    """
    Provider that composes grounding + planning models.
    
    Flow:
    1. Grounder analyzes screenshot to find elements
    2. Planner receives screen context + goal
    3. Planner decides action, grounder provides coordinates
    4. ONI executes with precise coordinates
    
    Example:
        composed = ComposedProvider(
            grounder=UITarsProvider(),
            planner=MistralProvider(),
        )
        result = await composed.generate(prompt, screenshot=img)
    """
    
    def __init__(
        self,
        grounder: UITarsProvider = None,
        planner: Any = None,
        use_grounding_for_clicks: bool = True,
    ):
        """
        Initialize composed provider.
        
        Args:
            grounder: Visual grounding model (UI-TARS, Moondream)
            planner: Planning/reasoning model (Mistral, Gemini)
            use_grounding_for_clicks: Use grounder to find click coords
        """
        self._grounder = grounder
        self._planner = planner
        self._use_grounding = use_grounding_for_clicks
        
        logger.info("composed_provider_init",
                   grounder=type(grounder).__name__ if grounder else "None",
                   planner=type(planner).__name__ if planner else "None")
    
    @property
    def name(self) -> str:
        grounder_name = self._grounder.__class__.__name__ if self._grounder else "OCR"
        planner_name = getattr(self._planner, 'name', 'Unknown')
        return f"Composed({grounder_name}+{planner_name})"
    
    @property
    def is_available(self) -> bool:
        return self._planner is not None
    
    async def generate(
        self,
        prompt: str,
        config: GenerationConfig = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate action using composed models.
        
        Args:
            prompt: Task/goal prompt
            config: Generation config
            **kwargs: Additional params (screenshot, ocr_text, etc.)
        """
        screenshot = kwargs.get("screenshot")
        ocr_text = kwargs.get("ocr_text", [])
        goal = kwargs.get("goal", "")
        
        # Step 1: Get planning decision from planner
        plan_result = await self._planner.generate(
            prompt=prompt,
            config=config,
            **kwargs,
        )
        
        # Step 2: If action needs grounding (click), use grounder
        action_data = self._parse_action(plan_result.text)
        
        if (action_data and 
            action_data.get("action") == "click" and 
            self._grounder and 
            screenshot and
            self._use_grounding):
            
            description = action_data.get("params", {}).get("description", "")
            if description:
                # Use grounder to find precise coordinates
                grounding = await self._grounder.find_element(
                    screenshot=screenshot,
                    description=description,
                )
                
                if grounding:
                    # Inject grounded coordinates into response
                    logger.info("grounding_success",
                               description=description,
                               coords=(grounding.x, grounding.y))
                    
                    # Modify response to include coordinates
                    enhanced_text = self._inject_coordinates(
                        plan_result.text,
                        grounding.x,
                        grounding.y,
                    )
                    
                    return GenerationResult(
                        text=enhanced_text,
                        tokens_generated=plan_result.tokens_generated,
                        tokens_prompt=plan_result.tokens_prompt,
                        generation_time_ms=plan_result.generation_time_ms,
                        finish_reason=plan_result.finish_reason,
                        metadata={
                            **plan_result.metadata,
                            "grounded": True,
                            "grounded_coords": (grounding.x, grounding.y),
                        },
                    )
        
        return plan_result
    
    def _parse_action(self, response: str) -> Optional[dict]:
        """Parse action from response."""
        import json
        import re
        
        # Try to find JSON
        json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except Exception:
                pass
        
        # Try code format: agent.click("description")
        click_match = re.search(r'agent\.click\(["\'](.+?)["\']\)', response)
        if click_match:
            return {
                "action": "click",
                "params": {"description": click_match.group(1)}
            }
        
        return None
    
    def _inject_coordinates(self, response: str, x: int, y: int) -> str:
        """Inject grounded coordinates into response."""
        import re
        
        # If response has click action, add coordinates
        # Pattern: agent.click("description") → agent.click("description", x=X, y=Y)
        def replace_click(match):
            desc = match.group(1)
            return f'agent.click("{desc}", x={x}, y={y})'
        
        modified = re.sub(
            r'agent\.click\(["\'](.+?)["\']\)',
            replace_click,
            response,
        )
        
        return modified
    
    async def ground_element(
        self,
        screenshot: bytes,
        description: str,
    ) -> Optional[GroundingResult]:
        """
        Ground an element by description.
        
        Can be called directly without full generation.
        """
        if not self._grounder:
            return None
        
        return await self._grounder.find_element(screenshot, description)


class ModelSelector:
    """
    Dynamically selects model based on task complexity.
    
    Simple tasks → Light model (Moondream, local)
    Complex tasks → Heavy model (GPT-4, Claude)
    """
    
    COMPLEXITY_KEYWORDS = {
        "high": ["analyze", "compare", "research", "complex", "multiple", "workflow"],
        "medium": ["create", "edit", "configure", "setup", "install"],
        "low": ["open", "close", "click", "type", "scroll"],
    }
    
    def __init__(
        self,
        light_model: Any = None,
        heavy_model: Any = None,
    ):
        self._light = light_model
        self._heavy = heavy_model
    
    def select_model(self, goal: str) -> Any:
        """Select appropriate model for goal."""
        goal_lower = goal.lower()
        
        for keyword in self.COMPLEXITY_KEYWORDS["high"]:
            if keyword in goal_lower:
                logger.info("model_selected", complexity="high")
                return self._heavy or self._light
        
        for keyword in self.COMPLEXITY_KEYWORDS["low"]:
            if keyword in goal_lower:
                logger.info("model_selected", complexity="low")
                return self._light or self._heavy
        
        # Default: medium complexity → light model
        return self._light or self._heavy


def create_composed_provider(
    planner: Any,
    grounder: UITarsProvider = None,
) -> ComposedProvider:
    """
    Factory function to create composed provider.
    
    Args:
        planner: Planning model (required)
        grounder: Grounding model (optional, uses OCR fallback)
    """
    return ComposedProvider(
        grounder=grounder,
        planner=planner,
        use_grounding_for_clicks=grounder is not None,
    )
