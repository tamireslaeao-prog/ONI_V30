"""
ONI v2.0 - Task Decomposer V2
Breaks complex goals into subtasks and executes them intelligently.
"""
import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, List, Optional
import structlog

logger = structlog.get_logger()


@dataclass
class SubTask:
    """A decomposed subtask."""
    action: str
    params: dict = field(default_factory=dict)
    description: str = ""
    requires_vision: bool = False
    wait_after: float = 1.0


class TaskDecomposer:
    """
    Decomposes complex goals into executable subtasks.
    """
    
    # Patterns for detecting actions in goals
    OPEN_APP_PATTERNS = [
        r"(?:abr[aei]|open|inicie?|start|rode?)\s+(?:o|a|the)?\s*(\w+)",
    ]
    
    NEW_DOC_PATTERNS = [
        r"(?:crie?|create?|novo|new)\s+(?:um\s+)?(?:novo\s+)?(?:documento|document|arquivo|file)",
    ]
    
    DRAW_PATTERNS = {
        "circle": [r"desenhe?\s+(?:um\s+)?(?:circulo|círculo|circle)", r"crie?\s+(?:um\s+)?(?:circulo|círculo|circle)"],
        "ellipse": [r"desenhe?\s+(?:uma?\s+)?(?:elipse|ellipse|oval)"],
        "rectangle": [r"desenhe?\s+(?:um\s+)?(?:quadrado|retângulo|retangulo|rectangle|square)", r"crie?\s+(?:um\s+)?(?:quadrado|retângulo|rectangle|square)"],
        "polygon": [r"desenhe?\s+(?:um\s+)?(?:polígono|poligono|polygon)"],
        "star": [r"desenhe?\s+(?:uma?\s+)?(?:estrela|star)"],
        "text": [r"(?:escreva?|digite?|write|type)\s+(?:um\s+)?(?:texto|text)"],
    }
    
    def decompose(self, goal: str) -> List[SubTask]:
        """Decompose a goal into subtasks."""
        goal_lower = goal.lower().strip()
        subtasks = []
        
        logger.info("decomposing_goal", goal=goal_lower)
        
        # Step 1: Detect app to open
        app_name = self._extract_app_name(goal_lower)
        if app_name:
            subtasks.append(SubTask(
                action="open_app",
                params={"app_name": app_name, "wait_time": 4.0},
                description=f"Open {app_name}",
                wait_after=4.0
            ))
        
        # Step 2: Detect new document
        if self._has_new_document(goal_lower):
            subtasks.append(SubTask(
                action="new_document",
                params={},
                description="New document (Ctrl+N)",
                wait_after=1.5
            ))
            # Wait for dialog and press Enter
            subtasks.append(SubTask(
                action="press_keys",
                params={"keys": ["enter"]},
                description="Confirm new document dialog",
                wait_after=2.0
            ))
        
        # Step 3: Detect drawing commands
        shape = self._extract_shape(goal_lower)
        is_corel = "corel" in goal_lower
        is_photoshop = "photoshop" in goal_lower or "ps" in goal_lower
        
        if shape:
            if is_corel:
                # CorelDRAW: Select tool then draw
                tool_action = self._get_corel_tool(shape)
                if tool_action:
                    subtasks.append(SubTask(
                        action=tool_action,
                        params={},
                        description=f"Select {shape} tool",
                        wait_after=0.5
                    ))
                # Draw the shape
                subtasks.append(SubTask(
                    action="draw_shape",
                    params={"shape": shape, "app": "coreldraw"},
                    description=f"Draw {shape}",
                    requires_vision=True,
                    wait_after=1.0
                ))
            elif is_photoshop:
                subtasks.append(SubTask(
                    action="ps_shape",
                    params={},
                    description="Select shape tool",
                    wait_after=0.5
                ))
                subtasks.append(SubTask(
                    action="draw_shape",
                    params={"shape": shape, "app": "photoshop"},
                    description=f"Draw {shape}",
                    requires_vision=True,
                    wait_after=1.0
                ))
        
        logger.info("decomposition_complete", subtasks=[s.description for s in subtasks])
        return subtasks
    
    def _extract_app_name(self, goal: str) -> Optional[str]:
        """Extract application name from goal."""
        app_mappings = {
            "coreldraw": "coreldraw",
            "corel draw": "coreldraw",
            "corel": "coreldraw",
            "photoshop": "photoshop",
            "ps": "photoshop",
            "after effects": "after effects",
            "aftereffects": "after effects",
            "ae": "after effects",
            "premiere": "premiere",
            "pr": "premiere",
            "cinema 4d": "cinema 4d",
            "cinema4d": "cinema 4d",
            "c4d": "cinema 4d",
            "notepad": "notepad",
            "bloco de notas": "notepad",
            "calculator": "calculator",
            "calculadora": "calculator",
            "calc": "calculator",
            "chrome": "chrome",
            "paint": "paint",
            "word": "word",
            "excel": "excel",
        }
        
        for keyword, app in app_mappings.items():
            if keyword in goal:
                return app
        
        # Try regex pattern
        for pattern in self.OPEN_APP_PATTERNS:
            match = re.search(pattern, goal)
            if match:
                extracted = match.group(1)
                skip_words = ["um", "uma", "novo", "new", "documento", "document", "o", "a"]
                if extracted not in skip_words:
                    return extracted
        
        return None
    
    def _has_new_document(self, goal: str) -> bool:
        """Check if goal mentions creating a new document."""
        for pattern in self.NEW_DOC_PATTERNS:
            if re.search(pattern, goal):
                return True
        return False
    
    def _extract_shape(self, goal: str) -> Optional[str]:
        """Extract shape to draw from goal."""
        for shape, patterns in self.DRAW_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, goal):
                    return shape
        return None
    
    def _get_corel_tool(self, shape: str) -> Optional[str]:
        """Get CorelDRAW tool action for a shape."""
        tool_map = {
            "circle": "corel_ellipse",
            "ellipse": "corel_ellipse",
            "rectangle": "corel_rectangle",
            "polygon": "corel_polygon",
            "star": "corel_star",
            "text": "corel_text",
        }
        return tool_map.get(shape)


