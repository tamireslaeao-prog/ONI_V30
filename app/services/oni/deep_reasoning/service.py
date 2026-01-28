"""
ONI Deep Reasoning - Service Orchestrator
"""
import structlog
from typing import Optional, Dict, Any
from .types import TaskDomain, TaskAnalysis, QualityCriteria
from .plans import (
    create_christmas_tree_plan, create_circle_plan, 
    create_square_plan, create_house_plan, create_heart_plan
)

logger = structlog.get_logger(__name__)


class DeepReasoningService:
    """Serviço de Raciocínio Profundo."""
    
    _current_analysis: Optional[TaskAnalysis] = None
    
    @classmethod
    def detect_domain(cls, task: str) -> TaskDomain:
        """Detecta o domínio da tarefa."""
        task_lower = task.lower()
        
        drawing_keywords = ["desenh", "draw", "pintar", "paint", "círculo", "circle", 
                          "quadrado", "square", "linha", "line", "forma", "shape",
                          "árvore", "tree", "logo", "ilustra", "carro", "car"]
        ui_keywords = ["clicar", "click", "abrir", "open", "fechar", "close"]
        web_keywords = ["navegue", "navigate", "site", "página", "page", "url"]
        file_keywords = ["arquivo", "file", "pasta", "folder", "copiar", "copy"]
        
        if any(kw in task_lower for kw in drawing_keywords):
            return TaskDomain.DRAWING
        elif any(kw in task_lower for kw in ui_keywords):
            return TaskDomain.UI_AUTOMATION
        elif any(kw in task_lower for kw in web_keywords):
            return TaskDomain.WEB_NAVIGATION
        elif any(kw in task_lower for kw in file_keywords):
            return TaskDomain.FILE_MANAGEMENT
        else:
            return TaskDomain.GENERAL
    
    @classmethod
    async def analyze_task(cls, task: str, context: Optional[Dict[str, Any]] = None) -> TaskAnalysis:
        """Análise profunda de uma tarefa."""
        context = context or {}
        domain = cls.detect_domain(task)
        
        logger.info("deep_reasoning_started", task=task, domain=domain.value)
        
        if domain == TaskDomain.DRAWING:
            analysis = await cls._analyze_drawing_task(task, context)
        else:
            analysis = await cls._analyze_general_task(task, context)
        
        cls._current_analysis = analysis
        return analysis
    
    @classmethod
    async def _analyze_drawing_task(cls, task: str, context: Dict[str, Any]) -> TaskAnalysis:
        """Análise especializada para tarefas de desenho."""
        canvas_bounds = context.get("canvas_bounds", {})
        center_x = canvas_bounds.get("center_x", 960)
        center_y = canvas_bounds.get("center_y", 540)
        
        task_lower = task.lower()
        
        if "árvore" in task_lower or "tree" in task_lower:
            if "natal" in task_lower or "christmas" in task_lower:
                return create_christmas_tree_plan(center_x, center_y, canvas_bounds)
        
        if "círculo" in task_lower or "circle" in task_lower:
            return create_circle_plan(center_x, center_y, canvas_bounds)
        
        if "quadrado" in task_lower or "square" in task_lower:
            return create_square_plan(center_x, center_y, canvas_bounds)
        
        if "casa" in task_lower or "house" in task_lower:
            return create_house_plan(center_x, center_y, canvas_bounds)
        
        if "coração" in task_lower or "heart" in task_lower:
            return create_heart_plan(center_x, center_y, canvas_bounds)
        
        # Fallback
        return create_circle_plan(center_x, center_y, canvas_bounds)
    
    @classmethod
    async def _analyze_general_task(cls, task: str, context: Dict[str, Any]) -> TaskAnalysis:
        """Análise para tarefas gerais."""
        return TaskAnalysis(
            original_task=task, domain=TaskDomain.GENERAL,
            goal_interpretation=f"Tarefa geral: {task}", quality_criteria=[],
            component_breakdown=["Análise", "Execução", "Verificação"],
            execution_strategy="Sequencial", estimated_steps=3, subtasks=[]
        )
    
    @classmethod
    def get_current_analysis(cls) -> Optional[TaskAnalysis]:
        return cls._current_analysis
    
    @classmethod
    def clear_analysis(cls):
        cls._current_analysis = None
