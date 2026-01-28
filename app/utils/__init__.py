"""
ONI v2.0 - Utilities Module
Common utility functions across subsystems
"""
import hashlib
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def timeit(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {duration:.2f}ms")
        return result
    return wrapper


def async_timeit(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure async function execution time."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {duration:.2f}ms")
        return result
    return wrapper


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID based on timestamp and random bytes."""
    import secrets
    timestamp = int(time.time() * 1000)
    random_part = secrets.token_hex(4)
    id_str = f"{prefix}{timestamp}_{random_part}"
    return id_str


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def normalize_coords(
    x: int,
    y: int,
    screen_width: int = 1920,
    screen_height: int = 1080,
) -> tuple[float, float]:
    """Normalize coordinates to 0-1 range."""
    return (x / screen_width, y / screen_height)


def denormalize_coords(
    x: float,
    y: float,
    screen_width: int = 1920,
    screen_height: int = 1080,
) -> tuple[int, int]:
    """Convert normalized coordinates back to pixels."""
    return (int(x * screen_width), int(y * screen_height))


def hash_content(content: str | bytes) -> str:
    """Generate SHA256 hash of content."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def safe_json_parse(text: str) -> dict | list | None:
    """Safely parse JSON, returning None on failure."""
    import json
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_json_from_text(text: str) -> dict | list | None:
    """Extract JSON from text that may have surrounding content."""
    import json
    import re
    
    # Try to find JSON object or array
    patterns = [
        r'\{[\s\S]*\}',  # Object
        r'\[[\s\S]*\]',  # Array
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 10.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
    
    async def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        import asyncio
        
        now = time.perf_counter()
        elapsed = now - self.last_call
        
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_call = time.perf_counter()


class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    initial_delay: float = 0.5
    max_delay: float = 10.0
    exponential_base: float = 2.0


async def retry_async(
    func: Callable,
    config: RetryConfig | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Retry an async function with exponential backoff."""
    import asyncio
    
    config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt < config.max_attempts - 1:
                delay = min(
                    config.initial_delay * (config.exponential_base ** attempt),
                    config.max_delay,
                )
                await asyncio.sleep(delay)
    
    raise last_exception
