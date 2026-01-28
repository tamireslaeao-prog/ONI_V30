"""
UNIVERSAL PERSISTENT SELF-HEALING ENGINE (UPSHE)
================================================
- Works with ANY module (Blender, Photoshop, Word, etc)
- Stores learned fixes in SQLite (survives restarts)
- Auto-loads on server startup
- Automatically adds new working fixes to permanent storage
"""
import re
import json
import sqlite_utils
import structlog
from typing import Callable, Any, Dict, Optional, List
from pathlib import Path
from datetime import datetime

logger = structlog.get_logger()

# Paths
DB_PATH = Path("data/memory/self_healing.db")
FIXES_JSON = Path("data/memory/known_fixes.json")

class UniversalSelfHealingEngine:
    """
    The immortal brain that learns from every error across all apps.
    """
    
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite_utils.Database(DB_PATH)
        self._init_schema()
        self._load_builtin_fixes()
        self._load_learned_fixes()
        logger.info("upshe_initialized", fixes_loaded=len(self.fixes))
    
    def _init_schema(self):
        """Create tables for storing learned fixes."""
        # Learned fixes table
        self.db["fixes"].create({
            "id": int,
            "error_pattern": str,      # Regex pattern
            "fix_type": str,           # 'import', 'replace', 'wrap', 'suggestion'
            "fix_data": str,           # JSON with fix details
            "app_context": str,        # 'universal', 'blender', 'photoshop', etc
            "success_count": int,
            "fail_count": int,
            "created_at": float,
            "last_used": float
        }, pk="id", if_not_exists=True)
        
        # Error history (for pattern mining)
        self.db["error_log"].create({
            "id": int,
            "timestamp": float,
            "app": str,
            "error_msg": str,
            "code_hash": str,
            "resolved": bool,
            "fix_id": int
        }, pk="id", if_not_exists=True)
    
    def _load_builtin_fixes(self):
        """Initialize with hardcoded common fixes."""
        self.fixes: Dict[str, Dict] = {}
        
        # Universal Python fixes
        builtins = [
            {
                "pattern": r"name '(\w+)' is not defined",
                "type": "import",
                "data": {
                    "Vector": "from mathutils import Vector",
                    "math": "import math",
                    "random": "import random",
                    "bmesh": "import bmesh",
                    "bpy": "import bpy",
                    "os": "import os",
                    "sys": "import sys",
                    "Path": "from pathlib import Path",
                    "datetime": "from datetime import datetime",
                    "json": "import json",
                    "re": "import re",
                    "asyncio": "import asyncio",
                    "cv2": "import cv2",
                    "np": "import numpy as np",
                    "numpy": "import numpy",
                    "pd": "import pandas as pd",
                    "win32com": "import win32com.client",
                },
                "context": "universal"
            },
            {
                "pattern": r"No module named '(\w+)'",
                "type": "suggestion",
                "data": {"action": "pip install {0}"},
                "context": "universal"
            },
            {
                "pattern": r"unexpected indent",
                "type": "suggestion",
                "data": {"action": "Check indentation consistency (tabs vs spaces)"},
                "context": "universal"
            },
            {
                "pattern": r"SyntaxError: invalid syntax",
                "type": "suggestion",
                "data": {"action": "Check for missing colons, brackets, or quotes"},
                "context": "universal"
            }
        ]
        
        for fix in builtins:
            self.fixes[fix["pattern"]] = fix
    
    def _load_learned_fixes(self):
        """Load fixes from database (learned over time)."""
        try:
            for row in self.db["fixes"].rows:
                pattern = row["error_pattern"]
                self.fixes[pattern] = {
                    "pattern": pattern,
                    "type": row["fix_type"],
                    "data": json.loads(row["fix_data"]),
                    "context": row["app_context"],
                    "db_id": row["id"]
                }
        except Exception as e:
            logger.warning("upshe_load_learned_failed", error=str(e))
    
    def execute_with_healing(self, 
                              code: str, 
                              executor_fn: Callable[[str], Dict],
                              app_context: str = "universal",
                              max_retries: int = 3) -> Dict:
        """
        Execute code with automatic error detection, patching, and retry.
        
        Args:
            code: The code/script to execute
            executor_fn: Function that runs the code, returns {'success': bool, 'error': str}
            app_context: Which app this is for (helps prioritize fixes)
            max_retries: How many times to try fixing
            
        Returns:
            Final execution result
        """
        current_code = code
        applied_fixes = []
        
        for attempt in range(max_retries):
            result = executor_fn(current_code)
            
            if result.get('success'):
                # SUCCESS! Record what worked
                if applied_fixes:
                    self._record_success(applied_fixes)
                    logger.info("upshe_healed", 
                               app=app_context, 
                               fixes=len(applied_fixes),
                               attempts=attempt+1)
                return result
            
            error = result.get('error', '')
            
            # Log error for pattern mining
            self._log_error(app_context, error, hash(code))
            
            # Try to find and apply a fix
            patched_code, fix_info = self._apply_fix(current_code, error, app_context)
            
            if patched_code == current_code:
                # No fix available
                logger.warning("upshe_no_fix", app=app_context, error=error[:100])
                return result
            
            current_code = patched_code
            applied_fixes.append(fix_info)
            logger.info("upshe_patching", attempt=attempt+1, fix=fix_info.get('pattern', '')[:50])
        
        return result
    
    def _apply_fix(self, code: str, error: str, app_context: str) -> tuple:
        """Try to apply a matching fix."""
        # Prioritize app-specific fixes, then universal
        sorted_fixes = sorted(
            self.fixes.items(),
            key=lambda x: (0 if x[1].get('context') == app_context else 1)
        )
        
        for pattern, fix_info in sorted_fixes:
            match = re.search(pattern, error)
            if match:
                new_code = self._execute_fix(code, match, fix_info)
                if new_code != code:
                    return new_code, fix_info
        
        return code, {}
    
    def _execute_fix(self, code: str, match: re.Match, fix_info: Dict) -> str:
        """Actually apply the fix to the code."""
        fix_type = fix_info.get('type')
        data = fix_info.get('data', {})
        
        if fix_type == 'import':
            # Inject missing import
            name = match.group(1) if match.lastindex else None
            if name and name in data:
                import_line = data[name]
                if import_line not in code:
                    return import_line + "\n" + code
        
        elif fix_type == 'replace':
            # Replace pattern with fix
            old = data.get('old', '')
            new = data.get('new', '')
            if old and old in code:
                return code.replace(old, new)
        
        elif fix_type == 'wrap':
            # Wrap code in try/except or other structure
            wrapper = data.get('wrapper', '')
            if wrapper:
                return wrapper.format(code=code)
        
        elif fix_type == 'suggestion':
            # Can't auto-fix, but log suggestion
            action = data.get('action', '').format(*match.groups())
            logger.warning("upshe_suggestion", action=action)
        
        return code
    
    def _record_success(self, fixes: List[Dict]):
        """Record that these fixes worked."""
        for fix in fixes:
            if 'db_id' in fix:
                try:
                    self.db["fixes"].update(fix['db_id'], {
                        "success_count": self.db["fixes"].get(fix['db_id'])["success_count"] + 1,
                        "last_used": datetime.now().timestamp()
                    })
                except:
                    pass
    
    def _log_error(self, app: str, error: str, code_hash: int):
        """Log error for future pattern analysis."""
        try:
            self.db["error_log"].insert({
                "timestamp": datetime.now().timestamp(),
                "app": app,
                "error_msg": error[:500],
                "code_hash": str(code_hash),
                "resolved": False,
                "fix_id": None
            })
        except Exception as e:
            logger.debug("error_log_failed", error=str(e))
    
    def learn_fix(self, error_pattern: str, fix_type: str, fix_data: Dict, app_context: str = "universal"):
        """
        PUBLIC API: Teach the system a new fix.
        Called when a human or the LLM discovers a new solution.
        """
        try:
            self.db["fixes"].insert({
                "error_pattern": error_pattern,
                "fix_type": fix_type,
                "fix_data": json.dumps(fix_data),
                "app_context": app_context,
                "success_count": 0,
                "fail_count": 0,
                "created_at": datetime.now().timestamp(),
                "last_used": None
            })
            
            # Add to memory
            self.fixes[error_pattern] = {
                "pattern": error_pattern,
                "type": fix_type,
                "data": fix_data,
                "context": app_context
            }
            
            logger.info("upshe_new_fix_learned", pattern=error_pattern[:50])
            return True
        except Exception as e:
            logger.error("upshe_learn_failed", error=str(e))
            return False
    
    def get_stats(self) -> Dict:
        """Return healing statistics."""
        return {
            "total_fixes": len(self.fixes),
            "total_errors_logged": self.db["error_log"].count,
            "successful_healings": sum(
                r["success_count"] for r in self.db["fixes"].rows
            )
        }

# Singleton
_engine = None

def get_healing_engine() -> UniversalSelfHealingEngine:
    global _engine
    if not _engine:
        _engine = UniversalSelfHealingEngine()
    return _engine