class SmartExecutor:
    """Executes subtasks using routines and vision."""
    
    def __init__(self, routines: Any, actuation: Any, vision: Any = None):
        self.routines = routines
        self.actuation = actuation
        self.vision = vision
        self._on_thought = None
    
    def set_thought_callback(self, callback):
        self._on_thought = callback
    
    def _emit(self, msg: str):
        if self._on_thought:
            self._on_thought(msg)
        logger.info("executor_thought", message=msg)
    
    async def execute_subtasks(self, subtasks: List[SubTask]) -> bool:
        """Execute a list of subtasks in order."""
        total = len(subtasks)
        
        for i, task in enumerate(subtasks, 1):
            self._emit(f"📌 Step {i}/{total}: {task.description}")
            
            try:
                if task.requires_vision:
                    success = await self._execute_with_vision(task)
                else:
                    success = await self._execute_routine(task)
                
                if not success:
                    self._emit(f"⚠️ Step {i} may have failed, continuing...")
                
                if task.wait_after > 0:
                    await asyncio.sleep(task.wait_after)
                    
            except Exception as e:
                logger.error("subtask_failed", task=task.action, error=str(e))
                self._emit(f"❌ Error in step {i}: {str(e)}")
        
        self._emit("✅ All steps completed!")
        return True
    
    async def _execute_routine(self, task: SubTask) -> bool:
        """Execute a task using routines."""
        action = task.action
        params = task.params
        
        if action == "open_app":
            return await self.routines.open_app(
                params.get("app_name", "app"),
                wait_time=params.get("wait_time", 2.0)
            )
        
        elif action == "new_document":
            return await self.routines.new_document()
        
        elif action == "save":
            return await self.routines.save()
        
        elif action == "close_window":
            return await self.routines.close_window()
        
        elif action == "press_keys":
            keys = params.get("keys", [])
            return await self.routines.press_keys(*keys)
        
        # CorelDRAW tools
        elif action == "corel_ellipse":
            return await self.routines.corel_ellipse()
        
        elif action == "corel_rectangle":
            return await self.routines.corel_rectangle()
        
        elif action == "corel_polygon":
            return await self.routines.corel_polygon()
        
        elif action == "corel_star":
            return await self.routines.corel_star()
        
        elif action == "corel_text":
            return await self.routines.corel_text()
        
        elif action == "corel_pick_tool":
            return await self.routines.corel_pick_tool()
        
        # Photoshop tools
        elif action == "ps_shape":
            return await self.routines.ps_shape()
        
        elif action == "ps_brush":
            return await self.routines.ps_brush()
        
        else:
            # Try dynamic call
            if hasattr(self.routines, action):
                method = getattr(self.routines, action)
                return await method(**params) if params else await method()
            
            logger.warning("unknown_routine", action=action)
            return False
    
    async def _execute_with_vision(self, task: SubTask) -> bool:
        """Execute a task that requires vision/mouse."""
        action = task.action
        params = task.params
        
        if action == "draw_shape":
            return await self._draw_shape(
                params.get("shape", "rectangle"),
                params.get("app", "coreldraw")
            )
        
        return False
    
    async def _draw_shape(self, shape: str, app: str) -> bool:
        """Draw a shape using mouse drag."""
        try:
            import pyautogui
            
            screen_w, screen_h = pyautogui.size()
            
            # Calculate drawing area (center of screen)
            center_x = screen_w // 2
            center_y = screen_h // 2
            size = 150  # pixels
            
            start_x = center_x - size
            start_y = center_y - size
            end_x = center_x + size
            end_y = center_y + size
            
            self._emit(f"🎨 Drawing {shape} at center...")
            
            if self.actuation:
                keyboard = self.actuation.keyboard
                mouse = self.actuation.mouse
                
                # For circle (perfect shape) in CorelDRAW, hold Ctrl
                # For square in CorelDRAW, hold Ctrl
                hold_ctrl = shape in ["circle", "square"] and app == "coreldraw"
                
                if hold_ctrl:
                    await keyboard.key_down("ctrl")
                    await asyncio.sleep(0.1)
                
                # Move to start, then drag
                await mouse.move(start_x, start_y)
                await asyncio.sleep(0.2)
                await mouse.drag(start_x, start_y, end_x, end_y, duration=0.5)
                
                if hold_ctrl:
                    await keyboard.key_up("ctrl")
                
                await asyncio.sleep(0.3)
                
                # Click to deselect
                await self.routines.corel_pick_tool()
                await asyncio.sleep(0.2)
                await mouse.click(center_x + 200, center_y + 200)
                
                self._emit(f"✅ {shape} drawn successfully!")
                return True
            
            return False
            
        except Exception as e:
            logger.error("draw_shape_failed", shape=shape, error=str(e))
            self._emit(f"❌ Failed to draw {shape}: {str(e)}")
            return False


# Singleton
_decomposer: TaskDecomposer | None = None

def get_decomposer() -> TaskDecomposer:
    global _decomposer
    if _decomposer is None:
        _decomposer = TaskDecomposer()
    return _decomposer
