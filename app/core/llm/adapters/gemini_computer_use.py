import uuid
from typing import Any, Dict, List, Optional
import logging

try:
    from google.genai import types
except ImportError:
    # Handle if google-genai is not installed, though it should be
    pass

logger = logging.getLogger(__name__)

class GeminiComputerUseAdapter:
    """Adapter for Google Gemini Computer Use capabilities."""

    @staticmethod
    def build_custom_function_declarations() -> List[Dict[str, Any]]:
        """
        Builds the custom function declarations required for Gemini 3 models to perform computer use.
        These map to the actions available in the Computer interface.
        """
        return [
            {
                "name": "click_at",
                "description": "Click at the specified x,y coordinates on the screen. Coordinates are normalized 0-999.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "x": {
                            "type": "INTEGER",
                            "description": "The x coordinate (0-999)"
                        },
                        "y": {
                            "type": "INTEGER",
                            "description": "The y coordinate (0-999)"
                        },
                         "button": {
                            "type": "STRING",
                            "description": "The mouse button to click (left, right, middle)",
                            "enum": ["left", "right", "middle"]
                        },
                        "clicks": {
                            "type": "INTEGER",
                            "description": "Number of clicks (1 for single, 2 for double)"
                        }
                    },
                    "required": ["x", "y"]
                }
            },
            {
                "name": "type_text_at",
                "description": "Type text at the specified coordinates.",
                 "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "x": {"type": "INTEGER"},
                        "y": {"type": "INTEGER"},
                        "text": {"type": "STRING"},
                        "submit": {"type": "BOOLEAN"}
                    },
                    "required": ["x", "y", "text"]
                }
            },
            {
                "name": "press_keys",
                "description": "Press a key combination (e.g. 'ctrl+c').",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "keys": {"type": "STRING"}
                    },
                    "required": ["keys"]
                }
            },
             {
                "name": "scroll",
                "description": "Scroll the screen.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                         "x": {"type": "INTEGER"},
                         "y": {"type": "INTEGER"},
                        "delta_x": {"type": "INTEGER"},
                        "delta_y": {"type": "INTEGER"}
                    },
                     "required": ["x", "y", "delta_y"]
                }
            },
             {
                "name": "wait",
                "description": "Wait for a specified duration.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "duration": {"type": "NUMBER"}
                    },
                    "required": ["duration"]
                }
            }
        ]

    @staticmethod
    def map_gemini_call_to_computer_action(
        function_call: Dict[str, Any],
        screen_width: int,
        screen_height: int
    ) -> Dict[str, Any]:
        """
        Maps a Gemini 3 custom function call to an internal computer action format.
        Handles coordinate denormalization (0-999 -> pixel coords).
        """
        fname = function_call.get("name")
        args = function_call.get("args", {})
        
        # Helper to denormalize
        def denorm_x(x): return int(x * screen_width / 1000)
        def denorm_y(y): return int(y * screen_height / 1000)

        action = {}
        
        if fname == "click_at":
            action = {
                "action": "click",
                "x": denorm_x(args.get("x", 0)),
                "y": denorm_y(args.get("y", 0)),
                "button": args.get("button", "left"),
                "clicks": args.get("clicks", 1)
            }
        elif fname == "type_text_at":
            # Note: Complex to handle "type at" strictly if we don't click first
            # We assume agent might click then type, or we chain it. 
            # For simplicity, we just type, but coordinates are provided for context.
            action = {
                "action": "type",
                "text": args.get("text", ""),
                # You might want to move mouse there first if supported
                "x": denorm_x(args.get("x", 0)),
                "y": denorm_y(args.get("y", 0))
            }
            if args.get("submit"):
                action["submit"] = True
                
        elif fname == "press_keys":
            action = {
                "action": "key",
                "keys": args.get("keys", "")
            }
        elif fname == "scroll":
             action = {
                "action": "scroll",
                "x": denorm_x(args.get("x", 0)),
                "y": denorm_y(args.get("y", 0)),
                "dx": args.get("delta_x", 0),
                "dy": args.get("delta_y", 0)
            }
        elif fname == "wait":
            action = {
                "action": "wait",
                "duration": args.get("duration", 1.0)
            }
        else:
            logger.warning(f"Unknown function call from Gemini: {fname}")
            
        return {
            "type": "computer_call",
            "call_id": str(uuid.uuid4()),
            "status": "pending",
            "action": action
        }
