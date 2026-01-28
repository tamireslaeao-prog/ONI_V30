"""
ONI v2.0 - Humanized Keyboard Controller
Natural typing with variable timing and optional errors
"""
import asyncio
import random
from dataclasses import dataclass
from typing import Literal, Optional

import structlog

from app.core.config import settings
from app.infrastructure.actuation.win32_input import Win32InputController
from app.soul.types import SoulToken

logger = structlog.get_logger()


@dataclass
class KeyboardConfig:
    """Keyboard configuration."""
    wpm: int = 60  # Words per minute
    error_rate: float = 0.0  # Typo probability (0-1)
    auto_correct: bool = True  # Backspace and retype errors
    punctuation_pause: float = 0.15  # Extra pause after punctuation
    word_pause: float = 0.08  # Extra pause between words


# Adjacent key mapping for realistic typos
ADJACENT_KEYS = {
    'a': ['s', 'q', 'z', 'w'],
    'b': ['v', 'n', 'g', 'h'],
    'c': ['x', 'v', 'd', 'f'],
    'd': ['s', 'f', 'e', 'r', 'c', 'x'],
    'e': ['w', 'r', 'd', 's'],
    'f': ['d', 'g', 'r', 't', 'c', 'v'],
    'g': ['f', 'h', 't', 'y', 'v', 'b'],
    'h': ['g', 'j', 'y', 'u', 'b', 'n'],
    'i': ['u', 'o', 'k', 'j'],
    'j': ['h', 'k', 'u', 'i', 'n', 'm'],
    'k': ['j', 'l', 'i', 'o', 'm'],
    'l': ['k', 'o', 'p'],
    'm': ['n', 'j', 'k'],
    'n': ['b', 'm', 'h', 'j'],
    'o': ['i', 'p', 'l', 'k'],
    'p': ['o', 'l'],
    'q': ['w', 'a'],
    'r': ['e', 't', 'd', 'f'],
    's': ['a', 'd', 'w', 'e', 'z', 'x'],
    't': ['r', 'y', 'f', 'g'],
    'u': ['y', 'i', 'h', 'j'],
    'v': ['c', 'b', 'f', 'g'],
    'w': ['q', 'e', 'a', 's'],
    'x': ['z', 'c', 's', 'd'],
    'y': ['t', 'u', 'g', 'h'],
    'z': ['a', 'x', 's'],
    # Fix P17: Expand Adjacent Keys
    '1': ['2', 'q'],
    '2': ['1', '3', 'q', 'w'],
    '3': ['2', '4', 'w', 'e'],
    '4': ['3', '5', 'e', 'r'],
    '5': ['4', '6', 'r', 't'],
    '6': ['5', '7', 't', 'y'],
    '7': ['6', '8', 'y', 'u'],
    '8': ['7', '9', 'u', 'i'],
    '9': ['8', '0', 'i', 'o'],
    '0': ['9', '-', 'o', 'p'],
    '-': ['0', '=', 'p', '['],
    '=': ['-', ']', '['],
    '[': ['p', ']', '-', '\''],
    ']': ['[', '\\', '=', '\''],
    '\\': [']', 'enter', 'backspace'],
    ';': ['l', '\'', 'p', '['],
    '\'': [';', '\\', '[', ']'],
    ',': ['m', '.', 'k', 'l'],
    '.': [',', '/', 'l', ';'],
    '/': ['.', '\'', ';'],
}


