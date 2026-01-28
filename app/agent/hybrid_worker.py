"""
ONI v4.0 - Hybrid Worker Agent
Now includes ReflectiveCoT for structured reasoning.
"""
import asyncio
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

import structlog

from app.core.config import settings
from app.grounding.hybrid import HybridGrounding, GroundingResult
from app.grounding.ui_tars import UITarsGrounding, GroundingError
from app.infrastructure.knowledge.routines_loader import get_routines_loader

# Import ReflectiveCoT for v4.0 reasoning
try:
    from app.agent.reflective_cot import ReflectiveCoTAgent, get_reflective_agent
    HAS_REFLECTIVE_COT = True
except ImportError:
    HAS_REFLECTIVE_COT = False

logger = structlog.get_logger()


@dataclass
class WorkerResult:
    """Result from worker action generation."""
    plan: str
    plan_code: str
    exec_code: str
    action_type: str
    params: dict[str, Any]
    reflection: str | None = None
    confidence: float = 0.9


@dataclass
class Trajectory:
    """Agent's execution trajectory for reflection."""
    steps: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[bytes] = field(default_factory=list)
    
    def add_step(
        self,
        action: str,
        result: str,
        screenshot: bytes | None = None,
    ) -> None:
        self.steps.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        if screenshot:
            self.screenshots.append(screenshot)
    
    def get_recent(self, n: int = 5) -> list[dict[str, Any]]:
        return self.steps[-n:]


