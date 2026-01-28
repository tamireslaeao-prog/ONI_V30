"""
ONI v2.0 - WebSocket Handler (Dashboard)
Real-time bidirectional communication with Neural Dashboard.

OPTIMIZED: Uses SharedVisionService to avoid duplicate captures.
"""
import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.dependencies import container
from app.services.vision_shared import get_shared_vision, CachedFrame

logger = structlog.get_logger()


class MessageType(str, Enum):
    """WebSocket message types."""
    # Client -> Server
    COMMAND = "command"
    GOAL = "goal"
    PRESET = "preset"
    ACTION_RESPONSE = "action_response"
    PING = "ping"
    REQUEST_FRAME = "request_frame"  # NEW: Explicit frame request
    
    # Server -> Client
    STATE_UPDATE = "state_update"
    VISION_FRAME = "vision_frame"
    THOUGHT = "thought"
    ACTION_REQUEST = "action_request"
    LOG = "log"
    METRICS = "metrics"
    PLAN_UPDATE = "plan_update"
    PONG = "pong"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: MessageType
    data: dict[str, Any]
    timestamp: str = ""
    
    def __init__(self, **data: Any) -> None:
        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = datetime.now().isoformat()
        super().__init__(**data)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()
        self._vision_subscribers = {}  # Track vision subscribers per connection
        self._agent_tasks: dict[WebSocket, asyncio.Task] = {} # FIX P6: Per-connection tasks
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info("dashboard_connected", total_connections=len(self.active_connections))
    
    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                
            # Unsubscribe from vision if subscribed
            if websocket in self._vision_subscribers:
                subscriber = self._vision_subscribers[websocket]
                shared_vision = get_shared_vision()
                await shared_vision.unsubscribe(subscriber)
                del self._vision_subscribers[websocket]
            
            # Cancel agent task if this connection owns one (Fix P6)
            if websocket in self._agent_tasks:
                task = self._agent_tasks[websocket]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self._agent_tasks[websocket]
                
        logger.info("dashboard_disconnected", total_connections=len(self.active_connections))
    
    async def send_message(self, websocket: WebSocket, message: WebSocketMessage) -> None:
        try:
            await websocket.send_json(message.model_dump())
        except Exception as e:
            logger.error("websocket_send_error", error=str(e))
    
    async def broadcast(self, message: WebSocketMessage) -> None:
        disconnected: list[WebSocket] = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message.model_dump())
            except Exception as e:
                # FIX P8: Log broadcast error
                logger.warning("broadcast_failed_for_client", error=str(e))
                disconnected.append(connection)
        
        for conn in disconnected:
            await self.disconnect(conn)
    
    async def broadcast_state(self, state: dict[str, Any]) -> None:
        await self.broadcast(WebSocketMessage(type=MessageType.STATE_UPDATE, data=state))
    
    async def broadcast_thought(self, content: str) -> None:
        await self.broadcast(WebSocketMessage(type=MessageType.THOUGHT, data={"content": content}))
    
    async def broadcast_plan(self, plan_data: dict[str, Any]) -> None:
        await self.broadcast(WebSocketMessage(type=MessageType.PLAN_UPDATE, data=plan_data))
    
    async def broadcast_log(self, level: str, message: str) -> None:
        await self.broadcast(WebSocketMessage(type=MessageType.LOG, data={"level": level, "message": message}))
    
    async def subscribe_to_vision(self, websocket: WebSocket, fps_limit: float = 10.0):
        """
        Subscribe this websocket to vision frames.
        Uses SharedVisionService to avoid duplicate captures.
        """
        if websocket in self._vision_subscribers:
            # FIX P5: Unsubscribe first to avoid leaks or duplicate streams
            logger.info("renewing_vision_subscription")
            old_sub = self._vision_subscribers[websocket]
            shared_vision = get_shared_vision()
            await shared_vision.unsubscribe(old_sub)
            del self._vision_subscribers[websocket]
        
        shared_vision = get_shared_vision()
        
        async def frame_callback(frame: CachedFrame):
            """Called when new frame is available."""
            try:
                # Get JPEG at lower quality for dashboard (bandwidth saving)
                jpeg_b64 = frame.get_jpeg_b64(quality=50)
                
                await self.send_message(websocket, WebSocketMessage(
                    type=MessageType.VISION_FRAME,
                    data={
                        "image": jpeg_b64,
                        "frame_number": frame.frame_number,
                        "resolution": f"{frame.resolution[0]}x{frame.resolution[1]}",
                        "timestamp": frame.timestamp
                    }
                ))
            except Exception as e:
                logger.error("frame_callback_error", error=str(e))
        
        subscriber = await shared_vision.subscribe(
            name=f"dashboard-{id(websocket)}",
            callback=frame_callback,
            fps_limit=fps_limit  # Dashboard only needs 10 FPS
        )
        
        self._vision_subscribers[websocket] = subscriber
        logger.info("dashboard_subscribed_to_vision", fps_limit=fps_limit)


