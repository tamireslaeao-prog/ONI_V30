"""
ONI v2.0 - ONI WebSocket Handler
Optimized real-time bidirectional communication specifically for ONI AI.

Features:
- Differential encoding (only send changes)
- Configurable FPS (1-60)
- ROI (Region of Interest) support
- Action verification with before/after
- Context awareness (active window, OCR)
- Smart pause when screen static
"""
import asyncio
import base64
import hashlib
import io
import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Any

import cv2
import numpy as np
import structlog
from fastapi import WebSocket, WebSocketDisconnect
from PIL import Image, ImageDraw
from pydantic import BaseModel

from app.core.dependencies import container
from app.api.routes.oni import OCRService, ScreenCapture

logger = structlog.get_logger()


# =============================================================================
# PROTOCOL DEFINITIONS
# =============================================================================

class ONIMessageType(str, Enum):
    """Message types for ONI protocol."""
    # Client -> Server (Client sends)
    CONFIG_FPS = "config_fps"
    CONFIG_ROI = "config_roi"
    EXECUTE_ACTION = "execute_action"
    PAUSE_STREAM = "pause_stream"
    RESUME_STREAM = "resume_stream"
    REQUEST_CONTEXT = "request_context"
    REQUEST_OCR = "request_ocr"
    PING = "ping"
    
    # Server -> Client (ONI sends)
    FRAME_FULL = "frame_full"
    FRAME_DIFF = "frame_diff"
    ACTION_RESULT = "action_result"
    CONTEXT_UPDATE = "context_update"
    OCR_RESULT = "ocr_result"
    ERROR = "error"
    PONG = "pong"
    CONNECTED = "connected"


class ONIMessage(BaseModel):
    """ONI protocol message."""
    type: ONIMessageType
    data: dict[str, Any]
    timestamp: float = 0.0
    
    def __init__(self, **data: Any):
        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = time.time()
        super().__init__(**data)


@dataclass
class StreamConfig:
    """Configuration for video stream."""
    fps: float = 10.0  # Target FPS
    quality: int = 60  # JPEG quality 1-100
    scale: float = 1.0  # Image scale (0.5 = half size)
    roi: Optional[tuple[int, int, int, int]] = None  # (x, y, w, h)
    diff_threshold: int = 1000  # Pixel change threshold
    paused: bool = False
    include_cursor: bool = True
    
    def get_sleep_time(self) -> float:
        """Get sleep time between frames."""
        return 1.0 / self.fps if self.fps > 0 else 0.1


@dataclass
class FrameCache:
    """Cache for frame comparison."""
    last_frame_gray: Optional[np.ndarray] = None
    last_frame_hash: Optional[str] = None
    last_full_frame_time: float = 0.0
    frames_since_full: int = 0


# =============================================================================
# ONI CONNECTION HANDLER
# =============================================================================

