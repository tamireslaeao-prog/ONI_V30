"""
ONI Services Package v7.0
Centralized exports for all ONI services.
"""

from app.services.oni.cognitive_memory import CognitiveMemoryService
from app.services.oni.stability import StabilityService
from app.services.oni.rollback import RollbackService
from app.services.oni.guards import ActionGuardService, UndoGuardService
from app.services.oni.set_of_mark import SetOfMarkService
from app.services.oni.embeddings import EmbeddingsService
from app.services.oni.auxiliary import (
    MetricsService, 
    CacheService, 
    SecurityService, 
    ComputerVisionService,
    AIService
)
from app.services.oni.universal_adapter import UniversalAdapterService, KnowledgeBase
from app.services.oni.error_recovery import ErrorRecoveryService, AnomalyDetector
from app.services.oni.error_learning import ErrorLearningService

# v7.0 New Services
from app.services.oni.vector_memory import VectorMemoryService, ExperienceType
from app.services.oni.dual_verification import DualVerificationService
from app.services.oni.sanity_checker import SanityCheckerService

# v23.0 Autonomous Executor - Anti Memória Episódica
from app.services.oni.autonomous_executor import AutonomousExecutor
from app.services.oni.infrastructure_discovery import InfrastructureDiscovery

__all__ = [
    # Core Memory
    "CognitiveMemoryService",
    "VectorMemoryService",  # v7.0
    "ExperienceType",  # v7.0
    # Stability & Guards
    "StabilityService", 
    "RollbackService",
    "ScreenshotGuardService",
    "UndoGuardService",
    # Vision & AI
    "SetOfMarkService",
    "EmbeddingsService",
    "ComputerVisionService",
    "AIService",
    # Metrics & Utils
    "MetricsService",
    "CacheService",
    "SecurityService",
    # Universal Services
    "UniversalAdapterService",
    "KnowledgeBase",
    "ErrorRecoveryService",
    "AnomalyDetector",
    "ErrorLearningService",
    # v7.0 Verification & Sanity
    "DualVerificationService",  # v7.0
    "SanityCheckerService",  # v7.0
    # v23.0 Autonomous Executor
    "AutonomousExecutor",
    "InfrastructureDiscovery",
]

