"""
ONI ArtMaster - Models
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, confloat, conint
from pathlib import Path
from .config import ArtMasterConfig
from .types import ApplicationType, ApplicationInfo

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None


class ApplicationInfoResponse(BaseResponse):
    """Response with detected application info."""
    application: Optional[ApplicationInfo] = None
    message: Optional[str] = None


class DrawRequest(BaseModel):
    """Request model for drawing."""
    image_path: str
    scale: confloat(ge=0.1, le=10.0) = 0.8
    max_shapes: conint(ge=1, le=1000) = 100
    high_fidelity: bool = False
    line_art: bool = False
    application: Optional[ApplicationType] = None  # Auto-detect if None
    create_layer: bool = False  # Create new layer (Photoshop only)
    layer_name: Optional[str] = None
    capture_final: bool = False
    validate_result: bool = False
    center_x: Optional[int] = None  # Override canvas center X (for multi-monitor)
    center_y: Optional[int] = None  # Override canvas center Y (for multi-monitor)
    
    @validator("image_path")
    def validate_image_path(cls, v):
        """Validate image path."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Image not found: {v}")
        if path.stat().st_size > ArtMasterConfig.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise ValueError(f"Image too large")
        return str(path.absolute())


class CalibrateRequest(BaseModel):
    """Request model for calibration."""
    canvas_limits: Optional[Dict[str, int]] = None
    center_x: Optional[int] = None
    center_y: Optional[int] = None
    duration: float = 1.0


class WorkflowResponse(BaseResponse):
    """Response for workflow execution."""
    application_used: Optional[ApplicationType] = None
    shapes_drawn: int
    total_shapes: int
    final_screenshot: Optional[str] = None
    validation_score: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
