"""
ONI v3.0 - Bridge Provider
LLM Provider that communicates with Antigravity via files.
Antigravity becomes the "brain" of ONI.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any

import structlog

from app.infrastructure.llm.base import GenerationConfig, GenerationResult

logger = structlog.get_logger()


class BridgeProvider:
    """
    LLM Provider that bridges ONI to Antigravity (Claude).
    
    Communication flow:
    1. ONI writes goal/context to bridge/request.json
    2. Antigravity reads and processes
    3. Antigravity writes response to bridge/response.json
    4. ONI reads response and executes action
    """
    
    def __init__(self, bridge_dir: Path | str | None = None):
        """
        Initialize bridge provider.
        
        Args:
            bridge_dir: Directory for bridge files
        """
        if bridge_dir is None:
            bridge_dir = Path(__file__).parent.parent.parent.parent / "bridge"
        self._bridge_dir = Path(bridge_dir)
        self._bridge_dir.mkdir(parents=True, exist_ok=True)
        
        # Bridge files
        self._request_file = self._bridge_dir / "request.json"
        self._response_file = self._bridge_dir / "response.json"
        self._status_file = self._bridge_dir / "status.json"
        self._screenshot_file = self._bridge_dir / "screenshot.png"
        
        # Polling settings
        self._poll_interval = 0.5  # seconds
        self._timeout = 120.0  # seconds
        
        # Session tracking
        self._request_id = 0
        
        logger.info("bridge_provider_init", bridge_dir=str(self._bridge_dir))
    
    @property
    def name(self) -> str:
        return "Antigravity Bridge"
    
    @property
    def is_available(self) -> bool:
        return True  # Always available
    
    async def generate(
        self,
        prompt: str,
        config: GenerationConfig | None = None,
        screenshot: bytes | None = None,
        ocr_text: list[str] | None = None,
        goal: str | None = None,
        previous_actions: list[dict] | None = None,
    ) -> GenerationResult:
        """
        Generate response by communicating with Antigravity.
        
        Args:
            prompt: The full prompt (for context)
            config: Generation config (ignored, Antigravity decides)
            screenshot: Current screenshot bytes
            ocr_text: OCR extracted text
            goal: Current goal
            previous_actions: Previous actions in trajectory
            
        Returns:
            GenerationResult with action from Antigravity
        """
        self._request_id += 1
        request_id = f"req_{self._request_id}_{int(time.time())}"
        
        # Save screenshot if provided
        if screenshot:
            self._screenshot_file.write_bytes(screenshot)
        
        # Write request
        request = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "goal": goal or self._extract_goal(prompt),
            "prompt": prompt,
            "ocr_text": ocr_text or [],
            "previous_actions": previous_actions or [],
            "screenshot_path": str(self._screenshot_file) if screenshot else None,
            "status": "pending",
        }
        
        self._request_file.write_text(
            json.dumps(request, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Update status
        self._write_status("waiting_for_antigravity", request_id)
        
        logger.info("bridge_request_sent", request_id=request_id, goal=request["goal"][:50])
        
        # Wait for response
        response = await self._wait_for_response(request_id)
        
        if response:
            logger.info("bridge_response_received", 
                       action=response.get("action"),
                       request_id=request_id)
            
            # Convert to GenerationResult format
            # Format: agent.action(params)
            action = response.get("action", "wait")
            params = response.get("params", {})
            reasoning = response.get("reasoning", "")
            
            # Build code string
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
            elif action == "done":
                code = 'agent.done()'
            elif action == "wait":
                secs = params.get("seconds", 1.0)
                code = f'agent.wait({secs})'
            else:
                code = f'agent.{action}()'
            
            return GenerationResult(
                text=f"(Reasoning) {reasoning}\n\n```python\n{code}\n```",
                tokens_generated=0,
                tokens_prompt=0,
                generation_time_ms=0.0,
                finish_reason="complete",
                metadata={"model": "antigravity"},
            )
        else:
            # Timeout
            logger.warning("bridge_timeout", request_id=request_id)
            return GenerationResult(
                text='```python\nagent.wait(2.0)\n```',
                tokens_generated=0,
                tokens_prompt=0,
                generation_time_ms=0.0,
                finish_reason="timeout",
                metadata={"model": "antigravity"},
            )
    
    async def _wait_for_response(self, request_id: str) -> dict | None:
        """Poll for response from Antigravity."""
        start_time = time.time()
        
        while time.time() - start_time < self._timeout:
            if self._response_file.exists():
                try:
                    response = json.loads(self._response_file.read_text(encoding="utf-8"))
                    
                    # Check if this is a response to our request
                    if response.get("request_id") == request_id:
                        # Clear response file
                        self._response_file.unlink()
                        self._write_status("response_received", request_id)
                        return response
                        
                except (json.JSONDecodeError, Exception) as e:
                    logger.debug("bridge_response_parse_error", error=str(e))
            
            await asyncio.sleep(self._poll_interval)
        
        return None
    
    def _write_status(self, status: str, request_id: str) -> None:
        """Update status file."""
        self._status_file.write_text(
            json.dumps({
                "status": status,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
            }, indent=2),
            encoding="utf-8"
        )
    
    def _extract_goal(self, prompt: str) -> str:
        """Extract goal from prompt."""
        if "task:" in prompt.lower():
            lines = prompt.split("\n")
            for line in lines:
                if "task:" in line.lower():
                    return line.split(":", 1)[1].strip()
        return prompt[:100]


# Global instance
bridge_provider: BridgeProvider | None = None


def get_bridge_provider() -> BridgeProvider:
    """Get or create bridge provider instance."""
    global bridge_provider
    if bridge_provider is None:
        bridge_provider = BridgeProvider()
    return bridge_provider
