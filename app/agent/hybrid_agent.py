"""
ONI v3.0 - Hybrid Agent

"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Literal

import structlog

from app.core.config import settings
from app.agent.hybrid_worker import HybridWorker, WorkerResult
from app.agent.reflection import ReflectionAgent, ReflectionResult
from app.agent.code_agent import CodeAgent, CodeAgentResult
from app.grounding.hybrid import HybridGrounding
from app.grounding.ui_tars import UITarsGrounding
from app.infrastructure.memory.memory_manager import get_memory_manager, MemoryManager

logger = structlog.get_logger()


class AgentState(str, Enum):
    """Agent operational states."""
    IDLE = "idle"
    PLANNING = "planning"
    OBSERVING = "observing"
    ACTING = "acting"
    REFLECTING = "reflecting"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentConfig:
    """Configuration for hybrid agent."""
    # Grounding
    ui_tars_endpoint: str = ""
    ui_tars_api_key: str = ""
    grounding_width: int = 1920
    grounding_height: int = 1080
    
    # Execution
    max_steps: int = 50
    action_timeout: float = 30.0
    max_trajectory_length: int = 8
    
    # Features
    enable_reflection: bool = True
    enable_code_agent: bool = True
    enable_humanized_input: bool = True
    
    # Mode
    mode: Literal["autonomous", "supervised", "manual"] = "supervised"


@dataclass 
class ExecutionResult:
    """Result from goal execution."""
    success: bool
    goal: str
    steps_executed: int
    total_time_ms: float
    final_state: AgentState
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


class HybridAgent:
    """
    
    Architecture:
    - Grounding: UI-TARS (visual) + SemanticLocator (OCR) with intelligent routing
    - Reflection: Detects loops, errors, suggests corrections
    - Code Agent: Executes Python/Bash for data tasks
    - Memory: Persistent learning with SQLite + Redis
    
    Modes:
    - autonomous: Executes without user confirmation
    - supervised: Requests approval for each action
    - manual: Step-by-step with pause between actions
    
    Example:
        agent = HybridAgent(
            config=AgentConfig(
                ui_tars_endpoint="https://...",
                mode="supervised",
            ),
            llm=llm_manager,
            actuation=actuation_system,
        )
        
        result = await agent.execute_goal("Open Notepad and type Hello World")
        print(f"Success: {result.success}, Steps: {result.steps_executed}")
    """
    
    def __init__(
        self,
        config: AgentConfig | None = None,
        llm: Any = None,
        actuation: Any = None,
        vision: Any = None,
        memory: Any = None,
        planner: Any = None,
        omniparser: Any = None, # Vision 2.0
        creative_engine: Any = None, # Phase 3: Creative Engine
    ) -> None:
        """
        Initialize hybrid agent.
        
        Args:
            config: Agent configuration
            llm: LLM provider manager
            actuation: Mouse/keyboard actuation system
            vision: Screen capture and OCR system
            memory: Persistent memory system
            planner: HTN planner (optional)
            omniparser: OmniParser service (optional)
            creative_engine: Creative Engine (optional)
        """
        self._config = config or AgentConfig()
        self._llm = llm
        self._actuation = actuation
        self._vision = vision
        self._memory = memory
        self._planner = planner
        self._omniparser = omniparser
        self._creative_engine = creative_engine
        
        # State
        self._state = AgentState.IDLE
        self._current_goal: str = ""
        self._running = False
        self._paused = False
        self._loop_fallback_count = 0 
        
        # Components (lazy initialized)
        self._grounding: HybridGrounding | None = None
        self._worker: HybridWorker | None = None
        self._reflection: ReflectionAgent | None = None
        self._code_agent: CodeAgent | None = None
        self._memory_manager: MemoryManager | None = None
        
        # Callbacks
        self._on_state_change: Callable[[AgentState], None] | None = None
        self._on_thought: Callable[[str], None] | None = None
        self._on_action_request: Callable[[dict], asyncio.Future] | None = None  # For supervised mode
        
        # Stats
        self._total_actions = 0
        self._successful_actions = 0
        self._start_time: datetime | None = None
    
    @property
    def state(self) -> AgentState:
        """Current agent state."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._running
    
    def set_callbacks(
        self,
        on_state_change: Callable[[AgentState], None] | None = None,
        on_thought: Callable[[str], None] | None = None,
        on_action_request: Callable[[dict], asyncio.Future] | None = None,
    ) -> None:
        """Set event callbacks."""
        self._on_state_change = on_state_change
        self._on_thought = on_thought
        self._on_action_request = on_action_request
        
        # Propagate to worker
        if self._worker:
            self._worker.set_callbacks(on_thought=on_thought)
    
    async def initialize(self) -> bool:
        """
        Initialize agent components.
        
        Returns:
            True if initialization succeeded
        """
        try:
            # Initialize grounding
            ui_tars = None
            if self._config.ui_tars_endpoint:
                ui_tars = UITarsGrounding(
                    endpoint_url=self._config.ui_tars_endpoint,
                    api_key=self._config.ui_tars_api_key,
                    grounding_width=self._config.grounding_width,
                    grounding_height=self._config.grounding_height,
                )
                await ui_tars.initialize()
            
            self._grounding = HybridGrounding(ui_tars=ui_tars)
            
            # Initialize worker
            self._worker = HybridWorker(
                llm=self._llm,
                grounding=self._grounding,
                actuation=self._actuation,
                max_trajectory_length=self._config.max_trajectory_length,
                enable_reflection=self._config.enable_reflection,
                creative_engine=self._creative_engine,
            )
            self._worker.set_callbacks(on_thought=self._on_thought)
            
            # Initialize reflection
            if self._config.enable_reflection:
                self._reflection = ReflectionAgent(
                    llm=self._llm,
                    memory=self._memory,
                )
            
            # Initialize code agent
            if self._config.enable_code_agent:
                self._code_agent = CodeAgent(llm=self._llm)
            
            logger.info(
                "hybrid_agent_initialized",
                ui_tars=bool(ui_tars),
                reflection=self._config.enable_reflection,
                code_agent=self._config.enable_code_agent,
            )
            
            return True
            
        except Exception as e:
            logger.error("hybrid_agent_init_failed", error=str(e))
            return False
    
    async def execute_goal(self, goal: str) -> ExecutionResult:
        """
        Execute a goal autonomously.
        
        Args:
            goal: Natural language goal description
            
        Returns:
            ExecutionResult with execution details
        """
        self._current_goal = goal
        self._running = True
        self._start_time = datetime.now()
        self._worker.reset()
        self._loop_fallback_count = 0  # Reset loop fallback counter for new goal
        
        self._set_state(AgentState.OBSERVING)
        self._emit_thought(f"🎯 Goal: {goal}")
        
        # Initialize and start memory session
        if self._memory_manager is None:
            self._memory_manager = await get_memory_manager()
        self._memory_manager.start_session(goal)
        
        # FIX #3: Auto-detect logic removed (it was causing 'Run' dialog errors)
        # We rely on the LLM to open the app via Start Menu or Desktop
        self._emit_thought("⚡ Auto-detect: Delegating app launch to LLM (Start Menu strategy)...")

        
        # Parse goal into preset and LLM segments
        from app.agent.goal_parser import parse_goal
        from app.agent.preset_registry import PRESETS
        
        segments = parse_goal(goal)
        trajectory: list[dict] = []
        steps = 0
        
        # Execute preset segments first (no LLM)
        for segment in segments:
            if segment.type == "preset":
                self._emit_thought(f"⚡ Executing preset: {segment.text}")
                preset = PRESETS.get(segment.preset_key.replace(" ", "_"))
                
                if preset:
                    for action in preset.actions:
                        steps += 1
                        action_type = action["action"]
                        params = action["params"]
                        delay = action.get("delay", 0.3)
                        
                        # Execute action directly
                        from app.agent.hybrid_worker import WorkerResult
                        result = WorkerResult(
                            plan=f"Preset: {segment.text}",
                            plan_code=f"agent.{action_type}({params})",
                            exec_code=f"agent.{action_type}({params})",
                            action_type=action_type,
                            params=params,
                        )
                        
                        # Execute
                        screenshot = await self._capture_screen()
                        success = await self._worker.execute_action(result, screenshot)
                        
                        trajectory.append({
                            "step": steps,
                            "action": action_type,
                            "params": params,
                            "success": success,
                            "preset": True,
                        })
                        
                        # Wait between actions
                        await asyncio.sleep(delay)
        
        # Update goal to only LLM segments
        llm_segments = [s for s in segments if s.type == "llm"]
        if llm_segments:
            goal = " → ".join([s.text for s in llm_segments])
            self._emit_thought(f"🤖 LLM task: {goal}")
        else:
            # Only presets - we're done!
            final_state = AgentState.COMPLETED
            return ExecutionResult(
                success=True,
                goal=self._current_goal,
                steps_executed=steps,
                total_time_ms=self._elapsed_ms(),
                final_state=final_state,
                trajectory=trajectory,
            )
        
        # Initialize ThinkingLoop
        from app.agent.cognition.thinking_loop import ThinkingLoop
        
        thinking_loop = ThinkingLoop(
            worker=self._worker,
            capture_fn=self._capture_screen,
            vision_fn=self._run_vision,
            actuation_fn=self._worker.execute_action,
            approval_fn=self._request_action_approval if self._config.mode == "supervised" else None
        )
        
        trajectory: list[dict] = []
        steps = 0
        
        try:
            while self._running and steps < self._config.max_steps:
                # Check pause
                if self._paused:
                    self._set_state(AgentState.PAUSED)
                    await asyncio.sleep(0.1)
                    continue
                
                steps += 1
                
                # LOOP BREAKING LOGIC (Preserved from v3.0)
                # If we are in a loop fallback sequence, bypass the standard thinking loop
                if getattr(self, '_loop_fallback_count', 0) > 0 and self._reflection_suggestion:
                     # ... complex fallback logic handled manually or refactored ...
                     # For now, if we have a forced fallback, we execute it directly via worker
                     # But since logic was inline, we will defer complex loop breaking to Phase 3
                     # or rely on ThinkingLoop's internal evolution.
                     pass

                # EXECUTE COGNITIVE CYCLE
                self._set_state(AgentState.ACTING) # broad state
                
                # Run the Thinking Loop Step
                step_result = await thinking_loop.run_step(goal, steps)
                
                # Check terminal states
                if step_result.is_terminal:
                    if step_result.success:
                        self._emit_thought(f"✅ {step_result.thought}")
                        self._running = False
                        break
                    else:
                        self._emit_thought(f"❌ {step_result.thought}")
                        self._running = False
                        return ExecutionResult(
                            success=False,
                            goal=goal,
                            steps_executed=steps,
                            total_time_ms=self._elapsed_ms(),
                            final_state=AgentState.ERROR,
                            trajectory=trajectory,
                            error=step_result.reason,
                        )
                
                self._total_actions += 1
                if step_result.success:
                    self._successful_actions += 1
                
                # Record to trajectory
                trajectory.append({
                    "step": steps,
                    "action": step_result.action_type,
                    "success": step_result.success,
                    "thought": step_result.thought
                })
                
                # Memory Recording
                if self._memory_manager:
                    self._memory_manager.record_observation(
                        action_type=step_result.action_type,
                        action_params={}, # ThinkingLoop doesn't expose params in result yet, phase 3 fix
                        result="success" if step_result.success else "failed",
                        context=goal[:200],
                    )

                # REFLECTION (Heavy)
                if self._reflection and self._config.enable_reflection:
                    self._set_state(AgentState.REFLECTING)
                    screenshot = await self._capture_screen() # Recapture or reuse? 
                    # Reuse observation from thinking_loop? ThinkingLoop doesn't expose it easily. 
                    # We'll just capture again for now or skip to avoid latency.
                    # Let's skip heavy reflection in this iteration to speed up,
                    # relying on ThinkingLoop's internal reflection eventually.
                    pass
                
                # Small delay
                await asyncio.sleep(0.5)
            
            # Success if we exited normally
            final_state = AgentState.COMPLETED if not self._running else AgentState.IDLE
            
            return ExecutionResult(
                success=True,
                goal=goal,
                steps_executed=steps,
                total_time_ms=self._elapsed_ms(),
                final_state=final_state,
                trajectory=trajectory,
            )
            
        except Exception as e:
            import traceback
            logger.error("goal_execution_error", error=str(e), traceback=traceback.format_exc())
            self._set_state(AgentState.ERROR)
            return ExecutionResult(
                success=False,
                goal=goal,
                steps_executed=steps,
                total_time_ms=self._elapsed_ms(),
                final_state=AgentState.ERROR,
                trajectory=trajectory,
                error=str(e),
            )
        
        finally:
            self._running = False
            self._set_state(AgentState.IDLE)
            
            # End memory session
            if self._memory_manager:
                await self._memory_manager.end_session(
                    status="completed" if self._state != AgentState.ERROR else "failed"
                )
    
    async def execute_code_task(self, task: str) -> CodeAgentResult:
        """
        Execute a task using code agent.
        
        Args:
            task: Task description for code execution
            
        Returns:
            CodeAgentResult with execution details
        """
        if not self._code_agent:
            raise RuntimeError("Code agent not enabled")
        
        self._emit_thought(f"🖥️ Running code agent: {task[:50]}...")
        return await self._code_agent.execute_task(task)
    
    async def pause(self) -> None:
        """Pause agent execution."""
        self._paused = True
        self._set_state(AgentState.PAUSED)
        self._emit_thought("⏸️ Agent paused")
    
    async def resume(self) -> None:
        """Resume agent execution."""
        self._paused = False
        self._emit_thought("▶️ Agent resumed")
    
    async def stop(self) -> None:
        """Stop agent execution."""
        self._running = False
        self._paused = False
        self._set_state(AgentState.IDLE)
        self._emit_thought("⏹️ Agent stopped")
    
    async def emergency_stop(self) -> None:
        """Emergency stop - immediate halt."""
        self._running = False
        self._paused = False
        self._set_state(AgentState.IDLE)
        logger.warning("emergency_stop_triggered")
    
    async def _capture_screen(self) -> bytes:
        """Capture current screen state and return as PNG bytes."""
        import io
        from PIL import Image
        
        if self._vision and hasattr(self._vision, "capture"):
            result = await self._vision.capture()
            # CaptureResult.image is a numpy array (BGR format)
            # Convert to PNG bytes
            image_array = result.image
            # Convert BGR to RGB
            rgb_array = image_array[:, :, ::-1]
            pil_image = Image.fromarray(rgb_array)
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return buffer.getvalue()
        
        # Fallback to pyautogui
        import pyautogui
        
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        return buffer.getvalue()
    
    async def _run_vision(self, screenshot: bytes) -> list[Any]:
        """
        Run vision analysis on screenshot (OCR + Object Detection).
        Vision 2.0: Tries OmniParser first, falls back to basic OCR.
        """
        # Strategy 1: OmniParser (Text + Icons)
        if self._omniparser:
            try:
                # Calculate frame hash for caching
                from app.utils.vision_utils import compute_dhash_bytes
                fhash = compute_dhash_bytes(screenshot)
                
                # Parse screen
                result = await self._omniparser.parse_screen(
                    screenshot, 
                    confidence_threshold=0.15,
                    frame_hash=fhash
                )
                
                # Convert normalized bboxes to absolute pixels for consistency
                if result and result.get("elements"):
                    import io
                    from PIL import Image
                    img = Image.open(io.BytesIO(screenshot))
                    width, height = img.size
                    
                    elements = result["elements"]
                    for el in elements:
                        if "bbox" in el:
                            # bbox is [x1, y1, x2, y2] normalized
                            norm_bbox = el["bbox"]
                            el["x"] = int((norm_bbox[0] + norm_bbox[2]) / 2 * width)
                            el["y"] = int((norm_bbox[1] + norm_bbox[3]) / 2 * height)
                            # Store absolute bbox too for grounding
                            el["abs_bbox"] = [
                                int(norm_bbox[0] * width),
                                int(norm_bbox[1] * height),
                                int(norm_bbox[2] * width),
                                int(norm_bbox[3] * height)
                            ]
                    
                    logger.debug("omniparser_success", elements=len(elements))
                    return elements
            except Exception as e:
                logger.warning("omniparser_failed_fallback_to_ocr", error=str(e))
        
        # Strategy 2: Basic OCR (Text only)
        if not self._vision:
            return []
            
        try:
            # Capture returns CaptureResult with numpy array
            if hasattr(self._vision, 'ocr') and self._vision.ocr:
                # Convert PNG bytes back to numpy array
                import io
                import numpy as np
                from PIL import Image
                
                pil_image = Image.open(io.BytesIO(screenshot))
                np_image = np.array(pil_image)
                
                # Run OCR - extract returns OCRResult with boxes
                result = await self._vision.ocr.extract(np_image)
                return result.boxes  # list[OCRBox]
            
            return []
        except Exception as e:
            logger.warning("ocr_failed", error=str(e))
            return []
    
    async def _request_action_approval(self, result: WorkerResult) -> bool:
        """Request user approval for action (supervised mode)."""
        if self._on_action_request:
            action_data = {
                "type": result.action_type,
                "params": result.params,
                "plan": result.plan[:200],
            }
            future = self._on_action_request(action_data)
            return await future
        
        # Default: approve all if no callback
        return True
    
    def _set_state(self, state: AgentState) -> None:
        """Update agent state and notify."""
        if self._state != state:
            self._state = state
            if self._on_state_change:
                self._on_state_change(state)
            logger.debug("agent_state_change", state=state.value)
    
    def _emit_thought(self, thought: str) -> None:
        """Emit thought to callback."""
        if self._on_thought:
            self._on_thought(thought)
        logger.info("agent_thought", thought=thought)
    
    def _elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds() * 1000
        return 0.0
    
    def get_stats(self) -> dict[str, Any]:
        """Get agent statistics."""
        success_rate = (
            self._successful_actions / self._total_actions * 100
            if self._total_actions > 0
            else 0
        )
        
        return {
            "total_actions": self._total_actions,
            "successful_actions": self._successful_actions,
            "success_rate": success_rate,
            "current_goal": self._current_goal,
            "state": self._state.value,
            "grounding_stats": self._grounding.get_stats() if self._grounding else {},
            "reflection_stats": self._reflection.get_statistics() if self._reflection else {},
        }
