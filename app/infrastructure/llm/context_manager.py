"""
ONI v2.0 - Context Manager
Dynamic context window management with semantic compression
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class ContextChunk:
    """A chunk of context with metadata."""
    id: str
    content: str
    role: str  # "system", "user", "assistant", "context"
    token_count: int
    importance_score: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_system(self) -> bool:
        return self.role == "system"
    
    @property
    def is_pinned(self) -> bool:
        return self.metadata.get("pinned", False)


@dataclass 
class ContextState:
    """Current state of the context window."""
    chunks: list[ContextChunk]
    total_tokens: int
    max_tokens: int
    compression_ratio: float = 1.0


class ContextManager:
    """
    Manages LLM context window dynamically.
    
    Features:
    - Semantic chunking
    - Importance scoring (recency, relevance, criticality)
    - Hierarchical pruning
    - Context reconstruction
    - LRU caching for frequently accessed chunks
    """
    
    def __init__(
        self,
        max_tokens: int | None = None,
        reserve_tokens: int = 512,
    ) -> None:
        """
        Initialize context manager.
        
        Args:
            max_tokens: Maximum context tokens
            reserve_tokens: Tokens to reserve for generation
        """
        self._max_tokens = max_tokens or settings.llm.context_size
        self._reserve_tokens = reserve_tokens
        self._effective_max = self._max_tokens - reserve_tokens
        
        self._chunks: list[ContextChunk] = []
        self._token_counter: callable = lambda x: len(x) // 4  # Default estimate
        
        # System prompt (always retained)
        self._system_prompt: str | None = None
        self._system_tokens: int = 0
    
    def set_token_counter(self, counter: callable) -> None:
        """Set a custom token counting function."""
        self._token_counter = counter
    
    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt (always retained)."""
        self._system_prompt = prompt
        self._system_tokens = self._token_counter(prompt)
        logger.debug("system_prompt_set", tokens=self._system_tokens)
    
    def add_chunk(
        self,
        content: str,
        role: str = "context",
        importance: float = 1.0,
        pinned: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Add a chunk to the context.
        
        Args:
            content: Chunk content
            role: Chunk role (system, user, assistant, context)
            importance: Base importance score
            pinned: If True, chunk is never pruned
            metadata: Additional metadata
            
        Returns:
            Chunk ID
        """
        chunk_id = self._generate_chunk_id(content)
        tokens = self._token_counter(content)
        
        chunk = ContextChunk(
            id=chunk_id,
            content=content,
            role=role,
            token_count=tokens,
            importance_score=importance,
            metadata=metadata or {},
        )
        
        if pinned:
            chunk.metadata["pinned"] = True
        
        self._chunks.append(chunk)
        
        # Trigger pruning if needed
        if self._get_total_tokens() > self._effective_max:
            self._prune_context()
        
        logger.debug(
            "chunk_added",
            id=chunk_id,
            role=role,
            tokens=tokens,
            total_chunks=len(self._chunks),
        )
        
        return chunk_id
    
    def add_message(
        self,
        role: str,
        content: str,
        importance: float = 1.0,
    ) -> str:
        """Add a conversation message as a chunk."""
        return self.add_chunk(
            content=content,
            role=role,
            importance=importance,
            metadata={"type": "message"},
        )
    
    def get_context(self, include_system: bool = True) -> str:
        """
        Get the current context as a string.
        
        Args:
            include_system: Include system prompt
            
        Returns:
            Formatted context string
        """
        parts = []
        
        if include_system and self._system_prompt:
            parts.append(self._system_prompt)
        
        for chunk in self._chunks:
            parts.append(chunk.content)
        
        return "\n\n".join(parts)
    
    def get_messages(self, include_system: bool = True) -> list[dict[str, str]]:
        """
        Get context as a list of messages.
        
        Returns:
            List of message dicts with role and content
        """
        messages = []
        
        if include_system and self._system_prompt:
            messages.append({
                "role": "system",
                "content": self._system_prompt,
            })
        
        for chunk in self._chunks:
            if chunk.role in ("user", "assistant", "system"):
                messages.append({
                    "role": chunk.role,
                    "content": chunk.content,
                })
        
        return messages
    
    def get_state(self) -> ContextState:
        """Get current context state."""
        total = self._get_total_tokens()
        return ContextState(
            chunks=list(self._chunks),
            total_tokens=total,
            max_tokens=self._effective_max,
            compression_ratio=total / self._effective_max if self._effective_max > 0 else 0,
        )
    
    def clear(self, keep_system: bool = True) -> None:
        """Clear all context chunks."""
        self._chunks.clear()
        if not keep_system:
            self._system_prompt = None
            self._system_tokens = 0
        logger.debug("context_cleared")
    
    # =========================================================================
    # Private Methods
    # =========================================================================
    
    def _generate_chunk_id(self, content: str) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{content[:100]}{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:12]
    
    def _get_total_tokens(self) -> int:
        """Calculate total tokens in context."""
        chunk_tokens = sum(c.token_count for c in self._chunks)
        return self._system_tokens + chunk_tokens
    
    def _calculate_importance(self, chunk: ContextChunk) -> float:
        """
        Calculate importance score for a chunk.
        
        Factors:
        - Base importance score
        - Recency (exponential decay)
        - Role (system > user > assistant > context)
        - Pinned status
        """
        if chunk.is_pinned:
            return float("inf")
        
        score = chunk.importance_score
        
        # Recency factor (decay over time)
        age_seconds = (datetime.now() - chunk.timestamp).total_seconds()
        recency_factor = 0.5 ** (age_seconds / 3600)  # Half-life of 1 hour
        score *= recency_factor
        
        # Role factor
        role_weights = {
            "system": 3.0,
            "user": 2.0,
            "assistant": 1.5,
            "context": 1.0,
        }
        score *= role_weights.get(chunk.role, 1.0)
        
        return score
    
    def _prune_context(self) -> None:
        """Prune context to fit within token limit."""
        target_tokens = int(self._effective_max * 0.8)  # Target 80% capacity
        
        while self._get_total_tokens() > target_tokens and self._chunks:
            # Calculate importance for all chunks
            scored_chunks = [
                (chunk, self._calculate_importance(chunk))
                for chunk in self._chunks
            ]
            
            # Find least important non-pinned chunk
            scored_chunks.sort(key=lambda x: x[1])
            
            for chunk, score in scored_chunks:
                if not chunk.is_pinned:
                    self._chunks.remove(chunk)
                    logger.debug(
                        "chunk_pruned",
                        id=chunk.id,
                        role=chunk.role,
                        score=score,
                    )
                    break
            else:
                # All chunks are pinned, can't prune more
                logger.warning("cannot_prune_all_chunks_pinned")
                break
    
    def _summarize_chunk(self, chunk: ContextChunk) -> ContextChunk:
        """
        Compress a chunk by summarizing it.
        
        Note: Actual summarization would require LLM call.
        This is a placeholder for the full implementation.
        """
        # For now, just truncate
        if len(chunk.content) > 500:
            summarized_content = chunk.content[:500] + "..."
            return ContextChunk(
                id=chunk.id,
                content=summarized_content,
                role=chunk.role,
                token_count=self._token_counter(summarized_content),
                importance_score=chunk.importance_score * 0.8,
                timestamp=chunk.timestamp,
                metadata={**chunk.metadata, "summarized": True},
            )
        return chunk
