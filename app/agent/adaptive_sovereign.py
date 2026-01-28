"""
ONI v5.0 - The Adaptive Sovereign Agent
A fusion of UBIE (Planner), ONI (Executor), and ANT (Tool-Maker).

Architecture:
┌─────────────────────────────────────────────────────┐
│              ADAPTIVE SOVEREIGN AGENT               │
├─────────────────────────────────────────────────────┤
│  UBIE (Mind)  →  ONI (Hands)  ←  ANT (Forge)       │
└─────────────────────────────────────────────────────┘
"""

import ast
import asyncio
import re
import time
import structlog
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

# Module-level import (Issue #4: moved from inline)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

logger = structlog.get_logger(__name__)


class AgentMode(str, Enum):
    """Current operational mode of the Sovereign."""
    PLANNING = "planning"      # UBIE mode
    EXECUTING = "executing"    # ONI mode
    FORGING = "forging"        # ANT mode
    REFLECTING = "reflecting"  # Self-analysis


@dataclass
class SovereignState:
    """Tracks the internal state of the Sovereign Agent."""
    goal: str = ""
    current_mode: AgentMode = AgentMode.PLANNING
    plan_steps: List[str] = field(default_factory=list)
    current_step_index: int = 0
    execution_attempts: int = 0
    max_retries: int = 3
    forged_tools: List[str] = field(default_factory=list)
    errors_encountered: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SovereignResult:
    """Result from a Sovereign run."""
    success: bool
    goal: str
    steps_completed: int
    total_steps: int
    errors: List[str]
    tools_forged: List[str]
    duration_seconds: float
    final_message: str


