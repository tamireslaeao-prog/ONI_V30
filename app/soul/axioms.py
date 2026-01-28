from enum import Enum, auto
from typing import Dict, Optional

class ViolenceLevel(Enum):
    CRITICAL = auto() # Stops the action immediately, requires user override or system halt
    MEDIUM = auto()   # Warns the user/log, high risk of failure
    LOW = auto()      # Logged as a minor violation

class Axiom:
    def __init__(self, id: int, statement: str, violation: str, violence: ViolenceLevel):
        self.id = id
        self.statement = statement
        self.violation_consequence = violation
        self.violence_level = violence

    def __repr__(self):
        return f"AXIOM-{self.id}: {self.statement} ({self.violence_level.name})"

class SoulKernel:
    """
    The immutable core of ONI's Identity.
    These axioms are not just text; they are identifying constraints.
    Reference: MASTER.md (The 10 Axioms)
    """
    
    AXIOMS: Dict[int, Axiom] = {
        1: Axiom(1, "read_terminal must use command_status to wait for output", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
        2: Axiom(2, "write_to_file must strictly precede opening any new file", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
        3: Axiom(3, "hybrid-vision must precede any visual action", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
        4: Axiom(4, "JSX code must be in .jsx files, never inline via PowerShell", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
        5: Axiom(5, "Use REST APIs for automation, never external .py scripts", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
        6: Axiom(6, "Canvas coordinates must come from canvas_limits, never hardcoded", "FALHA MÉDIA", ViolenceLevel.MEDIUM),
        7: Axiom(7, "Visual verification must follow Enter/Dialog interactions", "FALHA MÉDIA", ViolenceLevel.MEDIUM),
        8: Axiom(8, "SafeToAutoRun must be true for safe commands, avoiding unnecessary permissions", "FALHA LEVE", ViolenceLevel.LOW),
        9: Axiom(9, "Tree of Thoughts (3 strategies) must be used before giving up", "FALHA MÉDIA", ViolenceLevel.MEDIUM),
        10: Axiom(10, "User corrections must be recorded in MEUS_ERROS.md", "FALHA CRÍTICA", ViolenceLevel.CRITICAL),
    }

    @classmethod
    def get_axiom(cls, axiom_id: int) -> Optional[Axiom]:
        return cls.AXIOMS.get(axiom_id)

    @classmethod
    def list_axioms(cls) -> str:
        return "\n".join([str(axiom) for axiom in cls.AXIOMS.values()])
    
    # Placeholder for the future runtime enforcement logic
    @staticmethod
    def validate_action(action_context: dict) -> None:
        """
        Future implementation:
        Will analyze the 'action_context' (tool call, params) against the axioms.
        If a violation is detected based on heuristics (e.g. tool='read_terminal' and no 'command_status' followed),
        it will raise a KernelViolation exception.
        """
        pass
