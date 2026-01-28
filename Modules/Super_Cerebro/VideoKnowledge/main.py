import argparse
import sys
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import Optional

from .config import logger, API_BASE, DEFAULT_INTERVAL, DEFAULT_OUTPUT, DEFAULT_LANGUAGE, HEALTH_CHECK_TIMEOUT
from .utils import sanitize_filename, format_duration
from .downloader import VideoDownloader
from .transcriber import Transcriber
from .processor import FrameProcessor
from .generator import KnowledgeGenerator

class VideoKnowledgeGenerator:
    """Video Knowledge Generator V6 - Orchestrator (Modularized)"""
    
    VERSION = "6.0.0"
    
    def __init__(self, output_dir: str, interval: int = DEFAULT_INTERVAL, 
                 language: str = DEFAULT_LANGUAGE, debug: bool = False):
        self.output_dir = Path(output_dir)
        self.interval = interval
        self.language = language
        self.debug = debug
        self.video_downloader = VideoDownloader(self.output_dir)
        self.transcriber: Optional[Transcriber] = None
        self.processor: Optional[FrameProcessor] = None
        self.generator: Optional[KnowledgeGenerator] = None
        
        self.video_path: Optional[Path] = None
        self.video_dir: Optional[Path] = None
        self.title: str = ""
        self.stats = {
            "start_time": None,
            "retries_used": 0
        }

    async def check_oni_server(self) -> bool:
        """Checks if ONI server is reachable"""
        logger.info("🔍  Checking ONI server...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{API_BASE}/",
                    timeout=aiohttp.ClientTimeout(total=HEALTH_CHECK_TIMEOUT)
                ) as resp:
                    if resp.status in [200, 404, 422]:
                        logger.info(f"   ✅ ONI Server reachable at {API_BASE}")
                        return True
            except asyncio.TimeoutError:
                logger.warning(f"   ⏱️  Timeout connecting to server")
            except aiohttp.ClientConnectorError:
                logger.warning(f"   ❌ Connection refused")
            except Exception as e:
                if self.debug:
                    logger.warning(f"   ⚠️ Error: {e}")
        
        logger.error("   ❌ ONI Server is NOT reachable!")
        logger.error(f"   💡 Start server: cd ONIV24 && python run.py")
        return False

    async def process_from_url(self, url: str):
        """Complete Pipeline: URL -> Knowledge Base"""
        self._print_banner(url=url)
        self.stats["start_time"] = time.time()
        
        if not await self.check_oni_server():
            raise ConnectionError("ONI Server not reachable")
        
        # 1. Download
        self.video_path, self.title, self.video_dir = self.video_downloader.download_video(url)
        
        # 2. Transcribe
        self.transcriber = Transcriber(self.video_dir, self.video_path, self.title, self.language)
        self.transcriber.extract_transcript(url)
        
        # 3. Process Frames
        self.processor = FrameProcessor(self.video_path, self.video_dir, self.interval, self.debug)
        self.processor.extract_frames()
        
        # 4. Annotate
        await self.processor.annotate_all_frames()
        
        # Update stats from processor
        self.stats.update(self.processor.stats)
        
        # 5. Generate
        self.generator = KnowledgeGenerator(
            self.video_dir, self.video_path, self.title,
            self.processor.frame_paths, self.processor.annotations,
            self.transcriber.transcript_lines, self.interval, self.language,
            self.stats, self.VERSION
        )
        kb_path = self.generator.generate_knowledge_base()
        
        self._print_summary(kb_path)

    async def process_local_video(self, video_path: str):
        """Complete Pipeline: Local Video -> Knowledge Base"""
        self._print_banner(local=video_path)
        self.stats["start_time"] = time.time()
        
        if not await self.check_oni_server():
            raise ConnectionError("ONI Server not reachable")
        
        # 1. Setup Local
        self.video_path, self.title, self.video_dir = self.video_downloader.setup_local_video(video_path)
        
        # 2. Transcribe
        self.transcriber = Transcriber(self.video_dir, self.video_path, self.title, self.language)
        self.transcriber.extract_transcript()
        
        # 3. Process Frames
        self.processor = FrameProcessor(self.video_path, self.video_dir, self.interval, self.debug)
        self.processor.extract_frames()
        
        # 4. Annotate
        await self.processor.annotate_all_frames()
        
        # Update stats
        self.stats.update(self.processor.stats)
        
        # 5. Generate
        self.generator = KnowledgeGenerator(
            self.video_dir, self.video_path, self.title,
            self.processor.frame_paths, self.processor.annotations,
            self.transcriber.transcript_lines, self.interval, self.language,
            self.stats, self.VERSION
        )
        kb_path = self.generator.generate_knowledge_base()
        
        self._print_summary(kb_path)

    def _print_banner(self, url: str = None, local: str = None):
        print("\n" + "╔" + "═"*68 + "╗")
        print("║" + " 🎓 VIDEO KNOWLEDGE GENERATOR V6 (MODULAR) 10/10 ".center(68) + "║")
        print("╠" + "═"*68 + "╣")
        if url:
            print(f"║ 🌐 URL: {url[:55]}{'...' if len(url) > 55 else ''} ".ljust(68) + "║")
        if local:
            print(f"║ 📂 Local: {local[:52]}{'...' if len(local) > 52 else ''} ".ljust(68) + "║")
        print(f"║ ⏱️ Interval: {self.interval}s | 🌐 Lang: {self.language.upper()} ".ljust(68) + "║")
        print("╚" + "═"*68 + "╝\n")

    def _print_summary(self, kb_path: Path):
        elapsed = time.time() - self.stats["start_time"]
        
        print("\n" + "╔" + "═"*68 + "╗")
        print("║" + " ✅ PROCESS COMPLETE! ".center(68) + "║")
        print("╠" + "═"*68 + "╣")
        print(f"║ 📂 Dir: {str(self.video_dir)[:55]} ".ljust(68) + "║")
        print(f"║ 🎬 Video: {self.video_path.name[:50]} ".ljust(68) + "║")
        print(f"║ 📝 Lines: {len(self.transcriber.transcript_lines)} lines ".ljust(68) + "║")
        print(f"║ 🖼️ Frames: {self.stats.get('frames_extracted', 0)} extracted ".ljust(68) + "║")
        print(f"║ 🏷️ Annotated: {self.stats.get('frames_annotated', 0)} success ".ljust(68) + "║")
        print(f"║ 📚 Knowledge Base: {kb_path.name} ".ljust(68) + "║")
        print(f"║ ⏱️ Time: {format_duration(elapsed)} ".ljust(68) + "║")
        print("╚" + "═"*68 + "╝\n")
        print(f"💡 Open file to study:\n   {kb_path}\n")

async def main_async():
    parser = argparse.ArgumentParser(
        description="Video Knowledge Generator V6 (Modular)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("url", nargs='?', help="YouTube URL")
    parser.add_argument("--local", "-l", type=str, help="Local video path")
    parser.add_argument("--interval", "-i", type=int, default=DEFAULT_INTERVAL,
                       help=f"Frame interval (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--output", "-o", type=str, default=DEFAULT_OUTPUT,
                       help="Output directory")
    parser.add_argument("--language", "-lang", type=str, default=DEFAULT_LANGUAGE,
                       help=f"Language (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.url and not args.local:
        parser.error("You must provide a URL or --local path")
    
    generator = VideoKnowledgeGenerator(
        output_dir=args.output,
        interval=args.interval,
        language=args.language,
        debug=args.debug
    )
    
    try:
        if args.local:
            await generator.process_local_video(args.local)
        else:
            await generator.process_from_url(args.url)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