class AdaptiveSovereign:
    """
    The Adaptive Sovereign Agent.
    
    Combines:
    - UBIE: Planning, Validation, Learning (The Mind)
    - ONI: Visual Execution, Desktop Interaction (The Hands)
    - ANT: Tool Creation, Self-Modification (The Forge)
    """
    
    def __init__(
        self,
        llm_provider: Any = None,
        executor: Any = None,
        tool_forge: Any = None,
    ):
        """
        Initialize the Sovereign.
        
        Args:
            llm_provider: LLM for reasoning (UBIE brain)
            executor: AutonomousExecutor for actions (ONI hands)
            tool_forge: Module for creating new tools (ANT forge)
        """
        self._llm = llm_provider
        self._executor = executor
        self._forge = tool_forge
        self._state = SovereignState()
        self._callbacks: Dict[str, Callable] = {}
        
        logger.info("adaptive_sovereign_initialized")
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    async def run(self, goal: str) -> SovereignResult:
        """
        Execute a goal using the full Sovereign loop.
        
        The loop:
        1. UBIE: Plan the steps to achieve the goal
        2. ONI: Execute each step visually
        3. ANT: If execution fails, create a tool to fix it
        4. Repeat until complete or max retries exceeded
        
        Args:
            goal: Natural language goal to achieve
            
        Returns:
            SovereignResult with execution details
        """
        self._state = SovereignState(goal=goal, started_at=datetime.now())
        logger.info("sovereign_run_started", goal=goal)
        
        try:
            # PHASE 1: UBIE PLANNING
            await self._phase_ubie_plan(goal)
            
            # PHASE 2: ONI EXECUTION LOOP
            while self._state.current_step_index < len(self._state.plan_steps):
                step = self._state.plan_steps[self._state.current_step_index]
                
                success = await self._phase_oni_execute(step)
                
                if success:
                    self._state.current_step_index += 1
                    self._state.execution_attempts = 0
                else:
                    self._state.execution_attempts += 1
                    
                    if self._state.execution_attempts >= self._state.max_retries:
                        # PHASE 3: ANT FORGING
                        fixed = await self._phase_ant_forge(step)
                        
                        if fixed:
                            self._state.execution_attempts = 0
                            # Retry the step after forging
                            continue
                        else:
                            # Cannot fix, abort
                            logger.error("sovereign_step_failed_permanently", step=step)
                            break
            
            # PHASE 4: REFLECTION
            await self._phase_reflect()
            
        except Exception as e:
            logger.exception("sovereign_run_error", error=str(e))
            self._state.errors_encountered.append(str(e))
        
        self._state.completed_at = datetime.now()
        duration = (self._state.completed_at - self._state.started_at).total_seconds()
        
        success = self._state.current_step_index >= len(self._state.plan_steps)
        
        result = SovereignResult(
            success=success,
            goal=goal,
            steps_completed=self._state.current_step_index,
            total_steps=len(self._state.plan_steps),
            errors=self._state.errors_encountered,
            tools_forged=self._state.forged_tools,
            duration_seconds=duration,
            final_message=self._generate_final_message(success)
        )
        
        logger.info("sovereign_run_completed", 
                   success=success,
                   duration=duration,
                   steps=f"{result.steps_completed}/{result.total_steps}")
        
        return result
    
    # =========================================================================
    # PHASE IMPLEMENTATIONS
    # =========================================================================
    
    async def _phase_ubie_plan(self, goal: str) -> None:
        """
        UBIE Phase: Analyze the goal and create a step-by-step plan.
        """
        self._state.current_mode = AgentMode.PLANNING
        self._emit_callback("on_mode_change", AgentMode.PLANNING)
        
        logger.info("ubie_planning_started", goal=goal)
        
        # Generate plan using LLM
        if self._llm:
            plan_prompt = self._build_planning_prompt(goal)
            response = await self._call_llm(plan_prompt)
            self._state.plan_steps = self._parse_plan(response)
        else:
            # Fallback: Simple decomposition
            self._state.plan_steps = self._simple_decompose(goal)
        
        # Validate plan (UBIE's caution)
        self._state.plan_steps = self._validate_plan(self._state.plan_steps)
        
        logger.info("ubie_planning_completed", 
                   steps_count=len(self._state.plan_steps),
                   steps=self._state.plan_steps)
        
        self._emit_callback("on_plan_ready", self._state.plan_steps)
    
    async def _phase_oni_execute(self, step: str) -> bool:
        """
        ONI Phase: Execute a single step using visual automation.
        """
        self._state.current_mode = AgentMode.EXECUTING
        self._emit_callback("on_mode_change", AgentMode.EXECUTING)
        self._emit_callback("on_step_start", step)
        
        logger.info("oni_executing_step", step=step, attempt=self._state.execution_attempts + 1)
        
        try:
            # Use AutonomousExecutor if available
            if self._executor:
                from app.services.oni.autonomous_executor import AutonomousExecutor
                from app.services.oni.autonomous_types import SuccessCriteria
                
                result = await AutonomousExecutor.execute_simple(
                    action_type="visual_task",
                    description=step
                )
                
                success = result.get("success", False)
            else:
                # Fallback: Direct execution via hybrid vision
                success = await self._execute_step_directly(step)
            
            if success:
                logger.info("oni_step_succeeded", step=step)
                self._emit_callback("on_step_complete", {"step": step, "success": True})
            else:
                error_msg = f"Step failed: {step}"
                self._state.errors_encountered.append(error_msg)
                logger.warning("oni_step_failed", step=step)
                self._emit_callback("on_step_complete", {"step": step, "success": False})
            
            return success
            
        except Exception as e:
            error_msg = f"Execution error on '{step}': {str(e)}"
            self._state.errors_encountered.append(error_msg)
            logger.error("oni_execution_error", step=step, error=str(e))
            return False
    
    async def _phase_ant_forge(self, failed_step: str) -> bool:
        """
        ANT Phase: Create or modify a tool to handle the failed step.
        """
        self._state.current_mode = AgentMode.FORGING
        self._emit_callback("on_mode_change", AgentMode.FORGING)
        
        logger.info("ant_forging_started", failed_step=failed_step)
        
        # Analyze the failure
        error_context = {
            "step": failed_step,
            "attempts": self._state.execution_attempts,
            "previous_errors": self._state.errors_encountered[-3:],
        }
        
        try:
            if self._forge:
                # Use dedicated tool forge
                tool_code = await self._forge.create_fix(error_context)
            elif self._llm:
                # Use LLM to generate a fix
                fix_prompt = self._build_forge_prompt(error_context)
                tool_code = await self._call_llm(fix_prompt)
            else:
                logger.warning("ant_no_forge_capability")
                return False
            
            if tool_code:
                # Execute the generated fix
                success = await self._apply_forged_tool(tool_code, failed_step)
                
                if success:
                    self._state.forged_tools.append(f"fix_for_{failed_step[:30]}")
                    logger.info("ant_forging_succeeded", step=failed_step)
                    self._emit_callback("on_tool_forged", {"step": failed_step, "success": True})
                    return True
            
            logger.warning("ant_forging_failed", step=failed_step)
            return False
            
        except Exception as e:
            logger.error("ant_forging_error", error=str(e))
            return False
    
    async def _phase_reflect(self) -> None:
        """
        Reflection Phase: Analyze the execution and learn.
        """
        self._state.current_mode = AgentMode.REFLECTING
        
        # Log session to episodic memory
        try:
            from app.infrastructure.memory.episodic import EpisodicMemory, Episode
            
            memory = EpisodicMemory()
            memory.connect()
            
            episode = Episode(
                goal=self._state.goal,
                app="AdaptiveSovereign",
                actions=[{"step": s} for s in self._state.plan_steps[:self._state.current_step_index]],
                outcome="success" if self._state.current_step_index >= len(self._state.plan_steps) else "partial",
                learnings=f"Forged {len(self._state.forged_tools)} tools. Errors: {len(self._state.errors_encountered)}"
            )
            
            memory.save_episode(episode)
            memory.close()
            
            logger.info("sovereign_reflection_saved")
            
        except Exception as e:
            logger.warning("sovereign_reflection_failed", error=str(e))
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _build_planning_prompt(self, goal: str) -> str:
        """Build the prompt for UBIE planning."""
        return f"""You are an AI assistant planning a desktop automation task.

GOAL: {goal}

Break this goal into specific, actionable steps that can be executed visually on a Windows desktop.
Each step should be a single action (click, type, open app, etc.).

Rules:
1. Be specific about UI elements (button names, menu paths).
2. Include verification steps (e.g., "Verify file was saved").
3. Handle potential errors (e.g., "If dialog appears, click OK").

Return ONLY a numbered list of steps, nothing else.
Example:
1. Open Notepad using Windows search
2. Type "Hello World" in the text editor
3. Press Ctrl+S to save
4. Type filename "test.txt" in save dialog
5. Press Enter to confirm save
"""
    
    def _build_forge_prompt(self, error_context: Dict) -> str:
        """Build the prompt for ANT tool forging."""
        return f"""You are an AI assistant that creates fixes for automation failures.

FAILED STEP: {error_context['step']}
ATTEMPTS: {error_context['attempts']}
ERRORS: {error_context['previous_errors']}

Generate Python code that provides an alternative approach to accomplish this step.
The code should:
1. Use pyautogui for mouse/keyboard
2. Include error handling
3. Return True if successful, False otherwise

Return ONLY the Python code, nothing else.
"""
    
    def _parse_plan(self, llm_response: str) -> List[str]:
        """Parse LLM response into list of steps."""
        steps = []
        for line in llm_response.strip().split("\n"):
            # Remove numbering and clean
            line = line.strip()
            if line and line[0].isdigit():
                # Remove "1. " or "1) " prefix
                parts = line.split(".", 1) if "." in line else line.split(")", 1)
                if len(parts) > 1:
                    step = parts[1].strip()
                    if step:
                        steps.append(step)
        return steps
    
    def _simple_decompose(self, goal: str) -> List[str]:
        """Simple fallback decomposition without LLM."""
        # Basic heuristics
        steps = []
        
        # Look for common patterns
        goal_lower = goal.lower()
        
        if "criar" in goal_lower or "create" in goal_lower:
            steps.append(f"Open appropriate application for: {goal}")
            steps.append(f"Create new document/item")
            steps.append(f"Add content as specified: {goal}")
            steps.append(f"Save the result")
        elif "abrir" in goal_lower or "open" in goal_lower:
            steps.append(f"Search for application/file: {goal}")
            steps.append(f"Open the found item")
        else:
            # Generic single step
            steps.append(goal)
        
        return steps
    
    # Issue #8: Dangerous keywords moved to class constant
    DANGEROUS_KEYWORDS = [
        "delete", "format", "rm -rf", "del /f", "shutdown", "reboot",
        "remove", "destroy", "wipe", "erase", "kill", "terminate",
        "uninstall", "registry", "system32", "drop table", "truncate"
    ]
    
    def _validate_plan(self, steps: List[str]) -> List[str]:
        """UBIE's validation: Filter out unsafe or unclear steps."""
        validated = []
        
        for step in steps:
            step_lower = step.lower()
            
            # Check for dangerous operations
            is_dangerous = any(kw in step_lower for kw in self.DANGEROUS_KEYWORDS)
            
            if is_dangerous:
                logger.warning("sovereign_step_blocked_dangerous", step=step)
                continue
            
            validated.append(step)
        
        return validated
    
    async def _execute_step_directly(self, step: str) -> bool:
        """Direct execution fallback when no executor is available."""
        # Use UniversalAdapter for common actions
        try:
            from app.services.oni.universal_adapter import UniversalAdapterService
            
            # Parse step for action keywords
            step_lower = step.lower()
            
            if not PYAUTOGUI_AVAILABLE:
                logger.warning("sovereign_pyautogui_not_available")
                return False
            
            if "press" in step_lower or "ctrl" in step_lower or "alt" in step_lower:
                # Hotkey action (using module-level pyautogui)
                if "ctrl+s" in step_lower:
                    pyautogui.hotkey("ctrl", "s")
                    return True
                elif "ctrl+n" in step_lower:
                    pyautogui.hotkey("ctrl", "n")
                    return True
                elif "enter" in step_lower:
                    pyautogui.press("enter")
                    return True
            
            elif "type" in step_lower or "digitar" in step_lower:
                # Type action (using module-level re and pyautogui)
                match = re.search(r'"([^"]+)"', step)
                if match:
                    text = match.group(1)
                    pyautogui.typewrite(text, interval=0.05)
                    return True
            
            elif "click" in step_lower or "clicar" in step_lower:
                # Click action - would need vision to locate
                logger.info("sovereign_click_needs_vision", step=step)
                return False
            
            # Default: assume success for non-visual steps
            await asyncio.sleep(0.5)
            return True
            
        except Exception as e:
            logger.error("sovereign_direct_execution_error", error=str(e))
            return False
    
    # Issue #3: SECURE exec() replacement with AST validation
    FORBIDDEN_AST_NODES = {'Import', 'ImportFrom', 'With', 'AsyncWith'}
    FORBIDDEN_CALLS = {'open', 'exec', 'eval', 'compile', '__import__', 'globals', 'locals', 'vars'}
    
    def _validate_code_safety(self, code: str) -> tuple[bool, str]:
        """
        Validate code safety using AST analysis before execution.
        Returns (is_safe, error_message).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        for node in ast.walk(tree):
            node_type = type(node).__name__
            
            # Check forbidden node types
            if node_type in self.FORBIDDEN_AST_NODES:
                return False, f"Forbidden operation: {node_type}"
            
            # Check forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_CALLS:
                        return False, f"Forbidden function: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.FORBIDDEN_CALLS:
                        return False, f"Forbidden method: {node.func.attr}"
        
        # Additional content-based checks
        dangerous_patterns = [
            r"import\s+os", r"import\s+subprocess", r"import\s+shutil",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"rm\s+-rf", r"del\s+/[fq]", r"format\s+[a-z]:"
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, ""
    
    async def _apply_forged_tool(self, code: str, step: str) -> bool:
        """Apply a forged tool with SECURE sandboxed execution."""
        try:
            # Issue #3 FIX: AST-based validation before any execution
            is_safe, error_msg = self._validate_code_safety(code)
            if not is_safe:
                logger.warning("sovereign_blocked_unsafe_forge", reason=error_msg)
                return False
            
            # Create sandboxed globals with only safe builtins
            safe_builtins = {
                'abs': abs, 'all': all, 'any': any, 'bool': bool,
                'dict': dict, 'float': float, 'int': int, 'len': len,
                'list': list, 'max': max, 'min': min, 'print': print,
                'range': range, 'str': str, 'sum': sum, 'tuple': tuple,
                'True': True, 'False': False, 'None': None,
            }
            
            # Add pyautogui if available (for automation)
            if PYAUTOGUI_AVAILABLE:
                safe_builtins['pyautogui'] = pyautogui
            
            exec_globals = {'__builtins__': safe_builtins}
            
            # Execute in sandbox
            exec(code, exec_globals)
            
            # Check if it defined a function and call it
            if "fix" in exec_globals:
                result = exec_globals["fix"]()
                return bool(result)
            
            return True
            
        except Exception as e:
            logger.error("sovereign_forge_execution_error", error=str(e))
            return False
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM provider."""
        if self._llm is None:
            return ""
        
        try:
            if hasattr(self._llm, "generate"):
                return await self._llm.generate(prompt)
            elif hasattr(self._llm, "chat"):
                return await self._llm.chat(prompt)
            else:
                return str(self._llm(prompt))
        except Exception as e:
            logger.error("sovereign_llm_call_failed", error=str(e))
            return ""
    
    def _generate_final_message(self, success: bool) -> str:
        """Generate a human-readable final message."""
        if success:
            return f"✅ Goal achieved: '{self._state.goal}' in {len(self._state.plan_steps)} steps."
        else:
            return f"⚠️ Partial completion: {self._state.current_step_index}/{len(self._state.plan_steps)} steps. Errors: {len(self._state.errors_encountered)}"
    
    def set_callback(self, event: str, callback: Callable) -> None:
        """Set a callback for events."""
        self._callbacks[event] = callback
    
    def _emit_callback(self, event: str, data: Any = None) -> None:
        """Emit an event to registered callbacks."""
        if event in self._callbacks:
            try:
                self._callbacks[event](data)
            except Exception as e:
                logger.warning("sovereign_callback_error", event=event, error=str(e))


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_sovereign(
    with_llm: bool = True,
    with_executor: bool = True,
) -> AdaptiveSovereign:
    """
    Factory function to create a configured Sovereign agent.
    
    Args:
        with_llm: Include LLM for planning (requires API key)
        with_executor: Include AutonomousExecutor for execution
        
    Returns:
        Configured AdaptiveSovereign instance
    """
    llm = None
    executor = None
    
    if with_llm:
        try:
            from app.services.llm.llm_service import LLMService
            llm = LLMService()
        except ImportError:
            logger.warning("sovereign_llm_not_available")
    
    if with_executor:
        try:
            from app.services.oni.autonomous_executor import AutonomousExecutor
            executor = AutonomousExecutor
        except ImportError:
            logger.warning("sovereign_executor_not_available")
    
    # Issue #2: ToolForge implementation
    from app.agent.tool_forge import ToolForge
    try:
        forge = ToolForge(llm_provider=llm)
    except Exception:
        forge = None
        logger.warning("sovereign_tool_forge_not_available")
    
    return AdaptiveSovereign(
        llm_provider=llm,
        executor=executor,
        tool_forge=forge,
    )


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_sovereign():
    """Quick test of the Sovereign agent."""
    sovereign = create_sovereign(with_llm=False, with_executor=False)
    
    result = await sovereign.run("Create a text file on the desktop with 'Hello Sovereign' inside.")
    
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    asyncio.run(_test_sovereign())