class HumanizedKeyboard:
    """
    Humanized keyboard controller.
    
    Features:
    - Variable typing speed (Gaussian distribution)
    - Natural pauses (punctuation, words)
    - Optional realistic typos
    - Auto-correction with backspace
    - Support for special keys and shortcuts
    """
    
    def __init__(
        self,
        config: KeyboardConfig | None = None,
        use_win32: bool = True,
    ) -> None:
        """
        Initialize keyboard controller.
        
        Args:
            config: Typing configuration
            use_win32: Use Win32 API
        """
        self._config = config or KeyboardConfig(
            wpm=settings.actuation.typing_wpm,
            error_rate=settings.actuation.error_rate if settings.actuation.error_simulation_enabled else 0.0,
        )
        self._use_win32 = use_win32
        self._win32 = Win32InputController() if use_win32 else None
        
        # Calculate base delay between keystrokes
        # Average word = 5 characters, WPM = words per minute
        chars_per_second = (self._config.wpm * 5) / 60
        self._base_delay = 1.0 / chars_per_second
    
    def set_error_rate(self, rate: float) -> None:
        """
        Dynamically set error rate.
        Fix P15: Configurable Error Rate
        """
        self._config.error_rate = max(0.0, min(1.0, rate))
        
    async def type_text(
        self,
        text: str,
        with_errors: bool | None = None,
        token: Optional[SoulToken] = None,
    ) -> None:
        """
        Type text with human-like timing.
        
        Args:
            text: Text to type
            with_errors: Override error simulation
            token: SoulToken for axiom compliance
        """
        if token is None:
            logger.warning("keyboard_soul_missing", action="type", text_len=len(text))
            
        simulate_errors = with_errors if with_errors is not None else self._config.error_rate > 0
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Simulate typo
            if simulate_errors and random.random() < self._config.error_rate:
                typo = self._generate_typo(char)
                await self._type_char(typo)
                await self._random_delay()
                
                if self._config.auto_correct:
                    # Pause to "notice" the error
                    await asyncio.sleep(random.uniform(0.15, 0.4))
                    
                    # Backspace and retype
                    await self.press_key("backspace")
                    await asyncio.sleep(random.uniform(0.05, 0.1))
                    await self._type_char(char)
                else:
                    i += 1
                    continue
            else:
                await self._type_char(char)
            
            # Variable delay
            delay = self._calculate_delay(char, text, i)
            await asyncio.sleep(delay)
            
            i += 1
    
    async def press_key(self, key: str) -> None:
        """Press a single key."""
        if self._win32:
            self._win32.key_press(key)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_press(key)
    
    async def hotkey(self, *keys: str, token: Optional[SoulToken] = None) -> None:
        """
        Execute keyboard shortcut.
        
        Args:
            *keys: Keys to press together (e.g., "ctrl", "c")
            token: SoulToken for axiom compliance
        """
        if token is None:
            logger.warning("keyboard_soul_missing", action="hotkey", keys=keys)

        if self._win32:
            self._win32.hotkey(*keys)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_hotkey(*keys)
        
        # Fix P16: Add Natural Hotkey Delay
        await asyncio.sleep(random.uniform(0.03, 0.08))
    
    async def key_down(self, key: str) -> None:
        """Hold key down."""
        if self._win32:
            self._win32.key_down(key)
        else:
            import pyautogui
            pyautogui.keyDown(key) # TODO: Add SafePrimitive.safe_key_down
    
    async def key_up(self, key: str) -> None:
        """Release key."""
        if self._win32:
            self._win32.key_up(key)
        else:
            import pyautogui
            pyautogui.keyUp(key)
    
    # =========================================================================
    # Private Methods
    # =========================================================================
    
    async def _type_char(self, char: str) -> None:
        """Type a single character."""
        if self._win32:
            self._win32.type_char(char)
        else:
            from app.core.safe_execution import SafePrimitive
            SafePrimitive.safe_type(char)
    
    def _calculate_delay(self, char: str, text: str, index: int) -> float:
        """Calculate delay after typing a character."""
        # Base delay with Gaussian variation
        delay = random.gauss(self._base_delay, self._base_delay * 0.3)
        delay = max(0.01, delay)  # Minimum delay
        
        # Extra pause after punctuation
        if char in '.!?':
            delay += self._config.punctuation_pause + random.uniform(0, 0.1)
        elif char in ',;:':
            delay += self._config.punctuation_pause * 0.5
        
        # Pause after space (word boundary)
        if char == ' ':
            delay += self._config.word_pause + random.uniform(0, 0.05)
        
        # Faster for home row keys (muscle memory)
        if char.lower() in 'asdfghjkl':
            delay *= 0.85
        
        # Slower for numbers
        if char.isdigit():
            delay *= 1.2
        
        return delay
    
    async def _random_delay(self) -> None:
        """Add random delay between keystrokes."""
        delay = random.gauss(self._base_delay, self._base_delay * 0.3)
        await asyncio.sleep(max(0.01, delay))
    
    def _generate_typo(self, char: str) -> str:
        """Generate a realistic typo for a character."""
        char_lower = char.lower()
        
        if char_lower in ADJACENT_KEYS:
            # Adjacent key typo
            typo = random.choice(ADJACENT_KEYS[char_lower])
            # Preserve case
            if char.isupper():
                typo = typo.upper()
            return typo
        
        # For other characters, just return a random letter
        return random.choice('asdfghjkl')
