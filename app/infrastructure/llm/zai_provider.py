"""
ONI v4.0 - ZAI/GLM-4 LLM Provider
Direct integration with ZAI (Zhipu AI) GLM-4 API.
Supports vision models like GLM-4.6v-flash for GUI grounding.
"""

import os
import json
import base64
import httpx
from pathlib import Path
from typing import Any, Optional, List

import structlog

from app.infrastructure.llm.base import GenerationConfig, GenerationResult

logger = structlog.get_logger()


# ZAI Vision-aware prompt for GUI automation
ZAI_SYSTEM_PROMPT = """You are ONI, an AI that can SEE and INTERACT with Windows 10 desktop like a human.

# YOUR TASK
{goal}

# WHAT YOU SEE
Look at the screenshot image. Identify visual elements: buttons, icons, menus, text fields, toolbars.

{visual_context}

# PREVIOUS ACTIONS
{previous_actions}

# THINK STEP BY STEP (CRITICAL!)

Before choosing an action, ask yourself:
1. Is the TARGET APPLICATION already open and visible?
2. If I see the desktop or a different app, I need to OPEN the target app FIRST
3. If I see the target app, what specific action moves toward my goal?

## TO OPEN ANY APPLICATION (REQUIRED SEQUENCE):
Step 1: {{"action": "hotkey", "params": {{"keys": ["win"]}}}} - Opens Start Menu
Step 2: {{"action": "type", "params": {{"text": "appname"}}}} - Type app name  
Step 3: {{"action": "hotkey", "params": {{"keys": ["enter"]}}}} - Launch it
Step 4: {{"action": "wait", "params": {{"seconds": 5.0}}}} - Wait for app to load

## IF YOU SEE A PHOTOSHOP DIALOG (like "Vamos começar" or "New Document"):
- Press Enter or click the blue "Create" button to accept defaults
- {{"action": "hotkey", "params": {{"keys": ["enter"]}}}}

## IF PHOTOSHOP IS OPEN WITH A CANVAS:
1. Select Ellipse tool: {{"action": "hotkey", "params": {{"keys": ["u"]}}}}
2. Draw circle by dragging: {{"action": "drag", "params": {{"x1": 400, "y1": 300, "x2": 600, "y2": 500}}}}
3. When circle is drawn: {{"action": "done", "params": {{}}}}

## IF START MENU IS VISIBLE:
- Type the application name, then press Enter

# AVAILABLE ACTIONS (respond with ONE JSON)

1. hotkey - Keyboard shortcut
   {{"action": "hotkey", "params": {{"keys": ["win"]}}}}
   {{"action": "hotkey", "params": {{"keys": ["ctrl", "n"]}}}}
   {{"action": "hotkey", "params": {{"keys": ["u"]}}}} - Select shape tool
   {{"action": "hotkey", "params": {{"keys": ["enter"]}}}}

2. type - Type text
   {{"action": "type", "params": {{"text": "photoshop"}}}}

3. click - Click at coordinates (only when you SEE a specific button!)
   {{"action": "click", "params": {{"x": 150, "y": 300}}}}

4. drag - Draw shapes by dragging from point A to B (USE FOR CIRCLES!)
   {{"action": "drag", "params": {{"x1": 400, "y1": 300, "x2": 600, "y2": 500}}}}

5. wait - Wait for UI to respond
   {{"action": "wait", "params": {{"seconds": 2.0}}}}

6. done - Task completed successfully
   {{"action": "done", "params": {{}}}}

# CRITICAL RULES
1. IF NO APP IS OPEN → START WITH hotkey(["win"]) to open Start Menu!
2. IF PHOTOSHOP DIALOG VISIBLE → Press Enter to accept and continue
3. TO DRAW A CIRCLE → Use drag action, NOT click!
4. ONE action at a time - let the system execute before deciding next
5. Screen resolution is 1920x1080

# COMMON MISTAKES TO AVOID
❌ WRONG: Clicking random coordinates repeatedly
❌ WRONG: Clicking to draw (shapes need DRAG, not click!)
✅ RIGHT: hotkey(["u"]) to select tool → drag to draw shape → done

RESPOND WITH ONLY JSON - NO TEXT BEFORE OR AFTER:
"""



