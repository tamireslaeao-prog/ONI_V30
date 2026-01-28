"""
ONI v5.0 - Hierarchical Planner
Decomposes high-level goals into executable step-by-step plans.

Features:
- Goal decomposition using LLM or heuristics
- Plan validation and safety checking
- Hierarchical planning (sub-goals)
- Plan caching for common patterns
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class PlanStepType(str, Enum):
    """Types of plan steps."""
    VISUAL = "visual"       # Requires screen interaction
    CODE = "code"           # Can be done via code
    COMPOSITE = "composite"  # Contains sub-steps
    WAIT = "wait"           # Wait for condition
    VERIFY = "verify"       # Verification step


@dataclass
class PlanStep:
    """A single step in a plan."""
    id: int
    description: str
    step_type: PlanStepType = PlanStepType.VISUAL
    sub_steps: List["PlanStep"] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    estimated_duration_ms: float = 1000.0
    completed: bool = False
    error: Optional[str] = None


@dataclass
class Plan:
    """Complete execution plan."""
    goal: str
    steps: List[PlanStep]
    created_at: datetime = field(default_factory=datetime.now)
    total_estimated_ms: float = 0.0
    is_validated: bool = False
    validation_errors: List[str] = field(default_factory=list)


class HierarchicalPlanner:
    """
    Hierarchical goal planner.
    
    Decomposes complex goals into executable steps using:
    1. Pattern matching for known tasks
    2. LLM-based decomposition for novel tasks
    3. Heuristic fallback for simple tasks
    """
    
    # Known patterns for common tasks
    KNOWN_PATTERNS = {
        r"(abrir|open)\s+(.+)": [
            "Search for {app} in Start Menu",
            "Click on {app} icon",
            "Wait for {app} window to appear"
        ],
        r"(criar|create)\s+(arquivo|file|documento|document)\s+(.+)": [
            "Open appropriate application for {filetype}",
            "Create new document (Ctrl+N)",
            "Add content as specified",
            "Save file with name {filename} (Ctrl+S)"
        ],
        r"(salvar|save)\s+(.+)": [
            "Press Ctrl+S to save",
            "If save dialog appears, type filename",
            "Press Enter to confirm"
        ],
        r"(fechar|close)\s+(.+)": [
            "Focus on {app} window",
            "Press Alt+F4 to close",
            "Handle save prompt if appears"
        ],
    }
    
    # Dangerous keywords that should trigger warnings
    DANGEROUS_KEYWORDS = {
        "delete", "remove", "format", "rm -rf", "del /f", "shutdown", 
        "reboot", "restart", "kill", "terminate", "wipe", "erase",
        "uninstall", "registry", "system32"
    }
    
    def __init__(self, llm_provider: Any = None):
        """
        Initialize planner.
        
        Args:
            llm_provider: Optional LLM for complex decomposition
        """
        self._llm = llm_provider
        self._cache: Dict[str, Plan] = {}
        
        logger.info("hierarchical_planner_initialized")
    
    async def create_plan(self, goal: str) -> Plan:
        """
        Create an execution plan for a goal.
        
        Args:
            goal: Natural language goal description
            
        Returns:
            Plan with executable steps
        """
        logger.info("planner_creating_plan", goal=goal)
        
        # Check cache
        cache_key = goal.lower().strip()
        if cache_key in self._cache:
            logger.info("planner_cache_hit", goal=goal)
            return self._cache[cache_key]
        
        # Try pattern matching first
        steps = self._match_patterns(goal)
        
        if not steps:
            # Use LLM if available
            if self._llm:
                steps = await self._decompose_with_llm(goal)
            else:
                # Fallback to heuristics
                steps = self._heuristic_decompose(goal)
        
        # Build plan
        plan = Plan(
            goal=goal,
            steps=[
                PlanStep(id=i, description=step)
                for i, step in enumerate(steps)
            ]
        )
        
        # Calculate estimated time
        plan.total_estimated_ms = sum(s.estimated_duration_ms for s in plan.steps)
        
        # Validate plan
        plan = self._validate_plan(plan)
        
        # Cache if valid
        if plan.is_validated:
            self._cache[cache_key] = plan
        
        logger.info("planner_plan_created", 
                   goal=goal, 
                   steps_count=len(plan.steps),
                   validated=plan.is_validated)
        
        return plan
    
    def _match_patterns(self, goal: str) -> List[str]:
        """Match goal against known patterns."""
        goal_lower = goal.lower()
        
        for pattern, template_steps in self.KNOWN_PATTERNS.items():
            match = re.search(pattern, goal_lower, re.IGNORECASE)
            if match:
                # Extract captured groups
                groups = match.groups()
                
                # Format template steps with captured values
                formatted_steps = []
                for step in template_steps:
                    formatted = step
                    for i, group in enumerate(groups):
                        formatted = formatted.replace(f"{{g{i}}}", group or "")
                    formatted_steps.append(formatted)
                
                return formatted_steps
        
        return []
    
    async def _decompose_with_llm(self, goal: str) -> List[str]:
        """Use LLM to decompose complex goals."""
        prompt = f"""You are a Windows automation planner. Break this goal into specific, actionable steps.

