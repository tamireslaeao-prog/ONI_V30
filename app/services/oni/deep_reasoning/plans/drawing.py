"""
ONI Deep Reasoning - Drawing Plans Library
Contains hardcoded plans for common drawing tasks.
"""
from typing import Dict, Any
from ..types import TaskDomain, TaskAnalysis, QualityCriteria, Subtask


def create_christmas_tree_plan(center_x: int, center_y: int, canvas_bounds: Dict[str, Any]) -> TaskAnalysis:
    """Plano profissional para árvore de Natal."""
    subtasks = [
        Subtask(id="layer_1", description="Desenhar camada base", action_type="draw_triangle",
                parameters={"apex": {"x": center_x, "y": center_y - 80}, "color": "#228B22"}),
        Subtask(id="layer_2", description="Desenhar camada média", action_type="draw_triangle",
                parameters={"apex": {"x": center_x, "y": center_y - 120}, "color": "#2E8B57"}),
        Subtask(id="layer_3", description="Desenhar camada topo", action_type="draw_triangle",
                parameters={"apex": {"x": center_x, "y": center_y - 150}, "color": "#006400"}),
        Subtask(id="trunk", description="Desenhar tronco", action_type="draw_rectangle",
                parameters={"x": center_x - 20, "y": center_y + 60, "color": "#8B4513"}),
        Subtask(id="star", description="Desenhar estrela", action_type="draw_star",
                parameters={"center": {"x": center_x, "y": center_y - 155}, "color": "#FFD700"}),
    ]
    return TaskAnalysis(
        original_task="Desenhar árvore de Natal", domain=TaskDomain.DRAWING,
        goal_interpretation="Árvore de Natal profissional com 3 camadas, tronco e estrela",
        quality_criteria=[QualityCriteria("Centralização", "position", center_x)],
        component_breakdown=["Copa 3 camadas", "Tronco", "Estrela"],
        execution_strategy="Baixo para cima", estimated_steps=len(subtasks), subtasks=subtasks
    )


def create_circle_plan(center_x: int, center_y: int, canvas_bounds: Dict[str, Any]) -> TaskAnalysis:
    """Plano para círculo perfeito."""
    subtasks = [
        Subtask(id="select_tool", description="Selecionar Ellipse", action_type="hotkey", parameters={"keys": "F7"}),
        Subtask(id="draw_circle", description="Desenhar círculo", action_type="drag",
                parameters={"from": {"x": center_x - 80, "y": center_y - 80}, "to": {"x": center_x + 80, "y": center_y + 80}, "hold_ctrl": True}),
    ]
    return TaskAnalysis(
        original_task="Desenhar círculo", domain=TaskDomain.DRAWING,
        goal_interpretation="Círculo perfeito centralizado",
        quality_criteria=[QualityCriteria("Circularidade", "aspect_ratio", 1.0)],
        component_breakdown=["Círculo"], execution_strategy="F7 + Ctrl+Drag", estimated_steps=2, subtasks=subtasks
    )


def create_square_plan(center_x: int, center_y: int, canvas_bounds: Dict[str, Any]) -> TaskAnalysis:
    """Plano para quadrado."""
    half = 60
    subtasks = [
        Subtask(id="select_tool", description="Selecionar Rectangle", action_type="hotkey", parameters={"keys": "F6"}),
        Subtask(id="draw_square", description="Desenhar quadrado", action_type="drag",
                parameters={"from": {"x": center_x - half, "y": center_y - half}, "to": {"x": center_x + half, "y": center_y + half}, "hold_ctrl": True}),
    ]
    return TaskAnalysis(
        original_task="Desenhar quadrado", domain=TaskDomain.DRAWING,
        goal_interpretation="Quadrado perfeito centralizado",
        quality_criteria=[QualityCriteria("Simetria", "aspect_ratio", 1.0)],
        component_breakdown=["Quadrado"], execution_strategy="F6 + Ctrl+Drag", estimated_steps=2, subtasks=subtasks
    )


def create_house_plan(center_x: int, center_y: int, canvas_bounds: Dict[str, Any]) -> TaskAnalysis:
    """Plano para desenhar casa."""
    subtasks = [
        Subtask(id="body", description="Corpo da casa", action_type="draw_rectangle",
                parameters={"x": center_x - 80, "y": center_y - 20, "width": 160, "height": 120, "color": "#DEB887"}),
        Subtask(id="roof", description="Telhado", action_type="draw_triangle",
                parameters={"apex": {"x": center_x, "y": center_y - 100}, "color": "#8B0000"}),
        Subtask(id="door", description="Porta", action_type="draw_rectangle",
                parameters={"x": center_x - 20, "y": center_y + 40, "color": "#8B4513"}),
    ]
    return TaskAnalysis(
        original_task="Desenhar casa", domain=TaskDomain.DRAWING,
        goal_interpretation="Casa com telhado e porta",
        quality_criteria=[QualityCriteria("Componentes", "count", 3)],
        component_breakdown=["Corpo", "Telhado", "Porta"], execution_strategy="Sequencial", estimated_steps=3, subtasks=subtasks
    )


def create_heart_plan(center_x: int, center_y: int, canvas_bounds: Dict[str, Any]) -> TaskAnalysis:
    """Plano para coração."""
    subtasks = [
        Subtask(id="left_lobe", description="Lóbulo esquerdo", action_type="draw_arc",
                parameters={"center": {"x": center_x - 40, "y": center_y - 20}, "color": "#FF1493"}),
        Subtask(id="right_lobe", description="Lóbulo direito", action_type="draw_arc",
                parameters={"center": {"x": center_x + 40, "y": center_y - 20}, "color": "#FF1493"}),
        Subtask(id="tip", description="Ponta", action_type="draw_triangle",
                parameters={"apex": {"x": center_x, "y": center_y + 80}, "color": "#FF1493"}),
    ]
    return TaskAnalysis(
        original_task="Desenhar coração", domain=TaskDomain.DRAWING,
        goal_interpretation="Coração simétrico rosa",
        quality_criteria=[QualityCriteria("Simetria", "symmetry", True)],
        component_breakdown=["2 lóbulos", "Ponta"], execution_strategy="Lóbulos + Triângulo", estimated_steps=3, subtasks=subtasks
    )
