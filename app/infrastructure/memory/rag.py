"""
ONI v2.0 - Hybrid RAG Engine
Combines multiple retrieval strategies for optimal context retrieval
"""
from dataclasses import dataclass, field
from typing import Any

import structlog

from app.infrastructure.memory.episodic import EpisodicMemory
from app.infrastructure.memory.semantic import SemanticMemory, SemanticSearchResult

logger = structlog.get_logger()


@dataclass
class RAGResult:
    """Combined RAG retrieval result."""
    content: str
    source: str  # "semantic", "episodic", "keyword"
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridRAG:
    """
    Hybrid Retrieval-Augmented Generation engine.
    
    Combines multiple retrieval strategies:
    1. Dense Retrieval: Semantic embeddings (ChromaDB)
    2. Sparse Retrieval: BM25/FTS keyword matching (SQLite)
    3. Temporal Retrieval: Time-weighted recent experiences
    
    Uses RRF (Reciprocal Rank Fusion) to combine results.
    """
    
    def __init__(
        self,
        semantic_memory: SemanticMemory | None = None,
        episodic_memory: EpisodicMemory | None = None,
    ) -> None:
        """
        Initialize hybrid RAG.
        
        Args:
            semantic_memory: Semantic memory instance
            episodic_memory: Episodic memory instance
        """
        self._semantic = semantic_memory
        self._episodic = episodic_memory
    
    async def retrieve(
        self,
        query: str,
        goal: str | None = None,
        limit: int = 10,
        include_semantic: bool = True,
        include_episodic: bool = True,
    ) -> list[RAGResult]:
        """
        Retrieve relevant context using hybrid approach.
        
        Args:
            query: Search query
            goal: Current goal for context
            limit: Maximum results
            include_semantic: Include semantic search
            include_episodic: Include episodic search
            
        Returns:
            Fused and ranked results
        """
        all_results: list[tuple[RAGResult, int]] = []  # (result, rank)
        
        # Semantic retrieval
        if include_semantic and self._semantic:
            semantic_results = await self._semantic.search(query, limit=limit * 2)
            for i, result in enumerate(semantic_results):
                all_results.append((
                    RAGResult(
                        content=result.content,
                        source="semantic",
                        score=result.relevance_score,
                        metadata=result.metadata,
                    ),
                    i + 1,  # 1-indexed rank
                ))
        
        # Episodic retrieval (keyword-based)
        if include_episodic and self._episodic:
            episodes = self._episodic.search_episodes(query, limit=limit)
            for i, episode in enumerate(episodes):
                # Summarize episode
                summary = f"Goal: {episode.goal}\nStatus: {episode.status}\nActions: {len(episode.actions)}"
                all_results.append((
                    RAGResult(
                        content=summary,
                        source="episodic",
                        score=0.8 - (i * 0.1),  # Decay by rank
                        metadata={
                            "episode_id": episode.id,
                            "goal": episode.goal,
                            "status": episode.status,
                        },
                    ),
                    i + 1,
                ))
            
            # Also search for similar goals
            if goal:
                similar = self._episodic.get_similar_goals(goal, limit=5)
                for i, episode in enumerate(similar):
                    summary = f"Similar task: {episode.goal}\nResult: {episode.status}"
                    all_results.append((
                        RAGResult(
                            content=summary,
                            source="episodic_similar",
                            score=0.7 - (i * 0.1),
                            metadata={"episode_id": episode.id},
                        ),
                        i + 1,
                    ))
        
        # Apply RRF (Reciprocal Rank Fusion)
        fused_results = self._rrf_fusion(all_results, k=60)
        
        # Sort by fused score and limit
        fused_results.sort(key=lambda x: x.score, reverse=True)
        return fused_results[:limit]
    
    def _rrf_fusion(
        self,
        results: list[tuple[RAGResult, int]],
        k: int = 60,
    ) -> list[RAGResult]:
        """
        Apply Reciprocal Rank Fusion.
        
        RRF score = sum(1 / (k + rank)) for each result across sources
        """
        # Group by content for deduplication
        seen_content: dict[str, RAGResult] = {}
        content_scores: dict[str, float] = {}
        
        for result, rank in results:
            content_key = result.content[:100]  # Use first 100 chars as key
            
            rrf_score = 1.0 / (k + rank)
            
            if content_key in content_scores:
                content_scores[content_key] += rrf_score
            else:
                seen_content[content_key] = result
                content_scores[content_key] = rrf_score
        
        # Update scores and return
        fused = []
        for content_key, result in seen_content.items():
            result.score = content_scores[content_key]
            fused.append(result)
        
        return fused
    
    async def get_context_for_goal(
        self,
        goal: str,
        max_tokens: int = 2000,
    ) -> str:
        """
        Get optimized context for a goal.
        
        Args:
            goal: Current goal
            max_tokens: Maximum context tokens
            
        Returns:
            Formatted context string
        """
        results = await self.retrieve(goal, goal=goal, limit=10)
        
        context_parts = []
        estimated_tokens = 0
        
        for result in results:
            # Rough token estimate (4 chars per token)
            tokens = len(result.content) // 4
            
            if estimated_tokens + tokens > max_tokens:
                break
            
            context_parts.append(f"[{result.source}] {result.content}")
            estimated_tokens += tokens
        
        return "\n\n".join(context_parts)
    
    async def store_experience(
        self,
        goal: str,
        actions: list[dict[str, Any]],
        success: bool,
        insights: str | None = None,
    ) -> None:
        """
        Store experience for future retrieval.
        
        Args:
            goal: Goal that was attempted
            actions: Actions taken
            success: Whether goal was achieved
            insights: Any insights learned
        """
        if self._semantic:
            # Store as procedural knowledge
            content = f"Task: {goal}\n"
            content += f"Result: {'Success' if success else 'Failed'}\n"
            content += f"Actions: {len(actions)} steps\n"
            
            if insights:
                content += f"Insights: {insights}\n"
            
            await self._semantic.add(
                content=content,
                metadata={
                    "type": "experience",
                    "goal": goal,
                    "success": success,
                    "action_count": len(actions),
                },
            )
            
            logger.debug("experience_stored", goal=goal[:50], success=success)
