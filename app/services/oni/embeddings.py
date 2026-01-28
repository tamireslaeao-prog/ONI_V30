"""
ONI Embeddings Service
Semantic memory search using sentence-transformers.
"""

import time
import sqlite3
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class EmbeddingsService:
    """
    Semantic Embeddings Service (v6.0).
    Uses sentence-transformers for semantic memory search.
    """
    _model = None
    _embeddings_cache = {}
    DB_FILE = "oni_embeddings.db"
    
    @classmethod
    def _init_model(cls):
        """Lazy load sentence-transformers model."""
        if cls._model is not None:
            return True
            
        try:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("embeddings_model_loaded", model="all-MiniLM-L6-v2")
            return True
        except ImportError:
            logger.warning("sentence_transformers_not_installed")
            return False
        except Exception as e:
            logger.error("embeddings_init_failed", error=str(e))
            return False
    
    @classmethod
    def _init_db(cls):
        """Initialize embeddings database."""
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    app_name TEXT,
                    error_context TEXT,
                    x INTEGER,
                    y INTEGER,
                    strategy_used TEXT,
                    embedding BLOB
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_embed_app ON error_embeddings(app_name)")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("embeddings_db_init_failed", error=str(e))
    
    @classmethod
    def encode(cls, text: str) -> Optional[list]:
        """Encode text to embedding vector."""
        if not cls._init_model():
            return None
            
        try:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            if text_hash in cls._embeddings_cache:
                return cls._embeddings_cache[text_hash]
            
            embedding = cls._model.encode(text).tolist()
            cls._embeddings_cache[text_hash] = embedding
            return embedding
            
        except Exception as e:
            logger.error("embedding_encode_failed", error=str(e))
            return None
    
    @classmethod
    def store_error(cls, app_name: str, error_context: str, x: int, y: int, strategy: str):
        """Store error with its embedding for future semantic search."""
        embedding = cls.encode(error_context)
        if not embedding:
            return False
            
        try:
            cls._init_db()
            import pickle
            conn = sqlite3.connect(cls.DB_FILE)
            conn.execute("""
                INSERT INTO error_embeddings 
                (timestamp, app_name, error_context, x, y, strategy_used, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(), app_name, error_context, x, y, strategy,
                pickle.dumps(embedding)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error("store_error_embedding_failed", error=str(e))
            return False
    
    @classmethod
    def find_similar_errors(cls, query: str, app_name: str = None, limit: int = 5) -> list:
        """Find semantically similar errors from history."""
        query_embedding = cls.encode(query)
        if not query_embedding:
            return []
            
        try:
            import pickle
            import numpy as np
            
            cls._init_db()
            conn = sqlite3.connect(cls.DB_FILE)
            
            query_sql = "SELECT * FROM error_embeddings WHERE timestamp > ?"
            params = [time.time() - 2592000]
            
            if app_name:
                query_sql += " AND app_name = ?"
                params.append(app_name)
            
            cursor = conn.execute(query_sql, params)
            
            results = []
            query_vec = np.array(query_embedding)
            
            for row in cursor:
                try:
                    stored_embedding = pickle.loads(row[7])
                    stored_vec = np.array(stored_embedding)
                    
                    similarity = np.dot(query_vec, stored_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(stored_vec)
                    )
                    
                    if similarity > 0.6:
                        results.append({
                            "error_context": row[3],
                            "app": row[2],
                            "x": row[4],
                            "y": row[5],
                            "strategy": row[6],
                            "similarity": round(float(similarity), 3)
                        })
                except Exception:
                    continue
            
            conn.close()
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error("find_similar_errors_failed", error=str(e))
            return []
