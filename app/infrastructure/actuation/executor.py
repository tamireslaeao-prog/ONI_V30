"""
ONI v2.0 - Resilient Action Executor
Self-healing action execution with retry and verification
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.config import settings
from app.core.exceptions import ActionFailedError, ActionTimeoutError
from app.core.telemetry import telemetry
from app.core.prediction_engine import predictor
from app.infrastructure.actuation.fallback_ladder import FallbackStrategy

logger = structlog.get_logger()


class ActionType(str, Enum):
    """Types of actions."""
    CLICK = "click"
    TYPE = "type"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    DRAG = "drag"
    WAIT = "wait"
    VERIFY = "verify"
    LAUNCH = "launch"
    FOCUS = "focus"


class ActionStatus(str, Enum):
    """Action execution status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Action:
    """Action to execute."""
    type: ActionType
    params: dict[str, Any] = field(default_factory=dict)
    expected_outcome: str | None = None
    timeout: float = 30.0
    retry_count: int = 3
    intent: str | None = None
    strategy: FallbackStrategy = FallbackStrategy.UI_CLICK
    alternatives: list["Action"] = field(default_factory=list)

    

@dataclass
class ActionResult:
    """Result of action execution."""
    action: Action
    status: ActionStatus
    success: bool
    duration_ms: float
    retries: int = 0
    error: str | None = None
    verification: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# Type alias for verification function
VerifyFunc = Callable[[], Coroutine[Any, Any, bool]]


