"""
ONI v4.0 - Reflective Chain-of-Thought Agent
Implements structured reasoning with visual grounding.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple

import structlog

from app.infrastructure.llm.base import GenerationConfig, GenerationResult

logger = structlog.get_logger()


# Reflective Chain-of-Thought Prompt Template
REFLECTIVE_COT_PROMPT = """You are ONI, an intelligent GUI automation agent for Windows.

# CURRENT GOAL
{goal}

# WHAT I SEE ON SCREEN
{visual_context}

# MY ACTION HISTORY
{action_history}

# MY MEMORY
{memory_context}

---

# YOUR REASONING PROCESS

Follow this structured thinking:

## (Observation)
What I see on the screen right now. List visible elements, windows, text.

## (Analysis)  
What does this mean for my goal? Am I making progress? Any obstacles?

## (Memory)
What have I done before? What worked? What didn't?

## (Plan)
What are the next 2-3 steps to achieve my goal?

## (Decision)
What is the SINGLE next action I should take?

---

# ACTION FORMAT

Respond with a JSON action:

```json
{{
    "thought": "Brief reasoning for this action",
    "action": "hotkey|type|click|wait|done|fail",
    "params": {{...}},
    "confidence": 0.0-1.0
}}
```

## Action Examples:
- {{"action": "hotkey", "params": {{"keys": ["win", "r"]}}}}
- {{"action": "type", "params": {{"text": "notepad"}}}}
- {{"action": "click", "params": {{"description": "OK button", "x": 500, "y": 300}}}}
- {{"action": "wait", "params": {{"seconds": 2.0}}}}
- {{"action": "done", "params": {{}}}}

## CRITICAL RULES:
1. To open ANY app: Win+R → type appname → Enter
2. ONE action at a time
3. If stuck, try alternative approach
4. Use keyboard shortcuts when available
5. Click only on visible elements

Now reason through and provide your next action:
"""


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    action_type: str
    params: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class AgentMemory:
    """Agent's working memory."""
    observations: List[str] = field(default_factory=list)
    actions: List[ActionResult] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    
    def add_action(self, action: ActionResult):
        self.actions.append(action)
        # Keep only last 10 actions
        if len(self.actions) > 10:
            self.actions = self.actions[-10:]
    
    def add_observation(self, obs: str):
        self.observations.append(obs)
        if len(self.observations) > 5:
            self.observations = self.observations[-5:]
    
    def format_history(self) -> str:
        if not self.actions:
            return "No actions taken yet"
        
        lines = []
        for i, action in enumerate(self.actions[-5:], 1):
            status = "✓" if action.success else "✗"
            lines.append(f"{i}. [{status}] {action.action_type}: {action.params}")
        return "\n".join(lines)
    
    def format_memory(self) -> str:
        parts = []
        if self.notes:
            parts.append(f"Notes: {', '.join(self.notes[-3:])}")
        if self.failed_approaches:
            parts.append(f"Failed approaches: {', '.join(self.failed_approaches[-3:])}")
        return " | ".join(parts) if parts else "No accumulated memory"
    
    def detect_loop(self) -> bool:
        """Detect if agent is stuck in a loop."""
        if len(self.actions) < 3:
            return False
        
        last_3 = self.actions[-3:]
        # Check if last 3 actions are identical
        if all(a.action_type == last_3[0].action_type and 
               a.params == last_3[0].params for a in last_3):
            return True
        return False


