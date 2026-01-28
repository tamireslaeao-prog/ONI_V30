"""
ONI v9.0 - OmniParser Provider
Set-of-Mark (SOM) visual annotation for precise element targeting.

Uses Microsoft's OmniParser to overlay numbered IDs on UI elements,
allowing LLMs to reference elements by ID instead of coordinates.
"""

import base64
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)

# Constants
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080
COORD_EPSILON = 0.0001  # For floating point comparison

# Check if OmniParser is available
OMNIPARSER_AVAILABLE = False
try:
    from som import OmniParser
    OMNIPARSER_AVAILABLE = True
except ImportError:
    logger.warning("OmniParser not available. Install with: pip install cua-som")


@dataclass
class ParsedElement:
    """A parsed UI element with ID and coordinates."""
    id: int
    x: int
    y: int
    width: int
    height: int
    label: str = ""
    element_type: str = "unknown"
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center coordinates."""
        return (self.x, self.y)
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Get bounding box (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within element bounds."""
        left = self.x - self.width // 2
        right = self.x + self.width // 2
        top = self.y - self.height // 2
        bottom = self.y + self.height // 2
        return left <= x <= right and top <= y <= bottom


@dataclass
class OmniParseResult:
    """Result from OmniParser annotation."""
    annotated_image_b64: str
    elements: List[ParsedElement]
    id2xy: Dict[int, Tuple[int, int]] = field(default_factory=dict)
    
    def get_element(self, element_id: int) -> Optional[ParsedElement]:
        """Get element by ID."""
        for elem in self.elements:
            if elem.id == element_id:
                return elem
        return None
    
    def get_coords(self, element_id: int) -> Optional[Tuple[int, int]]:
        """Get center coordinates for element ID."""
        return self.id2xy.get(element_id)
    
    def find_elements_at_point(self, x: int, y: int) -> List[ParsedElement]:
        """Find all elements containing the given point."""
        return [elem for elem in self.elements if elem.contains_point(x, y)]
    
    def get_element_count(self) -> int:
        """Get total number of parsed elements."""
        return len(self.elements)


