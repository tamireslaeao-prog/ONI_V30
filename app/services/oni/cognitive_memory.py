"""
ONI Cognitive Memory Service
Manages persistent action history and semantic failure analysis.
"""

import time
import sqlite3
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class CognitiveMemoryService:
    """
    Cognitive Memory Service (v5.3 - SQLite).
    Manages persistent action history and semantic failure analysis.
    """
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DB_FILE = os.path.join(BASE_DIR, "data", "memory", "oni_cognitive.db")
    
    @classmethod
    def _get_conn(cls):
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
        
    @classmethod
    def init_db(cls):
        """Initialize database schema."""
        try:
            with cls._get_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS action_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        action_type TEXT,
                        app_name TEXT,
                        window_title TEXT,
                        x INTEGER,
                        y INTEGER,
                        success BOOLEAN,
                        strategy_used TEXT,
                        error_context TEXT,
                        latency_ms REAL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_loc ON action_history(app_name, x, y)")
        except Exception as e:
            logger.error("memory_init_failed", error=str(e))

    @classmethod
    def record_action(cls, x: int, y: int, app_name: str, success: bool, strategy: str = "click", context: str = ""):
        """Record an action outcome."""
        try:
            with cls._get_conn() as conn:
                conn.execute("""
                    INSERT INTO action_history 
                    (timestamp, action_type, app_name, x, y, success, strategy_used, error_context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    "smart_click",
                    app_name,
                    x, y,
                    success,
                    strategy,
                    context
                ))
        except Exception as e:
            logger.error("memory_record_failed", error=str(e))

    @classmethod
    def is_safe_to_click(cls, x: int, y: int, app_name: str, radius: int = 50) -> bool:
        """
        Check if an area is 'cursed' (high failure rate).
        Returns False if >3 failures in radius recently.
        """
        if not app_name: return True
        
        try:
            with cls._get_conn() as conn:
                cursor = conn.execute("""
                    SELECT x, y, success, timestamp 
                    FROM action_history 
                    WHERE app_name = ? 
                    AND timestamp > ?
                    AND x BETWEEN ? AND ?
                    AND y BETWEEN ? AND ?
                """, (
                    app_name,
                    time.time() - 86400,
                    x - radius, x + radius,
                    y - radius, y + radius
                ))
                
                failures = 0
                for row in cursor:
                    dist_sq = (row['x'] - x)**2 + (row['y'] - y)**2
                    if dist_sq <= radius**2 and not row['success']:
                        failures += 1
                        
                if failures >= 3:
                     logger.warning("unsafe_action_prevented", failures=failures, app=app_name)
                     return False
                     
                return True
        except Exception as e:
            logger.error("memory_safety_check_failed", error=str(e))
            return True

    @classmethod
    def cleanup_old_data(cls, days: int = 30) -> int:
        """Auto-cleanup: Remove action history older than X days."""
        try:
            cutoff = time.time() - (days * 86400)
            with cls._get_conn() as conn:
                cursor = conn.execute(
                    "DELETE FROM action_history WHERE timestamp < ?",
                    (cutoff,)
                )
                deleted = cursor.rowcount
                logger.info("memory_cleanup", deleted_rows=deleted, days=days)
                return deleted
        except Exception as e:
            logger.error("memory_cleanup_failed", error=str(e))
            return 0

    @classmethod
    def get_failure_hotspots(cls, app_name: str = None, limit: int = 20) -> list:
        """Get heatmap data: Areas with highest failure rates."""
        try:
            with cls._get_conn() as conn:
                query = """
                    SELECT 
                        x, y, app_name,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures,
                        COUNT(*) as total,
                        ROUND(100.0 * SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) as failure_rate
                    FROM action_history 
                    WHERE timestamp > ?
                """
                params = [time.time() - 604800]
                
                if app_name:
                    query += " AND app_name = ?"
                    params.append(app_name)
                    
                query += """
                    GROUP BY x, y, app_name
                    HAVING failures >= 2
                    ORDER BY failure_rate DESC, failures DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor = conn.execute(query, params)
                hotspots = []
                for row in cursor:
                    hotspots.append({
                        "x": row["x"],
                        "y": row["y"],
                        "app": row["app_name"],
                        "failures": row["failures"],
                        "total": row["total"],
                        "failure_rate": row["failure_rate"]
                    })
                return hotspots
        except Exception as e:
            logger.error("heatmap_query_failed", error=str(e))
            return []

    @classmethod
    def suggest_alternative_strategy(cls, x: int, y: int, app_name: str) -> Optional[str]:
        """Suggest alternative strategy based on past successes in similar areas."""
        try:
            with cls._get_conn() as conn:
                cursor = conn.execute("""
                    SELECT strategy_used, COUNT(*) as success_count
                    FROM action_history 
                    WHERE app_name = ?
                    AND success = 1
                    AND x BETWEEN ? AND ?
                    AND y BETWEEN ? AND ?
                    AND strategy_used != 'click'
                    GROUP BY strategy_used
                    ORDER BY success_count DESC
                    LIMIT 1
                """, (
                    app_name,
                    x - 100, x + 100,
                    y - 100, y + 100
                ))
                
                row = cursor.fetchone()
                if row and row["success_count"] >= 2:
                    return row["strategy_used"]
                return None
        except Exception as e:
            logger.error("strategy_suggestion_failed", error=str(e))
            return None


# Initialize DB on import
try:
    CognitiveMemoryService.init_db()
except Exception:
    pass
