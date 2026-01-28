import asyncio
import json
import httpx
import structlog
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = structlog.get_logger(__name__)

class MoltHeadlessService:
    """
    Integrates Moltbot's headless browser automation capabilities into ONI V30.
    Focuses on navigation, snapshots (Aria/AI), and actions (click, type, etc.).
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:18791"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.current_profile = "clawd"
        self.current_target_id = None

    async def check_health(self) -> bool:
        """Check if Moltbot browser control service is alive."""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            return response.status_code == 200
        except Exception:
            return False

    async def navigate(self, url: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """Navigate to a URL."""
        profile = profile or self.current_profile
        try:
            response = await self.client.post(
                f"{self.base_url}/navigate?profile={profile}",
                json={"url": url}
            )
            result = response.json()
            if result.get("ok"):
                self.current_target_id = result.get("targetId")
            return result
        except Exception as e:
            logger.error("molt_navigate_failed", error=str(e))
            return {"ok": False, "error": str(e)}

    async def get_snapshot(self, mode: str = "aria", profile: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a page snapshot for AI reasoning.
        Modes: 'aria' (Playwright aria-ref ids), 'role' (role+name based).
        """
        profile = profile or self.current_profile
        try:
            response = await self.client.get(
                f"{self.base_url}/snapshot?profile={profile}&refs={mode}&targetId={self.current_target_id or ''}"
            )
            return response.json()
        except Exception as e:
            logger.error("molt_snapshot_failed", error=str(e))
            return {"ok": False, "error": str(e)}

    async def act(self, action_kind: str, params: Dict[str, Any], profile: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform an action (click, type, hover, etc.) using Moltbot's action engine.
        Uses refs from the snapshot for precise targeting.
        """
        profile = profile or self.current_profile
        payload = {"kind": action_kind, "targetId": self.current_target_id, **params}
        try:
            response = await self.client.post(
                f"{self.base_url}/act?profile={profile}",
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error("molt_action_failed", action=action_kind, error=str(e))
            return {"ok": False, "error": str(e)}

    async def click(self, ref: str) -> Dict[str, Any]:
        """Helper for click action."""
        return await self.act("click", {"ref": ref})

    async def type_text(self, ref: str, text: str, submit: bool = False) -> Dict[str, Any]:
        """Helper for type action."""
        return await self.act("type", {"ref": ref, "text": text, "submit": submit})

    async def run_skill(self, skill_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Moltbot Skill action.
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/skills/{skill_name}/invoke",
                json={"action": action, "params": params}
            )
            return response.json()
        except Exception as e:
            logger.error("molt_skill_failed", skill=skill_name, action=action, error=str(e))
            return {"ok": False, "error": str(e)}

    async def run_extension(self, extension_name: str, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Moltbot Extension command.
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/extensions/{extension_name}/command",
                json={"command": command, "data": data}
            )
            return response.json()
        except Exception as e:
            logger.error("molt_extension_failed", extension=extension_name, command=command, error=str(e))
            return {"ok": False, "error": str(e)}

    async def close(self):
        """Close the client."""
        await self.client.aclose()

# Global instance
molt_service = MoltHeadlessService()
