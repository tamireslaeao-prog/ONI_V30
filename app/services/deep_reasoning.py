"""
ONI Deep Reasoning Service v2.0 (Refactored Phase 2)
Forwarding shim ensuring backward compatibility with new modular architecture.
"""
from app.services.oni.deep_reasoning.types import (
    TaskDomain, SubtaskStatus, QualityCriteria, Subtask, TaskAnalysis
)
from app.services.oni.deep_reasoning.service import DeepReasoningService
from app.services.oni.deep_reasoning.templates import (
    DRAWING_REASONING_TEMPLATE, GENERAL_REASONING_TEMPLATE
)