GOAL: {goal}

Rules:
1. Each step should be a single action (click, type, open, press keys)
2. Be specific about UI elements (button names, menu paths)
3. Include wait/verify steps after important actions
4. Keep steps simple and atomic

Return ONLY a numbered list of steps, nothing else.
Example format:
1. Open Notepad from Start Menu
2. Type "Hello World" in the editor
3. Press Ctrl+S to save
"""
        
        try:
            if hasattr(self._llm, "generate"):
                response = await self._llm.generate(prompt)
            elif hasattr(self._llm, "chat"):
                response = await self._llm.chat(prompt)
            else:
                response = str(self._llm(prompt))
            
            return self._parse_numbered_list(response)
            
        except Exception as e:
            logger.error("planner_llm_error", error=str(e))
            return self._heuristic_decompose(goal)
    
    def _heuristic_decompose(self, goal: str) -> List[str]:
        """Simple heuristic-based decomposition."""
        goal_lower = goal.lower()
        steps = []
        
        # Extract verbs and objects
        if any(word in goal_lower for word in ["criar", "create", "novo", "new"]):
            steps.extend([
                f"Open appropriate application for: {goal}",
                "Create new document (Ctrl+N)",
                "Add required content",
                "Save the document (Ctrl+S)"
            ])
        elif any(word in goal_lower for word in ["abrir", "open"]):
            steps.extend([
                f"Search for application: {goal}",
                "Click to open",
                "Wait for window to appear"
            ])
        elif any(word in goal_lower for word in ["editar", "edit", "modificar", "modify"]):
            steps.extend([
                f"Open target file/application: {goal}",
                "Make required modifications",
                "Save changes (Ctrl+S)"
            ])
        else:
            # Generic single step
            steps.append(goal)
        
        return steps
    
    def _parse_numbered_list(self, text: str) -> List[str]:
        """Parse a numbered list from text."""
        steps = []
        
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Match numbered lines: "1. Step" or "1) Step"
            match = re.match(r"^\d+[\.\)]\s*(.+)$", line)
            if match:
                step = match.group(1).strip()
                if step:
                    steps.append(step)
        
        return steps
    
    def _validate_plan(self, plan: Plan) -> Plan:
        """Validate plan for safety and completeness."""
        errors = []
        
        for step in plan.steps:
            step_lower = step.description.lower()
            
            # Check for dangerous operations
            for keyword in self.DANGEROUS_KEYWORDS:
                if keyword in step_lower:
                    errors.append(f"Step {step.id}: Contains dangerous keyword '{keyword}'")
        
        # Validate step count
        if len(plan.steps) == 0:
            errors.append("Plan has no steps")
        elif len(plan.steps) > 50:
            errors.append(f"Plan has too many steps ({len(plan.steps)})")
        
        plan.validation_errors = errors
        plan.is_validated = len(errors) == 0
        
        return plan
    
    def get_step(self, plan: Plan, index: int) -> Optional[PlanStep]:
        """Get a specific step from the plan."""
        if 0 <= index < len(plan.steps):
            return plan.steps[index]
        return None
    
    def mark_step_complete(self, plan: Plan, index: int, error: Optional[str] = None) -> None:
        """Mark a step as completed."""
        if 0 <= index < len(plan.steps):
            plan.steps[index].completed = True
            plan.steps[index].error = error
    
    def clear_cache(self) -> None:
        """Clear the plan cache."""
        self._cache.clear()
        logger.info("planner_cache_cleared")


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_planner():
    """Quick test of the HierarchicalPlanner."""
    planner = HierarchicalPlanner()
    
    # Test known pattern
    plan1 = await planner.create_plan("Abrir o Notepad")
    print(f"Plan 1: {len(plan1.steps)} steps, validated={plan1.is_validated}")
    for step in plan1.steps:
        print(f"  {step.id}: {step.description}")
    
    # Test heuristic
    plan2 = await planner.create_plan("Create a new Python script")
    print(f"\nPlan 2: {len(plan2.steps)} steps, validated={plan2.is_validated}")
    for step in plan2.steps:
        print(f"  {step.id}: {step.description}")
    
    return plan1, plan2


if __name__ == "__main__":
    asyncio.run(_test_planner())
