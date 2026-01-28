from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import structlog
from datetime import datetime
import asyncio

from app.agent.hybrid_worker import HybridWorker, WorkerResult
from app.soul.types import SoulToken, ValidatedCoordinate

logger = structlog.get_logger()

@dataclass
class Observation:
    screenshot: bytes
    ui_elements: List[Any]
    timestamp: float

@dataclass
class CognitiveStepResult:
    step_index: int
    action_type: str
    success: bool
    thought: str
    is_terminal: bool = False # If True, loop should end (Done/Fail)
    reason: Optional[str] = None

class ThinkingLoop:
    """
    FUTUROSOUL Phase 2: The Cognitive Engine.
    Orchestrates the THINK -> DECIDE -> ACT -> REFLECT cycle.
    """
    
    def __init__(
        self,
        worker: HybridWorker,
        capture_fn: Callable[[], Any], # Returns screenshot
        vision_fn: Callable[[Any], Any],  # Returns UI elements (Text + Icons)
        actuation_fn: Callable[[WorkerResult, Any], bool], # Executes action
        approval_fn: Optional[Callable[[WorkerResult], bool]] = None, # Supervised mode
    ):
        self.worker = worker
        self.capture_fn = capture_fn
        self.vision_fn = vision_fn
        self.actuation_fn = actuation_fn
        self.approval_fn = approval_fn
        self.history: List[Dict] = []
        self._running = False

    async def run_step(self, goal: str, step_index: int) -> CognitiveStepResult:
        """
        Execute one complete cognitive cycle.
        """
        logger.info("thinking_loop_step_start", step=step_index)
        
        try:
            # 1. OBSERVE
            observation = await self._observe()
            
            # 2. THINK & DECIDE
            decision = await self._decide(goal, observation)
            
            # Handle terminal actions/signals immediately
            if decision.action_type in ["done", "fail"]:
                success = True
                if decision.action_type == "fail":
                    success = False
                return CognitiveStepResult(
                    step_index=step_index,
                    action_type=decision.action_type,
                    success=success,
                    thought=f"Terminating: {decision.action_type}",
                    is_terminal=True,
                    reason=decision.params.get("reason")
                )

            # 3. APPROVAL (Supervised Mode)
            if self.approval_fn:
                approved = await self.approval_fn(decision)
                if not approved:
                    return CognitiveStepResult(
                        step_index=step_index,
                        action_type="paused",
                        success=False,
                        thought="Action rejected by user.",
                        is_terminal=False # Just pause, don't kill loop? Or maybe allow retry.
                    )

            # 4. ACT
            success = await self._act(decision, observation)
            
            # 5. REFLECT
            self._reflect(decision, success)
            
            return CognitiveStepResult(
                step_index=step_index,
                action_type=decision.action_type,
                success=success,
                thought=f"Executed {decision.action_type}",
                is_terminal=False
            )
            
        except Exception as e:
            logger.error("thinking_loop_error", error=str(e))
            return CognitiveStepResult(
                step_index=step_index,
                action_type="error",
                success=False,
                thought=f"Critical Error: {str(e)}",
                is_terminal=True,
                reason=str(e)
            )

    async def _observe(self) -> Observation:
        """Gather sensory input."""
        logger.debug("phase_observe")
        screenshot = await self.capture_fn()
        elements = []
        if self.vision_fn:
            elements = await self.vision_fn(screenshot)
        
        return Observation(
            screenshot=screenshot,
            ui_elements=elements,
            timestamp=datetime.now().timestamp()
        )

    async def _decide(self, goal: str, obs: Observation) -> WorkerResult:
        """Generate action plan."""
        logger.debug("phase_decide")
        return await self.worker.generate_action(goal, obs.screenshot, obs.ui_elements)

    async def _act(self, decision: WorkerResult, obs: Observation) -> bool:
        """Execute the decision."""
        logger.debug("phase_act", action=decision.action_type)
        return await self.actuation_fn(decision, obs.screenshot)

    def _reflect(self, decision: WorkerResult, success: bool):
        """Internal lightweight reflection."""
        logger.debug("phase_reflect", success=success)
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": decision.action_type,
            "success": success
        })
