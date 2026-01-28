import subprocess
import shutil
import logging
from pathlib import Path
from typing import Tuple, Optional
from .config import logger
from .utils import sanitize_filename

class VideoDownloader:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.video_dir: Optional[Path] = None
        self.video_path: Optional[Path] = None
        self.title: str = ""

    def download_video(self, url: str) -> Tuple[Path, str, Path]:
        """Downloads video from YouTube using yt-dlp"""
        logger.info("📥 STEP 1: Downloading video from YouTube...")
        
        # Get title
        try:
            result = subprocess.run(
                ["yt-dlp", "--get-title", url],
                capture_output=True, text=True, check=True, timeout=30
            )
            self.title = sanitize_filename(result.stdout.strip())
        except subprocess.TimeoutExpired:
            logger.warning("   ⏱️ Timeout obtaining title")
            self.title = "video_unknown"
        except subprocess.CalledProcessError as e:
            logger.warning(f"   ⚠️ Error obtaining title: {e}")
            self.title = "video_unknown"
        except FileNotFoundError:
            logger.error("   ❌ yt-dlp not found! Install with: pip install yt-dlp")
            raise
        
        self.video_dir = self.output_dir / self.title
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        self.video_path = self.video_dir / f"{self.title}.mp4"
        
        if self.video_path.exists():
            logger.info(f"   ✅ Video already exists: {self.video_path.name}")
            return self.video_path, self.title, self.video_dir
        
        # Download with progress
        logger.info(f"   Downloading '{self.title}'...")
        try:
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--progress",
                "-o", str(self.video_path),
                url
            ], check=True, timeout=600)  # 10 min max
            logger.info(f"   ✅ Download complete: {self.video_path.name}")
        except subprocess.TimeoutExpired:
            logger.error("   ❌ Timeout in download (>10min)")
            raise
            
        return self.video_path, self.title, self.video_dir
    
    def setup_local_video(self, video_path: str) -> Tuple[Path, str, Path]:
        """Configures local video processing"""
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        self.title = sanitize_filename(self.video_path.stem)
        self.video_dir = self.video_path.parent / self.title
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy or link video
        target = self.video_dir / self.video_path.name
        if not target.exists() and self.video_path != target:
            shutil.copy2(self.video_path, target)
            self.video_path = target
            
        logger.info(f"📂 Processing local video: {self.title}")
        return self.video_path, self.title, self.video_dir
