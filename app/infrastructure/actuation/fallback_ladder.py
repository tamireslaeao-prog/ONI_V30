"""
ONI v12.0 - Fallback Ladder
Defines deterministic fallback strategies and priorities.
"""
from enum import Enum, auto
from typing import Any, Callable

class FallbackStrategy(Enum):
    """Available execution strategies."""
    UI_CLICK = auto()      # Primary: interact with UI elements
    HOTKEY = auto()        # Secondary: keyboard shortcuts
    KEYBOARD_NAV = auto()  # Tertiary: Tab/Arrow navigation
    OCR_CLICK = auto()     # Fallback: Visual search + Click
    SHELL_CMD = auto()     # Backend: PowerShell/Bash
    API_DIRECT = auto()    # Backend: Direct API calls
    HUMAN_HELP = auto()    # Final: Ask user

class FallbackLadder:
    """
    Manages the sequence of strategies to try for a given intent.
    """
    
    def __init__(self):
        # Default timeouts in seconds
        self.timeouts = {
            FallbackStrategy.UI_CLICK: 2.0,
            FallbackStrategy.HOTKEY: 1.0,
            FallbackStrategy.KEYBOARD_NAV: 3.0,
            FallbackStrategy.OCR_CLICK: 5.0,
            FallbackStrategy.SHELL_CMD: 5.0,
            FallbackStrategy.API_DIRECT: 2.0,
        }
        
    def get_timeout(self, strategy: FallbackStrategy) -> float:
        return self.timeouts.get(strategy, 30.0)

# Global instance
fallback_ladder = FallbackLadder()