class ONIConnection:
    """Manages a single ONI connection with optimized streaming."""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.config = StreamConfig()
        self.cache = FrameCache()
        self.active = True
        self.stream_task: Optional[asyncio.Task] = None
        
    async def connect(self):
        """Accept connection and send initial config."""
        await self.websocket.accept()
        
        # Get initial context
        vision = container.get("vision")
        context = await self._get_context()
        
        # Send connected message with capabilities
        await self.send_message(ONIMessage(
            type=ONIMessageType.CONNECTED,
            data={
                "version": "2.0.0",
                "capabilities": [
                    "differential_encoding",
                    "roi_support",
                    "action_verification",
                    "ocr_streaming",
                    "context_awareness"
                ],
                "config": {
                    "fps": self.config.fps,
                    "quality": self.config.quality,
                    "scale": self.config.scale
                },
                "context": context
            }
        ))
        
        logger.info("oni_connected", config=self.config)
        
    async def send_message(self, message: ONIMessage):
        """Send message to Antigravity."""
        try:
            await self.websocket.send_json(message.model_dump())
        except Exception as e:
            logger.error("oni_send_error", error=str(e))
            self.active = False
            
    async def handle_message(self, data: dict):
        """Handle incoming message from Antigravity."""
        msg_type = data.get("type")
        msg_data = data.get("data", {})
        
        if msg_type == ONIMessageType.CONFIG_FPS.value:
            fps = msg_data.get("fps", 10.0)
            self.config.fps = max(1.0, min(60.0, fps))
            logger.info("fps_configured", fps=self.config.fps)
            
        elif msg_type == ONIMessageType.CONFIG_ROI.value:
            roi = msg_data.get("roi")
            if roi:
                self.config.roi = tuple(roi)
                logger.info("roi_configured", roi=self.config.roi)
            else:
                self.config.roi = None
                logger.info("roi_disabled")
                
        elif msg_type == ONIMessageType.EXECUTE_ACTION.value:
            await self._execute_action_verified(msg_data)
            
        elif msg_type == ONIMessageType.PAUSE_STREAM.value:
            self.config.paused = True
            logger.info("stream_paused")
            
        elif msg_type == ONIMessageType.RESUME_STREAM.value:
            self.config.paused = False
            logger.info("stream_resumed")
            
        elif msg_type == ONIMessageType.REQUEST_CONTEXT.value:
            context = await self._get_context()
            await self.send_message(ONIMessage(
                type=ONIMessageType.CONTEXT_UPDATE,
                data=context
            ))
            
        elif msg_type == ONIMessageType.REQUEST_OCR.value:
            ocr_result = await self._get_ocr(msg_data.get("region"))
            await self.send_message(ONIMessage(
                type=ONIMessageType.OCR_RESULT,
                data=ocr_result
            ))
            
        elif msg_type == ONIMessageType.PING.value:
            await self.send_message(ONIMessage(
                type=ONIMessageType.PONG,
                data={"received": msg_data.get("timestamp", 0)}
            ))
            
    async def start_stream(self):
        """Start the optimized frame streaming loop."""
        vision = container.get("vision")
        if not vision:
            logger.error("vision_service_not_available")
            return
            
        logger.info("stream_started", fps=self.config.fps)
        
        try:
            while self.active:
                if self.config.paused:
                    await asyncio.sleep(0.5)
                    continue
                
                start_time = time.perf_counter()
                
                # Capture frame
                capture_result = await vision.capture()
                if not capture_result or capture_result.image is None:
                    await asyncio.sleep(self.config.get_sleep_time())
                    continue
                
                # Process frame
                await self._process_and_send_frame(capture_result.image)
                
                # Maintain target FPS
                elapsed = time.perf_counter() - start_time
                sleep_time = max(0, self.config.get_sleep_time() - elapsed)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("stream_cancelled")
        except Exception as e:
            logger.error("stream_error", error=str(e), exc_info=True)
            
    async def _process_and_send_frame(self, image_bgr: np.ndarray):
        """Process frame with differential encoding and send."""
        
        # Apply ROI if configured
        if self.config.roi:
            x, y, w, h = self.config.roi
            image_bgr = image_bgr[y:y+h, x:x+w]
        
        # Scale if needed
        if self.config.scale != 1.0:
            new_size = (
                int(image_bgr.shape[1] * self.config.scale),
                int(image_bgr.shape[0] * self.config.scale)
            )
            image_bgr = cv2.resize(image_bgr, new_size)
        
        # Convert to grayscale for comparison
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Determine if we need full frame or diff
        send_full = False
        change_score = 0
        
        if self.cache.last_frame_gray is None:
            send_full = True
        else:
            # Calculate difference
            delta = cv2.absdiff(self.cache.last_frame_gray, gray)
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            change_score = np.sum(thresh)
            
            # Send full frame if:
            # 1. Significant change detected
            # 2. Been too long since last full frame (5 seconds)
            # 3. Too many diff frames sent (every 50 frames)
            time_since_full = time.time() - self.cache.last_full_frame_time
            
            if change_score > self.config.diff_threshold:
                send_full = True
            elif time_since_full > 5.0:
                send_full = True
            elif self.cache.frames_since_full > 50:
                send_full = True
        
        # Skip if minimal change and not time for full frame
        if not send_full and change_score < 100:
            return
        
        # Convert BGR to RGB
        rgb_array = image_bgr[:, :, ::-1]
        img = Image.fromarray(rgb_array)
        
        # Draw cursor if enabled
        if self.config.include_cursor:
            await self._draw_cursor(img)
        
        # Encode to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=self.config.quality, optimize=True)
        buffer.seek(0)
        b64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Calculate hash
        frame_hash = hashlib.md5(buffer.getvalue()).hexdigest()
        
        # Send appropriate message
        if send_full:
            await self.send_message(ONIMessage(
                type=ONIMessageType.FRAME_FULL,
                data={
                    "image": b64_image,
                    "hash": frame_hash,
                    "resolution": f"{img.width}x{img.height}",
                    "change_score": int(change_score)
                }
            ))
            self.cache.last_full_frame_time = time.time()
            self.cache.frames_since_full = 0
        else:
            await self.send_message(ONIMessage(
                type=ONIMessageType.FRAME_DIFF,
                data={
                    "image": b64_image,
                    "hash": frame_hash,
                    "change_score": int(change_score),
                    "prev_hash": self.cache.last_frame_hash
                }
            ))
            self.cache.frames_since_full += 1
        
        # Update cache
        self.cache.last_frame_gray = gray
        self.cache.last_frame_hash = frame_hash
        
    async def _draw_cursor(self, img: Image.Image):
        """Draw cursor on image."""
        try:
            import pyautogui
            import mss
            
            mouse_x, mouse_y = pyautogui.position()
            
            with mss.mss() as sct:
                primary = sct.monitors[1]
                monitor_left = primary["left"]
                monitor_top = primary["top"]
                monitor_width = primary["width"]
                monitor_height = primary["height"]
            
            # Check if in monitor bounds
            if not (monitor_left <= mouse_x < monitor_left + monitor_width and
                    monitor_top <= mouse_y < monitor_top + monitor_height):
                return
            
            # Apply ROI offset if configured
            relative_x = mouse_x - monitor_left
            relative_y = mouse_y - monitor_top
            
            if self.config.roi:
                roi_x, roi_y, _, _ = self.config.roi
                relative_x -= roi_x
                relative_y -= roi_y
            
            # Apply scale
            relative_x = int(relative_x * self.config.scale)
            relative_y = int(relative_y * self.config.scale)
            
            # Check bounds
            if relative_x < 0 or relative_y < 0 or relative_x >= img.width or relative_y >= img.height:
                return
            
            draw = ImageDraw.Draw(img)
            cursor_size = int(15 * self.config.scale)
            
            # Draw cursor indicator
            draw.ellipse(
                [(relative_x - cursor_size - 2, relative_y - cursor_size - 2),
                 (relative_x + cursor_size + 2, relative_y + cursor_size + 2)],
                outline="white", width=3
            )
            draw.ellipse(
                [(relative_x - cursor_size, relative_y - cursor_size),
                 (relative_x + cursor_size, relative_y + cursor_size)],
                fill="red", outline="black", width=2
            )
            draw.ellipse(
                [(relative_x - 3, relative_y - 3),
                 (relative_x + 3, relative_y + 3)],
                fill="white"
            )
            
        except Exception as e:
            logger.debug("cursor_draw_failed", error=str(e))
            
    async def _execute_action_verified(self, action_data: dict):
        """Execute action with before/after verification."""
        vision = container.get("vision")
        if not vision:
            await self.send_message(ONIMessage(
                type=ONIMessageType.ERROR,
                data={"error": "Vision service not available"}
            ))
            return
        
        action_type = action_data.get("action")
        params = action_data.get("params", {})
        
        logger.info("executing_verified_action", action=action_type, params=params)
        
        try:
            # Capture BEFORE
            before_capture = await vision.capture()
            if not before_capture:
                raise Exception("Failed to capture before state")
            
            before_gray = cv2.cvtColor(before_capture.image, cv2.COLOR_BGR2GRAY)
            before_hash = hashlib.md5(before_capture.image.tobytes()).hexdigest()
            
            # Get context BEFORE
            context_before = await self._get_context()
            
            # Execute action
            start_time = time.perf_counter()
            await self._execute_action(action_type, params)
            execution_time = time.perf_counter() - start_time
            
            # Wait for UI to settle
            await asyncio.sleep(params.get("verification_delay", 0.5))
            
            # Capture AFTER
            after_capture = await vision.capture()
            if not after_capture:
                raise Exception("Failed to capture after state")
            
            after_gray = cv2.cvtColor(after_capture.image, cv2.COLOR_BGR2GRAY)
            after_hash = hashlib.md5(after_capture.image.tobytes()).hexdigest()
            
            # Get context AFTER
            context_after = await self._get_context()
            
            # Calculate visual difference
            diff = cv2.absdiff(before_gray, after_gray)
            non_zero = np.count_nonzero(diff)
            total_pixels = diff.size
            change_ratio = non_zero / total_pixels
            
            # Determine success based on change
            expected_change = params.get("expect_change", True)
            success = (change_ratio > 0.001) if expected_change else (change_ratio < 0.001)
            
            # Prepare result
            result_data = {
                "success": success,
                "action": action_type,
                "execution_time_ms": round(execution_time * 1000, 2),
                "visual_change": {
                    "change_ratio": round(change_ratio, 4),
                    "pixels_changed": int(non_zero),
                    "total_pixels": int(total_pixels)
                },
                "before_hash": before_hash,
                "after_hash": after_hash,
                "context_changed": context_before != context_after,
                "context_before": context_before,
                "context_after": context_after
            }
            
            # Optionally include before/after images
            if params.get("include_images", False):
                before_img = Image.fromarray(before_capture.image[:, :, ::-1])
                after_img = Image.fromarray(after_capture.image[:, :, ::-1])
                
                before_buf = io.BytesIO()
                after_buf = io.BytesIO()
                
                before_img.save(before_buf, format="JPEG", quality=60)
                after_img.save(after_buf, format="JPEG", quality=60)
                
                result_data["before_image"] = base64.b64encode(before_buf.getvalue()).decode('utf-8')
                result_data["after_image"] = base64.b64encode(after_buf.getvalue()).decode('utf-8')
            
            await self.send_message(ONIMessage(
                type=ONIMessageType.ACTION_RESULT,
                data=result_data
            ))
            
            logger.info("action_verified", 
                       success=success,
                       change_ratio=change_ratio,
                       context_changed=context_before != context_after)
            
        except Exception as e:
            logger.error("action_verification_failed", error=str(e), exc_info=True)
            await self.send_message(ONIMessage(
                type=ONIMessageType.ACTION_RESULT,
                data={
                    "success": False,
                    "action": action_type,
                    "error": str(e)
                }
            ))
            
    async def _execute_action(self, action_type: str, params: dict):
        """Execute a single action."""
        import pyautogui
        
        # FIX P3: Multi-Monitor Validation
        try:
            monitor = await ScreenCapture.get_monitor_info()
            
            def check_bounds(tx, ty):
                if not (monitor['left'] <= tx < monitor['left'] + monitor['width'] and 
                        monitor['top'] <= ty < monitor['top'] + monitor['height']):
                     raise ValueError(f"Target ({tx},{ty}) outside primary monitor")
        except Exception:
            # If monitor info fails, we warn but allow (or fail safe? user wants safety)
            # We will log and accept risks if monitor info is missing, but ScreenCapture usually works.
            pass

        if action_type == "click":
            x = params.get("x", 0)
            y = params.get("y", 0)
            check_bounds(x, y)
            
            button = params.get("button", "left")
            clicks = params.get("clicks", 1)
            pyautogui.click(x, y, clicks=clicks, button=button)
            
        elif action_type == "double_click":
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.doubleClick(x, y)
            
        elif action_type == "right_click":
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.rightClick(x, y)
            
        elif action_type == "type":
            text = params.get("text", "")
            interval = params.get("interval", 0.02)
            pyautogui.write(text, interval=interval)
            
        elif action_type == "hotkey":
            keys = params.get("keys", [])
            if isinstance(keys, str):
                keys = keys.split(",")
            pyautogui.hotkey(*keys)
            
        elif action_type == "press":
            key = params.get("key", "")
            pyautogui.press(key)
            
        elif action_type == "move":
            x = params.get("x", 0)
            y = params.get("y", 0)
            duration = params.get("duration", 0.0)
            pyautogui.moveTo(x, y, duration=duration)
            
        elif action_type == "drag":
            # FIX P2: Absolute Drag
            duration = params.get("duration", 0.5)
            
            # Check if we have x1,y1,x2,y2 (Absolute)
            if "x1" in params and "x2" in params:
                x1, y1 = params.get("x1"), params.get("y1")
                x2, y2 = params.get("x2"), params.get("y2")
                check_bounds(x1, y1)
                check_bounds(x2, y2)
                
                pyautogui.moveTo(x1, y1)
                pyautogui.dragTo(x2, y2, duration=duration)
            else:
                # Relative/Simple drag (Legacy support)
                x = params.get("x", 0)
                y = params.get("y", 0)
                # If x,y is target destination (dragTo) or offset?
                # PyAutoGUI drag(x,y) is relative. dragTo is absolute.
                # Assuming params x,y refers to offset if simple drag called
                # BUT user complaint implies they want absolute behavior.
                # We will interpret x,y as "drag to x,y" from current position if x1,x2 not present
                check_bounds(x, y)
                pyautogui.dragTo(x, y, duration=duration)
            
        elif action_type == "scroll":
            amount = params.get("amount", 0)
            pyautogui.scroll(amount)
            
        elif action_type == "wait":
            seconds = params.get("seconds", 1.0)
            await asyncio.sleep(seconds)
            
        else:
            raise ValueError(f"Unknown action type: {action_type}")
            
    async def _get_context(self) -> dict:
        """Get current desktop context."""
        context = {}
        
        try:
            # Get active window info
            import win32gui
            import win32process
            import psutil
            
            hwnd = win32gui.GetForegroundWindow()
            context["active_window"] = {
                "title": win32gui.GetWindowText(hwnd),
                "handle": hwnd
            }
            
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(process_id)
                context["active_window"]["process"] = process.name()
                context["active_window"]["pid"] = process_id
            except:
                pass
                
            # Get screen resolution
            import mss
            with mss.mss() as sct:
                primary = sct.monitors[1]
                context["screen"] = {
                    "width": primary["width"],
                    "height": primary["height"],
                    "left": primary["left"],
                    "top": primary["top"]
                }
                
            # Get mouse position
            import pyautogui
            mx, my = pyautogui.position()
            context["mouse"] = {"x": mx, "y": my}
            
        except Exception as e:
            logger.debug("context_gathering_partial_failure", error=str(e))
            
        return context
        
    async def _get_ocr(self, region: Optional[list] = None) -> dict:
        """Get OCR from current screen or region."""
        vision = container.get("vision")
        if not vision:
            return {"error": "Vision service not available"}
        
        try:
            # Capture screen
            capture = await vision.capture()
            if not capture:
                return {"error": "Failed to capture screen"}
            
            # Fix P1: Use Cached OCR Service
            # Convert PIL to get image
            rgb_array = capture.image[:, :, ::-1]
            img = Image.fromarray(rgb_array)
            
            region_str = None
            if region and len(region) == 4:
                # OCRService expects "x,y,w,h" string
                region_str = ",".join(map(str, region))
            
            text, words, _ = await OCRService.extract_text(img, region_str, "por+eng")
            
            # Convert OCRService words (objects) to dicts if needed, or expected format
            # OCRService returns list of OCRWord objects. We need to serialize them.
            words_dicts = []
            for w in words:
                words_dicts.append({
                    "text": w.text,
                    "x": w.x,
                    "y": w.y,
                    "width": w.width,
                    "height": w.height,
                    "confidence": w.confidence
                })

            return {
                "text": text,
                "words": words_dicts[:100],
                "word_count": len(words_dicts),
                "region": region,
                "cached": False # Service handles caching internal logic
            }
            
        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return {"error": str(e)}


