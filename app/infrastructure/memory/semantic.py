"""
ONI v2.0 - Semantic Memory
Vector store using ChromaDB for knowledge retrieval
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""
    id: str
    content: str
    metadata: dict[str, Any]
    distance: float
    relevance_score: float


class SemanticMemory:
    """
    Semantic memory using ChromaDB vector store.
    
    Features:
    - Dense vector embeddings
    - Similarity search
    - Knowledge base storage
    - Procedural knowledge
    """
    
    def __init__(
        self,
        persist_path: Path | None = None,
        collection_name: str = "oni_knowledge",
    ) -> None:
        """
        Initialize semantic memory.
        
        Args:
            persist_path: Path to persist ChromaDB
            collection_name: Name of the collection
        """
        self._persist_path = persist_path or settings.memory.vector_store_path
        self._collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None
        self._embedding_fn: Any = None
    
    async def initialize(self) -> None:
        """Initialize ChromaDB and embedding function."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            self._persist_path.mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self._persist_path),
                anonymized_telemetry=False,
            ))
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            logger.info(
                "semantic_memory_initialized",
                path=str(self._persist_path),
                collection=self._collection_name,
            )
            
        except Exception as e:
            logger.warning("chromadb_init_failed", error=str(e))
            # Use fallback in-memory storage
            self._collection = None
    
    async def add(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
        id: str | None = None,
    ) -> str:
        """
        Add content to semantic memory.
        
        Args:
            content: Text content to store
            metadata: Additional metadata
            id: Optional ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        if self._collection is None:
            logger.warning("semantic_memory_not_initialized")
            return ""
        
        import uuid
        doc_id = id or str(uuid.uuid4())
        
        self._collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
        
        logger.debug("semantic_memory_added", id=doc_id, length=len(content))
        return doc_id
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SemanticSearchResult]:
        """
        Search semantic memory.
        
        Args:
            query: Search query
            limit: Maximum results
            filter: Metadata filter
            
        Returns:
            List of search results
        """
        if self._collection is None:
            return []
        
        results = self._collection.query(
            query_texts=[query],
            n_results=limit,
            where=filter,
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
        
        search_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results["distances"] else 0
            # Convert distance to relevance (cosine similarity)
            relevance = 1 - min(distance, 1)
            
            search_results.append(SemanticSearchResult(
                id=doc_id,
                content=results["documents"][0][i],
                metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                distance=distance,
                relevance_score=relevance,
            ))
        
        return search_results
    
    async def delete(self, id: str) -> None:
        """Delete document by ID."""
        if self._collection:
            self._collection.delete(ids=[id])
    
    async def update(
        self,
        id: str,
        content: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Update existing document."""
        if self._collection is None:
            return
        
        update_kwargs = {"ids": [id]}
        if content:
            update_kwargs["documents"] = [content]
        if metadata:
            update_kwargs["metadatas"] = [metadata]
        
        self._collection.update(**update_kwargs)
    
    async def get_count(self) -> int:
        """Get total document count."""
        if self._collection:
            return self._collection.count()
        return 0
    
    # =========================================================================
    # Knowledge Base Operations
    # =========================================================================
    
    async def add_application_knowledge(
        self,
        app_name: str,
        knowledge: str,
        category: str = "general",
    ) -> str:
        """Add application-specific knowledge."""
        return await self.add(
            content=knowledge,
            metadata={
                "type": "application_knowledge",
                "app_name": app_name,
                "category": category,
            },
        )
    
    async def add_procedure(
        self,
        name: str,
        steps: list[str],
        app_name: str | None = None,
    ) -> str:
        """Add procedural knowledge (how-to)."""
        content = f"Procedure: {name}\n\nSteps:\n" + "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(steps)
        )
        
        return await self.add(
            content=content,
            metadata={
                "type": "procedure",
                "name": name,
                "app_name": app_name,
            },
        )
    
    async def search_procedures(
        self,
        query: str,
        app_name: str | None = None,
        limit: int = 3,
    ) -> list[SemanticSearchResult]:
        """Search for relevant procedures."""
        filter = {"type": "procedure"}
        if app_name:
            filter["app_name"] = app_name
        
        return await self.search(query, limit=limit, filter=filter)
    
    async def search_app_knowledge(
        self,
        query: str,
        app_name: str,
        limit: int = 5,
    ) -> list[SemanticSearchResult]:
        """Search application-specific knowledge."""
        return await self.search(
            query,
            limit=limit,
            filter={"type": "application_knowledge", "app_name": app_name},
        )
