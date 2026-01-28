"""
ONI v3.0 - Memory Manager
Claude-Mem inspired persistent memory system.

Integrates:
- EpisodicMemory (SQLite + FTS5) for task history
- SemanticMemory (ChromaDB) for semantic search
- Session management with AI compression
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

import structlog

from app.infrastructure.memory.episodic import EpisodicMemory, Episode
from app.infrastructure.memory.semantic import SemanticMemory, SemanticSearchResult

logger = structlog.get_logger()


@dataclass
class Observation:
    """A single observation (action + result) in a session."""
    id: str
    session_id: str
    timestamp: datetime
    action_type: str
    action_params: dict[str, Any]
    result: str  # "success", "failed", "pending"
    context: str  # OCR text, window title, etc.
    error: str | None = None


@dataclass
class Session:
    """A work session containing multiple observations."""
    id: str
    goal: str
    start_time: datetime
    end_time: datetime | None = None
    observations: list[Observation] = field(default_factory=list)
    summary: str | None = None  # AI-generated summary
    status: str = "active"  # "active", "completed", "failed"


class MemoryManager:
    """
    Unified memory manager inspired by claude-mem.
    
    Features:
    - Records observations (actions + results) during execution
    - Searches past sessions for relevant context
    - Compresses sessions with AI summaries
    - Injects relevant context into LLM prompts
    """
    
    def __init__(
        self,
        episodic: EpisodicMemory | None = None,
        semantic: SemanticMemory | None = None,
        llm: Any = None,
    ):
        """
        Initialize memory manager.
        
        Args:
            episodic: EpisodicMemory instance
            semantic: SemanticMemory instance
            llm: LLM provider for compression
        """
        self._episodic = episodic
        self._semantic = semantic
        self._llm = llm
        
        # Current session
        self._current_session: Session | None = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize memory systems."""
        if self._initialized:
            return
        
        # Initialize episodic if not provided
        if self._episodic is None:
            self._episodic = EpisodicMemory()
            self._episodic.connect()
        
        # Initialize semantic if not provided
        if self._semantic is None:
            self._semantic = SemanticMemory()
            await self._semantic.initialize()
        
        self._initialized = True
        logger.info("memory_manager_initialized")
    
    def start_session(self, goal: str) -> str:
        """
        Start a new session.
        
        Args:
            goal: The goal for this session
            
        Returns:
            Session ID
        """
        session_id = str(uuid4())[:8]
        self._current_session = Session(
            id=session_id,
            goal=goal,
            start_time=datetime.now(),
        )
        logger.info("session_started", session_id=session_id, goal=goal[:50])
        return session_id
    
    def record_observation(
        self,
        action_type: str,
        action_params: dict[str, Any],
        result: str,
        context: str = "",
        error: str | None = None,
    ) -> str | None:
        """
        Record an observation in the current session.
        
        Args:
            action_type: Type of action (click, type, hotkey, etc.)
            action_params: Action parameters
            result: Result status
            context: Screen context (OCR, window title)
            error: Error message if failed
            
        Returns:
            Observation ID or None if no session
        """
        if self._current_session is None:
            return None
        
        obs_id = str(uuid4())[:8]
        observation = Observation(
            id=obs_id,
            session_id=self._current_session.id,
            timestamp=datetime.now(),
            action_type=action_type,
            action_params=action_params,
            result=result,
            context=context[:500],  # Limit context size
            error=error,
        )
        self._current_session.observations.append(observation)
        
        logger.debug(
            "observation_recorded",
            obs_id=obs_id,
            action=action_type,
            result=result,
        )
        return obs_id
    
    async def end_session(self, status: str = "completed") -> None:
        """
        End the current session and save to memory.
        
        Args:
            status: Final status ("completed", "failed")
        """
        if self._current_session is None:
            return
        
        self._current_session.end_time = datetime.now()
        self._current_session.status = status
        
        # Generate summary if LLM available
        if self._llm and len(self._current_session.observations) > 0:
            self._current_session.summary = await self._compress_session()
        
        # Save to episodic memory
        self._save_session_to_episodic()
        
        # Save to semantic memory
        await self._save_session_to_semantic()
        
        logger.info(
            "session_ended",
            session_id=self._current_session.id,
            status=status,
            observations=len(self._current_session.observations),
        )
        
        self._current_session = None
    
    async def _compress_session(self) -> str:
        """Use LLM to compress session into summary."""
        if not self._llm or not self._current_session:
            return ""
        
        # Build observations text
        obs_text = []
        for obs in self._current_session.observations[-10:]:  # Last 10
            status = "✓" if obs.result == "success" else "✗"
            obs_text.append(f"{status} {obs.action_type}({obs.action_params})")
        
        prompt = f"""Summarize this GUI automation session in 2-3 sentences:

Goal: {self._current_session.goal}
Actions:
{chr(10).join(obs_text)}

Summary:"""
        
        try:
            response = await self._llm.generate(prompt=prompt)
            return response.text.strip()[:500]
        except Exception as e:
            logger.warning("session_compression_failed", error=str(e))
            return f"Session for: {self._current_session.goal}"
    
    def _save_session_to_episodic(self) -> None:
        """Save session to episodic memory."""
        if not self._episodic or not self._current_session:
            return
        
        actions = [
            {
                "type": obs.action_type,
                "params": obs.action_params,
                "result": obs.result,
                "error": obs.error,
            }
            for obs in self._current_session.observations
        ]
        
        episode = Episode(
            id=0,  # Auto-generated
            goal=self._current_session.goal,
            status=self._current_session.status,
            actions=actions,
            start_time=self._current_session.start_time,
            end_time=self._current_session.end_time,
            error=None,
            metadata={
                "session_id": self._current_session.id,
                "summary": self._current_session.summary,
            },
        )
        
        self._episodic.save_episode(episode)
    
    async def _save_session_to_semantic(self) -> None:
        """Save session summary to semantic memory."""
        if not self._semantic or not self._current_session:
            return
        
        content = f"""Goal: {self._current_session.goal}
Status: {self._current_session.status}
Summary: {self._current_session.summary or 'N/A'}
Actions: {len(self._current_session.observations)}"""
        
        await self._semantic.add(
            content=content,
            metadata={
                "session_id": self._current_session.id,
                "goal": self._current_session.goal,
                "status": self._current_session.status,
            },
        )
    
    async def get_relevant_context(self, query: str, limit: int = 3) -> str:
        """
        Get relevant context from past sessions.
        
        Args:
            query: Current goal or context
            limit: Max results
            
        Returns:
            Formatted context string for LLM prompt
        """
        contexts = []
        
        # Search episodic memory
        if self._episodic:
            episodes = self._episodic.get_similar_goals(query, limit=limit)
            for ep in episodes:
                if ep.status == "success":
                    actions = [a.get("type", "") for a in ep.actions[:5]]
                    contexts.append(f"✓ Past success: {ep.goal[:50]} → {', '.join(actions)}")
        
        # Search semantic memory
        if self._semantic:
            results = await self._semantic.search(query, k=limit)
            for result in results:
                if result.score > 0.7:
                    contexts.append(f"📝 {result.content[:100]}")
        
        if not contexts:
            return ""
        
        return "# Relevant Past Context:\n" + "\n".join(contexts[:limit])
    
    def get_session_observations(self) -> list[Observation]:
        """Get observations from current session."""
        if self._current_session:
            return self._current_session.observations
        return []


# Global singleton
_manager: MemoryManager | None = None


async def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _manager
    if _manager is None:
        _manager = MemoryManager()
        await _manager.initialize()
    return _manager
