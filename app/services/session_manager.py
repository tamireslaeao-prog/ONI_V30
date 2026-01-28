import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

SESSION_FILE = Path("data/memory/session.json")

class SessionManager:
    """
    Context Infinite: Manages session persistence.
    Ensures ONI remembers who it is and what it was doing across reboots.
    """
    
    def __init__(self):
        self._ensure_path()
        self.current_session: Dict[str, Any] = self._load_session()

    def _ensure_path(self):
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load_session(self) -> Dict[str, Any]:
        """Load session from disk or return default."""
        if not SESSION_FILE.exists():
            return self._create_default_session()
        
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("session_loaded", last_active=data.get("last_active"))
                return data
        except Exception as e:
            logger.error("session_load_failed", error=str(e))
            return self._create_default_session()

    def _create_default_session(self) -> Dict[str, Any]:
        """Create a fresh session state."""
        return {
            "persona": "ONI", # Default to AI Assistant
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "context_summary": "System initialized.",
            "active_rules": ["MASTER.md"],
            "memory_kv": {} # Key-Value store for specific facts
        }

    def save_session(self, updates: Optional[Dict[str, Any]] = None):
        """Save current state to disk."""
        if updates:
            self.current_session.update(updates)
        
        self.current_session["last_active"] = datetime.now().isoformat()
        
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
            logger.info("session_saved")
        except Exception as e:
            logger.error("session_save_failed", error=str(e))

    def get_context(self) -> Dict[str, Any]:
        return self.current_session

    def update_persona(self, persona: str):
        self.save_session({"persona": persona})

    def update_summary(self, summary: str):
        self.save_session({"context_summary": summary})

# Singleton
_session_manager = None

def get_session_manager():
    global _session_manager
    if not _session_manager:
        _session_manager = SessionManager()
    return _session_manager
