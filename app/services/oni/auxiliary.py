"""
ONI Auxiliary Services
Cache, Metrics, Security, and Computer Vision services.
"""

import os
from typing import Any
from functools import lru_cache
import structlog

logger = structlog.get_logger(__name__)


class MetricsService:
    """Observability service for tracking performance and usage."""
    
    _metrics = {
        "requests_total": 0,
        "errors_total": 0,
        "actions_executed": 0,
        "ocr_processing_ms_total": 0.0,
        "ocr_count": 0,
        "screenshots_taken": 0
    }
    
    @classmethod
    def increment(cls, metric: str, amount: int = 1):
        if metric in cls._metrics:
            cls._metrics[metric] += amount
            
    @classmethod
    def record_latency(cls, metric: str, ms: float):
        if metric in cls._metrics:
            cls._metrics[metric] += ms
            
    @classmethod
    def get_metrics_prometheus(cls) -> str:
        """Return metrics in Prometheus format."""
        lines = [f"oni_{k} {v}" for k, v in cls._metrics.items()]
        return "\n".join(lines)


class CacheService:
    """Caching service for repetitive operations."""
    
    _cache = {}
    _max_size = 500
    
    @classmethod
    def get(cls, key: str):
        return cls._cache.get(key)
        
    @classmethod
    def set(cls, key: str, value: Any):
        if len(cls._cache) >= cls._max_size:
            cls._cache.pop(next(iter(cls._cache)))
        cls._cache[key] = value

    @classmethod
    def clear(cls):
        cls._cache.clear()


class SecurityService:
    """Security service for authentication and auditing."""
    
    # SECURITY FIX: No default token - must be configured or auto-generated
    _token: str | None = None
    
    @classmethod
    def _get_token(cls) -> str:
        """Get or generate security token."""
        if cls._token is None:
            env_token = os.getenv("ONI_API_SECRET")
            if env_token:
                cls._token = env_token
            else:
                import secrets
                cls._token = secrets.token_urlsafe(32)
                logger.warning(
                    "security_token_auto_generated",
                    message="No ONI_API_SECRET configured. Random token generated for this session."
                )
        return cls._token
    
    @classmethod
    def verify_token(cls, token: str) -> bool:
        return token == cls._get_token()

    @classmethod
    async def audit_log(cls, action: str, details: dict):
        logger.info("AUDIT_LOG", action=action, **details)


class ComputerVisionService:
    """Computer Vision service for template matching."""
    
    @staticmethod
    def match_template(screen_img, template_img, threshold=0.8):
        """Find template in screen using OpenCV."""
        try:
            import cv2
            import numpy as np
            
            screen_arr = np.array(screen_img)
            screen_bgr = cv2.cvtColor(screen_arr, cv2.COLOR_RGB2BGR)
            
            template_arr = np.array(template_img)
            template_bgr = cv2.cvtColor(template_arr, cv2.COLOR_RGB2BGR)
            
            result = cv2.matchTemplate(screen_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                h, w = template_bgr.shape[:2]
                return {
                    "found": True,
                    "x": max_loc[0], "y": max_loc[1],
                    "w": w, "h": h,
                    "confidence": float(max_val)
                }
            return {"found": False, "confidence": float(max_val)}
            
        except ImportError:
            return {"found": False, "error": "OpenCV not available"}
        except Exception as e:
            return {"found": False, "error": str(e)}


class AIService:
    """AI Service for Object Detection."""
    
    _model = None
    
    @classmethod
    def load_yolo(cls, model_path="yolov8n.pt"):
        try:
            from ultralytics import YOLO
            cls._model = YOLO(model_path)
            logger.info("yolo_model_loaded", model=model_path)
        except ImportError:
            logger.warning("ultralytics_not_installed")
        except Exception as e:
            logger.error("yolo_load_failed", error=str(e))

    @classmethod
    def detect_objects(cls, img, confidence=0.5):
        if not cls._model:
            cls.load_yolo()
            if not cls._model:
                return []
        
        try:
            results = cls._model(img, conf=confidence)
            detections = []
            for r in results:
                for box in r.boxes:
                    detections.append({
                        "class": cls._model.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "box": [float(x) for x in box.xyxy[0]]
                    })
            return detections
        except Exception as e:
            logger.error("detection_failed", error=str(e))
            return []