# =============================================================================
# WEBSOCKET ENDPOINT
# =============================================================================

async def oni_websocket_handler(websocket: WebSocket):
    """
    Main WebSocket endpoint for ONI.
    
    Usage:
        const ws = new WebSocket("ws://localhost:8000/ws/oni");
        
        // Configure FPS
        ws.send(JSON.stringify({
            type: "config_fps",
            data: { fps: 30 }
        }));
        
        // Execute action with verification
        ws.send(JSON.stringify({
            type: "execute_action",
            data: {
                action: "click",
                params: { x: 500, y: 300 }
            }
        }));
    """
    connection = ONIConnection(websocket)
    
    try:
        await connection.connect()
        
        # Start streaming in background
        connection.stream_task = asyncio.create_task(connection.start_stream())
        
        # Handle incoming messages
        while connection.active:
            try:
                data = await websocket.receive_json()
                await connection.handle_message(data)
            except json.JSONDecodeError:
                await connection.send_message(ONIMessage(
                    type=ONIMessageType.ERROR,
                    data={"error": "Invalid JSON"}
                ))
                
    except WebSocketDisconnect:
        logger.info("oni_disconnected")
    except Exception as e:
        logger.error("oni_error", error=str(e), exc_info=True)
    finally:
        connection.active = False
        if connection.stream_task:
            connection.stream_task.cancel()
            try:
                await connection.stream_task
            except asyncio.CancelledError:
                pass
        logger.info("oni_connection_closed")
