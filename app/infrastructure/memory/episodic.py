"""
ONI v2.0 - Episodic Memory
SQLite-based storage for task history and patterns
"""
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class Episode:
    """An episode (task execution record)."""
    id: int
    goal: str
    status: str  # "success", "failed", "partial"
    actions: list[dict[str, Any]]
    start_time: datetime
    end_time: datetime | None
    error: str | None
    metadata: dict[str, Any]


class EpisodicMemory:
    """
    Episodic memory using SQLite with FTS5 for full-text search.
    
    Features:
    - Task execution history
    - Error patterns and recovery strategies
    - UI element location cache
    - Full-text search
    """
    
    def __init__(self, db_path: Path | None = None) -> None:
        """
        Initialize episodic memory.
        
        Args:
            db_path: Path to SQLite database
        """
        self._db_path = db_path or settings.memory.sqlite_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
    
    def connect(self) -> None:
        """Connect to database and create tables."""
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info("episodic_memory_connected", path=str(self._db_path))
    
    def _create_tables(self) -> None:
        """Create database tables."""
        cursor = self._conn.cursor()
        
        # Episodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                actions TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                error TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                goal, actions, error,
                content='episodes',
                content_rowid='id'
            )
        """)
        
        # Error patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                context TEXT NOT NULL,
                recovery_strategy TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # UI element cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                element_text TEXT NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                confidence REAL,
                last_seen TEXT NOT NULL,
                hit_count INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodes_goal ON episodes(goal)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ui_elements_app ON ui_elements(app_name)")
        
        self._conn.commit()
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    # =========================================================================
    # Episode Operations
    # =========================================================================
    
    def save_episode(self, episode: Episode) -> int:
        """Save an episode to the database."""
        cursor = self._conn.cursor()
        
        cursor.execute("""
            INSERT INTO episodes (goal, status, actions, start_time, end_time, error, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            episode.goal,
            episode.status,
            json.dumps(episode.actions),
            episode.start_time.isoformat(),
            episode.end_time.isoformat() if episode.end_time else None,
            episode.error,
            json.dumps(episode.metadata),
        ))
        
        episode_id = cursor.lastrowid
        
        # Update FTS index
        cursor.execute("""
            INSERT INTO episodes_fts (rowid, goal, actions, error)
            VALUES (?, ?, ?, ?)
        """, (episode_id, episode.goal, json.dumps(episode.actions), episode.error or ""))
        
        self._conn.commit()
        logger.debug("episode_saved", id=episode_id, goal=episode.goal[:50])
        
        return episode_id
    
    def get_episode(self, episode_id: int) -> Episode | None:
        """Get episode by ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_episode(row)
        return None
    
    def search_episodes(self, query: str, limit: int = 10) -> list[Episode]:
        """Search episodes using full-text search."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT e.* FROM episodes e
            JOIN episodes_fts fts ON e.id = fts.rowid
            WHERE episodes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    def get_similar_goals(self, goal: str, limit: int = 5) -> list[Episode]:
        """Find episodes with similar goals."""
        # Simple word-based similarity search
        words = goal.lower().split()[:5]
        query = " OR ".join(words)
        return self.search_episodes(query, limit)
    
    def get_successful_patterns(self, goal: str) -> list[Episode]:
        """Get successful episodes for similar goal."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM episodes
            WHERE status = 'success' AND goal LIKE ?
            ORDER BY end_time DESC
            LIMIT 10
        """, (f"%{goal[:20]}%",))
        
        return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Convert database row to Episode."""
        return Episode(
            id=row["id"],
            goal=row["goal"],
            status=row["status"],
            actions=json.loads(row["actions"]),
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            error=row["error"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
    
    # =========================================================================
    # Error Pattern Operations
    # =========================================================================
    
    def save_error_pattern(
        self,
        error_type: str,
        context: dict[str, Any],
        recovery_strategy: str,
        success: bool,
    ) -> None:
        """Save or update an error pattern."""
        cursor = self._conn.cursor()
        
        # Check if pattern exists
        cursor.execute("""
            SELECT id, success_count, failure_count FROM error_patterns
            WHERE error_type = ? AND recovery_strategy = ?
        """, (error_type, recovery_strategy))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing
            if success:
                cursor.execute("""
                    UPDATE error_patterns SET success_count = success_count + 1
                    WHERE id = ?
                """, (row["id"],))
            else:
                cursor.execute("""
                    UPDATE error_patterns SET failure_count = failure_count + 1
                    WHERE id = ?
                """, (row["id"],))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO error_patterns (error_type, context, recovery_strategy, success_count, failure_count)
                VALUES (?, ?, ?, ?, ?)
            """, (error_type, json.dumps(context), recovery_strategy, 1 if success else 0, 0 if success else 1))
        
        self._conn.commit()
    
    def get_recovery_strategies(self, error_type: str) -> list[tuple[str, float]]:
        """Get ranked recovery strategies for an error type."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT recovery_strategy, success_count, failure_count
            FROM error_patterns
            WHERE error_type = ?
            ORDER BY (success_count * 1.0 / (success_count + failure_count + 1)) DESC
        """, (error_type,))
        
        results = []
        for row in cursor.fetchall():
            total = row["success_count"] + row["failure_count"]
            success_rate = row["success_count"] / total if total > 0 else 0
            results.append((row["recovery_strategy"], success_rate))
        
        return results
    
    # =========================================================================
    # UI Element Cache
    # =========================================================================
    
    def cache_ui_element(
        self,
        app_name: str,
        element_text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        confidence: float = 1.0,
    ) -> None:
        """Cache a UI element location."""
        cursor = self._conn.cursor()
        
        # Check if exists
        cursor.execute("""
            SELECT id, hit_count FROM ui_elements
            WHERE app_name = ? AND element_text = ?
        """, (app_name, element_text))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing
            cursor.execute("""
                UPDATE ui_elements
                SET x = ?, y = ?, width = ?, height = ?, confidence = ?,
                    last_seen = ?, hit_count = hit_count + 1
                WHERE id = ?
            """, (x, y, width, height, confidence, datetime.now().isoformat(), row["id"]))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO ui_elements (app_name, element_text, x, y, width, height, confidence, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (app_name, element_text, x, y, width, height, confidence, datetime.now().isoformat()))
        
        self._conn.commit()
    
    def get_cached_element(self, app_name: str, element_text: str) -> dict[str, Any] | None:
        """Get cached UI element location."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT x, y, width, height, confidence, last_seen
            FROM ui_elements
            WHERE app_name = ? AND element_text = ?
        """, (app_name, element_text))
        
        row = cursor.fetchone()
        if row:
            return {
                "x": row["x"],
                "y": row["y"],
                "width": row["width"],
                "height": row["height"],
                "confidence": row["confidence"],
                "last_seen": row["last_seen"],
            }
        return None
