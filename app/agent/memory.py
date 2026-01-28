"""
ONI v2.0 - Enhanced Agent Memory System

Persistent memory with pattern learning, session insights, and auto-cleanup.
Stores observations, actions, and learns from past experiences.
"""
import sqlite3
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Any
from collections import Counter
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Observation:
    """A single observation from the agent's experience."""
    timestamp: str
    goal: str
    action: dict
    result: str  # "success" or "failed"
    screen_context: str
    active_window: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SessionSummary:
    """Compressed summary of a session's experiences."""
    session_id: str
    goal: str
    start_time: str
    end_time: str
    total_actions: int
    successful_actions: int
    key_learnings: str


@dataclass
class LearnedPattern:
    """A pattern learned from successful executions."""
    goal_type: str
    action_sequence: list[dict]
    frequency: int
    success_rate: float


class AgentMemory:
    """
    Enhanced persistent memory system for the ONI agent.
    
    Features:
    - Observation storage with session tracking
    - Pattern learning from successful executions
    - Auto-cleanup of old data
    - Session insights extraction
    - Enriched context generation
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize memory with SQLite database."""
        self._db_path = db_path or Path("data/memory.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._conn: Optional[sqlite3.Connection] = None
        self._current_session: Optional[str] = None
        
        # In-memory cache of patterns
        self._pattern_cache: dict[str, list[LearnedPattern]] = {}
        self._cache_timestamp: Optional[datetime] = None
    
    def connect(self) -> None:
        """Connect to the database and create tables if needed."""
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info("memory_connected", db_path=str(self._db_path))
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def _create_tables(self) -> None:
        """Create the memory schema."""
        cursor = self._conn.cursor()
        
        # Observations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                goal TEXT NOT NULL,
                action TEXT NOT NULL,
                result TEXT NOT NULL,
                screen_context TEXT,
                active_window TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                final_result TEXT,
                total_actions INTEGER DEFAULT 0,
                successful_actions INTEGER DEFAULT 0
            )
        """)
        
        # Learned patterns table (NEW)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                action_sequence TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                last_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(goal_type, action_sequence)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_session 
            ON observations(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_goal 
            ON observations(goal)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_result 
            ON observations(result)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_goal_type 
            ON learned_patterns(goal_type)
        """)
        
        self._conn.commit()
    
    def start_session(self, goal: str) -> str:
        """Start a new session for a goal."""
        self._current_session = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (id, goal, start_time) VALUES (?, ?, ?)
        """, (self._current_session, goal, datetime.now().isoformat()))
        self._conn.commit()
        
        logger.info("memory_session_started", session_id=self._current_session, goal=goal[:50])
        return self._current_session
    
    def end_session(self, result: str = "completed") -> None:
        """End the current session with result analysis."""
        if not self._current_session:
            return
        
        cursor = self._conn.cursor()
        
        # Count actions in this session
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN result = 'success' THEN 1 ELSE 0 END) as successes
            FROM observations WHERE session_id = ?
        """, (self._current_session,))
        
        row = cursor.fetchone()
        total = row["total"] if row else 0
        successes = row["successes"] if row else 0
        
        # Update session
        cursor.execute("""
            UPDATE sessions SET 
                end_time = ?,
                final_result = ?,
                total_actions = ?,
                successful_actions = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), result, total, successes, self._current_session))
        
        self._conn.commit()
        
        # Learn patterns if successful
        if result == "success" and total > 0:
            self._learn_from_session(self._current_session)
        
        logger.info("memory_session_ended", 
                   session_id=self._current_session, 
                   result=result,
                   total_actions=total,
                   success_rate=successes/total if total > 0 else 0)
        
        self._current_session = None
    
    def store_observation(self, obs: Observation) -> None:
        """Store an observation from the current session."""
        if not self._conn:
            self.connect()
        
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO observations 
            (session_id, timestamp, goal, action, result, screen_context, active_window)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self._current_session or "standalone",
            obs.timestamp,
            obs.goal,
            json.dumps(obs.action) if isinstance(obs.action, dict) else obs.action,
            obs.result,
            obs.screen_context,
            obs.active_window
        ))
        self._conn.commit()
    
    def _learn_from_session(self, session_id: str) -> None:
        """Extract and store patterns from a successful session."""
        cursor = self._conn.cursor()
        
        # Get session info
        cursor.execute("SELECT goal FROM sessions WHERE id = ?", (session_id,))
        session = cursor.fetchone()
        if not session:
            return
        
        goal_type = self._classify_goal(session["goal"])
        
        # Get successful action sequence
        cursor.execute("""
            SELECT action FROM observations 
            WHERE session_id = ? AND result = 'success'
            ORDER BY timestamp
        """, (session_id,))
        
        actions = [json.loads(row["action"]) for row in cursor.fetchall()]
        
        if len(actions) < 2:
            return
        
        # Store pattern
        action_seq = json.dumps(actions)
        
        try:
            cursor.execute("""
                INSERT INTO learned_patterns (goal_type, action_sequence, frequency, last_used)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(goal_type, action_sequence) DO UPDATE SET
                    frequency = frequency + 1,
                    last_used = excluded.last_used
            """, (goal_type, action_seq, datetime.now().isoformat()))
            self._conn.commit()
            
            logger.info("pattern_learned", goal_type=goal_type, action_count=len(actions))
        except Exception as e:
            logger.warning("pattern_learning_failed", error=str(e))
        
        # Invalidate cache
        self._pattern_cache = {}
    
    def _classify_goal(self, goal: str) -> str:
        """Classify goal into a type for pattern matching."""
        goal_lower = goal.lower()
        
        if any(kw in goal_lower for kw in ["open", "launch", "start", "abrir"]):
            return "open_app"
        elif any(kw in goal_lower for kw in ["create", "new", "criar", "novo"]):
            return "create"
        elif any(kw in goal_lower for kw in ["draw", "desenhar", "paint"]):
            return "draw"
        elif any(kw in goal_lower for kw in ["save", "salvar"]):
            return "save"
        elif any(kw in goal_lower for kw in ["close", "fechar"]):
            return "close"
        else:
            return "general"
    
    def get_learned_patterns(self, goal_type: str, limit: int = 5) -> list[LearnedPattern]:
        """Get learned patterns for a goal type."""
        # Check cache
        if self._pattern_cache and goal_type in self._pattern_cache:
            return self._pattern_cache[goal_type][:limit]
        
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT goal_type, action_sequence, frequency, success_rate
            FROM learned_patterns
            WHERE goal_type = ?
            ORDER BY frequency DESC, success_rate DESC
            LIMIT ?
        """, (goal_type, limit))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append(LearnedPattern(
                goal_type=row["goal_type"],
                action_sequence=json.loads(row["action_sequence"]),
                frequency=row["frequency"],
                success_rate=row["success_rate"]
            ))
        
        self._pattern_cache[goal_type] = patterns
        return patterns
    
    def get_relevant_context(self, goal: str, limit: int = 5) -> str:
        """
        Get relevant past experiences for a goal.
        Uses keyword matching and learned patterns.
        """
        if not self._conn:
            self.connect()
        
        context_parts = []
        
        # Get learned patterns
        goal_type = self._classify_goal(goal)
        patterns = self.get_learned_patterns(goal_type, limit=2)
        
        if patterns:
            context_parts.append("LEARNED PATTERNS:")
            for p in patterns:
                actions = [a.get("action", "?") for a in p.action_sequence[:5]]
                context_parts.append(f"  • {' → '.join(actions)} (used {p.frequency}x)")
        
        # Get past successful observations
        cursor = self._conn.cursor()
        keywords = goal.lower().split()[:3]
        
        for keyword in keywords:
            if len(keyword) < 3:
                continue
            
            cursor.execute("""
                SELECT goal, action, active_window
                FROM observations 
                WHERE goal LIKE ? AND result = 'success'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{keyword}%", limit))
            
            rows = cursor.fetchall()
            
            if rows:
                context_parts.append(f"\nPAST SUCCESSES ('{keyword}'):")
                for row in rows:
                    action = json.loads(row["action"]) if row["action"] else {}
                    action_str = action.get("action", "unknown")
                    context_parts.append(f"  • {row['goal'][:40]} → {action_str}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_session_insights(self, session_id: str) -> dict[str, Any]:
        """Analyze a session and extract insights."""
        cursor = self._conn.cursor()
        
        cursor.execute("""
            SELECT * FROM observations
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))
        
        observations = [dict(row) for row in cursor.fetchall()]
        
        if not observations:
            return {}
        
        # Parse actions
        actions = []
        for obs in observations:
            try:
                actions.append(json.loads(obs["action"]))
            except:
                pass
        
        action_types = [a.get("action", "unknown") for a in actions]
        
        # Calculate metrics
        success_count = sum(1 for o in observations if o["result"] == "success")
        
        # Calculate duration
        try:
            start = datetime.fromisoformat(observations[0]["timestamp"])
            end = datetime.fromisoformat(observations[-1]["timestamp"])
            duration = (end - start).total_seconds()
        except:
            duration = 0
        
        insights = {
            "session_id": session_id,
            "total_actions": len(observations),
            "successful_actions": success_count,
            "success_rate": success_count / len(observations) if observations else 0,
            "duration_seconds": duration,
            "action_distribution": dict(Counter(action_types)),
            "most_common_action": Counter(action_types).most_common(1)[0] if action_types else None,
            "failed_actions": [
                json.loads(o["action"]) for o in observations 
                if o["result"] != "success"
            ],
            "efficiency_score": len(observations) / max(1, duration) if duration > 0 else 0,
        }
        
        return insights
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Remove old observations while keeping successful sessions.
        Returns number of deleted records.
        """
        cursor = self._conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        # Delete old observations, but keep those from successful sessions
        cursor.execute("""
            DELETE FROM observations
            WHERE created_at < ? 
            AND session_id NOT IN (
                SELECT id FROM sessions 
                WHERE final_result = 'success'
                ORDER BY end_time DESC 
                LIMIT 20
            )
        """, (cutoff,))
        
        deleted_obs = cursor.rowcount
        
        # Delete old unsuccessful sessions
        cursor.execute("""
            DELETE FROM sessions
            WHERE end_time < ?
            AND final_result != 'success'
        """, (cutoff,))
        
        deleted_sessions = cursor.rowcount
        
        # Delete rarely used patterns
        cursor.execute("""
            DELETE FROM learned_patterns
            WHERE frequency < 2
            AND last_used < ?
        """, (cutoff,))
        
        deleted_patterns = cursor.rowcount
        
        self._conn.commit()
        
        total = deleted_obs + deleted_sessions + deleted_patterns
        if total > 0:
            logger.info("memory_cleanup", 
                       observations=deleted_obs, 
                       sessions=deleted_sessions,
                       patterns=deleted_patterns)
        
        return total
    
    def get_enriched_context(self, goal: str, limit: int = 3) -> str:
        """Get enriched context with explanations and insights."""
        if not self._conn:
            self.connect()
        
        context_parts = []
        goal_type = self._classify_goal(goal)
        
        # Get patterns
        patterns = self.get_learned_patterns(goal_type, limit=2)
        if patterns:
            context_parts.append("🎓 LEARNED FROM EXPERIENCE:")
            for p in patterns:
                actions = [a.get("action", "?") for a in p.action_sequence[:6]]
                context_parts.append(f"   Pattern: {' → '.join(actions)}")
                context_parts.append(f"   Used {p.frequency}x with {p.success_rate:.0%} success")
        
        # Get similar sessions
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT id, goal, total_actions, successful_actions
            FROM sessions
            WHERE goal LIKE ? AND final_result = 'success'
            ORDER BY end_time DESC
            LIMIT ?
        """, (f"%{goal_type}%", limit))
        
        similar = cursor.fetchall()
        if similar:
            context_parts.append("\n🎯 SIMILAR PAST GOALS:")
            for row in similar:
                success_rate = row["successful_actions"] / max(1, row["total_actions"])
                context_parts.append(f"   • {row['goal'][:40]}")
                context_parts.append(f"     {row['total_actions']} actions, {success_rate:.0%} success")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_session_stats(self) -> dict[str, Any]:
        """Get overall statistics about stored memory."""
        if not self._conn:
            self.connect()
        
        cursor = self._conn.cursor()
        
        # Observations count
        cursor.execute("SELECT COUNT(*) as count FROM observations")
        obs_count = cursor.fetchone()["count"]
        
        # Sessions count
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        session_count = cursor.fetchone()["count"]
        
        # Patterns count
        cursor.execute("SELECT COUNT(*) as count FROM learned_patterns")
        pattern_count = cursor.fetchone()["count"]
        
        # Success rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN final_result = 'success' THEN 1 ELSE 0 END) as successes
            FROM sessions WHERE final_result IS NOT NULL
        """)
        row = cursor.fetchone()
        success_rate = row["successes"] / max(1, row["total"]) if row else 0
        
        # Top patterns
        cursor.execute("""
            SELECT goal_type, SUM(frequency) as total_freq
            FROM learned_patterns
            GROUP BY goal_type
            ORDER BY total_freq DESC
            LIMIT 5
        """)
        top_patterns = {row["goal_type"]: row["total_freq"] for row in cursor.fetchall()}
        
        return {
            "total_observations": obs_count,
            "total_sessions": session_count,
            "total_patterns": pattern_count,
            "overall_success_rate": success_rate,
            "top_goal_types": top_patterns,
            "db_path": str(self._db_path),
        }


# Global memory instance
_memory: Optional[AgentMemory] = None


def get_memory() -> AgentMemory:
    """Get or create the global memory instance."""
    global _memory
    if _memory is None:
        _memory = AgentMemory()
        _memory.connect()
    return _memory
