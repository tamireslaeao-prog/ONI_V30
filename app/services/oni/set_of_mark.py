"""
ONI Set-of-Mark Service
Overlays numbered tags on clickable UI elements for VLM grounding.
"""

import io
import structlog

logger = structlog.get_logger(__name__)


class SetOfMarkService:
    """
    Set-of-Mark (SoM) Service (v6.0).
    Overlays numbered tags on clickable UI elements for VLM grounding.
    """
    
    @staticmethod
    async def annotate_screen(vision_service, ui_tree_elements: list) -> tuple:
        """
        Overlay numbered markers on UI elements.
        Returns (annotated_image_bytes, element_map).
        """
        try:
            from PIL import Image, ImageDraw
            
            capture = await vision_service.capture()
            if not capture:
                return None, {}
            
            # Convert to PIL
            rgb_array = capture.image[:, :, ::-1]
            img = Image.fromarray(rgb_array)
            draw = ImageDraw.Draw(img)
            
            element_map = {}
            
            for idx, elem in enumerate(ui_tree_elements[:50]):
                x = elem.get("center_x", elem.get("x", 0))
                y = elem.get("center_y", elem.get("y", 0))
                tag = f"[{idx}]"
                
                # Draw tag background
                bbox = draw.textbbox((x, y), tag)
                padding = 2
                draw.rectangle(
                    [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding],
                    fill="red"
                )
                draw.text((x, y), tag, fill="white")
                
                element_map[idx] = {
                    "x": x,
                    "y": y,
                    "role": elem.get("role", "unknown"),
                    "title": elem.get("title", ""),
                    "text": elem.get("text", "")
                }
            
            # Convert to bytes
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            
            logger.info("som_annotated", elements=len(element_map))
            return buf.getvalue(), element_map
            
        except Exception as e:
            logger.error("som_annotation_failed", error=str(e))
            return None, {}
