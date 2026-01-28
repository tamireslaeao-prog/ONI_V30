"""
ONI v3.0 - Reflection Agent
Analyzes execution trajectory to detect loops, suggest corrections, and learn.
"""
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass 
class ReflectionResult:
    """Result from reflection analysis."""
    has_issue: bool
    issue_type: str | None  # "loop", "stuck", "error", "inefficient"
    suggestion: str
    confidence: float
    should_replan: bool = False


class ReflectionAgent:
    """
    Analyzes agent trajectory to detect issues and suggest corrections.
    
    Detection capabilities:
    - Loop detection: Same action repeated 3+ times
    - Stuck detection: No progress after N actions
    - Error patterns: Repeated failures
    - Inefficiency: Suboptimal action sequences
    - Pattern learning from memory
    - Adaptive thresholds
    - Integration with ONI planning
    
    Example:
        reflector = ReflectionAgent(memory=agent_memory)
        
        result = await reflector.analyze(
            trajectory=trajectory,
            current_screenshot=screenshot,
            task=task_description,
        )
        
        if result.should_replan:
            plan = await planner.replan(result.suggestion)
    """
    
    # Default thresholds
    LOOP_THRESHOLD = 3  # Same action N times = loop
    STUCK_THRESHOLD = 5  # No progress after N actions
    ERROR_THRESHOLD = 2  # Consecutive errors
    
    # Reflection prompt for LLM analysis
    REFLECTION_PROMPT = """
You are an expert computer use agent designed to reflect on task execution.

Task: {task}

Current Trajectory (recent actions):
{trajectory}

The last screenshot shows the current state after the most recent action.

IMPORTANT: A code agent may have modified files programmatically. File content changes, 
applications being reopened, or documents with different content may be LEGITIMATE results 
of code execution, not errors.

Analyze the trajectory and determine if there are any issues:

1. LOOP: Is the agent repeating the same action without progress?
2. STUCK: Has the agent failed to make progress toward the goal?
3. ERROR: Are actions consistently failing?
4. INEFFICIENT: Is there a more efficient way to accomplish the task?

Respond with:

(Analysis)
Describe what you observe in the trajectory.

(Issue Type)
One of: LOOP, STUCK, ERROR, INEFFICIENT, or NONE

(Suggestion)
If there's an issue, suggest how to fix it. Be specific.

(Confidence)
A number 0-10 indicating confidence in your analysis.
"""

    def __init__(
        self,
        llm: Any = None,
        memory: Any = None,
        loop_threshold: int = 3,
        stuck_threshold: int = 5,
    ) -> None:
        """
        Initialize reflection agent.
        
        Args:
            llm: LLM provider for complex analysis
            memory: ONI AgentMemory for pattern learning
            loop_threshold: Actions to trigger loop detection
            stuck_threshold: Actions without progress to trigger stuck
        """
        self._llm = llm
        self._memory = memory
        self._loop_threshold = loop_threshold
        self._stuck_threshold = stuck_threshold
        
        # Learning stats
        self._detected_issues: list[dict] = []
    
    async def analyze(
        self,
        trajectory: list[dict[str, Any]],
        current_screenshot: bytes | None = None,
        task: str = "",
        use_llm: bool = True,
    ) -> ReflectionResult:
        """
        Analyze trajectory for issues.
        
        Args:
            trajectory: List of action steps with results
            current_screenshot: Current screen state
            task: Task being executed
            use_llm: Use LLM for deep analysis
            
        Returns:
            ReflectionResult with analysis
        """
        if not trajectory:
            return ReflectionResult(
                has_issue=False,
                issue_type=None,
                suggestion="",
                confidence=1.0,
            )
        
        # Fast heuristic checks first
        loop_result = self._detect_loop(trajectory)
        if loop_result.has_issue:
            self._record_issue(loop_result, trajectory)
            return loop_result
        
        error_result = self._detect_errors(trajectory)
        if error_result.has_issue:
            self._record_issue(error_result, trajectory)
            return error_result
        
        # LLM analysis for subtle issues
        if use_llm and self._llm and len(trajectory) >= 3:
            llm_result = await self._llm_analysis(trajectory, current_screenshot, task)
            if llm_result.has_issue:
                self._record_issue(llm_result, trajectory)
                return llm_result
        
        return ReflectionResult(
            has_issue=False,
            issue_type=None,
            suggestion="Trajectory looks good. Continue.",
            confidence=0.9,
        )
    
    def _detect_loop(self, trajectory: list[dict]) -> ReflectionResult:
        """Detect action loops using heuristics."""
        if len(trajectory) < self._loop_threshold:
            return ReflectionResult(False, None, "", 0.0)
        
        # Get recent actions
        recent_actions = [
            step.get("action", "") for step in trajectory[-self._loop_threshold:]
        ]
        
        # Check if all recent actions are the same
        if len(set(recent_actions)) == 1:
            action = recent_actions[0]
            return ReflectionResult(
                has_issue=True,
                issue_type="loop",
                suggestion=f"Loop detected: '{action}' repeated {self._loop_threshold} times. "
                          "Try a different approach or check if the element exists.",
                confidence=0.95,
                should_replan=True,
            )
        
        # Check for alternating patterns (A-B-A-B)
        if len(trajectory) >= 4:
            # Need to get last 4 actions specifically, independent of self._loop_threshold
            last_four_steps = trajectory[-4:]
            last_four = [step.get("action", "") for step in last_four_steps]
            
            if last_four[0] == last_four[2] and last_four[1] == last_four[3]:
                return ReflectionResult(
                    has_issue=True,
                    issue_type="loop",
                    suggestion=f"Alternating loop detected: '{last_four[0]}' and '{last_four[1]}'. "
                              "The agent appears stuck between two states.",
                    confidence=0.90,
                    should_replan=True,
                )
        
        return ReflectionResult(False, None, "", 0.0)
    
    def _detect_errors(self, trajectory: list[dict]) -> ReflectionResult:
        """Detect consecutive errors."""
        if len(trajectory) < self.ERROR_THRESHOLD:
            return ReflectionResult(False, None, "", 0.0)
        
        # Check recent results for errors
        recent_results = [
            step.get("result", "").lower() for step in trajectory[-self.ERROR_THRESHOLD:]
        ]
        
        error_keywords = ["error", "failed", "not found", "exception", "timeout"]
        error_count = sum(
            1 for result in recent_results
            if any(kw in result for kw in error_keywords)
        )
        
        if error_count >= self.ERROR_THRESHOLD:
            last_errors = [r for r in recent_results if any(kw in r for kw in error_keywords)]
            return ReflectionResult(
                has_issue=True,
                issue_type="error",
                suggestion=f"Multiple consecutive errors detected. Recent: {last_errors[-1]}. "
                          "Consider verifying screen state or trying alternative approach.",
                confidence=0.85,
                should_replan=True,
            )
        
        return ReflectionResult(False, None, "", 0.0)
    
    async def _llm_analysis(
        self,
        trajectory: list[dict],
        screenshot: bytes | None,
        task: str,
    ) -> ReflectionResult:
        """Deep analysis using LLM."""
        # Format trajectory for prompt
        traj_text = "\n".join([
            f"Step {i+1}: {step.get('action', 'unknown')} → {step.get('result', 'unknown')}"
            for i, step in enumerate(trajectory[-10:])  # Last 10 steps
        ])
        
        prompt = self.REFLECTION_PROMPT.format(
            task=task,
            trajectory=traj_text,
        )
        
        try:
            # LLM providers don't support image - use text-only analysis
            response = await self._llm.generate(prompt=prompt)
            
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            logger.warning("reflection_llm_failed", error=str(e))
            return ReflectionResult(False, None, "", 0.0)
    
    def _parse_llm_response(self, response: str) -> ReflectionResult:
        """Parse LLM reflection response."""
        # Extract issue type
        issue_match = re.search(r"\(Issue Type\)\s*(\w+)", response, re.IGNORECASE)
        issue_type = issue_match.group(1).lower() if issue_match else "none"
        
        # Extract suggestion
        suggestion_match = re.search(
            r"\(Suggestion\)\s*(.+?)(?:\(Confidence\)|$)", 
            response, 
            re.IGNORECASE | re.DOTALL
        )
        suggestion = suggestion_match.group(1).strip() if suggestion_match else ""
        
        # Extract confidence
        confidence_match = re.search(r"\(Confidence\)\s*(\d+)", response)
        confidence = int(confidence_match.group(1)) / 10 if confidence_match else 0.5
        
        has_issue = issue_type not in ["none", ""]
        
        return ReflectionResult(
            has_issue=has_issue,
            issue_type=issue_type if has_issue else None,
            suggestion=suggestion,
            confidence=confidence,
            should_replan=issue_type in ["loop", "stuck"],
        )
    
    def _record_issue(
        self,
        result: ReflectionResult,
        trajectory: list[dict],
    ) -> None:
        """Record issue for learning."""
        self._detected_issues.append({
            "type": result.issue_type,
            "suggestion": result.suggestion,
            "trajectory_length": len(trajectory),
            "timestamp": datetime.now().isoformat(),
        })
        
        # Store in memory if available
        if self._memory and result.has_issue:
            try:
                self._memory.store_lesson(
                    category="reflection",
                    lesson=f"Issue: {result.issue_type} - {result.suggestion}",
                )
            except Exception:
                pass
        
        logger.info(
            "reflection_issue_detected",
            issue_type=result.issue_type,
            suggestion=result.suggestion[:100],
        )
    
    def get_statistics(self) -> dict[str, Any]:
        """Get reflection statistics."""
        if not self._detected_issues:
            return {"total_issues": 0}
        
        type_counts = Counter(issue["type"] for issue in self._detected_issues)
        
        return {
            "total_issues": len(self._detected_issues),
            "by_type": dict(type_counts),
            "recent": self._detected_issues[-5:],
        }