class ZAIProvider:
    """
    LLM Provider for ZAI (Zhipu AI) GLM-4 models.
    
    Supports:
    - GLM-4.6v-flash (vision model - can see screenshots)
    - GLM-4.5-flash (fast text model)
    - GLM-4 series (various capabilities)
    
    The vision models can directly analyze screenshots for GUI grounding.
    """
    
    # ZAI API endpoint
    BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
    ):
        """
        Initialize ZAI provider.
        
        Args:
            api_key: ZAI API key
            model: Model name (e.g., glm-4.6v-flash)
        """
        self._api_key = api_key or os.getenv("ZAI_API_KEY")
        self._model = model or os.getenv("ZAI_MODEL", "glm-4.6v-flash")
        
        # Try loading from .env if not in env
        if not self._api_key:
            env_file = Path(__file__).parent.parent.parent.parent / ".env"
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("ZAI_API_KEY="):
                        self._api_key = line.split("=", 1)[1].strip().strip('"\'')
                    elif line.startswith("ZAI_MODEL="):
                        self._model = line.split("=", 1)[1].strip().strip('"\'')
        
        # Check if model supports vision
        self._supports_vision = "v" in self._model.lower() or "vision" in self._model.lower()
        
        logger.info("zai_provider_init", model=self._model, vision=self._supports_vision)
    
    @property
    def name(self) -> str:
        return f"ZAI ({self._model})"
    
    @property
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    async def generate(
        self,
        prompt: str,
        config: GenerationConfig = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate response using ZAI API.
        
        For vision models, can include screenshot in the request.
        """
        if not self._api_key:
            logger.error("zai_no_api_key")
            return GenerationResult(
                text='```python\nagent.wait(2.0)\n```',
                tokens_generated=0,
                tokens_prompt=0,
                generation_time_ms=0.0,
                finish_reason="error",
                metadata={"error": "No API key"},
            )
        
        # Extract context from kwargs
        screenshot_data = kwargs.get("screenshot")
        ocr_data = kwargs.get("ocr_text", [])
        goal = kwargs.get("goal", "Complete the task")
        previous_actions = kwargs.get("previous_actions", [])
        
        # Build enhanced prompt with visual context
        visual_ctx = self._build_visual_context(ocr_data)
        actions_ctx = self._format_actions(previous_actions)
        
        enhanced_prompt = ZAI_SYSTEM_PROMPT.format(
            goal=goal,
            visual_context=visual_ctx,
            previous_actions=actions_ctx,
        )
        
        # TRICK: Add JSON prefix to force model to output JSON
        # This makes the model "continue" the JSON object
        enhanced_prompt += "\n\nStart your response with:\n{"
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        # Build message content
        if screenshot_data and self._supports_vision:
            # Vision model - include screenshot
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            content = [
                {"type": "text", "text": enhanced_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_b64}"
                    }
                }
            ]
        else:
            # Text-only model
            content = enhanced_prompt
        
        messages = [{"role": "user", "content": content}]
        
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": config.max_tokens if config else 512,
            "temperature": config.temperature if config else 0.1,  # Lower temp for JSON
            "top_p": config.top_p if config else 0.9,
        }
        
        logger.info("zai_request", 
                   model=self._model, 
                   goal=goal[:50],
                   has_screenshot=screenshot_data is not None)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
            
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # GLM-4.6v uses reasoning_content when in reasoning mode
            if not text or not text.strip():
                reasoning = data["choices"][0]["message"].get("reasoning_content", "")
                if reasoning:
                    logger.info("zai_using_reasoning_content", reasoning_preview=reasoning[:100])
                    # Prepend { since we asked model to continue JSON
                    text = "{" + reasoning if not reasoning.startswith("{") else reasoning
            
            # If text doesn't start with {, prepend it (we asked model to continue)
            if text and not text.strip().startswith("{"):
                text = "{" + text
            
            # DEBUG: Log full response
            logger.info("zai_full_response", 
                       text=text[:100] if text else "EMPTY",
                       text_length=len(text) if text else 0,
                       data_keys=list(data.keys()))
            
            # Check for empty response
            if not text or not text.strip():
                logger.error("zai_empty_response", data=str(data)[:500])
                return self._fallback_result("Empty response from ZAI")
            
            # Convert to code format if needed
            code_text = self._convert_to_code(text)
            
            logger.info("zai_response", response=text[:100])
            
            return GenerationResult(
                text=code_text,
                tokens_generated=usage.get("completion_tokens", 0),
                tokens_prompt=usage.get("prompt_tokens", 0),
                generation_time_ms=0.0,
                finish_reason="complete",
                metadata={"model": self._model, "provider": "zai"},
            )
            
        except httpx.HTTPStatusError as e:
            logger.error("zai_api_error", 
                        status=e.response.status_code,
                        error=e.response.text[:200])
            return self._fallback_result(f"API error: {e.response.status_code}")
            
        except Exception as e:
            logger.error("zai_error", error=str(e))
            return self._fallback_result(str(e))
    
    def _build_visual_context(self, ocr_text: List[str]) -> str:
        """Build visual context from OCR."""
        if ocr_text and len(ocr_text) > 0:
            visible = ", ".join(f'"{t}"' for t in ocr_text[:15] if t.strip())
            return f"Visible text: {visible}"
        return "Looking at screenshot for visual elements"
    
    def _format_actions(self, actions: List) -> str:
        """Format previous actions with better context."""
        if not actions:
            return "⚠️ No actions taken yet - I need to START by opening the application with hotkey(['win'])!"
        
        lines = [f"Completed {len(actions)} steps so far:"]
        for i, a in enumerate(actions[-5:], 1):
            if isinstance(a, dict):
                action_type = a.get('action', 'unknown')
                params = a.get('params', {})
                result = a.get('result', 'executed')
                
                # Format params nicely
                if action_type == 'click' and 'x' in params:
                    detail = f"at ({params.get('x')}, {params.get('y')})"
                elif action_type == 'type':
                    detail = f"'{params.get('text', '')}'"
                elif action_type == 'hotkey':
                    keys = params.get('keys', [])
                    detail = f"[{', '.join(keys)}]"
                else:
                    detail = str(params)[:30]
                
                lines.append(f"  Step {i}: {action_type} {detail} → {result}")
            else:
                lines.append(f"  Step {i}: {a}")
        
        # Warning if many actions without progress
        if len(actions) >= 3:
            # Check if repeating same action
            recent = [a.get('action', '') if isinstance(a, dict) else str(a) for a in actions[-3:]]
            if len(set(recent)) == 1:
                lines.append("\n⚠️ LOOP DETECTED - same action repeated! Try a DIFFERENT approach!")
                lines.append("💡 TIP: If app not open, use hotkey(['win']) first!")
        
        if len(actions) >= 5:
            lines.append("\n⚠️ MANY STEPS TAKEN - verify you are making progress toward the goal!")
        
        return "\n".join(lines)
    
    def _convert_to_code(self, response: str) -> str:
        """Convert JSON response to Python code format."""
        
        logger.debug("convert_to_code_input", response=response[:150] if response else "empty")
        
        # Clean up response - remove leading/trailing whitespace
        response = response.strip()
        
        try:
            # Try to parse the entire response as JSON first
            if response.startswith('{'):
                data = json.loads(response)
                action = data.get("action", "wait")
                params = data.get("params", {})
                
                logger.info("convert_to_code_parsed", action=action, params=params)
                
                # Convert to agent.action() format
                code = self._build_agent_code(action, params)
                logger.info("convert_to_code_result", code=code)
                return f"```python\n{code}\n```"
            
            # Look for JSON object in response (handles markdown code blocks)
            # Find balanced braces
            start = response.find('{')
            if start != -1:
                # Find matching closing brace
                brace_count = 0
                for i, char in enumerate(response[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = response[start:i+1]
                            logger.debug("convert_to_code_extracted_json", json=json_str[:100])
                            data = json.loads(json_str)
                            action = data.get("action", "wait")
                            params = data.get("params", {})
                            
                            logger.info("convert_to_code_parsed", action=action, params=params)
                            code = self._build_agent_code(action, params)
                            logger.info("convert_to_code_result", code=code)
                            return f"```python\n{code}\n```"
            
            logger.warning("convert_to_code_no_json_found", response_preview=response[:100])
                
        except json.JSONDecodeError as e:
            logger.error("convert_to_code_json_error", error=str(e), response=response[:100])
        except Exception as e:
            logger.error("convert_to_code_error", error=str(e))
        
        # Fallback - use Win key to open Start Menu
        logger.warning("convert_to_code_using_fallback")
        return '```python\nagent.hotkey("win")\n```'
    
    def _build_agent_code(self, action: str, params: dict) -> str:
        """Build agent.action() code from action and params."""
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
        elif action == "drag":
            x1 = params.get("x1", 0)
            y1 = params.get("y1", 0)
            x2 = params.get("x2", 0)
            y2 = params.get("y2", 0)
            return f'agent.drag(x1={x1}, y1={y1}, x2={x2}, y2={y2})'
        elif action == "wait":
            secs = params.get("seconds", 1.0)
            return f'agent.wait({secs})'
        elif action == "done":
            return 'agent.done()'
        else:
            return f'agent.{action}()'
    
    def _fallback_result(self, error: str) -> GenerationResult:
        """Return fallback on error."""
        return GenerationResult(
            text='```python\nagent.hotkey("win", "r")\n```',
            tokens_generated=0,
            tokens_prompt=0,
            generation_time_ms=0.0,
            finish_reason="error",
            metadata={"error": error},
        )


def get_zai_provider() -> ZAIProvider:
    """Get configured ZAI provider."""
    return ZAIProvider()
