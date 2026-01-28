"""
ONI Enums
Action types, mouse buttons, and image formats.
"""

from enum import Enum


class ActionType(str, Enum):
    """Supported action types."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    TYPEWRITE = "typewrite"
    HOTKEY = "hotkey"
    PRESS = "press"
    MOVE = "move"
    DRAG = "drag"
    SCROLL = "scroll"
    WAIT = "wait"


class MouseButton(str, Enum):
    """Mouse button types."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ImageFormat(str, Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
