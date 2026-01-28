"""
ONI v5.0 - Reasoning Engine
Provides metacognitive capabilities for self-reflection and error detection.

Features:
- Loop detection (detecting stuck states)
- Error pattern recognition
- Self-correction suggestions
- Confidence scoring
"""

import asyncio
import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class ReasoningType(str, Enum):
    """Types of reasoning operations."""
    REFLECTION = "reflection"
    LOOP_DETECTION = "loop_detection"
    ERROR_ANALYSIS = "error_analysis"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    SUGGESTION = "suggestion"


@dataclass
class ReasoningResult:
    """Result from reasoning operation."""
    reasoning_type: ReasoningType
    conclusion: str
    confidence: float  # 0.0 to 1.0
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Observation:
    """Single observation for pattern analysis."""
    screen_hash: str
    window_title: str
    timestamp: datetime
    action_taken: Optional[str] = None
    result: Optional[str] = None


class ReasoningEngine:
    """
    Metacognitive reasoning engine.
    
    Provides self-reflection capabilities:
    - Detects when agent is stuck in loops
    - Analyzes error patterns
    - Suggests alternative approaches
    - Assesses confidence in actions
    """
    
    def __init__(self, 
                 history_size: int = 20,
                 loop_threshold: int = 3,
                 confidence_decay: float = 0.9):
        """
        Initialize reasoning engine.
        
        Args:
            history_size: Number of observations to keep
            loop_threshold: Repeated states before loop detection
            confidence_decay: Decay factor for confidence over time
        """
        self._history: deque[Observation] = deque(maxlen=history_size)
        self._loop_threshold = loop_threshold
        self._confidence_decay = confidence_decay
        self._error_patterns: Dict[str, int] = {}
        self._base_confidence = 0.8
        
        logger.info("reasoning_engine_initialized", 
                   history_size=history_size,
                   loop_threshold=loop_threshold)
    
    def add_observation(self, 
                       screen_data: bytes,
                       window_title: str,
                       action: Optional[str] = None,
                       result: Optional[str] = None) -> None:
        """
        Add an observation to the history.
        
        Args:
            screen_data: Screenshot bytes (used for hashing)
            window_title: Current window title
            action: Action that was taken
            result: Result of the action
        """
        # Create hash of screen for comparison
        screen_hash = hashlib.md5(screen_data).hexdigest()[:16] if screen_data else ""
        
        observation = Observation(
            screen_hash=screen_hash,
            window_title=window_title,
            timestamp=datetime.now(),
            action_taken=action,
            result=result
        )
        
        self._history.append(observation)
        
        # Track error patterns
        if result and ("error" in result.lower() or "failed" in result.lower()):
            error_key = f"{action}:{window_title}"
            self._error_patterns[error_key] = self._error_patterns.get(error_key, 0) + 1
    
    def detect_loop(self) -> ReasoningResult:
        """
        Detect if the agent is stuck in a loop.
        
        Returns:
            ReasoningResult with loop detection details
        """
        if len(self._history) < self._loop_threshold:
            return ReasoningResult(
                reasoning_type=ReasoningType.LOOP_DETECTION,
                conclusion="Not enough history for loop detection",
                confidence=0.0
            )
        
        # Count repeated screen states
        screen_counts: Dict[str, int] = {}
        for obs in self._history:
            screen_counts[obs.screen_hash] = screen_counts.get(obs.screen_hash, 0) + 1
        
        # Find max repetition
        max_count = max(screen_counts.values()) if screen_counts else 0
        
        # Count repeated actions
        action_counts: Dict[str, int] = {}
        for obs in self._history:
            if obs.action_taken:
                action_counts[obs.action_taken] = action_counts.get(obs.action_taken, 0) + 1
        
        max_action_count = max(action_counts.values()) if action_counts else 0
        
        # Determine if looping
        is_looping = max_count >= self._loop_threshold or max_action_count >= self._loop_threshold
        
        suggestions = []
        if is_looping:
            suggestions = [
                "Try a different approach to the current step",
                "Check if a dialog or popup is blocking progress",
                "Verify the target application is in the expected state",
                "Consider breaking down the step into smaller actions"
            ]
        
        return ReasoningResult(
            reasoning_type=ReasoningType.LOOP_DETECTION,
            conclusion="Loop detected" if is_looping else "No loop detected",
            confidence=min(max_count / self._loop_threshold, 1.0) if is_looping else 0.0,
            suggestions=suggestions,
            metadata={
                "max_screen_repeat": max_count,
                "max_action_repeat": max_action_count,
                "threshold": self._loop_threshold
            }
        )
    
    def analyze_errors(self) -> ReasoningResult:
        """
        Analyze error patterns in the history.
        
        Returns:
            ReasoningResult with error analysis
        """
        if not self._error_patterns:
            return ReasoningResult(
                reasoning_type=ReasoningType.ERROR_ANALYSIS,
                conclusion="No errors recorded",
                confidence=1.0
            )
        
        # Find most common errors
        sorted_errors = sorted(
            self._error_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        suggestions = []
        top_errors = sorted_errors[:3]
        
        for error_key, count in top_errors:
            action, window = error_key.split(":", 1)
            suggestions.append(f"Action '{action}' failed {count}x in '{window}' - try alternative")
        
        return ReasoningResult(
            reasoning_type=ReasoningType.ERROR_ANALYSIS,
            conclusion=f"Found {len(self._error_patterns)} error patterns",
            confidence=0.8,
            suggestions=suggestions,
            metadata={
                "error_patterns": dict(sorted_errors[:5]),
                "total_errors": sum(self._error_patterns.values())
            }
        )
    
    def assess_confidence(self, 
                         proposed_action: str,
                         current_window: str) -> ReasoningResult:
        """
        Assess confidence for a proposed action.
        
        Args:
            proposed_action: Action being considered
            current_window: Current window context
            
        Returns:
            ReasoningResult with confidence assessment
        """
        confidence = self._base_confidence
        suggestions = []
        
        # Reduce confidence if this action failed before
        error_key = f"{proposed_action}:{current_window}"
        if error_key in self._error_patterns:
            failures = self._error_patterns[error_key]
            confidence *= (self._confidence_decay ** failures)
            suggestions.append(f"This action failed {failures}x before in this context")
        
        # Reduce confidence if we're in a potential loop
        loop_result = self.detect_loop()
        if loop_result.confidence > 0.5:
            confidence *= 0.7
            suggestions.extend(loop_result.suggestions[:2])
        
        # Boost confidence for known safe actions
        safe_actions = {"save", "ctrl+s", "escape", "enter", "wait"}
        if any(safe in proposed_action.lower() for safe in safe_actions):
            confidence = min(confidence * 1.1, 1.0)
        
        # Assess conclusion based on confidence level
        if confidence >= 0.8:
            conclusion = "High confidence - proceed with action"
        elif confidence >= 0.5:
            conclusion = "Medium confidence - proceed with caution"
        else:
            conclusion = "Low confidence - consider alternatives"
        
        return ReasoningResult(
            reasoning_type=ReasoningType.CONFIDENCE_ASSESSMENT,
            conclusion=conclusion,
            confidence=confidence,
            suggestions=suggestions,
            metadata={
                "proposed_action": proposed_action,
                "current_window": current_window,
                "historical_failures": self._error_patterns.get(error_key, 0)
            }
        )
    
    def suggest_alternatives(self, 
                            failed_action: str,
                            context: Dict[str, Any]) -> ReasoningResult:
        """
        Suggest alternative approaches after a failure.
        
        Args:
            failed_action: The action that failed
            context: Current execution context
            
        Returns:
            ReasoningResult with suggestions
        """
        suggestions = []
        action_lower = failed_action.lower()
        
        # Clickrelated failures
        if "click" in action_lower:
            suggestions.extend([
                "Try using keyboard shortcut instead of clicking",
                "Wait longer for element to appear (add delay)",
                "Try double-click instead of single click",
                "Check if element is visible in current viewport"
            ])
        
        # Type-related failures
        if "type" in action_lower or "digitar" in action_lower:
            suggestions.extend([
                "Ensure target field is focused first",
                "Use clipboard paste (Ctrl+V) instead of typing",
                "Clear existing content before typing (Ctrl+A)",
                "Check if input field is enabled/editable"
            ])
        
        # Open-related failures
        if "open" in action_lower or "abrir" in action_lower:
            suggestions.extend([
                "Use Windows Run dialog (Win+R) instead of Start Menu",
                "Try full path to executable",
                "Check if application is already running",
                "Use search (Win+S) to find application"
            ])
        
        # Save-related failures
        if "save" in action_lower or "salvar" in action_lower:
            suggestions.extend([
                "Use Save As (Ctrl+Shift+S) if filename dialog appears",
                "Ensure write permissions in target directory",
                "Close any blocking dialogs first",
                "Check available disk space"
            ])
        
        # Generic suggestions if no specific ones
        if not suggestions:
            suggestions = [
                "Try a different approach to achieve the same goal",
                "Break down the action into smaller steps",
                "Verify application state before retrying",
                "Consider using automation APIs instead of visual interaction"
            ]
        
        return ReasoningResult(
            reasoning_type=ReasoningType.SUGGESTION,
            conclusion=f"Generated {len(suggestions)} alternative approaches",
            confidence=0.7,
            suggestions=suggestions,
            metadata={
                "failed_action": failed_action,
                "context": context
            }
        )
    
    def reflect(self, goal: str, steps_completed: int, total_steps: int) -> ReasoningResult:
        """
        Perform self-reflection on current progress.
        
        Args:
            goal: Current goal
            steps_completed: Number of completed steps
            total_steps: Total planned steps
            
        Returns:
            ReasoningResult with reflection
        """
        progress = steps_completed / total_steps if total_steps > 0 else 0
        
        # Gather insights
        loop_result = self.detect_loop()
        error_result = self.analyze_errors()
        
        suggestions = []
        
        # Progress-based suggestions
        if progress < 0.3 and steps_completed > 5:
            suggestions.append("Progress is slow - consider simplifying the approach")
        
        # Add loop and error suggestions
        if loop_result.confidence > 0.3:
            suggestions.extend(loop_result.suggestions[:2])
        if error_result.metadata.get("total_errors", 0) > 3:
            suggestions.extend(error_result.suggestions[:2])
        
        # Overall assessment
        if progress >= 0.8 and loop_result.confidence < 0.3:
            conclusion = "Good progress - continue current approach"
        elif loop_result.confidence > 0.5:
            conclusion = "Potential issue detected - consider changing strategy"
        else:
            conclusion = "Normal progress - monitoring for issues"
        
        return ReasoningResult(
            reasoning_type=ReasoningType.REFLECTION,
            conclusion=conclusion,
            confidence=1.0 - loop_result.confidence,
            suggestions=suggestions,
            metadata={
                "goal": goal,
                "progress": progress,
                "steps_completed": steps_completed,
                "total_steps": total_steps,
                "loop_confidence": loop_result.confidence,
                "total_errors": error_result.metadata.get("total_errors", 0)
            }
        )
    
    def clear_history(self) -> None:
        """Clear observation history and error patterns."""
        self._history.clear()
        self._error_patterns.clear()
        logger.info("reasoning_engine_history_cleared")


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_reasoning_engine():
    """Quick test of the ReasoningEngine."""
    engine = ReasoningEngine(loop_threshold=3)
    
    # Simulate some observations
    for i in range(5):
        engine.add_observation(
            screen_data=b"screen_data_" + str(i % 2).encode(),  # Alternating screens
            window_title="Notepad",
            action="click_save",
            result="success" if i % 2 == 0 else "failed"
        )
    
    # Test loop detection
    loop_result = engine.detect_loop()
    print(f"Loop detection: {loop_result.conclusion} (confidence: {loop_result.confidence:.2f})")
    
    # Test error analysis
    error_result = engine.analyze_errors()
    print(f"Error analysis: {error_result.conclusion}")
    
    # Test confidence assessment
    conf_result = engine.assess_confidence("click_save", "Notepad")
    print(f"Confidence: {conf_result.conclusion} ({conf_result.confidence:.2f})")
    
    # Test reflection
    reflect_result = engine.reflect("Save a file in Notepad", 3, 5)
    print(f"Reflection: {reflect_result.conclusion}")
    
    return loop_result, error_result, conf_result, reflect_result


if __name__ == "__main__":
    asyncio.run(_test_reasoning_engine())
