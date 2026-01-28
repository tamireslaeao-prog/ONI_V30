from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from enum import Enum

class ValidationSource(Enum):
    HYBRID_VISION = "hybrid_vision"
    ANNOTATED_MAP = "annotated_map"
    SYSTEM_CALLCULUS = "system_calculus"
    USER_OVERRIDE = "user_override"

@dataclass(frozen=True)
class SoulToken:
    """
    Proof that an Axiom was respected.
    Used as a required argument in critical functions.
    """
    axiom_id: int
    timestamp: float
    context: str

@dataclass(frozen=True)
class ValidatedCoordinate:
    """
    An (x, y) coordinate that has been visually verified.
    NativeService will eventually require this instead of raw ints.
    """
    x: int
    y: int
    source: ValidationSource
    timestamp: float
    
    @classmethod
    def from_vision(cls, x: int, y: int):
        return cls(x, y, ValidationSource.HYBRID_VISION, datetime.now().timestamp())

@dataclass(frozen=True)
class SafeFilePath:
    """
    A file path that respects Protocol PWF (Write-First) and Backup rules.
    """
    path: Path
    exists: bool
    is_safe: bool = True # Could check for forbidden dirs
    
    def __post_init__(self):
        # Basic sanity check
        item = str(self.path).lower()
        if "windows\\system32" in item:
            object.__setattr__(self, 'is_safe', False)

    @classmethod
    def from_path(cls, path_str: str):
        p = Path(path_str)
        return cls(p, p.exists())
