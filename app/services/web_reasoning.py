"""
ONI Web-Based Reasoning Service v1.0
Sistema de raciocínio que consulta a web para gerar planos dinâmicos.

Fluxo:
1. Recebe tarefa (ex: "Desenhe uma Ferrari")
2. Busca tutorial na web
3. Extrai passos do tutorial
4. Converte para ações ONI executáveis
"""

import re
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TutorialStep:
    """Um passo extraído de um tutorial."""
    step_number: int
    description: str
    action_hint: str = ""  # e.g., "draw", "add", "connect"
    details: str = ""


@dataclass  
class WebSearchResult:
    """Resultado de uma busca web."""
    query: str
    steps: List[TutorialStep]
    source: str = "web_search"
    confidence: float = 0.0


class WebReasoningService:
    """
    Serviço que usa consulta web para gerar planos de execução.
    
    Features:
    - Busca tutoriais "how to draw X step by step"
    - Extrai passos numerados
    - Converte para ações ONI
    """
    
    # Cache de buscas recentes
    _cache: Dict[str, WebSearchResult] = {}
    
    @classmethod
    async def search_tutorial(cls, task: str, domain: str = "drawing") -> WebSearchResult:
        """
        Busca tutorial na web para a tarefa.
        
        Args:
            task: Descrição da tarefa (ex: "desenhe uma Ferrari")
            domain: Domínio da tarefa (drawing, ui, etc.)
            
        Returns:
            WebSearchResult com passos extraídos
        """
        # Gerar query de busca
        query = cls._generate_search_query(task, domain)
        
        # Verificar cache
        if query in cls._cache:
            logger.info("web_reasoning_cache_hit", query=query)
            return cls._cache[query]
        
        logger.info("web_reasoning_search", query=query)
        
        # Simular busca web (em produção, usar API real)
        # Por enquanto, usar heurísticas baseadas em keywords
        steps = await cls._extract_steps_from_knowledge(task, domain)
        
        result = WebSearchResult(
            query=query,
            steps=steps,
            source="knowledge_base",
            confidence=0.8 if steps else 0.0
        )
        
        # Cachear resultado
        cls._cache[query] = result
        
        return result
    
    @classmethod
    def _generate_search_query(cls, task: str, domain: str) -> str:
        """Gera query de busca otimizada."""
        # Extrair objeto principal da tarefa
        task_lower = task.lower()
        
        # Remover verbos comuns
        for verb in ["desenhe", "draw", "pintar", "paint", "crie", "create", "faça", "make"]:
            task_lower = task_lower.replace(verb, "").strip()
        
        # Remover artigos
        for article in ["uma", "um", "a", "the", "an"]:
            task_lower = re.sub(rf"\b{article}\b", "", task_lower).strip()
        
        object_name = task_lower.strip()
        
        if domain == "drawing":
            return f"how to draw {object_name} step by step simple"
        else:
            return f"how to {task} tutorial steps"
    
    @classmethod
    async def _extract_steps_from_knowledge(
        cls, 
        task: str, 
        domain: str
    ) -> List[TutorialStep]:
        """
        Extrai passos usando conhecimento embutido.
        Funciona como fallback quando busca web não disponível.
        
        Para DESENHOS, usa decomposição genérica baseada em:
        - Formas básicas (retângulos, elipses, linhas)
        - Proporções padrão
        - Ordem de construção (base → detalhes)
        """
        task_lower = task.lower()
        
        # Detectar tipo de objeto para desenho
        if domain == "drawing":
            return await cls._generate_drawing_steps(task_lower)
        else:
            return []
    
    @classmethod
    async def _generate_drawing_steps(cls, task: str) -> List[TutorialStep]:
        """
        Gera passos genéricos para qualquer desenho.
        
        Estratégia: Decompor em formas básicas universais.
        """
        steps = []
        
        # Identificar categoria do objeto
        vehicle_keywords = ["carro", "car", "ferrari", "lamborghini", "truck", "caminhão", "moto", "bike"]
        animal_keywords = ["cachorro", "dog", "gato", "cat", "pássaro", "bird", "peixe", "fish"]
        person_keywords = ["pessoa", "person", "face", "rosto", "corpo", "body"]
        building_keywords = ["casa", "house", "prédio", "building", "castelo", "castle"]
        nature_keywords = ["árvore", "tree", "flor", "flower", "sol", "sun", "nuvem", "cloud"]
        
        if any(kw in task for kw in vehicle_keywords):
            steps = cls._get_vehicle_steps(task)
        elif any(kw in task for kw in animal_keywords):
            steps = cls._get_animal_steps(task)
        elif any(kw in task for kw in person_keywords):
            steps = cls._get_person_steps(task)
        elif any(kw in task for kw in building_keywords):
            steps = cls._get_building_steps(task)
        elif any(kw in task for kw in nature_keywords):
            steps = cls._get_nature_steps(task)
        else:
            # Decomposição genérica
            steps = cls._get_generic_steps(task)
        
        return steps
    
    @classmethod
    def _get_vehicle_steps(cls, task: str) -> List[TutorialStep]:
        """Passos para desenhar veículos (carro, Ferrari, etc.)."""
        
        is_sports_car = any(kw in task for kw in ["ferrari", "lamborghini", "sports", "esportivo"])
        
        if is_sports_car:
            return [
                TutorialStep(1, "Desenhar retângulo baixo e largo para o corpo principal", "draw_rectangle", 
                           "Proporção 4:1 (largura:altura), cor vermelha"),
                TutorialStep(2, "Adicionar inclinação do capô na frente", "draw_line",
                           "Linha diagonal descendo da esquerda"),
                TutorialStep(3, "Desenhar para-brisa inclinado", "draw_trapezoid",
                           "Trapézio fino no topo"),
                TutorialStep(4, "Adicionar traseira aerodinâmica", "draw_line",
                           "Curva suave descendo atrás"),
                TutorialStep(5, "Desenhar roda dianteira", "draw_circle",
                           "Círculo preto com centro cinza, posição 1/4 da frente"),
                TutorialStep(6, "Desenhar roda traseira", "draw_circle",
                           "Círculo preto com centro cinza, posição 3/4 da frente"),
                TutorialStep(7, "Adicionar farol dianteiro", "draw_ellipse",
                           "Elipse amarela pequena na frente"),
                TutorialStep(8, "Adicionar lanterna traseira", "draw_rectangle",
                           "Retângulo vermelho escuro atrás"),
                TutorialStep(9, "Desenhar grade frontal", "draw_lines",
                           "Linhas horizontais na frente"),
                TutorialStep(10, "Adicionar espelho retrovisor", "draw_small_shape",
                            "Pequeno retângulo saindo do topo"),
            ]
        else:
            # Carro genérico
            return [
                TutorialStep(1, "Desenhar retângulo para corpo do carro", "draw_rectangle",
                           "Proporção 3:1"),
                TutorialStep(2, "Adicionar teto/cabine", "draw_trapezoid",
                           "Trapézio no topo central"),
                TutorialStep(3, "Desenhar rodas", "draw_circles",
                           "2 círculos pretos embaixo"),
                TutorialStep(4, "Adicionar janelas", "draw_rectangles",
                           "Retângulos azuis na cabine"),
                TutorialStep(5, "Adicionar faróis e lanternas", "draw_small_shapes",
                           "Pequenos detalhes nas extremidades"),
            ]
    
    @classmethod
    def _get_animal_steps(cls, task: str) -> List[TutorialStep]:
        """Passos para desenhar animais."""
        return [
            TutorialStep(1, "Desenhar corpo (elipse principal)", "draw_ellipse",
                        "Forma oval horizontal"),
            TutorialStep(2, "Adicionar cabeça", "draw_circle",
                        "Círculo conectado ao corpo"),
            TutorialStep(3, "Desenhar pernas/patas", "draw_lines",
                        "4 linhas ou formas apropriadas"),
            TutorialStep(4, "Adicionar orelhas", "draw_shapes",
                        "Formas no topo da cabeça"),
            TutorialStep(5, "Desenhar rabo", "draw_curve",
                        "Curva saindo do corpo"),
            TutorialStep(6, "Adicionar olhos e focinho", "draw_details",
                        "Pequenos círculos e formas no rosto"),
        ]
    
    @classmethod
    def _get_person_steps(cls, task: str) -> List[TutorialStep]:
        """Passos para desenhar pessoas."""
        return [
            TutorialStep(1, "Desenhar cabeça (círculo)", "draw_circle",
                        "Círculo no topo"),
            TutorialStep(2, "Desenhar corpo/tronco", "draw_rectangle",
                        "Retângulo ou oval abaixo da cabeça"),
            TutorialStep(3, "Adicionar braços", "draw_lines",
                        "2 linhas saindo dos lados do tronco"),
            TutorialStep(4, "Adicionar pernas", "draw_lines",
                        "2 linhas saindo da base do tronco"),
            TutorialStep(5, "Desenhar rosto", "draw_details",
                        "Olhos, nariz, boca"),
            TutorialStep(6, "Adicionar cabelo", "draw_curves",
                        "Linhas ou forma no topo da cabeça"),
        ]
    
    @classmethod
    def _get_building_steps(cls, task: str) -> List[TutorialStep]:
        """Passos para desenhar construções."""
        return [
            TutorialStep(1, "Desenhar base/corpo principal", "draw_rectangle",
                        "Retângulo grande vertical"),
            TutorialStep(2, "Adicionar teto", "draw_triangle",
                        "Triângulo no topo ou retângulo"),
            TutorialStep(3, "Desenhar porta", "draw_rectangle",
                        "Retângulo na base central"),
            TutorialStep(4, "Adicionar janelas", "draw_rectangles",
                        "Múltiplos retângulos pequenos"),
            TutorialStep(5, "Adicionar detalhes", "draw_details",
                        "Chaminé, decorações, etc."),
        ]
    
    @classmethod
    def _get_nature_steps(cls, task: str) -> List[TutorialStep]:
        """Passos para desenhar elementos naturais."""
        return [
            TutorialStep(1, "Desenhar forma principal", "draw_shape",
                        "Forma base do elemento"),
            TutorialStep(2, "Adicionar estrutura de suporte", "draw_line",
                        "Tronco, caule, etc."),
            TutorialStep(3, "Adicionar detalhes maiores", "draw_shapes",
                        "Folhas, pétalas, raios"),
            TutorialStep(4, "Adicionar detalhes menores", "draw_details",
                        "Texturas, sombras"),
        ]
    
    @classmethod
    def _get_generic_steps(cls, task: str) -> List[TutorialStep]:
        """Passos genéricos para qualquer desenho."""
        return [
            TutorialStep(1, "Analisar referência mental do objeto", "think",
                        "Identificar formas básicas que compõem o objeto"),
            TutorialStep(2, "Desenhar forma base principal", "draw_shape",
                        "A maior forma que define o objeto"),
            TutorialStep(3, "Adicionar formas secundárias", "draw_shapes",
                        "Partes menores conectadas à forma principal"),
            TutorialStep(4, "Adicionar detalhes estruturais", "draw_lines",
                        "Linhas que definem a estrutura"),
            TutorialStep(5, "Adicionar detalhes finais", "draw_details",
                        "Pequenos elementos que completam o desenho"),
        ]
    
    @classmethod
    def convert_to_drawing_actions(
        cls,
        steps: List[TutorialStep],
        center_x: int,
        center_y: int,
        scale: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Converte TutorialSteps em ações de desenho concretas.
        
        Usa coordenadas relativas ao centro do canvas.
        """
        actions = []
        
        # Definir tamanho base do desenho
        base_width = int(300 * scale)
        base_height = int(150 * scale)
        
        for step in steps:
            action = {
                "step_number": step.step_number,
                "description": step.description,
                "action_hint": step.action_hint,
                "details": step.details,
                "type": "brush_stroke",  # Padrão para Photoshop
                "executed": False
            }
            
            # Converter action_hint em coordenadas genéricas
            if "rectangle" in step.action_hint:
                action["coords"] = cls._get_rectangle_coords(
                    step, center_x, center_y, base_width, base_height
                )
            elif "circle" in step.action_hint:
                action["coords"] = cls._get_circle_coords(
                    step, center_x, center_y, base_width, base_height
                )
            elif "line" in step.action_hint:
                action["coords"] = cls._get_line_coords(
                    step, center_x, center_y, base_width, base_height
                )
            else:
                action["coords"] = {
                    "center_x": center_x,
                    "center_y": center_y
                }
            
            actions.append(action)
        
        return actions
    
    @classmethod
    def _get_rectangle_coords(
        cls, step: TutorialStep, cx: int, cy: int, w: int, h: int
    ) -> Dict[str, int]:
        """Calcula coordenadas para retângulo baseado no contexto."""
        
        desc = step.description.lower()
        
        if "corpo" in desc or "principal" in desc or "base" in desc:
            # Corpo principal - ocupa maior parte
            return {
                "x1": cx - w//2, "y1": cy - h//4,
                "x2": cx + w//2, "y2": cy + h//4
            }
        elif "teto" in desc or "cabine" in desc:
            # Teto - menor, no topo
            return {
                "x1": cx - w//4, "y1": cy - h//2,
                "x2": cx + w//4, "y2": cy - h//4
            }
        else:
            # Genérico
            return {
                "x1": cx - w//3, "y1": cy - h//3,
                "x2": cx + w//3, "y2": cy + h//3
            }
    
    @classmethod
    def _get_circle_coords(
        cls, step: TutorialStep, cx: int, cy: int, w: int, h: int
    ) -> Dict[str, int]:
        """Calcula coordenadas para círculo baseado no contexto."""
        
        desc = step.description.lower()
        radius = h // 4
        
        if "dianteira" in desc or "frente" in desc:
            # Roda dianteira
            return {
                "center_x": cx - w//3,
                "center_y": cy + h//4,
                "radius": radius
            }
        elif "traseira" in desc or "atrás" in desc:
            # Roda traseira
            return {
                "center_x": cx + w//3,
                "center_y": cy + h//4,
                "radius": radius
            }
        else:
            return {
                "center_x": cx,
                "center_y": cy,
                "radius": radius
            }
    
    @classmethod
    def _get_line_coords(
        cls, step: TutorialStep, cx: int, cy: int, w: int, h: int
    ) -> Dict[str, int]:
        """Calcula coordenadas para linha baseado no contexto."""
        return {
            "x1": cx - w//4, "y1": cy,
            "x2": cx + w//4, "y2": cy
        }
    
    @classmethod
    def clear_cache(cls):
        """Limpa o cache de buscas."""
        cls._cache.clear()
        logger.info("web_reasoning_cache_cleared")
