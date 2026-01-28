"""
ONI v5.0 - Cognitive Agent Core
Base class for all cognitive agents in the ONI system.

Provides common functionality for:
- State management
- Logging and telemetry
- Event callbacks
- Memory integration
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class CognitiveState(str, Enum):
    """States for cognitive agents."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class CognitiveContext:
    """Context passed between cognitive operations."""
    goal: str = ""
    current_step: int = 0
    total_steps: int = 0
    observations: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CognitiveAgent(ABC):
    """
    Abstract base class for cognitive agents.
    
    All cognitive agents (HybridAgent, AdaptiveSovereign, etc.)
    should inherit from this class to ensure consistent behavior.
    """
    
    def __init__(self, name: str = "CognitiveAgent"):
        """
        Initialize cognitive agent.
        
        Args:
            name: Human-readable agent name
        """
        self._name = name
        self._state = CognitiveState.IDLE
        self._context = CognitiveContext()
        self._callbacks: Dict[str, Callable] = {}
        self._is_running = False
        self._stop_requested = False
        
        logger.info(f"{name}_initialized")
    
    # =========================================================================
    # PROPERTIES
    # =========================================================================
    
    @property
    def name(self) -> str:
        """Agent name."""
        return self._name
    
    @property
    def state(self) -> CognitiveState:
        """Current agent state."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        return self._is_running
    
    @property
    def context(self) -> CognitiveContext:
        """Current execution context."""
        return self._context
    
    # =========================================================================
    # ABSTRACT METHODS
    # =========================================================================
    
    @abstractmethod
    async def think(self, observation: Any) -> Any:
        """
        Process an observation and decide on next action.
        
        Args:
            observation: Current state observation
            
        Returns:
            Decision/action to take
        """
        pass
    
    @abstractmethod
    async def act(self, decision: Any) -> Any:
        """
        Execute a decided action.
        
        Args:
            decision: Decision from think()
            
        Returns:
            Action result
        """
        pass
    
    @abstractmethod
    async def observe(self) -> Any:
        """
        Capture current state observation.
        
        Returns:
            Observation data
        """
        pass
    
    # =========================================================================
    # COMMON METHODS
    # =========================================================================
    
    async def run_loop(self, goal: str, max_iterations: int = 50) -> CognitiveContext:
        """
        Run the cognitive loop: observe → think → act → repeat.
        
        Args:
            goal: Goal to achieve
            max_iterations: Maximum loop iterations
            
        Returns:
            Final execution context
        """
        self._context = CognitiveContext(
            goal=goal,
            started_at=datetime.now()
        )
        self._is_running = True
        self._stop_requested = False
        
        logger.info(f"{self._name}_loop_started", goal=goal)
        self._emit_callback("on_start", goal)
        
        try:
            for iteration in range(max_iterations):
                if self._stop_requested:
                    logger.info(f"{self._name}_stop_requested")
                    break
                
                self._context.current_step = iteration + 1
                
                # 1. Observe
                self._set_state(CognitiveState.WAITING)
                observation = await self.observe()
                self._context.observations.append({
                    "step": iteration,
                    "data": observation,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 2. Think
                self._set_state(CognitiveState.THINKING)
                decision = await self.think(observation)
                
                if decision is None or (isinstance(decision, dict) and decision.get("done")):
                    logger.info(f"{self._name}_goal_achieved")
                    break
                
                # 3. Act
                self._set_state(CognitiveState.ACTING)
                result = await self.act(decision)
                self._context.actions_taken.append({
                    "step": iteration,
                    "decision": decision,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                self._emit_callback("on_step", {
                    "step": iteration,
                    "observation": observation,
                    "decision": decision,
                    "result": result
                })
            
            self._set_state(CognitiveState.COMPLETED)
            
        except Exception as e:
            self._context.errors.append(str(e))
            self._set_state(CognitiveState.ERROR)
            logger.exception(f"{self._name}_loop_error", error=str(e))
            self._emit_callback("on_error", str(e))
        
        finally:
            self._is_running = False
            self._context.completed_at = datetime.now()
            self._context.total_steps = self._context.current_step
            
            self._emit_callback("on_complete", self._context)
        
        return self._context
    
    def stop(self) -> None:
        """Request graceful stop of the cognitive loop."""
        self._stop_requested = True
        logger.info(f"{self._name}_stop_requested")
    
    def set_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for an event.
        
        Events:
            - on_start: Called when loop starts (goal)
            - on_step: Called after each iteration (step_data)
            - on_complete: Called when loop ends (context)
            - on_error: Called on error (error_message)
            - on_state_change: Called when state changes (new_state)
        """
        self._callbacks[event] = callback
    
    def _set_state(self, state: CognitiveState) -> None:
        """Update state and emit callback."""
        old_state = self._state
        self._state = state
        if old_state != state:
            logger.debug(f"{self._name}_state_change", 
                        old=old_state.value, new=state.value)
            self._emit_callback("on_state_change", state)
    
    def _emit_callback(self, event: str, data: Any = None) -> None:
        """Emit an event to registered callback."""
        if event in self._callbacks:
            try:
                self._callbacks[event](data)
            except Exception as e:
                logger.warning(f"{self._name}_callback_error", 
                              event=event, error=str(e))


# =============================================================================
# EXAMPLE IMPLEMENTATION
# =============================================================================

class SimpleCognitiveAgent(CognitiveAgent):
    """Simple example implementation of CognitiveAgent."""
    
    def __init__(self):
        super().__init__("SimpleCognitiveAgent")
        self._counter = 0
    
    async def observe(self) -> Dict[str, Any]:
        """Simple observation: just return counter."""
        return {"counter": self._counter}
    
    async def think(self, observation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Simple decision: increment until 5."""
        if observation["counter"] >= 5:
            return {"done": True}
        return {"action": "increment"}
    
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Simple action: increment counter."""
        if decision.get("action") == "increment":
            self._counter += 1
        return {"new_value": self._counter}


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_cognitive_agent():
    """Quick test of CognitiveAgent."""
    agent = SimpleCognitiveAgent()
    
    context = await agent.run_loop("Count to 5", max_iterations=10)
    
    print(f"Final state: {agent.state.value}")
    print(f"Steps taken: {context.total_steps}")
    print(f"Actions: {len(context.actions_taken)}")
    
    return context


if __name__ == "__main__":
    asyncio.run(_test_cognitive_agent())
