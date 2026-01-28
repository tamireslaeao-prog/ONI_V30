import sqlite_utils
from pathlib import Path
from datetime import datetime, timedelta
import structlog
import shutil
import os
from typing import Optional, List, Dict, Any

logger = structlog.get_logger()

DB_PATH = Path("data/memory/actions.db")
KNOWLEDGE_PATH = Path("memo/MEUS_ERROS.md")
MODULES_PATH = Path("Modules")

class CognitiveMemoryService:
    """
    The Active Learning Engine of ONI.
    Autonomously detects failures, registers fixes, and promotes skills.
    """
    
    def __init__(self):
        self.db = sqlite_utils.Database(DB_PATH)
        self._init_schema()
        self._ensure_paths()

    def _ensure_paths(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not KNOWLEDGE_PATH.exists():
            KNOWLEDGE_PATH.write_text("# 🧠 ONI SELF-HEALING REGISTRY\n\n", encoding='utf-8')

    def _init_schema(self):
        """Initialize database schema."""
        # Action History (Short Term Memory)
        self.db["action_history"].create({
            "id": int,
            "timestamp": float,
            "app_name": str,
            "action_type": str,
            "target_desc": str,
            "success": bool,
            "error_msg": str
        }, pk="id", if_not_exists=True)
        
        # Learned Solutions (Long Term Memory)
        self.db["learned_solutions"].create({
            "id": int,
            "timestamp": float,
            "error_pattern": str,
            "solution_desc": str,
            "promoted_file": str
        }, pk="id", if_not_exists=True)

    def record_action(self, app_name: str, action: str, target: str, success: bool, error: str = None):
        """Record raw action outcome."""
        try:
            self.db["action_history"].insert({
                "timestamp": datetime.now().timestamp(),
                "app_name": app_name,
                "action_type": action,
                "target_desc": target,
                "success": success,
                "error_msg": error or ""
            })
            
            # AUTO-HEALING TRIGGER:
            # If we just succeeded after a recent failure on same target, register a fix.
            if success:
                self._check_for_resolution(app_name, action, target)
                
        except Exception as e:
            logger.error("memory_write_failed", error=str(e))

    def _check_for_resolution(self, app_name, action, target):
        """Did I just fix a problem?"""
        last_failure = self.db.query(f"""
            SELECT * FROM action_history 
            WHERE app_name = ? AND action_type = ? AND target_desc = ? AND success = 0
            ORDER BY timestamp DESC LIMIT 1
        """, (app_name, action, target))
        
        try:
            fail = next(last_failure)
            # If failure was recent (< 5 mins)
            if datetime.now().timestamp() - fail['timestamp'] < 300:
                fix_msg = f"Automatic Resolution: {action} on {target} succeeded after error '{fail['error_msg']}'"
                self._register_knowledge(fail['error_msg'], fix_msg)
        except StopIteration:
            pass # No recent failure, normal operations

    def promote_script_if_success(self, script_path: str, module_name: str):
        """
        Public API to be called by Executors after running a temp script.
        If script ran successfully, promote it to Modules/ automatically.
        """
        path = Path(script_path)
        if not path.exists(): return
        
        # Define destination
        dest_dir = MODULES_PATH / module_name / "Library"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / path.name
        
        try:
            # Copy file (Don't move, keep temp for reference or move? user prefers clean temp)
            # Let's Copy for safety, overwrite if exists (update skill)
            shutil.copy2(path, dest_file)
            
            msg = f"Skill Promoted: {path.name} -> {dest_file}"
            logger.info("self_healing_promotion", src=str(path), dst=str(dest_file))
            
            # Register in Knowledge Base
            self._register_knowledge("New Capability Detected", msg)
            
            return True
        except Exception as e:
            logger.error("promotion_failed", error=str(e))
            return False

    def _register_knowledge(self, problem: str, solution: str):
        """Writes directly to MEUS_ERROS.md (Persistent Knowledge)"""
        entry = f"""
## 🩹 Auto-Healing Event [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
- **Problem/Pattern:** {problem}
- **Solution/Action:** {solution}
- **Status:** FIXED & LOGGED
"""
        try:
            # Append to Markdown
            with open(KNOWLEDGE_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
            
            # Log to DB
            self.db["learned_solutions"].insert({
                "timestamp": datetime.now().timestamp(),
                "error_pattern": problem,
                "solution_desc": solution,
                "promoted_file": ""
            })
            
            logger.info("knowledge_base_updated", pattern=problem)
        except Exception as e:
            logger.error("kb_write_failed", error=str(e))

# Singleton
_cognitive_memory = None

def get_cognitive_memory():
    global _cognitive_memory
    if not _cognitive_memory:
        _cognitive_memory = CognitiveMemoryService()
    return _cognitive_memory