class HybridWorker:
    """
    
    From Agent-S:
    - LLM-based action generation with structured prompts
    - Reflection on trajectory for loop detection
    - Code agent integration for data tasks
    
    From ONI:
    - Humanized mouse movement (Bezier curves, Fitts's Law)
    - Humanized keyboard (variable WPM, typo simulation)
    - Win32 API for reliable input injection
    - Pre-defined routines for common tasks
    
    Example:
        worker = HybridWorker(
            llm=llm_manager,
            grounding=HybridGrounding(...),
            actuation=actuation_system,
        )
        
        result = await worker.generate_and_execute(
            instruction="Open Notepad and type Hello World",
            screenshot=screenshot_bytes,
        )
    """
    
    # System prompt template (inspired by Agent-S procedural memory)
    SYSTEM_PROMPT = textwrap.dedent("""
        You are an expert GUI automation agent. Your task: {task}
        You are working on {platform}.
        
        # Available Actions
        - click(description: str) - Click on a visible element by its text/description
        - type(text: str) - Type text at cursor position
        - hotkey(key1, key2, ...) - Press keyboard shortcut with separate keys
        - scroll(direction: str, amount: int) - Scroll up/down
        - wait(seconds: float) - Wait before next action
        - generate_assets(mood: str, style: str) - Generate SVG/Palette (Phase 3)
        - done() - Task completed successfully
        - fail(reason: str) - Task cannot be completed
        
        # CRITICAL: HOW TO OPEN ANY APPLICATION
        You MUST follow these steps IN ORDER:
        STEP 1: hotkey("win") - FIRST open Start Menu (Search)
        STEP 2: type("appname") - THEN type the app name
        STEP 3: wait(1.0) - WAIT a moment for search results
        STEP 4: hotkey("enter") - FINALLY press Enter
        
        If an app is not open, your FIRST action MUST be: agent.hotkey("win")
        
        ## Common app names:
        - CorelDRAW: "coreldraw"
        - Photoshop: "photoshop"
        - Paint: "mspaint"
        - Notepad: "notepad"
        - Calculator: "calc"
        
        # Response Format
        ```python
        agent.hotkey("win")
        ```
        
        ## RULES:
        1. ONE action per response only
        2. Use hotkey("key1", "key2") format
        3. To open apps: FIRST Start Menu (Win), THEN type, THEN Enter
        4. Call done() ONLY when task is fully completed
    """).strip()
    
    def __init__(
        self,
        llm: Any = None,
        grounding: HybridGrounding | None = None,
        actuation: Any = None,
        platform: str = "windows",
        max_trajectory_length: int = 8,
        enable_reflection: bool = True,
        creative_engine: Any = None, # Phase 3
    ) -> None:
        """
        Initialize hybrid worker.
        
        Args:
            llm: LLM provider
            grounding: Hybrid grounding system
            actuation: Actuation system
            platform: OS platform
            max_trajectory_length: Max context
            enable_reflection: Enable reflection
            creative_engine: Creative Engine service
        """
        self._llm = llm
        self._grounding = grounding
        self._actuation = actuation
        self._platform = platform
        self._max_trajectory_length = max_trajectory_length
        self._enable_reflection = enable_reflection
        self._creative_engine = creative_engine
        
        # State
        self._trajectory = Trajectory()
        self._current_task: str = ""
        self._turn_count = 0
        self._notes: list[str] = []  # Knowledge buffer like Agent-S
        self._routines_loader = None  # Lazy loaded
        
        # Callbacks
        self._on_thought: Callable[[str], None] | None = None
        self._on_action: Callable[[dict], None] | None = None
    
    def set_callbacks(
        self,
        on_thought: Callable[[str], None] | None = None,
        on_action: Callable[[dict], None] | None = None,
    ) -> None:
        """Set callback functions for events."""
        self._on_thought = on_thought
        self._on_action = on_action
    
    def reset(self) -> None:
        """Reset worker state for new task."""
        self._trajectory = Trajectory()
        self._turn_count = 0
        self._notes = []
    
    async def generate_action(
        self,
        instruction: str,
        screenshot: bytes,
        ui_elements: list[Any] | None = None, # Renamed from ocr_boxes
    ) -> WorkerResult:
        """
        Generate next action based on instruction and screen state.
        
        Args:
            instruction: Task instruction
            screenshot: Current screenshot (for grounding, not LLM)
            ui_elements: Pre-computed vision results (OmniParser or OCR)
            
        Returns:
            WorkerResult with action to execute
        """
        self._current_task = instruction
        
        # Lazy-load routines loader
        if self._routines_loader is None:
            self._routines_loader = await get_routines_loader()
        
        # Build prompt with Vision context
        prompt = self._build_prompt(instruction, ui_elements, self._trajectory)
        
        # Generate with LLM (or Antigravity Bridge)
        if self._llm is None:
            raise RuntimeError("LLM not configured")
        
        # Extract OCR/Text for bridge (backward compatibility)
        ocr_text = []
        if ui_elements:
            for el in ui_elements[:30]:
                if isinstance(el, dict):
                    if el.get('text'):
                         ocr_text.append(el['text'])
                elif hasattr(el, 'text'):
                    ocr_text.append(el.text)
        
        # Get previous actions
        prev_actions = self._trajectory.get_recent(5) if self._trajectory.steps else []
        
        # Call LLM/Bridge - pass extra data if supported
        try:
            response = await self._llm.generate(
                prompt=prompt,
                screenshot=screenshot if hasattr(self._llm, 'generate') else None,
                ocr_text=ocr_text,
                goal=instruction,
                previous_actions=prev_actions,
            )
        except TypeError:
            # Fallback for providers that don't accept extra params
            response = await self._llm.generate(prompt=prompt)
        
        # Parse response
        plan_code = self._parse_code(response.text)
        action_type, params = self._parse_action(plan_code)
        
        self._emit_thought(f"🎯 Next: {action_type}")
        self._turn_count += 1
        
        return WorkerResult(
            plan=response.text,
            plan_code=plan_code,
            exec_code=plan_code,
            action_type=action_type,
            params=params,
        )
    
    async def execute_action(
        self,
        result: WorkerResult,
        screenshot: bytes,
    ) -> bool:
        """
        Execute generated action with humanized input.
        """
        # Phase 3: Runtime Guardian
        try:
            from app.infrastructure.safety.action_guardian import ActionGuardian
            guardian = ActionGuardian()
            guardian.validate_action(result.action_type, result.params)
        except Exception as e:
            logger.error("guardian_blocked_action", error=str(e))
            self._emit_thought(f"🛡️ Guardian Blocked: {e}")
            self._trajectory.add_step(result.action_type, f"Blocked: {e}")
            return False

        action_type = result.action_type
        params = result.params
        
        try:
            if action_type == "click":
                return await self._execute_click(params, screenshot)
            elif action_type == "type":
                return await self._execute_type(params)
            elif action_type == "hotkey":
                return await self._execute_hotkey(params)
            elif action_type == "scroll":
                return await self._execute_scroll(params)
            elif action_type == "drag":
                return await self._execute_drag(params)
            elif action_type == "wait":
                return await self._execute_wait(params)
            elif action_type == "generate_assets":
                return await self._execute_generate_assets(params)
            elif action_type == "done":
                self._emit_thought("✅ Task completed!")
                return True
            elif action_type == "fail":
                self._emit_thought(f"❌ Task failed: {params.get('reason', 'unknown')}")
                return False
            else:
                logger.warning("unknown_action_type", action_type=action_type)
                return False
                
        except Exception as e:
            logger.error("action_execution_failed", action=action_type, error=str(e))
            self._trajectory.add_step(action_type, f"Error: {e}")
            return False
    
    async def _execute_click(
        self,
        params: dict[str, Any],
        screenshot: bytes,
    ) -> bool:
        """Execute click with direct coordinates OR grounding-based location."""
        clicks = params.get("clicks", 1)
        button = params.get("button", "left")
        
        # Priority 1: Direct coordinates from LLM vision analysis
        if "x" in params and "y" in params:
            x = int(params["x"])
            y = int(params["y"])
            
            # Execute with humanized mouse
            if self._actuation and hasattr(self._actuation, "mouse"):
                for _ in range(clicks):
                    await self._actuation.mouse.click(x, y, button)
                    if clicks > 1:
                        await asyncio.sleep(0.1)
            
            self._emit_thought(f"🖱️ Clicked at ({x}, {y})")
            self._trajectory.add_step(f"click({x}, {y})", "success")
            
            if self._on_action:
                self._on_action({
                    "type": "click",
                    "target": f"({x}, {y})",
                    "coordinates": (x, y),
                })
            
            return True
        
        # Priority 2: Description-based - use grounding to find element
        description = params.get("description", "")
        if description:
            if not self._grounding:
                raise RuntimeError("Grounding not configured")
            
            try:
                result = await self._grounding.locate(description, screenshot)
            except GroundingError as e:
                self._emit_thought(f"⚠️ Could not find: {description}")
                return False
            
            if self._actuation and hasattr(self._actuation, "mouse"):
                for _ in range(clicks):
                    await self._actuation.mouse.click(result.x, result.y, button)
                    if clicks > 1:
                        await asyncio.sleep(0.1)
            
            self._emit_thought(f"🖱️ Clicked '{description}' at ({result.x}, {result.y})")
            self._trajectory.add_step(f"click({description})", f"at ({result.x}, {result.y})")
            
            if self._on_action:
                self._on_action({
                    "type": "click",
                    "target": description,
                    "coordinates": (result.x, result.y),
                })
            
            return True
        
        self._emit_thought("⚠️ Click action missing coordinates or description")
        return False
    
    async def _execute_drag(self, params: dict[str, Any]) -> bool:
        """Execute click-and-drag from one point to another."""
        x1 = int(params.get("x1", 0))
        y1 = int(params.get("y1", 0))
        x2 = int(params.get("x2", 0))
        y2 = int(params.get("y2", 0))
        
        if self._actuation and hasattr(self._actuation, "mouse"):
            # Move to start, press, drag to end, release
            await self._actuation.mouse.move(x1, y1)
            await asyncio.sleep(0.1)
            await self._actuation.mouse.press()
            await asyncio.sleep(0.05)
            await self._actuation.mouse.move(x2, y2, duration=0.3)
            await asyncio.sleep(0.05)
            await self._actuation.mouse.release()
        
        self._emit_thought(f"🖱️ Dragged from ({x1}, {y1}) to ({x2}, {y2})")
        self._trajectory.add_step(f"drag({x1},{y1} -> {x2},{y2})", "success")
        
        if self._on_action:
            self._on_action({
                "type": "drag",
                "start": (x1, y1),
                "end": (x2, y2),
            })
        
        return True
    
    async def _execute_type(self, params: dict[str, Any]) -> bool:
        """Execute typing with humanized keyboard."""
        text = params.get("text", "")
        
        if self._actuation and hasattr(self._actuation, "keyboard"):
            await self._actuation.keyboard.type_text(text)
        
        self._emit_thought(f"⌨️ Typed: '{text[:30]}...' " if len(text) > 30 else f"⌨️ Typed: '{text}'")
        self._trajectory.add_step(f"type({text[:20]}...)", "success")
        
        return True
    
    async def _execute_hotkey(self, params: dict[str, Any]) -> bool:
        """Execute keyboard shortcut."""
        keys = params.get("keys", [])
        
        if self._actuation and hasattr(self._actuation, "keyboard"):
            await self._actuation.keyboard.hotkey(*keys)
        
        key_str = "+".join(keys)
        self._emit_thought(f"⌨️ Hotkey: {key_str}")
        self._trajectory.add_step(f"hotkey({key_str})", "success")
        
        return True
    
    async def _execute_scroll(self, params: dict[str, Any]) -> bool:
        """Execute scroll."""
        direction = params.get("direction", "down")
        amount = params.get("amount", 3)
        
        scroll_amount = amount if direction == "up" else -amount
        
        if self._actuation and hasattr(self._actuation, "mouse"):
            await self._actuation.mouse.scroll(scroll_amount)
        
        self._emit_thought(f"📜 Scrolled {direction} {amount}")
        self._trajectory.add_step(f"scroll({direction}, {amount})", "success")
        
        return True
    
    async def _execute_wait(self, params: dict[str, Any]) -> bool:
        """Execute wait."""
        seconds = params.get("seconds", 1.0)
        
        await asyncio.sleep(seconds)
        
        self._emit_thought(f"⏳ Waited {seconds}s")
        self._trajectory.add_step(f"wait({seconds})", "success")
        
        return True

    async def _execute_generate_assets(self, params: dict[str, Any]) -> bool:
        """Generating creative assets (Phase 3)."""
        mood = params.get("mood", "cyberpunk")
        style = params.get("style", "geometric")
        
        if not self._creative_engine:
            self._emit_thought("⚠️ Creative Engine not available")
            return False

        try:
            # Generate assets
            result = self._creative_engine.generate_theme_assets(mood=mood, style=style)
            
            # Save to disk (RENDER folder)
            import os
            render_dir = "D:\\RENDER"
            if not os.path.exists(render_dir):
                os.makedirs(render_dir)
                
            timestamp = int(datetime.now().timestamp())
            svg_path = f"{render_dir}\\oni_art_{timestamp}.svg"
            
            with open(svg_path, "w") as f:
                f.write(result["background_svg"])
                
            palette = result["palette"]
            info = f"Generated {mood}/{style} art at {svg_path}. Colors: {palette.primary}, {palette.secondary}"
            
            self._emit_thought(f"🎨 {info}")
            self._trajectory.add_step(f"generate_assets({mood})", f"Saved to {svg_path}")
            return True
            
        except Exception as e:
            logger.error("asset_generation_failed", error=str(e))
            self._emit_thought(f"❌ Asset Loop Failed: {e}")
            return False
    
    def _build_prompt(
        self, 
        goal: str, 
        ui_elements: list[Any] | None = None, # Previously ocr_boxes
        trajectory: Trajectory | None = None,
    ) -> str:
        """
        Build prompt for the LLM.
        Vision 2.0: Supports rich UI elements (Text + Icons).
        """
        prompt = self.SYSTEM_PROMPT.format(
            task=goal,
            platform=self._platform,
        )
        
        # Format trajectory (history)
        traj_obj = trajectory or self._trajectory
        history_str = ""
        if isinstance(traj_obj, Trajectory):
            steps = traj_obj.get_recent(5)
            lines = []
            for s in steps:
                lines.append(f"- {s.get('action')}: {s.get('result')}")
            history_str = "\n".join(lines)
        elif isinstance(traj_obj, list):
            # Fallback if raw list passed
            lines = []
            for s in traj_obj[-5:]:
                 lines.append(f"- {s.get('action')}: {s.get('success', 'unknown')}")
            history_str = "\n".join(lines)

        prompt += f"\n\n# Previous Actions:\n{history_str}\n"

        # Format UI Elements (Screen State)
        if ui_elements:
            prompt += "\n# Current Screen Elements (Vision 2.0):\n"
            
            # Sort by Y then X for natural reading order
            # Handle both dicts (OmniParser) and OCRBox objects
            def get_sort_key(e):
                if isinstance(e, dict):
                    return (e.get('y', 0), e.get('x', 0))
                return (getattr(e, 'midpoint', (0,0))[1], getattr(e, 'midpoint', (0,0))[0])
                
            sorted_elements = sorted(ui_elements, key=get_sort_key)
            
            lines = []
            for el in sorted_elements[:30]: # Limit to 30 important elements
                # Handle Dict (OmniParser/Vision 2.0)
                if isinstance(el, dict):
                    el_type = el.get("type", "unknown").upper()
                    text = el.get("text", "")
                    label = el.get("label", "")
                    x, y = el.get("x", 0), el.get("y", 0)
                    
                    if el_type == "TEXT":
                        lines.append(f"- [TEXT] \"{text}\" at ({x}, {y})")
                    elif el_type == "ICON":
                        desc = f"\"{label}\"" if label else "unknown icon"
                        lines.append(f"- [ICON] {desc} at ({x}, {y})")
                    else:
                        lines.append(f"- [{el_type}] at ({x}, {y})")
                        
                # Handle OCRBox (Legacy/Fallback)
                elif hasattr(el, 'text'):
                     lines.append(f"- [TEXT] \"{el.text}\" at ({el.midpoint[0]}, {el.midpoint[1]})")
            
            prompt += "\n".join(lines)
            if len(sorted_elements) > 30:
                prompt += f"\n... and {len(sorted_elements)-30} more elements"

        else:
            prompt += "\n# Note: No visual elements detected. Use element descriptions like 'File menu', 'OK button' based on standard UI knowledge."
        
        # Add notes buffer
        if self._notes:
            prompt += f"\n\n# Notes: {', '.join(self._notes)}\n"
        
        # Add relevant routines/shortcuts from JSON knowledge base
        if self._routines_loader:
            routines_context = self._routines_loader.get_prompt_context(goal, limit=3)
            if routines_context:
                prompt += f"\n\n{routines_context}\n"
        
        prompt += "\n\nGenerate the next action to accomplish the task."
        
        return prompt
    
    def _parse_code(self, response: str) -> str:
        """Extract Python code from response - only first action."""
        logger.debug("parse_code_input", response_preview=response[:200] if response else "empty")
        
        # PRIORITY 1: Look for code block with agent.* call
        code_match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            logger.debug("parse_code_found_block", code=code[:100])
            # Find first agent.* call in code block
            agent_match = re.search(r'(agent\.\w+\([^)]*\))', code)
            if agent_match:
                logger.info("parse_code_result", action=agent_match.group(1))
                return agent_match.group(1)
        
        # PRIORITY 2: Look for agent.* call anywhere in response
        agent_match = re.search(r'(agent\.\w+\([^)]*\))', response)
        if agent_match:
            logger.info("parse_code_result", action=agent_match.group(1))
            return agent_match.group(1)
        
        # PRIORITY 3: Try to parse JSON format {"action": "...", "params": {...}}
        json_match = re.search(r'\{[^{}]*"action"\s*:\s*"(\w+)"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                import json
                json_str = re.search(r'(\{[^{}]*"action"[^{}]*\})', response, re.DOTALL)
                if json_str:
                    data = json.loads(json_str.group(1))
                    action = data.get("action", "wait")
                    params = data.get("params", {})
                    
                    # Convert JSON to agent.* code
                    if action == "hotkey":
                        keys = params.get("keys", [])
                        keys_str = ", ".join(f'"{k}"' for k in keys)
                        return f'agent.hotkey({keys_str})'
                    elif action == "type":
                        text = params.get("text", "")
                        return f'agent.type("{text}")'
                    elif action == "click":
                        if "x" in params and "y" in params:
                            return f'agent.click(x={params["x"]}, y={params["y"]})'
                        else:
                            desc = params.get("description", "")
                            return f'agent.click("{desc}")'
                    elif action == "wait":
                        secs = params.get("seconds", 1.0)
                        return f'agent.wait({secs})'
                    elif action == "done":
                        return 'agent.done()'
                    elif action == "fail":
                        reason = params.get("reason", "unknown")
                        return f'agent.fail("{reason}")'
                    else:
                        return f'agent.{action}()'
            except (json.JSONDecodeError, KeyError):
                pass
        
        # PRIORITY 4 (LAST): Natural language fallbacks - only if nothing else matched
        response_lower = response.lower()
        
        if any(kw in response_lower for kw in ["open run", "win+r", "win r", "windows+r", "executar"]):
            return 'agent.hotkey("win", "r")'
        
        if any(kw in response_lower for kw in ["press enter", "tecla enter", "pressionar enter"]):
            return 'agent.hotkey("enter")'
        
        if any(kw in response_lower for kw in ["type coreldraw", "digitar coreldraw", "escrever coreldraw"]):
            return 'agent.type("coreldraw")'
        
        if any(kw in response_lower for kw in ["type photoshop", "digitar photoshop"]):
            return 'agent.type("photoshop")'
        
        if any(kw in response_lower for kw in ["type notepad", "digitar notepad"]):
            return 'agent.type("notepad")'
        
        # Try to extract type("text") from response
        type_match = re.search(r'(?:type|digitar|escrever)["\\s:]+([a-zA-Z0-9_]+)', response_lower)
        if type_match:
            return f'agent.type("{type_match.group(1)}")'
        
        # Check for done/complete
        if any(kw in response_lower for kw in ["task complete", "tarefa concluída", "done", "finished"]):
            return 'agent.done()'
        
        return ""
    
    def _parse_action(self, code: str) -> tuple[str, dict[str, Any]]:
        """Parse action type and params from code."""
        if not code:
            return "unknown", {}
        
        # Parse agent.action(params)
        match = re.match(r"agent\.(\w+)\((.*)\)", code, re.DOTALL)
        if not match:
            return "unknown", {}
        
        action_type = match.group(1)
        params_str = match.group(2).strip()
        
        # Parse params based on action type
        if action_type == "click":
            # click(x=78, y=464) OR click("description") OR click("description", clicks=1, button="left")
            parts = self._split_params(params_str)
            description = ""
            x = None
            y = None
            clicks = 1
            button = "left"
            
            for i, part in enumerate(parts):
                part = part.strip()
                if "=" in part:
                    # Keyword argument
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key == "x":
                        try:
                            x = int(value)
                        except ValueError:
                            x = None
                    elif key == "y":
                        try:
                            y = int(value)
                        except ValueError:
                            y = None
                    elif key == "clicks":
                        try:
                            clicks = int(value)
                        except ValueError:
                            clicks = 1
                    elif key == "button":
                        button = value
                else:
                    # Positional argument
                    if i == 0:
                        description = part.strip('"\'')
                    elif i == 1:
                        try:
                            clicks = int(part)
                        except ValueError:
                            clicks = 1
                    elif i == 2:
                        button = part.strip('"\'')
            
            params_dict = {
                "clicks": clicks,
                "button": button,
            }
            
            # Add x,y if present (priority over description)
            if x is not None and y is not None:
                params_dict["x"] = x
                params_dict["y"] = y
            elif description:
                params_dict["description"] = description
            
            return action_type, params_dict
        
        elif action_type == "type":
            return action_type, {"text": params_str.strip('"\'')}
        
        elif action_type == "hotkey":
            # Handle both comma-separated and plus-separated keys
            # e.g. hotkey("ctrl", "c") or hotkey("ctrl+c") or hotkey("win+n")
            raw_keys = params_str.strip().strip('"\'')
            if "+" in raw_keys and "," not in raw_keys:
                # Plus-separated: hotkey("ctrl+c")
                keys = [k.strip() for k in raw_keys.split("+")]
            else:
                # Comma-separated: hotkey("ctrl", "c")
                keys = [k.strip().strip('"\'') for k in params_str.split(",")]
            return action_type, {"keys": keys}
        
        elif action_type == "scroll":
            parts = self._split_params(params_str)
            return action_type, {
                "direction": parts[0].strip('"\'') if parts else "down",
                "amount": int(parts[1]) if len(parts) > 1 else 3,
            }
        
        elif action_type == "drag":
            # drag(x1=100, y1=200, x2=400, y2=500)
            parts = self._split_params(params_str)
            x1 = y1 = x2 = y2 = 0
            
            for part in parts:
                part = part.strip()
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    try:
                        value = int(value.strip())
                        if key == "x1":
                            x1 = value
                        elif key == "y1":
                            y1 = value
                        elif key == "x2":
                            x2 = value
                        elif key == "y2":
                            y2 = value
                    except ValueError:
                        pass
            
            return action_type, {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        
        elif action_type == "wait":
            return action_type, {"seconds": float(params_str) if params_str else 1.0}
        
        elif action_type == "done":
            return action_type, {}
        
        elif action_type == "fail":
            return action_type, {"reason": params_str.strip('"\'')}
        
        return action_type, {}
    
    def _split_params(self, params_str: str) -> list[str]:
        """Split parameter string handling quoted strings."""
        params = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for char in params_str:
            if char in '"\'':
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current += char
            elif char == ',' and not in_quotes:
                if current.strip():
                    params.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            params.append(current.strip())
        
        return params
    
    def _emit_thought(self, thought: str) -> None:
        """Emit thought to callback."""
        if self._on_thought:
            self._on_thought(thought)
        logger.info("worker_thought", thought=thought)
    
    def save_note(self, text: str) -> None:
        """Save note to knowledge buffer (like Agent-S save_to_knowledge)."""
        self._notes.append(text)
        logger.info("note_saved", text=text[:50])