# Global connection manager
manager = ConnectionManager()

# Track agent task (Removed global - moved to ConnectionManager)
# _agent_task: asyncio.Task | None = None


async def websocket_endpoint(websocket: WebSocket) -> None:
    """Main WebSocket endpoint handler for Dashboard."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        await manager.send_message(websocket, WebSocketMessage(
            type=MessageType.STATE_UPDATE,
            data={
                "status": "connected",
                "version": "2.0.0",
                "capabilities": ["vision", "actuation", "planning"],
                "note": "Vision streaming via SharedVisionService"
            }
        ))
        
        # Message loop
        while True:
            try:
                data = await websocket.receive_json()
                await handle_message(websocket, data)
            except json.JSONDecodeError:
                await manager.send_message(websocket, WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": "Invalid JSON"}
                ))
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        await manager.disconnect(websocket)


async def handle_message(websocket: WebSocket, data: dict[str, Any]) -> None:
    """Handle incoming WebSocket message."""
async def handle_message(websocket: WebSocket, data: dict[str, Any]) -> None:
    """Handle incoming WebSocket message."""
    # global _agent_task (Removed)
    
    msg_type = data.get("type", "")
    msg_data = data.get("data", {})
    
    if msg_type == MessageType.PING.value:
        await manager.send_message(websocket, WebSocketMessage(
            type=MessageType.PONG,
            data={"received": data.get("timestamp", "")}
        ))
    
    elif msg_type == MessageType.REQUEST_FRAME.value:
        """
        NEW: Dashboard explicitly requests vision frames.
        This is more efficient than auto-streaming.
        """
        fps_limit = msg_data.get("fps", 10.0)
        await manager.subscribe_to_vision(websocket, fps_limit)
    
    elif msg_type == MessageType.GOAL.value:
        goal = msg_data.get("goal", "")
        logger.info("goal_received", goal=goal)
        
        # Set goal on agent
        if container.has("agent"):
            agent = container.get("agent")
            
            # Setup callbacks to broadcast to WebSocket
            agent.set_callbacks(
                on_state_change=lambda s: asyncio.create_task(
                    manager.broadcast_state({"status": s.value if hasattr(s, 'value') else str(s)})
                ),
                on_thought=lambda t: asyncio.create_task(
                    manager.broadcast_thought(t)
                ),
            )
            
            try:
                # Check if this is HybridAgent (v3) or CognitiveAgent (legacy)
                if hasattr(agent, 'execute_goal'):
                    # HybridAgent v3 - store goal for later execution
                    agent._current_goal = goal
                    await manager.broadcast_state({"goal_accepted": True, "goal": goal})
                    await manager.broadcast_log("info", f"Goal set: {goal} (v3.0 HybridAgent)")
                    await manager.broadcast_plan({"steps": [{"description": "Ready to execute", "status": "pending"}]})
                else:
                    # Legacy CognitiveAgent
                    plan = await agent.set_goal(goal)
                    plan_steps = [
                        {"description": s.description, "status": s.status.value}
                        for s in plan.steps
                    ]
                    await manager.broadcast_plan({"steps": plan_steps})
                    await manager.broadcast_state({"goal_accepted": True, "goal": goal})
                    await manager.broadcast_log("info", f"Goal set: {goal}")
                
            except Exception as e:
                logger.error("goal_set_error", error=str(e))
                await manager.broadcast_log("error", f"Failed to set goal: {e}")
        else:
            await manager.broadcast_log("warning", "Agent not available")
    
    elif msg_type == MessageType.COMMAND.value:
        command = msg_data.get("command", "")
        logger.info("command_received", command=command)
        
        if container.has("agent"):
            agent = container.get("agent")
            
            if command == "start":
                if not agent.is_running:
                    # Start agent in background task linked to this connection
                    task = asyncio.create_task(run_agent_with_broadcast(agent))
                    manager._agent_tasks[websocket] = task # FIX P6
                    
                    await manager.broadcast_state({"status": "ACTING"})
                    await manager.broadcast_log("info", "Agent started")
                    
            elif command == "pause":
                await agent.pause()
                await manager.broadcast_state({"status": "PAUSED"})
                await manager.broadcast_log("info", "Agent paused")
                
            elif command == "stop":
                await agent.stop()
                if websocket in manager._agent_tasks:
                    t = manager._agent_tasks[websocket]
                    t.cancel()
                    del manager._agent_tasks[websocket]
                await manager.broadcast_state({"status": "IDLE"})
                await manager.broadcast_log("info", "Agent stopped")
                
            elif command == "emergency_stop":
                await agent.emergency_stop()
                # Cancel ALL agent tasks? Or just this one? Safer to cancel this one.
                if websocket in manager._agent_tasks:
                    t = manager._agent_tasks[websocket]
                    t.cancel()
                    del manager._agent_tasks[websocket]
                await manager.broadcast_state({"status": "IDLE"})
                await manager.broadcast_log("warning", "EMERGENCY STOP")
        else:
            await manager.broadcast_log("error", "Agent not available")
    
    elif msg_type == MessageType.PRESET.value:
        preset = msg_data.get("preset", "")
        logger.info("preset_received", preset=preset)
        
        # Execute pre-programmed routine without LLM
        await manager.broadcast_thought(f"⚡ Executing preset: {preset}")
        await manager.broadcast_state({"status": "ACTING"})
        
        # Run preset in background
        asyncio.create_task(execute_preset_routine(preset))
    
    elif msg_type == MessageType.ACTION_RESPONSE.value:
        action_id = msg_data.get("id", "")
        approved = msg_data.get("approved", False)
        logger.info("action_response", action_id=action_id, approved=approved)
    
    else:
        await manager.send_message(websocket, WebSocketMessage(
            type=MessageType.ERROR,
            data={"error": f"Unknown message type: {msg_type}"}
        ))


async def run_agent_with_broadcast(agent) -> None:
    """Run agent and broadcast updates."""
    try:
        await manager.broadcast_thought("Starting agent execution...")
        
        # Check if this is HybridAgent (v3) or CognitiveAgent (legacy)
        if hasattr(agent, 'execute_goal'):
            # HybridAgent v3
            goal = getattr(agent, '_current_goal', '')
            if not goal:
                await manager.broadcast_log("error", "No goal set")
                return
            
            await manager.broadcast_thought(f"🎯 Executing: {goal}")
            result = await agent.execute_goal(goal)
            
            # Broadcast result
            if result.success:
                await manager.broadcast_state({"status": "COMPLETED"})
                await manager.broadcast_log("info", f"✅ Goal completed in {result.steps_executed} steps")
                await manager.broadcast_thought(f"✅ Task completed successfully!")
            else:
                await manager.broadcast_state({"status": "ERROR"})
                await manager.broadcast_log("error", f"❌ Goal failed: {result.error}")
                await manager.broadcast_thought(f"❌ Task failed: {result.error}")
            
            # Broadcast stats
            stats = agent.get_stats()
            await manager.broadcast(WebSocketMessage(
                type=MessageType.METRICS,
                data={
                    "actions": stats.get("total_actions", 0),
                    "success_rate": f"{stats.get('success_rate', 0):.1f}%",
                    "grounding": stats.get("grounding_stats", {}),
                }
            ))
        else:
            # Legacy CognitiveAgent
            await agent.start()
        
        await manager.broadcast_state({"status": "IDLE"})
        await manager.broadcast_log("info", "Agent completed")
        
    except asyncio.CancelledError:
        await manager.broadcast_log("info", "Agent cancelled")
    except Exception as e:
        logger.error("agent_run_error", error=str(e))
        await manager.broadcast_log("error", f"Agent error: {e}")
        await manager.broadcast_state({"status": "ERROR"})


# =============================================================================
# Pre-programmed Routines (No LLM required)
# =============================================================================

PRESET_ROUTINES = {
    "start_menu": [
        {"action": "hotkey", "keys": ["win"], "delay": 0.5},
    ],
    "open_coreldraw": [
        {"action": "hotkey", "keys": ["win"], "delay": 0.5},
        {"action": "type", "text": "coreldraw", "delay": 0.3},
        {"action": "hotkey", "keys": ["enter"], "delay": 5.0},
        {"action": "hotkey", "keys": ["ctrl", "n"], "delay": 1.0},
        {"action": "hotkey", "keys": ["enter"], "delay": 2.0},
        {"action": "thought", "text": "✅ CorelDRAW opened with new document"},
    ],
    "open_photoshop": [
        {"action": "hotkey", "keys": ["win"], "delay": 0.5},
        {"action": "type", "text": "photoshop", "delay": 0.3},
        {"action": "hotkey", "keys": ["enter"], "delay": 8.0},
        {"action": "hotkey", "keys": ["ctrl", "n"], "delay": 1.0},
        {"action": "hotkey", "keys": ["enter"], "delay": 2.0},
        {"action": "thought", "text": "✅ Photoshop opened with new document"},
    ],
    "open_notepad": [
        {"action": "hotkey", "keys": ["win"], "delay": 0.5},
        {"action": "type", "text": "notepad", "delay": 0.3},
        {"action": "hotkey", "keys": ["enter"], "delay": 1.0},
        {"action": "thought", "text": "✅ Notepad opened"},
    ],
    "open_explorer": [
        {"action": "hotkey", "keys": ["win", "e"], "delay": 1.0},
        {"action": "thought", "text": "✅ File Explorer opened"},
    ],
    "open_browser": [
        {"action": "hotkey", "keys": ["win"], "delay": 0.5},
        {"action": "type", "text": "chrome", "delay": 0.3},
        {"action": "hotkey", "keys": ["enter"], "delay": 2.0},
        {"action": "thought", "text": "✅ Browser opened"},
    ],
    "screenshot": [
        {"action": "hotkey", "keys": ["win", "shift", "s"], "delay": 0.5},
        {"action": "thought", "text": "📷 Screenshot tool activated"},
    ],
    "close_window": [
        {"action": "hotkey", "keys": ["alt", "f4"], "delay": 0.5},
        {"action": "thought", "text": "❌ Window closed"},
    ],
}


async def execute_preset_routine(preset_name: str) -> None:
    """Execute a pre-programmed routine without LLM."""
    import pyautogui
    import time
    
    routine = PRESET_ROUTINES.get(preset_name)
    if not routine:
        await manager.broadcast_log("error", f"Unknown preset: {preset_name}")
        await manager.broadcast_state({"status": "IDLE"})
        return
    
    await manager.broadcast_log("info", f"⚡ Executing preset: {preset_name}")
    
    try:
        for step in routine:
            action = step.get("action", "")
            delay = step.get("delay", 0.3)
            
            if action == "hotkey":
                keys = step.get("keys", [])
                await manager.broadcast_thought(f"⌨️ Hotkey: {'+'.join(keys)}")
                pyautogui.hotkey(*keys)
            
            elif action == "type":
                text = step.get("text", "")
                await manager.broadcast_thought(f"⌨️ Typing: {text}")
                pyautogui.typewrite(text, interval=0.05)
            
            elif action == "click":
                x = step.get("x", 0)
                y = step.get("y", 0)
                await manager.broadcast_thought(f"🖱️ Click: ({x}, {y})")
                pyautogui.click(x, y)
            
            elif action == "thought":
                text = step.get("text", "")
                await manager.broadcast_thought(text)
            
            # Wait between actions
            await asyncio.sleep(delay)
        
        await manager.broadcast_state({"status": "IDLE"})
        await manager.broadcast_log("info", f"✅ Preset '{preset_name}' completed")
        
    except Exception as e:
        logger.error("preset_execution_error", preset=preset_name, error=str(e))
        await manager.broadcast_log("error", f"Preset failed: {e}")
        await manager.broadcast_state({"status": "ERROR"})
