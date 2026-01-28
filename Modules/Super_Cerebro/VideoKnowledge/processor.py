import cv2
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .config import logger, API_BASE, INITIAL_TIMEOUT, RETRY_BACKOFF, MAX_RETRIES, BATCH_SIZE, RATE_LIMIT_DELAY
from .utils import seconds_to_timestamp, parse_timestamp, format_duration, ProgressTracker

# Check dependencies
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import sys
    import os

    # Portable Path: Modules/Super_Cerebro/VideoKnowledge -> ... -> ONI_V30
    current = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current))))
    if root not in sys.path:
        sys.path.insert(0, root)
    
    from app.services.oni.ui_analyzer_optimized import OptimizedUIAnalyzer
    UI_ANALYZER_AVAILABLE = True
except ImportError:
    UI_ANALYZER_AVAILABLE = False

class FrameProcessor:
    def __init__(self, video_path: Path, video_dir: Path, interval: int, debug: bool = False):
        self.video_path = video_path
        self.video_dir = video_dir
        self.interval = interval
        self.debug = debug
        self.frames_dir: Optional[Path] = None
        self.annotated_dir: Optional[Path] = None
        self.frame_paths: List[Path] = []
        self.annotations: List[Dict] = []
        self.stats = {
            "frames_extracted": 0,
            "frames_annotated": 0,
            "frames_failed": 0,
            "total_elements": 0,
            "retries_used": 0
        }

    def extract_frames(self) -> List[Path]:
        """Extracts frames from video every N seconds"""
        logger.info(f"🎬 STEP 3: Extracting frames (interval: {self.interval}s)...")
        
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required: pip install opencv-python")
        
        self.frames_dir = self.video_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        # Check cache
        existing = sorted(self.frames_dir.glob("frame_*.png"))
        if len(existing) > 5:
            logger.info(f"   ✅ {len(existing)} frames already exist (cache)")
            self.frame_paths = existing
            self.stats["frames_extracted"] = len(existing)
            return existing
        
        # Open video
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {self.video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        expected_frames = int(duration / self.interval) + 1
        
        logger.info(f"   📊 Duration: {format_duration(duration)}")
        logger.info(f"   📊 FPS: {fps:.1f}")
        logger.info(f"   📊 Expected frames: ~{expected_frames}")
        
        frame_skip = max(1, int(fps * self.interval))
        paths = []
        frame_num = 0
        saved = 0
        
        # Progress tracking
        progress = ProgressTracker(expected_frames, "Extracting")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_num % frame_skip == 0:
                ts_sec = frame_num / fps
                ts_str = seconds_to_timestamp(ts_sec)
                name = f"frame_{saved:04d}_{ts_str}.png"
                path = self.frames_dir / name
                
                cv2.imwrite(str(path), frame)
                paths.append(path)
                saved += 1
                progress.update()
            
            frame_num += 1
        
        cap.release()
        progress.close()
        
        self.frame_paths = paths
        self.stats["frames_extracted"] = len(paths)
        logger.info(f"   ✅ Total: {len(paths)} frames extracted")
        return paths

    async def annotate_all_frames(self) -> List[Dict]:
        """Process all frames with visual annotation"""
        logger.info("🏷️ STEP 4: Annotating frames with ONI Hybrid Vision...")
        
        self.annotated_dir = self.video_dir / "annotated"
        self.annotated_dir.mkdir(exist_ok=True)
        
        annotations = []
        total = len(self.frame_paths)
        
        connector = aiohttp.TCPConnector(limit=BATCH_SIZE, limit_per_host=BATCH_SIZE)
        timeout = aiohttp.ClientTimeout(total=INITIAL_TIMEOUT * 2)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            progress = ProgressTracker(total, "Annotating")
            
            for i in range(0, total, BATCH_SIZE):
                batch = self.frame_paths[i:i+BATCH_SIZE]
                tasks = [self.annotate_frame_with_retry(session, fp) for fp in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, r in enumerate(results):
                    if isinstance(r, Exception):
                        logger.warning(f"   ⚠️ Exception: {r}")
                        self.stats["frames_failed"] += 1
                        annotations.append(None)
                    elif r:
                        annotations.append(r)
                        self.stats["frames_annotated"] += 1
                    else:
                        annotations.append(None)
                        self.stats["frames_failed"] += 1
                    
                    progress.update()
                
                await asyncio.sleep(RATE_LIMIT_DELAY)
            
            progress.close()
        
        logger.info(f"   ✅ Success: {self.stats['frames_annotated']}/{total}")
        if self.stats["frames_failed"] > 0:
            logger.warning(f"   ⚠️ Failed: {self.stats['frames_failed']}")
        if self.stats["retries_used"] > 0:
            logger.info(f"   🔄 Retries used: {self.stats['retries_used']}")
            
        self.annotations = annotations
        return annotations

    async def annotate_frame_with_retry(self, session: aiohttp.ClientSession, 
                                        frame_path: Path, 
                                        retry: int = 0) -> Optional[Dict]:
        """Annotates frame with retry and exponential backoff"""
        json_path = self.annotated_dir / f"{frame_path.stem}.json"
        annotated_img = self.annotated_dir / f"{frame_path.stem}_annotated.png"
        
        # Cache check
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding='utf-8'))
                if data:
                    return data
            except json.JSONDecodeError:
                json_path.unlink()
        
        timeout = INITIAL_TIMEOUT * (RETRY_BACKOFF ** retry)
        
        try:
            if not frame_path.exists():
                logger.warning(f"   ❌ Frame does not exist: {frame_path.name}")
                return None
            
            url = f"{API_BASE}/api/segmentation/ui-regions"
            params = {
                "image_path": str(frame_path),
                "min_area": 300
            }
            
            async with session.get(
                url, 
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    processed = self._process_annotation_result(result, frame_path)
                    
                    json_path.write_text(json.dumps(processed, indent=2), encoding='utf-8')
                    
                    # GENERATE ANNOTATED IMAGE LOCALLY
                    if CV2_AVAILABLE and not annotated_img.exists():
                        self._generate_annotated_image(frame_path, annotated_img, result)
                    
                    return processed
                    
                elif resp.status == 422:
                    if retry == 0:
                        return await self._try_alternative_endpoint(session, frame_path)
                    logger.warning(f"   ⚠️ Error 422 for {frame_path.name}")
                    return None
                    
                else:
                    logger.warning(f"   ⚠️ HTTP {resp.status} for {frame_path.name}")
                    if retry < MAX_RETRIES:
                        await asyncio.sleep(RETRY_BACKOFF ** retry)
                        self.stats["retries_used"] += 1
                        return await self.annotate_frame_with_retry(session, frame_path, retry + 1)
                    return None
                    
        except asyncio.TimeoutError:
            if retry < MAX_RETRIES:
                logger.warning(f"   ⏱️ Timeout {frame_path.name}, attempt {retry + 1}/{MAX_RETRIES}")
                self.stats["retries_used"] += 1
                return await self.annotate_frame_with_retry(session, frame_path, retry + 1)
            logger.warning(f"   ❌ Final timeout: {frame_path.name}")
            return None
            
        except aiohttp.ClientError as e:
            logger.warning(f"   ⚠️ Connection error: {e}")
            if retry < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF ** retry)
                self.stats["retries_used"] += 1
                return await self.annotate_frame_with_retry(session, frame_path, retry + 1)
            return None
            
        except Exception as e:
            logger.error(f"   ❌ Unexpected error in {frame_path.name}: {type(e).__name__}: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None

    async def _try_alternative_endpoint(self, session: aiohttp.ClientSession, 
                                        frame_path: Path) -> Optional[Dict]:
        """Tries alternative endpoint if primary fails"""
        alt_endpoints = [
            f"{API_BASE}/api/vision/ui-analyze",
            f"{API_BASE}/api/omniparser/analyze",
        ]
        
        for endpoint in alt_endpoints:
            try:
                params = {
                    "screenshot_path": str(frame_path),
                    "annotate": "true"
                }
                
                async with session.get(
                    endpoint, 
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=INITIAL_TIMEOUT)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return self._process_annotation_result(result, frame_path)
            except:
                continue
                
        return None

    def _process_annotation_result(self, result: Dict, frame_path: Path) -> Dict:
        """Processes and normalizes annotation result"""
        processed = {
            "frame": frame_path.name,
            "timestamp": parse_timestamp(frame_path.name),
            "total_elements": 0,
            "key_buttons": [],
            "elements": [],
            "raw_response": result if self.debug else None
        }
        
        if "elements" in result:
            elements = result["elements"]
            processed["total_elements"] = len(elements)
            processed["elements"] = elements
            
            buttons = []
            for elem in elements[:15]:
                if isinstance(elem, dict):
                    text = elem.get("text") or elem.get("label") or elem.get("content", "")
                    elem_type = elem.get("type") or elem.get("class") or "unknown"
                    
                    if text and len(text) < 50:
                        buttons.append({
                            "text": text[:30],
                            "type": elem_type,
                            "rect": elem.get("rect") or elem.get("bbox")
                        })
            
            processed["key_buttons"] = buttons
            
        elif "ui_elements" in result:
            elements = result["ui_elements"]
            processed["total_elements"] = len(elements)
            processed["elements"] = elements
            
        elif "detections" in result:
            detections = result["detections"]
            processed["total_elements"] = len(detections)
            processed["elements"] = detections
            
        else:
            processed["total_elements"] = len(result)
        
        self.stats["total_elements"] += processed["total_elements"]
        return processed

    def _generate_annotated_image(self, frame_path: Path, output_path: Path, regions: Dict):
        """Generates annotated image"""
        try:
            # PREFERRED: OptimizedUIAnalyzer
            if UI_ANALYZER_AVAILABLE:
                analyzer = OptimizedUIAnalyzer(
                    str(frame_path),
                    max_buttons=50,
                    max_texts=80,
                    min_confidence=0.5
                )
                ui_data = analyzer.analyze()
                analyzer.create_clean_annotation(str(output_path))
                return
            
            # FALLBACK: OpenCV simple rectangles
            if not CV2_AVAILABLE:
                return
                
            img = cv2.imread(str(frame_path))
            if img is None:
                return
            
            colors = [
                (0, 255, 0),    # Green
                (255, 0, 0),    # Blue
                (0, 0, 255),    # Red
                (255, 255, 0),  # Cyan
                (255, 0, 255),  # Magenta
                (0, 255, 255),  # Yellow
            ]
            
            detected_regions = regions.get("regions", [])
            
            for i, region in enumerate(detected_regions[:20]):
                bbox = region.get("bbox", region.get("rect", {}))
                if isinstance(bbox, dict):
                    x = bbox.get("x", bbox.get("left", 0))
                    y = bbox.get("y", bbox.get("top", 0))
                    w = bbox.get("width", bbox.get("w", 100))
                    h = bbox.get("height", bbox.get("h", 50))
                elif isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                    x, y, w, h = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
                else:
                    continue
                
                color = colors[i % len(colors)]
                cv2.rectangle(img, (int(x), int(y)), (int(x+w), int(y+h)), color, 2)
                cv2.putText(img, str(i), (int(x)+3, int(y)+15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.imwrite(str(output_path), img)
            
        except Exception as e:
            if self.debug:
                logger.warning(f"   ⚠️ Error generating annotated: {e}")
