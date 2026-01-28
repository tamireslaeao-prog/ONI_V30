"""
ONI v2.0 - Event Bus System
Async pub/sub for decoupled component communication
"""
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger()


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """Base event class."""
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    source: str = "unknown"
    data: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Specific Event Types
# =============================================================================

@dataclass
class AgentEvent(Event):
    """Agent-related events."""
    source: str = "agent"


@dataclass
class GoalSetEvent(AgentEvent):
    """Fired when a new goal is set."""
    goal: str = ""


@dataclass
class ActionExecutedEvent(AgentEvent):
    """Fired after an action is executed."""
    action_type: str = ""
    target: str = ""
    success: bool = True
    duration_ms: float = 0.0


@dataclass
class CycleCompletedEvent(AgentEvent):
    """Fired after an OODA-R cycle completes."""
    cycle_number: int = 0
    actions_taken: int = 0


@dataclass
class VisionEvent(Event):
    """Vision-related events."""
    source: str = "vision"


@dataclass
class ScreenCapturedEvent(VisionEvent):
    """Fired when screen is captured."""
    width: int = 0
    height: int = 0
    capture_time_ms: float = 0.0


@dataclass
class OCRCompletedEvent(VisionEvent):
    """Fired when OCR processing completes."""
    text_regions_found: int = 0
    processing_time_ms: float = 0.0


@dataclass
class SystemEvent(Event):
    """System-level events."""
    source: str = "system"


@dataclass
class ErrorEvent(SystemEvent):
    """Error occurred."""
    error_type: str = ""
    error_message: str = ""
    priority: EventPriority = EventPriority.HIGH


@dataclass
class EmergencyStopEvent(SystemEvent):
    """Emergency stop triggered."""
    reason: str = ""
    priority: EventPriority = EventPriority.CRITICAL


# Type alias for event handlers
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Async event bus for pub/sub communication.
    
    Features:
    - Priority-based event handling
    - Async handlers
    - Event filtering
    - Handler groups for batch unsubscription
    """
    
    def __init__(self) -> None:
        self._handlers: dict[type[Event], list[tuple[EventHandler, EventPriority]]] = defaultdict(list)
        self._handler_groups: dict[str, list[tuple[type[Event], EventHandler]]] = defaultdict(list)
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        self._processing = False
        self._history: list[Event] = []
        self._max_history = 1000
    
    def subscribe(
        self,
        event_type: type[Event],
        handler: EventHandler,
        priority: EventPriority = EventPriority.NORMAL,
        group: str | None = None,
    ) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async handler function
            priority: Handler priority (higher = called first)
            group: Optional group name for batch unsubscription
        """
        self._handlers[event_type].append((handler, priority))
        # Sort by priority (descending)
        self._handlers[event_type].sort(key=lambda x: x[1].value, reverse=True)
        
        if group:
            self._handler_groups[group].append((event_type, handler))
        
        logger.debug("event_handler_subscribed", event_type=event_type.__name__, group=group)
    
    def unsubscribe(self, event_type: type[Event], handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        self._handlers[event_type] = [
            (h, p) for h, p in self._handlers[event_type] if h != handler
        ]
    
    def unsubscribe_group(self, group: str) -> None:
        """Unsubscribe all handlers in a group."""
        if group in self._handler_groups:
            for event_type, handler in self._handler_groups[group]:
                self.unsubscribe(event_type, handler)
            del self._handler_groups[group]
            logger.debug("event_group_unsubscribed", group=group)
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Add to history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Get handlers for exact type and parent types
        handlers: list[tuple[EventHandler, EventPriority]] = []
        for event_class in type(event).__mro__:
            if event_class in self._handlers:
                handlers.extend(self._handlers[event_class])
        
        # Sort by priority and execute
        handlers.sort(key=lambda x: x[1].value, reverse=True)
        
        for handler, _ in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    "event_handler_error",
                    event_type=type(event).__name__,
                    error=str(e),
                )
    
    async def publish_async(self, event: Event) -> None:
        """Queue event for async processing."""
        await self._event_queue.put(event)
    
    async def start_processing(self) -> None:
        """Start processing queued events."""
        self._processing = True
        while self._processing:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=0.1)
                await self.publish(event)
            except asyncio.TimeoutError:
                continue
    
    def stop_processing(self) -> None:
        """Stop event processing loop."""
        self._processing = False
    
    def get_history(
        self,
        event_type: type[Event] | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Get event history, optionally filtered by type."""
        events = self._history
        if event_type:
            events = [e for e in events if isinstance(e, event_type)]
        return events[-limit:]
