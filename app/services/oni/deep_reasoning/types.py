"""
ONI Deep Reasoning - Types
"""
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class TaskDomain(str, Enum):
    """Domínios de tarefas suportados."""
    DRAWING = "drawing"
    UI_AUTOMATION = "ui_automation"
    FILE_MANAGEMENT = "file_management"
    WEB_NAVIGATION = "web_navigation"
    GENERAL = "general"


class SubtaskStatus(str, Enum):
    """Status de uma subtarefa."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class QualityCriteria:
    """Critérios de qualidade para uma tarefa."""
    description: str
    metric: str
    target_value: Any
    weight: float = 1.0


@dataclass
class Subtask:
    """Uma subtarefa decomposta."""
    id: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    preconditions: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    verification_method: str = "visual"
    status: SubtaskStatus = SubtaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 2


@dataclass
class TaskAnalysis:
    """Resultado da análise profunda de uma tarefa."""
    original_task: str
    domain: TaskDomain
    goal_interpretation: str
    quality_criteria: List[QualityCriteria]
    component_breakdown: List[str]
    execution_strategy: str
    estimated_steps: int
    subtasks: List[Subtask] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "original_task": self.original_task,
            "domain": self.domain.value,
            "goal_interpretation": self.goal_interpretation,
            "quality_criteria": [
                {"description": qc.description, "metric": qc.metric, "target": qc.target_value}
                for qc in self.quality_criteria
            ],
            "component_breakdown": self.component_breakdown,
            "execution_strategy": self.execution_strategy,
            "estimated_steps": self.estimated_steps,
            "subtasks_count": len(self.subtasks)
        }
