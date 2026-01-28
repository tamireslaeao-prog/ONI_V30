"""
ONI Cortex Service (Reflex Engine v1.0)
The Central Nervous System for Predictive Automation.
"""

import sqlite3
import time
import json
import os
import structlog
from typing import Optional, Dict, List, Any

logger = structlog.get_logger(__name__)

class CortexService:
    """
    Manages the Unified Cognitive Memory (oni_cortex.db).
    Implements the 'Read-Before-Act' loop.
    """
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DB_FILE = os.path.join(BASE_DIR, "data", "memory", "oni_cortex.db")

    @classmethod
    def _get_conn(cls):
        os.makedirs(os.path.dirname(cls.DB_FILE), exist_ok=True)
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_brain(cls):
        """Initialize the synaptic pathways (Schema)."""
        try:
            with cls._get_conn() as conn:
                # 1. Episodic Memory (What happened?)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS episodic_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        context_hash TEXT,      -- Hash(App + Window + Action)
                        app_name TEXT,
                        action_type TEXT,
                        outcome TEXT,           -- 'SUCCESS', 'FAIL', 'CRASH'
                        error_signature TEXT,   -- OCR or Exception contents
                        strategy_used TEXT,
                        duration_ms REAL
                    )
                """)
                
                # 2. Reflex Rules (What works?)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS reflex_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trigger_signature TEXT,  -- The 'Symptom' (Error code/text)
                        context_app TEXT,        -- The 'Patient' (App name)
                        strategy_name TEXT,      -- The 'Cure'
                        success_count INTEGER DEFAULT 0,
                        fail_count INTEGER DEFAULT 0,
                        confidence_score REAL DEFAULT 0.0, -- (Success / Total)
                        last_updated REAL,
                        UNIQUE(trigger_signature, context_app, strategy_name)
                    )
                """)
                
                # Indexes for speed
                conn.execute("CREATE INDEX IF NOT EXISTS idx_reflex_trigger ON reflex_rules(trigger_signature, context_app)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_episodic_context ON episodic_memory(context_hash)")
                
        except Exception as e:
            logger.error("cortex_lobotomy_failed", error=str(e))

    @classmethod
    def recall_reflex(cls, error_signature: str, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Reflex Arc: Fast lookup for a proven solution.
        Returns strategy only if confidence > 0.8 (Mastery).
        """
        try:
            # Normalize signature
            sig_hash = str(hash(error_signature)) # Simple hash for grouping similar errors
            
            with cls._get_conn() as conn:
                cursor = conn.execute("""
                    SELECT strategy_name, confidence_score, success_count
                    FROM reflex_rules
                    WHERE trigger_signature = ? AND context_app = ?
                    ORDER BY confidence_score DESC, success_count DESC
                    LIMIT 1
                """, (error_signature, app_name))
                
                row = cursor.fetchone()
                if row:
                    if row['confidence_score'] > 0.8 and row['success_count'] >= 3:
                        logger.info("reflex_triggered", strategy=row['strategy_name'], conf=row['confidence_score'])
                        return {
                            "strategy": row['strategy_name'],
                            "confidence": row['confidence_score'],
                            "is_reflex": True
                        }
        except Exception as e:
            logger.error("cortex_recall_failed", error=str(e))
        return None

    @classmethod
    def memorize_outcome(cls, error_signature: str, app_name: str, strategy: str, success: bool):
        """
        Synaptic Plasticity: Reinforce or Weaken a connection based on result.
        """
        try:
            timestamp = time.time()
            with cls._get_conn() as conn:
                # 1. Upsert Rule
                conn.execute("""
                    INSERT OR IGNORE INTO reflex_rules 
                    (trigger_signature, context_app, strategy_name, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (error_signature, app_name, strategy, timestamp))
                
                # 2. Update Weights
                if success:
                    sql = "UPDATE reflex_rules SET success_count = success_count + 1 WHERE trigger_signature=? AND context_app=? AND strategy_name=?"
                else:
                    sql = "UPDATE reflex_rules SET fail_count = fail_count + 1 WHERE trigger_signature=? AND context_app=? AND strategy_name=?"
                
                conn.execute(sql, (error_signature, app_name, strategy))
                
                # 3. Recalculate Confidence (Bayesian-ish smoothing can be added later, simple ratio for now)
                conn.execute("""
                    UPDATE reflex_rules 
                    SET confidence_score = (CAST(success_count AS REAL) / (success_count + fail_count)),
                        last_updated = ?
                    WHERE trigger_signature=? AND context_app=? AND strategy_name=?
                """, (timestamp, error_signature, app_name, strategy))
                
        except Exception as e:
            logger.error("cortex_learning_failed", error=str(e))

    @classmethod
    def record_episode(cls, app_name: str, action: str, outcome: str, error: str = ""):
        """Log raw history for dreaming (offline analysis)."""
        try:
            with cls._get_conn() as conn:
                conn.execute("""
                    INSERT INTO episodic_memory (timestamp, app_name, action_type, outcome, error_signature)
                    VALUES (?, ?, ?, ?, ?)
                """, (time.time(), app_name, action, outcome, error))
        except Exception:
            pass

# Initialize on import
CortexService.init_brain()
