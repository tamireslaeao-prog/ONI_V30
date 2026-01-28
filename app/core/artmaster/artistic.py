import random
import math
import pyautogui
import time
import logging
from typing import Tuple, List
from .photoshop_master import PhotoshopMasterPureGUI

logger = logging.getLogger(__name__)

class ArtisticStylesGUI:
    """
    Implements artistic painting styles and brush dynamics.
    """
    def __init__(self, master: PhotoshopMasterPureGUI):
        self.master = master
        self.mouse = master.mouse

    def apply_van_gogh_style(self, region: Tuple[int, int, int, int], num_swirls: int = 5):
        """
        Paints swirls in the defined region.
        """
        logger.info("Applying Van Gogh Style...")
        self.master.select_tool("brush")
        
        x1, y1, x2, y2 = region
        
        for _ in range(num_swirls):
            center_x = random.randint(x1, x2)
            center_y = random.randint(y1, y2)
            radius = random.randint(30, 80)
            
            # Draw a spiral
            points = self._generate_spiral((center_x, center_y), radius, rotations=3)
            self.master.paint_stroke(points, mode="ARTISTIC")
            
            # Optional: Simulate color jitter by pressing shortcut 'x' (swap colors) occasionally
            if random.random() < 0.3:
                pyautogui.press('x')

    def apply_pointillism(self, region: Tuple[int, int, int, int], density: int = 50):
        """
        Paints random points/dots in the region.
        """
        logger.info("Applying Pointillism...")
        self.master.select_tool("brush")
        
        x1, y1, x2, y2 = region
        
        for _ in range(density):
            px = random.randint(x1, x2)
            py = random.randint(y1, y2)
            
            self.mouse.move((px, py), (px, py), mode="TURBO")
            pyautogui.click()
            time.sleep(0.01)

    def _generate_spiral(self, center: Tuple[int, int], radius: float, rotations: float) -> List[Tuple[int, int]]:
        points = []
        steps = int(rotations * 30) # resolution
        for i in range(steps):
            angle = i * (math.pi / 10)
            r = radius * (i / steps)
            x = center[0] + int(r * math.cos(angle))
            y = center[1] + int(r * math.sin(angle))
            points.append((x, y))
        return points
