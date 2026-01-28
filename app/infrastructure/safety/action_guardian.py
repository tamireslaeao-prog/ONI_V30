"""
ONI Runtime Guardian
Middlewares for safe execution of Agent actions.
"""
from typing import Dict, Any, List
import structlog
from app.core.config import settings
from app.soul.exceptions import AxiomViolationError

logger = structlog.get_logger()

class ActionGuardian:
    """
    Intercepts and validates actions before execution.
    Part of Phase 3: Runtime Enforcement.
    """
    
    def __init__(self):
        self._forbidden_commands = [
            "rm -rf", "del /s", "format", "mkfs"
        ]
        self._critical_paths = [
            "C:\\Windows", "/etc/passwd", "/bin"
        ]

    def validate_action(self, action_type: str, params: Dict[str, Any]) -> None:
        """
        Validate an action against safety rules.
        Raises AxiomViolationError if unsafe.
        """
        if not settings.safety.enforce_axioms:
            return

        # Rule 1: No Destructive Commands without Confirmation (Not implemented yet, so block)
        if action_type == "terminal":
            cmd = params.get("command", "").lower()
            for forbidden in self._forbidden_commands:
                if forbidden in cmd:
                    raise AxiomViolationError(
                        f"Destructive command blocked: {forbidden}", 
                        axiom_id=8
                    )

        # Rule 2: Path Traversal Protection
        target_path = params.get("path", "")
        if target_path:
            for critical in self._critical_paths:
                if critical.lower() in str(target_path).lower():
                     raise AxiomViolationError(
                        f"Access to critical path blocked: {critical}", 
                        axiom_id=2
                    )

        # Rule 3: Blind Click Check (Redundant with HumanMouse check checking logic, but good double guard)
        if action_type == "click":
             # This is a soft check, actual enforcement happens in HumanMouse with ValidatedCoordinate
             pass

        logger.debug("guardian_action_approved", action=action_type)