class ResilientExecutor:
    """
    Resilient action executor with self-healing capabilities.
    
    Features:
    - Pre-execution checks
    - Execution monitoring
    - Post-execution verification
    - Automatic retry with exponential backoff
    - Alternative strategy fallback
    - Human escalation
    """
    
    def __init__(
        self,
        mouse: Any = None,
        keyboard: Any = None,
        window_manager: Any = None,
    ) -> None:
        """
        Initialize executor.
        
        Args:
            mouse: Humanized mouse controller
            keyboard: Humanized keyboard controller
            window_manager: Window manager
        """
        self._mouse = mouse
        self._keyboard = keyboard
        self._window_manager = window_manager
        
        self._action_handlers: dict[ActionType, Callable] = {
            ActionType.CLICK: self._execute_click,
            ActionType.TYPE: self._execute_type,
            ActionType.HOTKEY: self._execute_hotkey,
            ActionType.SCROLL: self._execute_scroll,
            ActionType.WAIT: self._execute_wait,
            ActionType.FOCUS: self._execute_focus,
        }
        
        self._execution_history: list[ActionResult] = []
    
    async def execute(
        self,
        action: Action,
        verify_func: VerifyFunc | None = None,
    ) -> ActionResult:
        """Execute action with resilient fallback strategy."""
        import time
        from app.infrastructure.actuation.fallback_ladder import fallback_ladder
        
        start_time = time.perf_counter()
        
        # Determine strategy queue
        # Primary action is first
        queue = [action]
        # Alternatives follow
        queue.extend(action.alternatives)
        
        last_result = None
        
        for attempt_action in queue:
            # Check timeout for this strategy
            strategy_timeout = fallback_ladder.get_timeout(attempt_action.strategy)
            attempt_action.timeout = min(attempt_action.timeout, strategy_timeout)
            
            logger.info("trying_strategy", strategy=attempt_action.strategy.name, intent=attempt_action.intent)
            
            # Use inner execute loop for retries of CURRENT strategy
            last_result = await self._execute_single_strategy(attempt_action, verify_func)
            
            if last_result.success:
                return last_result
                
            # If failed, proceed to next strategy in queue
            logger.warning("strategy_failed", strategy=attempt_action.strategy.name, error=last_result.error)

        # All strategies failed
        return last_result if last_result else ActionResult(
            action=action,
            status=ActionStatus.FAILED,
            success=False,
            duration_ms=(time.perf_counter() - start_time) * 1000,
            error="All strategies failed"
        )

    async def _execute_single_strategy(
        self,
        action: Action,
        verify_func: VerifyFunc | None = None,
    ) -> ActionResult:
        """
        Execute a single action strategy with retry and verification.
        (Original execute logic moved here)
        """
        import time
        start_time = time.perf_counter()
        retries = 0
        last_error = None
        
        while retries <= action.retry_count:
            try:
                # Prediction Check
                context_hash = f"{action.type}_{action.strategy.name}"
                confidence = predictor.predict_success(action.type.value, context_hash)
                
                # Should we skip this strategy entirely?
                if predictor.should_skip_to_fallback(confidence, threshold=0.2):
                    logger.warning("skipping_low_confidence_strategy", strategy=action.strategy.name, confidence=confidence)
                    # Break loop to return failed result immediately, moving to next strategy
                    last_error = f"Skipped due to low confidence ({confidence:.2f})"
                    break 
                
                # Pre-execution check
                await self._pre_execution_check(action)
                
                # Execute with timeout
                async with asyncio.timeout(action.timeout):
                    await self._execute_action(action)
                
                # Post-execution verification
                if verify_func:
                    await asyncio.sleep(0.2)
                    verified = await verify_func()
                    if not verified:
                        raise ActionFailedError("Verification failed")
                
                # Success
                duration = (time.perf_counter() - start_time) * 1000
                result = ActionResult(
                    action=action,
                    status=ActionStatus.COMPLETED,
                    success=True,
                    duration_ms=duration,
                    retries=retries,
                )
                
                self._execution_history.append(result)
                
                # Telemetry Success
                telemetry.log_action({
                    "action_type": action.type.value,
                    "intent": action.intent or "unknown",
                    "strategy_used": action.strategy.name,
                    "attempts": retries + 1,
                    "latency_ms": duration,
                    "success": True,
                    "context": action.params.get("context", {})
                })
                
                # Update Predictor
                predictor.update_outcome(action.type.value, context_hash, True)

                logger.info(
                    "action_completed",
                    action_type=action.type.value,
                    duration_ms=duration,
                    retries=retries,
                )
                
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {action.timeout}s"
                retries += 1
                
            except ActionFailedError as e:
                last_error = str(e)
                retries += 1
                
            except Exception as e:
                last_error = str(e)
                retries += 1
            
            if retries <= action.retry_count:
                logger.warning(
                    "action_retrying",
                    action_type=action.type.value,
                    retry=retries,
                    error=last_error,
                )
                await asyncio.sleep(min(2 ** retries, 10))
        
        # Failure for this strategy
        duration = (time.perf_counter() - start_time) * 1000
        result = ActionResult(
            action=action,
            status=ActionStatus.FAILED,
            success=False,
            duration_ms=duration,
            retries=retries, # adjusted from -1 to actual retries made
            error=last_error,
        )
        
        self._execution_history.append(result)
        
        # Telemetry Failure
        telemetry.log_action({
            "action_type": action.type.value,
            "intent": action.intent or "unknown",
            "strategy_used": action.strategy.name,
            "attempts": retries,
            "latency_ms": duration,
            "success": False,
            "error": last_error,
            "context": action.params.get("context", {})
        })
        
        # Update Predictor (Failure)
        context_hash = f"{action.type}_{action.strategy.name}"
        predictor.update_outcome(action.type.value, context_hash, False)
        
        return result
    
    async def _pre_execution_check(self, action: Action) -> None:
        """Perform pre-execution checks."""
        # Check if target window exists (for focus actions)
        if action.type == ActionType.FOCUS:
            title = action.params.get("title", "")
            if self._window_manager and title:
                window = self._window_manager.find_window(title)
                if not window:
                    raise ActionFailedError(f"Window not found: {title}")
    
    async def _execute_action(self, action: Action) -> None:
        """Execute the action."""
        handler = self._action_handlers.get(action.type)
        if handler:
            await handler(action.params)
        else:
            raise ActionFailedError(f"Unknown action type: {action.type}")
    
    async def _execute_click(self, params: dict[str, Any]) -> None:
        """Execute click action."""
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        double = params.get("double", False)
        
        if self._mouse:
            if double:
                await self._mouse.double_click(x, y)
            else:
                await self._mouse.click(x, y, button)
        else:
            from app.core.safe_execution import SafePrimitive
            if double:
                # SafePrimitive doesn't have doubleClick yet, compose it
                SafePrimitive.safe_click(x, y, clicks=2, button=button)
            else:
                SafePrimitive.safe_click(x, y, button=button)
    
    async def _execute_type(self, params: dict[str, Any]) -> None:
        """Execute type action."""
        text = params.get("text", "")
        
        if self._keyboard:
            await self._keyboard.type_text(text)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_type(text)
    
    async def _execute_hotkey(self, params: dict[str, Any]) -> None:
        """Execute hotkey action."""
        keys = params.get("keys", [])
        
        if self._keyboard:
            await self._keyboard.hotkey(*keys)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_hotkey(*keys)
    
    async def _execute_scroll(self, params: dict[str, Any]) -> None:
        """Execute scroll action."""
        amount = params.get("amount", 3)
        x = params.get("x")
        y = params.get("y")
        
        if self._mouse:
            await self._mouse.scroll(amount, x, y)
        else:
            import pyautogui
            pyautogui.scroll(amount, x, y)
    
    async def _execute_wait(self, params: dict[str, Any]) -> None:
        """Execute wait action."""
        seconds = params.get("seconds", 1.0)
        await asyncio.sleep(seconds)
    
    async def _execute_focus(self, params: dict[str, Any]) -> None:
        """Execute focus window action."""
        title = params.get("title", "")
        
        if self._window_manager:
            success = self._window_manager.focus_window(title)
            if not success:
                raise ActionFailedError(f"Failed to focus window: {title}")
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_success_rate(self, last_n: int = 100) -> float:
        """Get success rate of recent actions."""
        recent = self._execution_history[-last_n:]
        if not recent:
            return 1.0
        
        successes = sum(1 for r in recent if r.success)
        return successes / len(recent)
    
    def get_average_duration(
        self,
        action_type: ActionType | None = None,
        last_n: int = 50,
    ) -> float:
        """Get average action duration."""
        recent = self._execution_history[-last_n:]
        
        if action_type:
            recent = [r for r in recent if r.action.type == action_type]
        
        if not recent:
            return 0.0
        
        return sum(r.duration_ms for r in recent) / len(recent)
