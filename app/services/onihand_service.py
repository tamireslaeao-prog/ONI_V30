import structlog
import asyncio
import re
from typing import Optional, Dict, Any, Tuple, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.dependencies import container
from app.infrastructure.vision.uitars_provider import UITarsProvider, GroundingResult
from app.services.stability_service import get_stability_service
from app.services.cognitive_memory_service import get_cognitive_memory

logger = structlog.get_logger()


class ActionType(str, Enum):
    """Supported action types."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    HOVER = "hover"
    DRAG = "drag"
    SCROLL = "scroll"
    PRESS_KEY = "press_key"


@dataclass
class ActionInstruction:
    """Parsed instruction with action details."""
    action_type: ActionType
    target_description: str
    text_input: Optional[str] = None
    key_name: Optional[str] = None
    scroll_amount: Optional[int] = None
    drag_to_description: Optional[str] = None
    
    @property
    def requires_grounding(self) -> bool:
        """Check if action requires visual grounding."""
        return self.target_description is not None


@dataclass
class ActionResult:
    """Result of an executed action."""
    success: bool
    action_type: ActionType
    coordinates: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    grounding_confidence: Optional[float] = None
    execution_time_ms: Optional[int] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "action": self.action_type.value,
            "coordinates": self.coordinates,
            "error": self.error,
            "grounding_confidence": self.grounding_confidence,
            "execution_time_ms": self.execution_time_ms,
            "retry_count": self.retry_count
        }


class InstructionParser:
    """Parse natural language instructions into structured actions."""
    
    # Action patterns (order matters - most specific first)
    PATTERNS = [
        (r"double[- ]click (?:on |the )?(.+)", ActionType.DOUBLE_CLICK),
        (r"right[- ]click (?:on |the )?(.+)", ActionType.RIGHT_CLICK),
        (r"click (?:on |the )?(.+)", ActionType.CLICK),
        (r"type ['\"](.+?)['\"] (?:in |into |on )?(.+)", ActionType.TYPE),
        (r"enter ['\"](.+?)['\"] (?:in |into |on )?(.+)", ActionType.TYPE),
        (r"hover (?:over |on )?(.+)", ActionType.HOVER),
        (r"drag (.+) to (.+)", ActionType.DRAG),
        (r"scroll (up|down|left|right)(?: (\d+))?(?: (?:on |in )?(.+))?", ActionType.SCROLL),
        (r"press (?:the )?(\w+)(?: key)?", ActionType.PRESS_KEY),
    ]
    
    @classmethod
    def parse(cls, instruction: str) -> Optional[ActionInstruction]:
        """
        Parse instruction string into ActionInstruction.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            ActionInstruction or None if parsing fails
        """
        instruction = instruction.strip().lower()
        
        for pattern, action_type in cls.PATTERNS:
            match = re.match(pattern, instruction, re.IGNORECASE)
            if match:
                return cls._build_instruction(action_type, match)
        
        # Default to click if contains recognizable element description
        if any(word in instruction for word in ["button", "link", "icon", "menu", "field"]):
            return ActionInstruction(
                action_type=ActionType.CLICK,
                target_description=instruction
            )
        
        logger.warning("instruction_parse_failed", instruction=instruction)
        return None
    
    @classmethod
    def _build_instruction(cls, action_type: ActionType, match: re.Match) -> ActionInstruction:
        """Build ActionInstruction from regex match."""
        groups = match.groups()
        
        if action_type == ActionType.TYPE:
            return ActionInstruction(
                action_type=action_type,
                text_input=groups[0],
                target_description=groups[1]
            )
        elif action_type == ActionType.DRAG:
            return ActionInstruction(
                action_type=action_type,
                target_description=groups[0],
                drag_to_description=groups[1]
            )
        elif action_type == ActionType.SCROLL:
            direction = groups[0]
            amount = int(groups[1]) if groups[1] else 100
            target = groups[2] if len(groups) > 2 and groups[2] else None
            return ActionInstruction(
                action_type=action_type,
                target_description=target,
                scroll_amount=amount if direction in ["down", "right"] else -amount
            )
        elif action_type == ActionType.PRESS_KEY:
            return ActionInstruction(
                action_type=action_type,
                target_description=None,
                key_name=groups[0]
            )
        else:
            return ActionInstruction(
                action_type=action_type,
                target_description=groups[0]
            )


class ElementCache:
    """Cache recently found elements to speed up repeated actions."""
    
    def __init__(self, ttl_seconds: int = 30, max_size: int = 50):
        self._cache: Dict[str, Tuple[GroundingResult, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_size = max_size
    
    def get(self, description: str) -> Optional[GroundingResult]:
        """Get cached element if still valid."""
        if description in self._cache:
            result, timestamp = self._cache[description]
            if datetime.now() - timestamp < self.ttl:
                logger.debug("element_cache_hit", description=description)
                return result
            else:
                del self._cache[description]
        return None
    
    def set(self, description: str, result: GroundingResult):
        """Cache element result."""
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        
        self._cache[description] = (result, datetime.now())
        logger.debug("element_cached", description=description)
    
    def clear(self):
        """Clear all cached elements."""
        self._cache.clear()


class OnihandService:
    """
    Implements 'Onihand-like' capabilities for ONI.
    Bridging the gap between High-Level Intent and Low-Level Action.
    
    Features:
    - Natural language instruction parsing
    - Multiple action types (click, type, drag, etc.)
    - Retry logic with exponential backoff
    - Element caching for performance
    - Comprehensive error handling
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        grounding_timeout: float = 10.0,
        cache_ttl: int = 30
    ):
        self.uitars: Optional[UITarsProvider] = None
        self.mouse = None
        self.keyboard = None
        self._initialized = False
        
        # Configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.grounding_timeout = grounding_timeout
        
        # Element cache
        self.element_cache = ElementCache(ttl_seconds=cache_ttl)
        
        # Metrics
        self.actions_executed = 0
        self.actions_executed = 0
        self.actions_failed = 0
        self.stability_service = get_stability_service()
        self.memory = get_cognitive_memory()

    async def initialize(self):
        """Initialize dependencies with comprehensive error handling."""
        if self._initialized:
            return

        try:
            # Get UITars (Grounding)
            if container.has("grounding"):
                grounding = container.get("grounding")
                if hasattr(grounding, "ui_tars") and grounding.ui_tars:
                    self.uitars = grounding.ui_tars.provider if hasattr(grounding.ui_tars, 'provider') else grounding.ui_tars
            
            # Fallback to direct provider creation
            if not self.uitars:
                try:
                    from app.infrastructure.vision.uitars_provider import get_uitars_provider
                    self.uitars = get_uitars_provider()
                except Exception as e:
                    logger.error("onihand_uitars_init_failed", error=str(e))

            # Get Mouse
            if container.has("mouse"):
                self.mouse = container.get("mouse")
            
            # Get Keyboard (optional)
            if container.has("keyboard"):
                self.keyboard = container.get("keyboard")
            
            self._initialized = True
            logger.info("onihand_service_initialized", 
                       uitars=bool(self.uitars),
                       mouse=bool(self.mouse),
                       keyboard=bool(self.keyboard))
        
        except Exception as e:
            logger.error("onihand_initialization_failed", error=str(e))
            raise

    async def act(self, instruction: str) -> Dict[str, Any]:
        """
        Execute a high-level action from natural language instruction.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Dict with execution results
        """
        start_time = datetime.now()
        
        if not self._initialized:
            await self.initialize()

        # Validate dependencies
        if not self.mouse:
            return self._error_result("Mouse control not available")

        # Parse instruction
        parsed = InstructionParser.parse(instruction)
        if not parsed:
            return self._error_result(f"Could not parse instruction: '{instruction}'")
        
        logger.info("onihand_executing", 
                   instruction=instruction,
                   action_type=parsed.action_type.value)

        # Execute with retry logic
        result = await self._execute_with_retry(parsed)
        
        # Add execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        result.execution_time_ms = execution_time
        
        # Update metrics
        if result.success:
            self.actions_executed += 1
        else:
            self.actions_failed += 1
        
        logger.info("onihand_completed",
                   success=result.success,
                   execution_time_ms=execution_time,
                   retries=result.retry_count)
        
        return result.to_dict()

    async def _execute_with_retry(self, instruction: ActionInstruction) -> ActionResult:
        """Execute action with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await self._execute_action(instruction)
                result.retry_count = attempt
                
                if result.success:
                    return result
                
                last_error = result.error
                
            except Exception as e:
                last_error = str(e)
                logger.warning("onihand_action_failed",
                             attempt=attempt + 1,
                             error=last_error)
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        
        return ActionResult(
            success=False,
            action_type=instruction.action_type,
            error=f"Failed after {self.max_retries} attempts: {last_error}",
            retry_count=self.max_retries
        )

    async def _execute_action(self, instruction: ActionInstruction) -> ActionResult:
        """Execute single action attempt."""
        
        # Actions that require grounding
        if instruction.requires_grounding:
            element = await self._find_element(instruction.target_description)
            if not element:
                return ActionResult(
                    success=False,
                    action_type=instruction.action_type,
                    error=f"Could not locate: '{instruction.target_description}'"
                )
            
            target_x, target_y = element.x, element.y
            confidence = element.confidence
        else:
            target_x, target_y = None, None
            confidence = None

        # STABILITY CHECK (Temporal Intelligence)
        # Verify UI is stable before acting to prevent premature clicks
        roi = None
        if target_x and target_y:
            # Check 100x100 area around target
            roi = (target_x - 50, target_y - 50, 100, 100)
        
        
        # COGNITIVE MEMORY CHECK (The Brain)
        app_name = "Global" # TODO: get active window title
        if instruction.action_type in file_actions and target_x:
             if not self.memory.is_safe_to_click(app_name, target_x, target_y):
                 return ActionResult(success=False, action_type=instruction.action_type, error="Cognitive Block: High failure rate zone")

        is_stable = await self.stability_service.wait_until_stable(roi, timeout=5.0)
        if not is_stable:
             logger.warning("ui_unstable_action_forced", roi=roi)

        # Execute based on action type
        success = True
        error_msg = None
        try:
            if instruction.action_type == ActionType.CLICK:
                await self.mouse.move_to(target_x, target_y)
                await asyncio.sleep(0.1)
                await self.mouse.click()
                
            elif instruction.action_type == ActionType.DOUBLE_CLICK:
                await self.mouse.move_to(target_x, target_y)
                await asyncio.sleep(0.1)
                await self.mouse.click()
                await asyncio.sleep(0.05)
                await self.mouse.click()
                
            elif instruction.action_type == ActionType.RIGHT_CLICK:
                await self.mouse.move_to(target_x, target_y)
                await asyncio.sleep(0.1)
                await self.mouse.right_click()
                
            elif instruction.action_type == ActionType.HOVER:
                await self.mouse.move_to(target_x, target_y)
                await asyncio.sleep(0.3)  # Hover duration
                
            elif instruction.action_type == ActionType.TYPE:
                if not self.keyboard:
                    raise Exception("Keyboard control not available")
                await self.mouse.move_to(target_x, target_y)
                await asyncio.sleep(0.1)
                await self.mouse.click()  # Focus element
                await asyncio.sleep(0.1)
                await self.keyboard.type_text(instruction.text_input)
                
            elif instruction.action_type == ActionType.PRESS_KEY:
                if not self.keyboard:
                    raise Exception("Keyboard control not available")
                await self.keyboard.press_key(instruction.key_name)
                
            elif instruction.action_type == ActionType.DRAG:
                # Find destination element
                dest_element = await self._find_element(instruction.drag_to_description)
                if not dest_element:
                    raise Exception(f"Could not locate destination: '{instruction.drag_to_description}'")
                await self.mouse.drag(target_x, target_y, dest_element.x, dest_element.y)
                
            elif instruction.action_type == ActionType.SCROLL:
                if target_x and target_y:
                    await self.mouse.move_to(target_x, target_y)
                await self.mouse.scroll(instruction.scroll_amount)
        except Exception as e:
            success = False
            error_msg = str(e)
            raise e
        finally:
            # RECORD MEMORY
            if target_x:
                self.memory.record_action(
                    app_name, 
                    instruction.action_type.value, 
                    instruction.target_description or "",
                    target_x, target_y, 
                    success, 
                    error=error_msg
                )

        return ActionResult(
            success=True,
            action_type=instruction.action_type,
            coordinates={"x": target_x, "y": target_y} if target_x else None,
            grounding_confidence=confidence
        )

    async def _verify_action_success(self, 
                                   action: ActionType, 
                                   target_desc: str,
                                   before_state: Dict[str, Any]) -> float:
        """
        Multi-Modal Verification (The 'Sense' of the system).
        Returns confidence score (0.0 to 1.0).
        """
        # TODO: Implement full 3-signal check (Visual, Text, Tree)
        # For now, we return 1.0 to unblock
        return 1.0

    async def _find_element(self, description: str) -> Optional[GroundingResult]:
        """Find element using visual grounding with caching."""
        
        # Check cache first
        cached = self.element_cache.get(description)
        if cached:
            return cached
        
        if not self.uitars:
            logger.error("onihand_uitars_unavailable")
            return None

        # Capture screen
        vision = container.get("vision")
        if not vision:
            logger.error("onihand_vision_unavailable")
            return None
            
        screenshot_data = await vision.capture()
        if not screenshot_data or "image" not in screenshot_data:
            logger.error("onihand_screenshot_failed")
            return None
             
        # Decode screenshot
        import base64
        image_bytes = base64.b64decode(screenshot_data["image"])

        # Grounding with timeout
        logger.debug("onihand_grounding", description=description)
        
        try:
            result = await asyncio.wait_for(
                self.uitars.find_element(screenshot=image_bytes, description=description),
                timeout=self.grounding_timeout
            )
            
            if result:
                self.element_cache.set(description, result)
                logger.debug("onihand_element_found",
                           description=description,
                           confidence=result.confidence)
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("onihand_grounding_timeout", description=description)
            return None

    def _error_result(self, error: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {
            "success": False,
            "error": error,
            "action": None,
            "coordinates": None
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        total = self.actions_executed + self.actions_failed
        success_rate = (self.actions_executed / total * 100) if total > 0 else 0
        
        return {
            "actions_executed": self.actions_executed,
            "actions_failed": self.actions_failed,
            "success_rate": round(success_rate, 1),
            "cache_size": len(self.element_cache._cache)
        }

    def clear_cache(self):
        """Clear element cache."""
        self.element_cache.clear()
        logger.info("onihand_cache_cleared")
