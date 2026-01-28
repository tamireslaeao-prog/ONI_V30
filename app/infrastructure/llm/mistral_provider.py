"""
ONI v3.0 - Enhanced Mistral LLM Provider with Visual Intelligence
Direct integration with Mistral API + real-time screen analysis.
"""

import os
import json
import base64
import asyncio
import httpx
from pathlib import Path
from typing import Any

import structlog

from app.infrastructure.llm.base import GenerationConfig, GenerationResult

logger = structlog.get_logger()


# Enhanced system prompt with visual awareness
VISUAL_SYSTEM_PROMPT = """You are an expert GUI automation agent with VISUAL AWARENESS.

# YOUR TASK: {goal}
# PLATFORM: Windows

# WHAT YOU SEE ON SCREEN RIGHT NOW:
{screen_context}

# PREVIOUS ACTIONS TAKEN:
{previous_actions}

# AVAILABLE ACTIONS (respond with ONE JSON object):

1. hotkey - Press keyboard shortcut
   {{"action": "hotkey", "params": {{"keys": ["win", "r"]}}}}

2. type - Type text
   {{"action": "type", "params": {{"text": "notepad"}}}}

3. click - Click on visible text/element
   {{"action": "click", "params": {{"description": "File menu"}}}}

4. wait - Wait for UI to load
   {{"action": "wait", "params": {{"seconds": 2.0}}}}

5. done - Task is FULLY completed
   {{"action": "done", "params": {{}}}}

# CRITICAL RULES:

## To open ANY application:
1. FIRST: hotkey ["win", "r"] to open Run dialog
2. SECOND: type the app name
3. THIRD: hotkey ["enter"] to run

## App names for Run dialog:
- CorelDRAW: coreldraw
- Photoshop: photoshop  
- Notepad: notepad
- Paint: mspaint
- Calculator: calc

## Decision Logic:
- If you see "Run" or "Open:" or "Executar" → Run dialog is open, proceed to type
- If you see the app name in title bar → App is open, proceed with task
- If no Run dialog visible → Start with hotkey ["win", "r"]
- NEVER repeat the same action twice in a row

## Response:
Respond with ONLY a JSON object, no explanation:
"""


class MistralProvider:
    """
    Enhanced LLM Provider with Mistral API + Visual Intelligence.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self._model = model or os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self._base_url = "https://api.mistral.ai/v1/chat/completions"
        
        if not self._api_key:
            env_file = Path(__file__).parent.parent.parent.parent / ".env"
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("MISTRAL_API_KEY="):
                        self._api_key = line.split("=", 1)[1].strip().strip('"\'')
                    elif line.startswith("MISTRAL_MODEL="):
                        self._model = line.split("=", 1)[1].strip().strip('"\'')
        
        logger.info("mistral_provider_init", model=self._model, visual=True)
    
    @property
    def name(self) -> str:
        return f"Mistral ({self._model})"
    
    @property
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    def _build_screen_context(self, ocr_text: list = None, previous_actions: list = None) -> str:
        """Build visual context from OCR data."""
        if ocr_text and len(ocr_text) > 0:
            # Format OCR text nicely
            visible_text = ", ".join(f'"{t}"' for t in ocr_text[:15] if t.strip())
            screen_context = f"Visible text on screen: {visible_text}"
        else:
            screen_context = "No text detected on screen (desktop or empty area)"
        
        if previous_actions and len(previous_actions) > 0:
            actions_str = "\n".join(f"- {a.get('action', a)}" for a in previous_actions[-3:])
        else:
            actions_str = "None (this is the first action)"
        
        return screen_context, actions_str
    
    async def generate(
        self,
        prompt: str,
        config: GenerationConfig | None = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate response using Mistral API with visual context.
        """
        if not self._api_key:
            logger.error("mistral_no_api_key")
            return GenerationResult(
                text='```python\nagent.wait(2.0)\n```',
                tokens_generated=0,
                tokens_prompt=0,
                generation_time_ms=0.0,
                finish_reason="error",
                metadata={"error": "No API key"},
            )
        
        # Extract visual context from kwargs
        ocr_text = kwargs.get("ocr_text", [])
        goal = kwargs.get("goal", "Complete the task")
        previous_actions = kwargs.get("previous_actions", [])
        
        # Build enhanced prompt with visual awareness
        screen_context, actions_str = self._build_screen_context(ocr_text, previous_actions)
        
        enhanced_prompt = VISUAL_SYSTEM_PROMPT.format(
            goal=goal,
            screen_context=screen_context,
            previous_actions=actions_str,
        )
        
        logger.info("mistral_visual_request", 
                   goal=goal[:50], 
                   ocr_count=len(ocr_text),
                   prev_actions=len(previous_actions))
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        messages = [{"role": "user", "content": enhanced_prompt}]
        
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": config.max_tokens if config else 512,
            "temperature": 0.2,  # Lower for more consistent actions
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._base_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                # Parse JSON and convert to code format expected by worker
                code_text = self._convert_json_to_code(text)
                
                logger.info("mistral_visual_response", response=text[:100])
                
                return GenerationResult(
                    text=code_text,
                    tokens_generated=usage.get("completion_tokens", 0),
                    tokens_prompt=usage.get("prompt_tokens", 0),
                    generation_time_ms=0.0,
                    finish_reason="complete",
                    metadata={"model": self._model},
                )
                
        except httpx.HTTPStatusError as e:
            logger.error("mistral_api_error", status=e.response.status_code)
            return self._fallback_result("API error")
        except Exception as e:
            logger.error("mistral_error", error=str(e))
            return self._fallback_result(str(e))
    
    def _convert_json_to_code(self, response: str) -> str:
        """Convert JSON response to Python code format expected by worker."""
        try:
            # Extract JSON from response
            json_text = response.strip()
            
            # Remove markdown code blocks
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            # Find JSON object
            if not json_text.startswith("{"):
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_text = response[start:end]
            
            data = json.loads(json_text)
            action = data.get("action", "wait")
            params = data.get("params", {})
            
            # Convert to agent.action() format
            if action == "hotkey":
                keys = params.get("keys", [])
                keys_str = ", ".join(f'"{k}"' for k in keys)
                code = f'agent.hotkey({keys_str})'
            elif action == "type":
                text = params.get("text", "")
                code = f'agent.type("{text}")'
            elif action == "click":
                desc = params.get("description", "")
                code = f'agent.click("{desc}")'
            elif action == "wait":
                secs = params.get("seconds", 1.0)
                code = f'agent.wait({secs})'
            elif action == "done":
                code = 'agent.done()'
            else:
                code = f'agent.{action}()'
            
            return f"(Visual Analysis) Executing {action}\n\n```python\n{code}\n```"
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("json_parse_failed", error=str(e))
            # Default to Win+R if parse fails
            return '(Fallback) Opening Run dialog\n\n```python\nagent.hotkey("win", "r")\n```'
    
    def _fallback_result(self, error: str) -> GenerationResult:
        """Return fallback result on error."""
        return GenerationResult(
            text='```python\nagent.hotkey("win", "r")\n```',
            tokens_generated=0,
            tokens_prompt=0,
            generation_time_ms=0.0,
            finish_reason="error",
            metadata={"error": error},
        )


def get_mistral_provider() -> MistralProvider:
    """Get a configured Mistral provider instance."""
    return MistralProvider()
