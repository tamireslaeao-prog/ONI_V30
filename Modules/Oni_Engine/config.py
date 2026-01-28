
import os
from dataclasses import dataclass, field
from pathlib import Path

def _get_oni_root():
    """Discover ONI root dynamically based on this file's location."""
    # This file is at: ONIV24/Modules/Oni_Engine/config.py
    # So root is 3 levels up
    return str(Path(__file__).parent.parent.parent.resolve())

@dataclass
class ONIConfig:
    """Configuração centralizada do sistema ONI."""
    
    # Paths - discovered dynamically
    oni_root: str = field(default_factory=_get_oni_root)
    ffmpeg_path: str = None
    temp_dir: str = None
    output_dir: str = None
    
    # Audio Processing
    sample_rate: int = 44100
    whisper_model: str = "base"
    language: str = "pt"
    
    # Video Processing
    video_width: int = 1920
    video_height: int = 1080
    video_fps: int = 30
    frame_extract_interval: float = 2.0
    
    # Scene Detection
    scene_change_threshold: float = 35.0
    min_scene_duration: float = 1.0
    
    def __post_init__(self):
        """Auto-configure paths."""
        if self.ffmpeg_path is None:
            self.ffmpeg_path = os.path.join(
                self.oni_root, "data", "bin", "ffmpeg", "bin", "ffmpeg.exe"
            )
        
        if self.temp_dir is None:
            self.temp_dir = os.path.join(self.oni_root, "temp")
        
        if self.output_dir is None:
            self.output_dir = os.path.join(self.oni_root, "output")
        
        # Ensure directories exist
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Inject FFmpeg to PATH
        ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
