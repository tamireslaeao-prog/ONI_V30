"""
ONI v5.0 - Fallback Strategies
Extracted fallback strategies from HybridAgent for better modularity.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FallbackResult:
    """Result from a fallback strategy execution."""
    action_type: str
    params: dict
    description: str
    should_continue: bool = True


class FallbackStrategyManager:
    """
    Manages fallback strategies for different application contexts.
    
    When the LLM returns 'unknown' actions or when loops are detected,
    this manager provides context-aware fallback actions.
    """
    
    def __init__(self, worker: Any = None, emit_thought: Callable[[str], None] = None):
        """
        Initialize fallback manager.
        
        Args:
            worker: HybridWorker instance for executing actions
            emit_thought: Callback to emit thoughts to UI
        """
        self._worker = worker
        self._emit_thought = emit_thought or (lambda x: None)
        self._fallback_counts: dict[str, int] = {}
    
    def reset(self, goal: str) -> None:
        """Reset fallback counts for a new goal."""
        goal_key = goal.lower()[:50]
        self._fallback_counts[goal_key] = 0
    
    def get_fallback_count(self, goal: str) -> int:
        """Get current fallback count for a goal."""
        goal_key = goal.lower()[:50]
        return self._fallback_counts.get(goal_key, 0)
    
    def increment_fallback(self, goal: str) -> int:
        """Increment and return fallback count."""
        goal_key = goal.lower()[:50]
        count = self._fallback_counts.get(goal_key, 0) + 1
        self._fallback_counts[goal_key] = count
        return count
    
    def get_unknown_fallback(self, goal: str, trajectory: list[dict]) -> Optional[dict]:
        """
        Get fallback action when LLM returns 'unknown'.
        
        Args:
            goal: Current goal
            trajectory: Action trajectory so far
            
        Returns:
            WorkerResult-like dict or None
        """
        unknown_count = sum(1 for t in trajectory if t.get("action") == "unknown")
        goal_lower = goal.lower()
        
        # Check if this is an app-launching task
        app_names = ["corel", "photoshop", "notepad", "excel", "word", "blender", "chrome", "firefox"]
        is_app_task = any(app in goal_lower for app in app_names)
        
        if not is_app_task:
            return None
        
        # Extract app name
        app_name = "notepad"
        for app in app_names:
            if app in goal_lower:
                app_name = app
                break
        
        if unknown_count == 0:
            self._emit_thought("🔧 Fallback: Opening Run dialog...")
            return {
                "plan": "Smart fallback - open Run dialog",
                "plan_code": 'agent.hotkey("win", "r")',
                "exec_code": 'agent.hotkey("win", "r")',
                "action_type": "hotkey",
                "params": {"keys": ["win", "r"]},
            }
        
        elif unknown_count == 1:
            self._emit_thought(f"🔧 Fallback: Typing {app_name}...")
            return {
                "plan": f"Smart fallback - type {app_name}",
                "plan_code": f'agent.type("{app_name}")',
                "exec_code": f'agent.type("{app_name}")',
                "action_type": "type",
                "params": {"text": app_name},
            }
        
        elif unknown_count == 2:
            self._emit_thought("🔧 Fallback: Pressing Enter...")
            return {
                "plan": "Smart fallback - press Enter",
                "plan_code": 'agent.hotkey("enter")',
                "exec_code": 'agent.hotkey("enter")',
                "action_type": "hotkey",
                "params": {"keys": ["enter"]},
            }
        
        return None
    
    async def execute_loop_fallback(
        self,
        goal: str,
        screenshot: bytes,
        worker: Any
    ) -> bool:
        """
        Execute fallback strategy when loop is detected.
        
        Args:
            goal: Current goal
            screenshot: Current screenshot
            worker: HybridWorker to execute actions
            
        Returns:
            True if should continue execution, False to stop
        """
        goal_lower = goal.lower()
        count = self.increment_fallback(goal)
        
        # Create WorkerResult on-demand
        from app.agent.hybrid_worker import WorkerResult
        
        # GRAPHICS APP CONTEXT
        if any(app in goal_lower for app in ["photoshop", "coreldraw", "paint", "gimp"]):
            return await self._graphics_app_fallback(count, screenshot, worker)
        
        # TEXT/OFFICE APP CONTEXT
        elif any(app in goal_lower for app in ["notepad", "word", "excel"]):
            return await self._office_app_fallback(count, screenshot, worker)
        
        # GENERIC FALLBACK
        else:
            return await self._generic_fallback(count)
    
    async def _graphics_app_fallback(
        self, count: int, screenshot: bytes, worker: Any
    ) -> bool:
        """Fallback strategies for graphics applications."""
        from app.agent.hybrid_worker import WorkerResult
        
        if count == 1:
            self._emit_thought("🎨 Creating new document (Ctrl+N)...")
            result = WorkerResult(
                plan="Graphics app fallback - new document",
                plan_code='agent.hotkey("ctrl", "n")',
                exec_code='agent.hotkey("ctrl", "n")',
                action_type="hotkey",
                params={"keys": ["ctrl", "n"]},
            )
            await worker.execute_action(result, screenshot)
            await asyncio.sleep(1.0)
            
            # Accept dialog
            result = WorkerResult(
                plan="Accept new document dialog",
                plan_code='agent.hotkey("enter")',
                exec_code='agent.hotkey("enter")',
                action_type="hotkey",
                params={"keys": ["enter"]},
            )
            await worker.execute_action(result, screenshot)
            await asyncio.sleep(2.0)
            return True
        
        elif count == 2:
            self._emit_thought("🔵 Selecting Ellipse tool (U)...")
            result = WorkerResult(
                plan="Select Ellipse tool",
                plan_code='agent.hotkey("u")',
                exec_code='agent.hotkey("u")',
                action_type="hotkey",
                params={"keys": ["u"]},
            )
            await worker.execute_action(result, screenshot)
            await asyncio.sleep(0.5)
            return True
        
        elif count == 3:
            self._emit_thought("✏️ Drawing circle in center of canvas...")
            result = WorkerResult(
                plan="Draw circle via drag",
                plan_code='agent.drag(x1=400, y1=300, x2=600, y2=500)',
                exec_code='agent.drag(x1=400, y1=300, x2=600, y2=500)',
                action_type="drag",
                params={"x1": 400, "y1": 300, "x2": 600, "y2": 500},
            )
            await worker.execute_action(result, screenshot)
            await asyncio.sleep(1.0)
            return True
        
        else:
            self._emit_thought("✅ Fallback complete - marking done...")
            return False
    
    async def _office_app_fallback(
        self, count: int, screenshot: bytes, worker: Any
    ) -> bool:
        """Fallback strategies for office applications."""
        from app.agent.hybrid_worker import WorkerResult
        
        if count == 1:
            self._emit_thought("📝 Focusing on text area...")
            result = WorkerResult(
                plan="Office app fallback - click center",
                plan_code='agent.click(x=960, y=540)',
                exec_code='agent.click(x=960, y=540)',
                action_type="click",
                params={"x": 960, "y": 540},
            )
            await worker.execute_action(result, screenshot)
            await asyncio.sleep(0.5)
            return True
        
        else:
            self._emit_thought("⏳ Waiting for UI...")
            await asyncio.sleep(2.0)
            return count < 3
    
    async def _generic_fallback(self, count: int) -> bool:
        """Generic fallback for unknown applications."""
        if count < 3:
            self._emit_thought("⏳ Waiting for UI to stabilize...")
            await asyncio.sleep(2.0)
            return True
        
        self._emit_thought("⚠️ Too many loops - stopping execution")
        return False


# Singleton instance
_fallback_manager: FallbackStrategyManager | None = None


def get_fallback_manager(
    worker: Any = None,
    emit_thought: Callable[[str], None] = None
) -> FallbackStrategyManager:
    """Get or create the fallback manager singleton."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = FallbackStrategyManager(worker, emit_thought)
    elif worker is not None:
        _fallback_manager._worker = worker
        _fallback_manager._emit_thought = emit_thought or (lambda x: None)
    return _fallback_manager