class ReflectiveCoTAgent:
    """
    Agent with Reflective Chain-of-Thought reasoning.
    
    Features:
    - Structured observation → analysis → plan → action
    - Visual grounding integration
    - Action memory and loop detection
    - Confidence-based decision making
    """
    
    def __init__(
        self,
        llm_provider: Any,
        visual_grounder: Any = None,
        max_steps: int = 50,
        confidence_threshold: float = 0.5,
    ):
        """
        Initialize ReflectiveCoT agent.
        
        Args:
            llm_provider: LLM provider for reasoning
            visual_grounder: Optional UI-TARS provider for grounding
            max_steps: Maximum steps before giving up
            confidence_threshold: Minimum confidence to execute action
        """
        self._llm = llm_provider
        self._grounder = visual_grounder
        self._max_steps = max_steps
        self._confidence_threshold = confidence_threshold
        
        # State
        self._memory = AgentMemory()
        self._step_count = 0
        self._current_goal = ""
        
        # Callbacks
        self._on_thought: Optional[Callable[[str], None]] = None
        self._on_action: Optional[Callable[[dict], None]] = None
    
    def set_callbacks(
        self,
        on_thought: Callable[[str], None] = None,
        on_action: Callable[[dict], None] = None,
    ):
        self._on_thought = on_thought
        self._on_action = on_action
    
    def reset(self):
        """Reset agent state for new goal."""
        self._memory = AgentMemory()
        self._step_count = 0
        self._current_goal = ""
    
    def _emit_thought(self, thought: str):
        if self._on_thought:
            self._on_thought(thought)
        logger.info("agent_thought", thought=thought)
    
    async def reason(
        self,
        goal: str,
        ocr_text: List[str],
        screenshot: bytes = None,
    ) -> dict:
        """
        Reason about next action using Chain-of-Thought.
        
        Returns:
            Action dict with thought, action, params, confidence
        """
        self._current_goal = goal
        self._step_count += 1
        
        # Check step limit
        if self._step_count > self._max_steps:
            return {
                "thought": "Maximum steps reached",
                "action": "fail",
                "params": {"reason": "Step limit exceeded"},
                "confidence": 1.0,
            }
        
        # Check for loops
        if self._memory.detect_loop():
            self._emit_thought("🔄 Loop detected! Trying alternative approach...")
            self._memory.failed_approaches.append(
                f"{self._memory.actions[-1].action_type}:{self._memory.actions[-1].params}"
            )
        
        # Build visual context
        visual_context = self._build_visual_context(ocr_text)
        
        # Add grounding info if available
        if self._grounder and screenshot:
            try:
                #  Could enhance with UI-TARS detection
                pass
            except Exception as e:
                logger.warning("grounding_failed", error=str(e))
        
        # Build prompt
        prompt = REFLECTIVE_COT_PROMPT.format(
            goal=goal,
            visual_context=visual_context,
            action_history=self._memory.format_history(),
            memory_context=self._memory.format_memory(),
        )
        
        # Get LLM response
        try:
            response = await self._llm.generate(
                prompt=prompt,
                config=GenerationConfig(
                    max_tokens=800,
                    temperature=0.3,
                ),
            )
            
            # Parse response
            action = self._parse_action_response(response.text)
            
            # Emit thought
            if action.get("thought"):
                self._emit_thought(f"💭 {action['thought']}")
            
            return action
            
        except Exception as e:
            logger.error("reasoning_failed", error=str(e))
            return {
                "thought": f"Reasoning error: {str(e)}",
                "action": "wait",
                "params": {"seconds": 1.0},
                "confidence": 0.5,
            }
    
    def _build_visual_context(self, ocr_text: List[str]) -> str:
        """Build visual context string from OCR."""
        if not ocr_text:
            return "No text detected on screen (possibly desktop or loading)"
        
        # Limit and format
        visible_text = ocr_text[:20]
        formatted = ", ".join(f'"{t}"' for t in visible_text if t.strip())
        
        return f"Visible text: {formatted}"
    
    def _parse_action_response(self, response: str) -> dict:
        """Parse action JSON from LLM response."""
        import re
        
        # Try to find JSON in response
        json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response, re.DOTALL)
        
        if json_match:
            try:
                action = json.loads(json_match.group())
                
                # Validate action
                if action.get("action") not in ["hotkey", "type", "click", "wait", "done", "fail"]:
                    action["action"] = "wait"
                    action["params"] = {"seconds": 1.0}
                
                action.setdefault("confidence", 0.8)
                action.setdefault("thought", "")
                action.setdefault("params", {})
                
                return action
                
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to extract action from text
        response_lower = response.lower()
        
        if "win+r" in response_lower or "win, r" in response_lower:
            return {
                "thought": "Opening Run dialog",
                "action": "hotkey",
                "params": {"keys": ["win", "r"]},
                "confidence": 0.9,
            }
        
        if "done" in response_lower and "task" in response_lower:
            return {
                "thought": "Task appears complete",
                "action": "done",
                "params": {},
                "confidence": 0.8,
            }
        
        # Default fallback
        return {
            "thought": "Could not parse action, waiting",
            "action": "wait",
            "params": {"seconds": 1.0},
            "confidence": 0.5,
        }
    
    def record_action_result(self, action_type: str, params: dict, success: bool, error: str = None):
        """Record result of executed action."""
        result = ActionResult(
            success=success,
            action_type=action_type,
            params=params,
            error=error,
        )
        self._memory.add_action(result)
    
    def add_observation(self, observation: str):
        """Add an observation to memory."""
        self._memory.add_observation(observation)


def get_reflective_agent(llm_provider: Any) -> ReflectiveCoTAgent:
    """Create a configured ReflectiveCoT agent."""
    return ReflectiveCoTAgent(llm_provider=llm_provider)
