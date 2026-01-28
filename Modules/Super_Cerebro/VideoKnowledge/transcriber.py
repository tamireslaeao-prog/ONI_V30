import re
import subprocess
from pathlib import Path
from typing import Optional, List
from .config import logger, WHISPER_MODEL
from .utils import seconds_to_timestamp

class Transcriber:
    def __init__(self, video_dir: Path, video_path: Path, title: str, language: str):
        self.video_dir = video_dir
        self.video_path = video_path
        self.title = title
        self.language = language
        self.transcript_lines: List[str] = []

    def extract_transcript(self, url: Optional[str] = None) -> Path:
        """Extracts transcript (YT captions or Whisper)"""
        logger.info("📝 STEP 2: Extracting transcript...")
        
        transcript_path = self.video_dir / f"{self.title}.txt"
        
        if transcript_path.exists():
            logger.info(f"   ✅ Transcript already exists")
            self._load_transcript(transcript_path)
            return transcript_path
        
        # Try YouTube captions
        if url:
            result_path = self._download_youtube_captions(url, transcript_path)
            if result_path and result_path.exists():
                self._load_transcript(result_path)
                return result_path
        
        # Fallback: Whisper or empty
        result_path = self._transcribe_with_whisper(transcript_path)
        self._load_transcript(result_path)
        return result_path
    
    def _download_youtube_captions(self, url: str, output_path: Path) -> Optional[Path]:
        """Attempts to download YouTube captions"""
        try:
            logger.info("   Trying YouTube captions...")
            
            # Configure languages
            sub_langs = f"{self.language},{self.language}-BR,en" if self.language == "pt" else f"{self.language},en"
            
            subprocess.run([
                "yt-dlp",
                "--write-auto-sub",
                "--sub-lang", sub_langs,
                "--skip-download",
                "--sub-format", "vtt",
                "-o", str(self.video_dir / self.title),
                url
            ], check=True, capture_output=True, timeout=60)
            
            # Convert VTT to TXT
            vtt_files = list(self.video_dir.glob("*.vtt"))
            if vtt_files:
                lines = []
                current_time = "00m00s"
                
                with open(vtt_files[0], 'r', encoding='utf-8') as f:
                    for line in f:
                        # Capture timestamps
                        time_match = re.match(r'^(\d{2}):(\d{2}):\d{2}\.\d+', line)
                        if time_match:
                            mins = int(time_match.group(1)) * 60 + int(time_match.group(2))
                            secs = mins % 60
                            mins = mins // 60
                            current_time = f"{mins:02d}m{secs:02d}s"
                        
                        # Capture text
                        if (not line.startswith('WEBVTT') and 
                            '-->' not in line and 
                            not re.match(r'^\d{2}:\d{2}', line) and
                            line.strip()):
                            clean = re.sub(r'<[^>]+>', '', line).strip()
                            if clean and not clean.startswith('WEBVTT'):
                                lines.append(f"{current_time}: {clean}")
                
                # Remove consecutive duplicates
                unique_lines = []
                for line in lines:
                    if not unique_lines or line.split(': ', 1)[-1] != unique_lines[-1].split(': ', 1)[-1]:
                        unique_lines.append(line)
                
                output_path.write_text('\n'.join(unique_lines), encoding='utf-8')
                
                # Clean VTT files
                for vtt in vtt_files:
                    vtt.unlink()
                    
                logger.info(f"   ✅ Captions extracted: {len(unique_lines)} lines")
                return output_path
                
        except subprocess.TimeoutExpired:
            logger.warning("   ⏱️ Timeout obtaining captions")
        except subprocess.CalledProcessError:
            logger.warning("   ⚠️ YT captions unavailable")
        except Exception as e:
            logger.warning(f"   ⚠️ Error in captions: {e}")
        
        return None
    
    def _transcribe_with_whisper(self, output_path: Path) -> Path:
        """Transcribes with Faster-Whisper (4x faster) or OpenAI Whisper as fallback"""
        
        # Try faster-whisper first (much faster)
        try:
            from faster_whisper import WhisperModel
            logger.info(f"   🚀 Transcribing with Faster-Whisper ({WHISPER_MODEL})...")
            logger.info("   ⚡ Optimized mode enabled!")
            
            # Detect device
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            model = WhisperModel(WHISPER_MODEL, device=device, compute_type=compute_type)
            segments, info = model.transcribe(str(self.video_path), language=self.language)
            
            lines = []
            for seg in segments:
                ts = seconds_to_timestamp(seg.start)
                text = seg.text.strip()
                if text:
                    lines.append(f"{ts}: {text}")
            
            output_path.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"   ✅ Transcription: {len(lines)} segments (faster-whisper)")
            return output_path
            
        except ImportError:
            logger.info("   ℹ️ faster-whisper not available, trying openai-whisper...")
        except Exception as e:
            logger.warning(f"   ⚠️ Error in faster-whisper: {e}, trying fallback...")
        
        # Fallback: openai-whisper original
        try:
            import whisper
            logger.info(f"   🎤 Transcribing with OpenAI Whisper ({WHISPER_MODEL})...")
            logger.info("   ⏳ This may take a few minutes...")
            
            model = whisper.load_model(WHISPER_MODEL)
            result = model.transcribe(str(self.video_path), language=self.language)
            
            lines = []
            for seg in result['segments']:
                ts = seconds_to_timestamp(seg['start'])
                text = seg['text'].strip()
                if text:
                    lines.append(f"{ts}: {text}")
            
            output_path.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"   ✅ Transcription: {len(lines)} segments (openai-whisper)")
            return output_path
            
        except ImportError:
            logger.warning("   ⚠️ No Whisper available!")
            logger.warning("   💡 Install: pip install faster-whisper  OR  pip install openai-whisper")
        except Exception as e:
            logger.warning(f"   ⚠️ Error in Whisper: {e}")
        
        # Fallback: empty placeholder file
        logger.info("   📄 Creating placeholder transcript...")
        output_path.write_text("(Transcription not available)", encoding='utf-8')
        return output_path
    
    def _load_transcript(self, path: Path):
        """Loads transcript into memory"""
        if path.exists():
            content = path.read_text(encoding='utf-8')
            self.transcript_lines = [line.strip() for line in content.split('\n') if line.strip()]
            logger.info(f"   📖 Transcript: {len(self.transcript_lines)} lines")
