"""
ONI Autonomous Types
Shared execution types for autonomous system.
"""

from enum import Enum
from dataclasses import dataclass, field
import time
from typing import Dict, Any

class ExecutionPhase(str, Enum):
    """Fases da execução autônoma."""
    PRE_SCAN = "pre_scan"
    EXECUTE = "execute"
    POST_SCAN = "post_scan"
    VERIFY = "verify"
    RECOVER = "recover"
    COMPLETE = "complete"


class SuccessCriteria(str, Enum):
    """Critérios de sucesso pré-definidos."""
    WINDOW_TITLE_CONTAINS = "window_title_contains"
    WINDOW_TITLE_CHANGED = "window_title_changed"
    SCREEN_CHANGED = "screen_changed"
    FILE_EXISTS = "file_exists"
    FILES_COUNT_GTE = "files_count_gte"
    ELEMENT_VISIBLE = "element_visible"
    NO_ERROR_POPUP = "no_error_popup"
    CUSTOM = "custom"


@dataclass
class ExecutionState:
    """Estado persistente da execução."""
    task_id: str
    current_phase: ExecutionPhase
    last_scan_timestamp: float = 0
    last_scan_path: str = ""
    last_window_title: str = ""
    last_screen_hash: str = ""
    actions_executed: int = 0
    recoveries_attempted: int = 0
    started_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "current_phase": self.current_phase.value,
            "last_scan_timestamp": self.last_scan_timestamp,
            "last_scan_path": self.last_scan_path,
            "last_window_title": self.last_window_title,
            "last_screen_hash": self.last_screen_hash,
            "actions_executed": self.actions_executed,
            "recoveries_attempted": self.recoveries_attempted,
            "started_at": self.started_at,
            "elapsed_seconds": time.time() - self.started_at
        }


@dataclass
class ActionResult:
    """Resultado de uma ação autônoma."""
    success: bool
    phase: ExecutionPhase
    pre_scan_path: str = ""
    post_scan_path: str = ""
    action_output: Any = None
    error: str = ""
    recovery_applied: str = ""
    execution_time_ms: float = 0
