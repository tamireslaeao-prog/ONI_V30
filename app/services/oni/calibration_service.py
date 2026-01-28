"""
ONI v11.0 - Calibration Service
Fixes coordinate transformation issues:
- DPI scaling (100%, 125%, 150%, etc.)
- Viewport vs Screen coordinates
- Multi-monitor offsets
"""

import ctypes
from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CalibrationResult:
    """Result of coordinate calibration."""
    original_x: int
    original_y: int
    calibrated_x: int
    calibrated_y: int
    dpi_factor: float
    window_offset: Tuple[int, int]
    monitor_offset: Tuple[int, int]
    source: str
    transformations_applied: list


@dataclass
class MonitorInfo:
    """Information about a monitor."""
    index: int
    x: int
    y: int
    width: int
    height: int
    is_primary: bool
    dpi_scale: float


class CalibrationService:
    """
    Coordinate Calibration Service for accurate clicking.
    
    Handles all coordinate transformation issues:
    1. DPI Scaling - Windows often runs at 125%, 150%, etc.
    2. Viewport→Screen - Browser coordinates vs screen coordinates
    3. Multi-monitor - Offset for secondary monitors
    
    Example:
        calibrator = CalibrationService()
        
        # Coordinates from browser/VLM
        raw_x, raw_y = 500, 300
        
        # Calibrate before clicking
        result = calibrator.calibrate(raw_x, raw_y, source="viewport")
        click(result.calibrated_x, result.calibrated_y)
    """
    
    def __init__(self):
        """Initialize Calibration Service."""
        self._dpi_scale = self._detect_dpi_scale()
        self._monitors = self._detect_monitors()
        self._window_offsets: Dict[str, Tuple[int, int]] = {}
        
        logger.info(
            "calibration_service_init",
            dpi_scale=self._dpi_scale,
            monitors=len(self._monitors)
        )
    
    def _detect_dpi_scale(self) -> float:
        """Detect Windows DPI scaling factor."""
        try:
            # Try to make process DPI aware first
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                pass
            
            # Get DPI for primary monitor
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
            # Get logical vs physical resolution
            logical_width = user32.GetSystemMetrics(0)
            
            # Get physical resolution via DC
            dc = user32.GetDC(0)
            gdi32 = ctypes.windll.gdi32
            physical_width = gdi32.GetDeviceCaps(dc, 118)  # DESKTOPHORZRES
            user32.ReleaseDC(0, dc)
            
            if physical_width and logical_width:
                scale = physical_width / logical_width
                logger.info("dpi_scale_detected", scale=scale)
                return scale
            
            return 1.0
            
        except Exception as e:
            logger.warning("dpi_detection_failed", error=str(e))
            return 1.0
    
    def _detect_monitors(self) -> list[MonitorInfo]:
        """Detect all monitors and their properties."""
        monitors = []
        
        try:
            user32 = ctypes.windll.user32
            
            # Get primary monitor size
            primary_width = user32.GetSystemMetrics(0)
            primary_height = user32.GetSystemMetrics(1)
            
            monitors.append(MonitorInfo(
                index=0,
                x=0,
                y=0,
                width=primary_width,
                height=primary_height,
                is_primary=True,
                dpi_scale=self._dpi_scale
            ))
            
            # Try to get secondary monitor info via EnumDisplayMonitors
            # For simplicity, just check virtual screen size
            virtual_width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
            virtual_height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
            virtual_x = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
            virtual_y = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
            
            # If virtual screen is larger, there are additional monitors
            if virtual_width > primary_width or virtual_x < 0:
                logger.info(
                    "multi_monitor_detected",
                    virtual_size=(virtual_width, virtual_height),
                    virtual_offset=(virtual_x, virtual_y)
                )
            
        except Exception as e:
            logger.warning("monitor_detection_failed", error=str(e))
            # Default to 1920x1080 primary
            monitors.append(MonitorInfo(
                index=0, x=0, y=0, width=1920, height=1080,
                is_primary=True, dpi_scale=1.0
            ))
        
        return monitors
    
    def set_window_offset(self, window_name: str, offset: Tuple[int, int]) -> None:
        """Set viewport offset for a specific window."""
        self._window_offsets[window_name] = offset
        logger.debug("window_offset_set", window=window_name, offset=offset)
    
    def calibrate(
        self,
        x: int,
        y: int,
        source: Literal["screen", "viewport", "vlm", "browser"] = "screen",
        window_name: Optional[str] = None,
        apply_dpi: bool = True,
        target_monitor: int = 0,
    ) -> CalibrationResult:
        """
        Calibrate coordinates from various sources.
        
        Args:
            x: Raw X coordinate
            y: Raw Y coordinate
            source: Source of coordinates
                - "screen": Already screen coordinates
                - "viewport": Browser viewport (needs window offset)
                - "vlm": From vision model (may need DPI adjustment)
                - "browser": Same as viewport
            window_name: Name of window for offset lookup
            apply_dpi: Whether to apply DPI scaling
            target_monitor: Target monitor index
            
        Returns:
            CalibrationResult with calibrated coordinates
        """
        original_x, original_y = x, y
        transformations = []
        
        # Get window offset
        window_offset = (0, 0)
        if window_name and window_name in self._window_offsets:
            window_offset = self._window_offsets[window_name]
        
        # Get monitor offset
        monitor_offset = (0, 0)
        if target_monitor < len(self._monitors):
            monitor = self._monitors[target_monitor]
            monitor_offset = (monitor.x, monitor.y)
        
        # Apply transformations based on source
        cal_x, cal_y = x, y
        
        if source in ("viewport", "browser"):
            # Add window offset for viewport coordinates
            cal_x += window_offset[0]
            cal_y += window_offset[1]
            transformations.append(f"window_offset({window_offset})")
        
        if source == "vlm" and apply_dpi:
            # VLM coordinates might be in logical pixels
            # Only apply if DPI is significantly different from 1.0
            if abs(self._dpi_scale - 1.0) > 0.05:
                cal_x = int(cal_x * self._dpi_scale)
                cal_y = int(cal_y * self._dpi_scale)
                transformations.append(f"dpi_scale({self._dpi_scale})")
        
        if target_monitor > 0:
            # Add monitor offset for non-primary monitors
            cal_x += monitor_offset[0]
            cal_y += monitor_offset[1]
            transformations.append(f"monitor_offset({monitor_offset})")
        
        logger.debug(
            "coordinates_calibrated",
            original=(original_x, original_y),
            calibrated=(cal_x, cal_y),
            source=source,
            transformations=transformations
        )
        
        return CalibrationResult(
            original_x=original_x,
            original_y=original_y,
            calibrated_x=cal_x,
            calibrated_y=cal_y,
            dpi_factor=self._dpi_scale,
            window_offset=window_offset,
            monitor_offset=monitor_offset,
            source=source,
            transformations_applied=transformations
        )
    
    def calibrate_for_click(
        self,
        x: int,
        y: int,
        source: Literal["screen", "viewport", "vlm", "browser"] = "vlm",
    ) -> Tuple[int, int]:
        """
        Simplified calibration returning just coordinates.
        
        Args:
            x: Raw X coordinate
            y: Raw Y coordinate
            source: Source type
            
        Returns:
            Tuple of (calibrated_x, calibrated_y)
        """
        result = self.calibrate(x, y, source)
        return (result.calibrated_x, result.calibrated_y)
    
    def get_primary_monitor(self) -> MonitorInfo:
        """Get primary monitor info."""
        for m in self._monitors:
            if m.is_primary:
                return m
        return self._monitors[0] if self._monitors else MonitorInfo(
            index=0, x=0, y=0, width=1920, height=1080,
            is_primary=True, dpi_scale=1.0
        )
    
    def is_point_in_primary(self, x: int, y: int) -> bool:
        """Check if point is within primary monitor bounds."""
        primary = self.get_primary_monitor()
        return (
            primary.x <= x < primary.x + primary.width and
            primary.y <= y < primary.y + primary.height
        )
    
    def refresh(self) -> None:
        """Refresh DPI and monitor detection."""
        self._dpi_scale = self._detect_dpi_scale()
        self._monitors = self._detect_monitors()
        logger.info("calibration_refreshed", dpi=self._dpi_scale)
    
    @property
    def dpi_scale(self) -> float:
        """Current DPI scale factor."""
        return self._dpi_scale
    
    @property  
    def monitors(self) -> list[MonitorInfo]:
        """List of detected monitors."""
        return self._monitors


# Global singleton
_calibration_service: Optional[CalibrationService] = None


def get_calibration_service() -> CalibrationService:
    """Get or create CalibrationService singleton."""
    global _calibration_service
    if _calibration_service is None:
        _calibration_service = CalibrationService()
    return _calibration_service
