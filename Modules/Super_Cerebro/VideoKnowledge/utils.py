import re
import time
import re
from typing import Optional, Tuple

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

class ProgressTracker:
    """Progress tracker with or without tqdm"""
    
    def __init__(self, total: int, desc: str = ""):
        self.total = total
        self.desc = desc
        self.current = 0
        self.start_time = time.time()
        
        if TQDM_AVAILABLE:
            self.pbar = tqdm(total=total, desc=desc, unit="frame")
        else:
            self.pbar = None
            
    def update(self, n: int = 1):
        self.current += n
        if self.pbar:
            self.pbar.update(n)
        else:
            elapsed = time.time() - self.start_time
            eta = (elapsed / self.current) * (self.total - self.current) if self.current > 0 else 0
            print(f"\r   {self.desc}: {self.current}/{self.total} "
                  f"({100*self.current/self.total:.1f}%) ETA: {eta:.0f}s", end="", flush=True)
            
    def close(self):
        if self.pbar:
            self.pbar.close()
        else:
            print()  # New line

def sanitize_filename(name: str) -> str:
    """Removes invalid characters from filenames"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:100]

def seconds_to_timestamp(seconds: float) -> str:
    """Converts seconds to MM:SS"""
    m, s = int(seconds // 60), int(seconds % 60)
    return f"{m:02d}m{s:02d}s"

def parse_timestamp(frame_name: str) -> Optional[Tuple[int, int]]:
    """Extracts minutes and seconds from frame name"""
    match = re.search(r'(\d+)m(\d+)s', frame_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None

def format_duration(seconds: float) -> str:
    """Formats duration in HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    return f"{minutes}m{secs:02d}s"
