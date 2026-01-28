"""
ONI Soul Exceptions.
Defines errors related to Axiom violations and Soul Token failures.
"""

class AxiomViolationError(Exception):
    """
    Raised when a core Axiom is violated in Strict Mode.
    Example: Moving mouse without visual validation (Blind Action).
    """
    def __init__(self, message: str, axiom_id: int):
        self.axiom_id = axiom_id
        super().__init__(f"AXIOM-{axiom_id} VIOLATION: {message}")
