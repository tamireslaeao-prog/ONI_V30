"""
ONI v2.0 - Custom Exceptions
Hierarchical exception system for all ONI components
"""
from typing import Any


class ONIError(Exception):
    """Base exception for all ONI errors."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None, is_critical: bool = False) -> None:
        self.message = message
        self.details = details or {}
        self.is_critical = is_critical
        super().__init__(self.message)
    
    def __str__(self) -> str:
        prefix = "[CRITICAL] " if self.is_critical else ""
        if self.details:
            return f"{prefix}{self.message} | Details: {self.details}"
        return f"{prefix}{self.message}"


# =============================================================================
# LLM Exceptions
# =============================================================================

class LLMError(ONIError):
    """Base exception for LLM-related errors."""
    pass


class ModelNotFoundError(LLMError):
    """Model file not found."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class InferenceError(LLMError):
    """Error during LLM inference."""
    pass


class GrammarError(LLMError):
    """Error in GBNF grammar parsing or application."""
    pass


class ContextOverflowError(LLMError):
    """Context window exceeded."""
    pass


# =============================================================================
# Vision Exceptions
# =============================================================================

class VisionError(ONIError):
    """Base exception for vision-related errors."""
    pass


class CaptureError(VisionError):
    """Screen capture failed."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class OCRError(VisionError):
    """OCR processing failed."""
    pass


class ElementNotFoundError(VisionError):
    """UI element not found on screen."""
    
    def __init__(self, target: str, confidence: float = 0.0) -> None:
        super().__init__(
            f"Element not found: '{target}'",
            {"target": target, "confidence": confidence},
            is_critical=False # Usually recoverable
        )
        self.target = target
        self.confidence = confidence


class MultipleElementsFoundError(VisionError):
    """Multiple matching elements found when expecting one."""
    pass


# =============================================================================
# Actuation Exceptions
# =============================================================================

class ActuationError(ONIError):
    """Base exception for actuation-related errors."""
    def __init__(self, message: str, details: dict[str, Any] | None = None, is_critical: bool = True) -> None:
        super().__init__(message, details, is_critical=is_critical)


class ActionTimeoutError(ActuationError):
    """Action execution timed out."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class ActionFailedError(ActuationError):
    """Action failed to produce expected result."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class WindowNotFoundError(ActuationError):
    """Target window not found."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


# =============================================================================
# Memory Exceptions
# =============================================================================

class MemoryError(ONIError):
    """Base exception for memory-related errors."""
    pass


class StorageConnectionError(MemoryError):
    """Failed to connect to storage backend."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class RetrievalError(MemoryError):
    """Failed to retrieve from memory."""
    pass


# =============================================================================
# Agent Exceptions
# =============================================================================

class AgentError(ONIError):
    """Base exception for agent-related errors."""
    pass


class PlanningError(AgentError):
    """Error during task planning."""
    pass


class ExecutionError(AgentError):
    """Error during plan execution."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details, is_critical=True)


class GoalAmbiguousError(AgentError):
    """Goal is too ambiguous to plan."""
    pass


class MaxRetriesExceededError(AgentError):
    """Maximum retry attempts exceeded."""
    pass


# =============================================================================
# API Exceptions  
# =============================================================================

class APIError(ONIError):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(APIError):
    """Authentication failed."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass
