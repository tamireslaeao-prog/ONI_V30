"""
ONI v7.0 - Vector Memory Service
Semantic memory using ChromaDB for efficient vector search.
"""

import time
import uuid
from typing import Optional, List, Dict, Any
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class ExperienceType(str, Enum):
    """Type of experience stored in memory."""
    SUCCESS = "success"
    FAILURE = "failure"
    INSIGHT = "insight"
    CORRECTION = "correction"
    ERROR = "error"


class VectorMemoryService:
    """
    Vector Memory Service using ChromaDB.
    
    Features:
    - Semantic similarity search
    - Episodic memory (successes + failures)
    - Fast retrieval with embeddings
    """
    
    _client = None
    _collection = None
    COLLECTION_NAME = "oni_experiences"
    PERSIST_DIR = "data/chroma"
    
    @classmethod
    def _init_client(cls) -> bool:
        """Lazy initialize ChromaDB client."""
        if cls._client is not None:
            return True
            
        try:
            import chromadb
            from chromadb.config import Settings
            
            cls._client = chromadb.Client(Settings(
                persist_directory=cls.PERSIST_DIR,
                anonymized_telemetry=False
            ))
            
            cls._collection = cls._client.get_or_create_collection(
                name=cls.COLLECTION_NAME,
                metadata={"description": "ONI episodic memory"}
            )
            
            logger.info("vector_memory_initialized", 
                       collection=cls.COLLECTION_NAME,
                       persist_dir=cls.PERSIST_DIR)
            return True
            
        except ImportError:
            logger.warning("chromadb_not_installed", 
                          hint="pip install chromadb")
            return False
        except Exception as e:
            logger.error("vector_memory_init_failed", error=str(e))
            return False
    
    @classmethod
    def add_experience(
        cls,
        content: str,
        experience_type: ExperienceType,
        app_name: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add an experience to memory.
        
        Args:
            content: Description of the experience
            experience_type: success, failure, insight, correction, error
            app_name: Application context
            metadata: Additional metadata
            
        Returns:
            ID of the stored experience
        """
        if not cls._init_client():
            return None
            
        try:
            exp_id = str(uuid.uuid4())[:8]
            
            full_metadata = {
                "type": experience_type.value,
                "app": app_name,
                "timestamp": time.time(),
                **(metadata or {})
            }
            
            cls._collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[exp_id]
            )
            
            logger.info("experience_added", 
                       id=exp_id, 
                       type=experience_type.value,
                       app=app_name)
            return exp_id
            
        except Exception as e:
            logger.error("add_experience_failed", error=str(e))
            return None
    
    @classmethod
    def query_similar(
        cls,
        query: str,
        n_results: int = 5,
        experience_type: Optional[ExperienceType] = None,
        app_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find semantically similar experiences.
        
        Args:
            query: Search query
            n_results: Number of results to return
            experience_type: Filter by type
            app_name: Filter by app
            
        Returns:
            List of similar experiences with similarity scores
        """
        if not cls._init_client():
            return []
            
        try:
            # Build filter
            where_filter = {}
            if experience_type:
                where_filter["type"] = experience_type.value
            if app_name:
                where_filter["app"] = app_name
            
            results = cls._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            experiences = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    exp = {
                        "id": results['ids'][0][i] if results['ids'] else None,
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results.get('distances') else None
                    }
                    # Convert distance to similarity (0-1)
                    if exp['distance'] is not None:
                        exp['similarity'] = round(1 - exp['distance'], 3)
                    experiences.append(exp)
            
            logger.debug("query_similar_results", 
                        query=query[:50], 
                        results=len(experiences))
            return experiences
            
        except Exception as e:
            logger.error("query_similar_failed", error=str(e))
            return []
    
    @classmethod
    def store_success(cls, action: str, app_name: str, context: str = "") -> Optional[str]:
        """Shortcut to store a successful action."""
        content = f"SUCCESS: {action}"
        if context:
            content += f" | Context: {context}"
        return cls.add_experience(content, ExperienceType.SUCCESS, app_name)
    
    @classmethod
    def store_failure(cls, action: str, app_name: str, error: str = "") -> Optional[str]:
        """Shortcut to store a failed action."""
        content = f"FAILURE: {action}"
        if error:
            content += f" | Error: {error}"
        return cls.add_experience(content, ExperienceType.FAILURE, app_name)
    
    @classmethod
    def store_insight(cls, insight: str, app_name: str = "") -> Optional[str]:
        """Store a learned insight."""
        return cls.add_experience(
            f"INSIGHT: {insight}", 
            ExperienceType.INSIGHT, 
            app_name
        )
    
    @classmethod
    def store_correction(cls, wrong: str, correct: str, app_name: str = "") -> Optional[str]:
        """Store a correction (wrong -> correct)."""
        content = f"CORRECTION: Instead of '{wrong}', use '{correct}'"
        return cls.add_experience(content, ExperienceType.CORRECTION, app_name)
    
    @classmethod
    def build_context(cls, task: str, app_name: str = "", max_experiences: int = 3) -> str:
        """
        Build a context string with relevant past experiences.
        
        Useful for augmenting prompts with relevant memories.
        """
        experiences = cls.query_similar(task, n_results=max_experiences, app_name=app_name)
        
        if not experiences:
            return ""
        
        context_parts = ["## Relevant Past Experiences:"]
        for exp in experiences:
            sim = exp.get('similarity', 0)
            content = exp.get('content', '')
            exp_type = exp.get('metadata', {}).get('type', 'unknown')
            context_parts.append(f"- [{exp_type}] {content} (relevance: {sim:.0%})")
        
        return "\n".join(context_parts)
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get memory statistics."""
        if not cls._init_client():
            return {"error": "ChromaDB not initialized"}
            
        try:
            count = cls._collection.count()
            return {
                "total_experiences": count,
                "collection": cls.COLLECTION_NAME,
                "persist_dir": cls.PERSIST_DIR
            }
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def clear_old_experiences(cls, days: int = 30) -> int:
        """Remove experiences older than X days."""
        if not cls._init_client():
            return 0
            
        try:
            cutoff = time.time() - (days * 86400)
            
            # ChromaDB doesn't support delete by filter directly
            # We need to get IDs first
            results = cls._collection.get(
                where={"timestamp": {"$lt": cutoff}}
            )
            
            if results and results['ids']:
                cls._collection.delete(ids=results['ids'])
                logger.info("experiences_cleaned", count=len(results['ids']), days=days)
                return len(results['ids'])
            
            return 0
            
        except Exception as e:
            logger.error("cleanup_failed", error=str(e))
            return 0


# Initialize on import
try:
    VectorMemoryService._init_client()
except Exception:
    pass