class OmniParserProvider:
    """
    OmniParser Visual Grounding Provider.
    
    Uses Set-of-Mark (SOM) to annotate screenshots with numbered IDs.
    This eliminates coordinate errors since LLMs reference elements by ID.
    
    Usage:
        provider = OmniParserProvider()
        result = await provider.parse_screenshot(screenshot_b64)
        # LLM sees annotated image with IDs
        # LLM says "click element 5"
        coords = result.get_coords(5)  # Returns (x, y)
    """
    
    _parser = None
    _parser_lock = threading.Lock()
    
    def __init__(
        self, 
        screen_width: int = DEFAULT_SCREEN_WIDTH, 
        screen_height: int = DEFAULT_SCREEN_HEIGHT
    ):
        """
        Initialize OmniParser provider.
        
        Args:
            screen_width: Screen width for coordinate scaling
            screen_height: Screen height for coordinate scaling
        """
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError(f"Invalid screen dimensions: {screen_width}x{screen_height}")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self._ensure_parser_initialized()
    
    def _ensure_parser_initialized(self) -> None:
        """Initialize OmniParser singleton (thread-safe)."""
        if not OMNIPARSER_AVAILABLE:
            return
        
        if OmniParserProvider._parser is None:
            with OmniParserProvider._parser_lock:
                # Double-check after acquiring lock
                if OmniParserProvider._parser is None:
                    try:
                        OmniParserProvider._parser = OmniParser()
                        logger.info("OmniParser initialized successfully")
                    except Exception as e:
                        logger.error("Failed to initialize OmniParser", error=str(e))
    
    @property
    def is_available(self) -> bool:
        """Check if OmniParser is available."""
        return OMNIPARSER_AVAILABLE and OmniParserProvider._parser is not None
    
    def _normalize_to_pixels(
        self,
        norm_coord: float,
        dimension: int
    ) -> int:
        """Convert normalized coordinate (0-1) to pixel coordinate."""
        return max(0, min(int(norm_coord * dimension), dimension - 1))
    
    def _build_parsed_element(
        self,
        elem: any,
        width: int,
        height: int
    ) -> ParsedElement:
        """Build ParsedElement from OmniParser element."""
        # Calculate center coordinates
        norm_x = (elem.bbox.x1 + elem.bbox.x2) / 2
        norm_y = (elem.bbox.y1 + elem.bbox.y2) / 2
        pixel_x = self._normalize_to_pixels(norm_x, width)
        pixel_y = self._normalize_to_pixels(norm_y, height)
        
        # Calculate dimensions
        elem_width = self._normalize_to_pixels(
            elem.bbox.x2 - elem.bbox.x1, 
            width
        )
        elem_height = self._normalize_to_pixels(
            elem.bbox.y2 - elem.bbox.y1, 
            height
        )
        
        return ParsedElement(
            id=elem.id,
            x=pixel_x,
            y=pixel_y,
            width=max(1, elem_width),  # Ensure minimum size
            height=max(1, elem_height),
            label=getattr(elem, 'label', ''),
            element_type=getattr(elem, 'type', 'unknown')
        )
    
    async def parse_screenshot(
        self, 
        screenshot_b64: str,
        screen_size: Optional[Tuple[int, int]] = None,
        frame_hash: Optional[str] = None
    ) -> Optional[OmniParseResult]:
        """
        Parse screenshot and annotate with element IDs.
        
        Args:
            screenshot_b64: Base64 encoded screenshot (PNG)
            screen_size: Optional (width, height) for coordinate scaling
            frame_hash: Optional dHash for checking inference cache
            
        Returns:
            OmniParseResult with annotated image and element mappings,
            or None if parsing fails or OmniParser unavailable
        """
        if not self.is_available:
            logger.warning("OmniParser not available, returning None")
            return None
        
        if not screenshot_b64:
            logger.error("Empty screenshot_b64 provided")
            return None

        # 1. Check Cache
        from app.services.vision.vision_cache import get_vision_cache
        cache = get_vision_cache()
        if frame_hash:
            cached_data = cache.get(f"som_{frame_hash}")
            if cached_data:
                logger.debug(f"SOM cache hit for hash {frame_hash}")
                return OmniParseResult(
                    annotated_image_b64=cached_data["annotated_image_b64"],
                    elements=[ParsedElement(**e) for e in cached_data["elements"]],
                    id2xy={int(k): v for k, v in cached_data["id2xy"].items()}
                )
        
        width, height = screen_size if screen_size else (self.screen_width, self.screen_height)
        
        if width <= 0 or height <= 0:
            logger.error("Invalid screen dimensions", width=width, height=height)
            return None
        
        try:
            # Parse with OmniParser
            result = OmniParserProvider._parser.parse(screenshot_b64)
            
            if not hasattr(result, 'elements') or not hasattr(result, 'annotated_image_base64'):
                logger.error("Invalid OmniParser result structure")
                return None
            
            # Build element list and ID mapping
            elements = []
            id2xy = {}
            
            for elem in result.elements:
                parsed = self._build_parsed_element(elem, width, height)
                elements.append(parsed)
                id2xy[parsed.id] = (parsed.x, parsed.y)
            
            logger.info(
                "OmniParser parsed screenshot",
                num_elements=len(elements),
                screen_size=(width, height)
            )
            
            parse_result = OmniParseResult(
                annotated_image_b64=result.annotated_image_base64,
                elements=elements,
                id2xy=id2xy
            )

            # 2. Update Cache
            if frame_hash:
                import dataclasses
                cache.set(f"som_{frame_hash}", {
                    "annotated_image_b64": parse_result.annotated_image_base64,
                    "elements": [dataclasses.asdict(e) for e in elements],
                    "id2xy": {str(k): v for k, v in id2xy.items()}
                })
            
            return parse_result
            
        except Exception as e:
            logger.error("OmniParser parse failed", error=str(e), exc_info=True)
            return None
    
    async def click_element(
        self, 
        element_id: int, 
        result: OmniParseResult
    ) -> Optional[Tuple[int, int]]:
        """
        Get click coordinates for an element ID.
        
        Args:
            element_id: The element ID to click
            result: Previous parse result
            
        Returns:
            (x, y) coordinates or None if not found
        """
        if result is None:
            logger.warning("Cannot click element: result is None")
            return None
        
        coords = result.get_coords(element_id)
        
        if coords:
            logger.info(
                "OmniParser element click", 
                element_id=element_id, 
                coords=coords
            )
        else:
            logger.warning(
                "Element ID not found", 
                element_id=element_id,
                available_ids=list(result.id2xy.keys())[:10]  # Show first 10 IDs
            )
        
        return coords
    
    def get_element_by_id(
        self,
        element_id: int,
        result: OmniParseResult
    ) -> Optional[ParsedElement]:
        """
        Get full element details by ID.
        
        Args:
            element_id: Element ID to retrieve
            result: Parse result containing elements
            
        Returns:
            ParsedElement or None if not found
        """
        return result.get_element(element_id) if result else None


# Global singleton
_omniparser_provider: Optional[OmniParserProvider] = None
_provider_lock = threading.Lock()


def get_omniparser_provider(
    screen_width: int = DEFAULT_SCREEN_WIDTH,
    screen_height: int = DEFAULT_SCREEN_HEIGHT
) -> OmniParserProvider:
    """
    Get or create OmniParser provider singleton (thread-safe).
    
    Args:
        screen_width: Screen width (used only on first creation)
        screen_height: Screen height (used only on first creation)
    """
    global _omniparser_provider
    
    if _omniparser_provider is None:
        with _provider_lock:
            # Double-check after acquiring lock
            if _omniparser_provider is None:
                _omniparser_provider = OmniParserProvider(screen_width, screen_height)
    
    return _omniparser_provider


def reset_omniparser_provider() -> None:
    """Reset the global OmniParser provider (useful for testing)."""
    global _omniparser_provider
    with _provider_lock:
        _omniparser_provider = None
