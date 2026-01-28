"""
ONI v2.0 - Semantic Locator
Intelligent UI element location using fuzzy and semantic matching
"""
from dataclasses import dataclass
from typing import Any, Literal, List, Dict, Set, Optional, Union

import numpy as np
import structlog
from rapidfuzz import fuzz, process

from app.core.config import settings
from app.core.exceptions import ElementNotFoundError
from app.infrastructure.vision.ocr.tesseract import OCRBox

logger = structlog.get_logger()

# Constants
DEFAULT_FUZZY_THRESHOLD = 0.7
MIN_THRESHOLD = 0.0
MAX_THRESHOLD = 1.0
DEFAULT_MATCH_CUTOFF = 50  # For rapidfuzz


@dataclass
class LocatorMatch:
    """Match result from semantic locator."""
    text: str
    confidence: float
    x: int
    y: int
    width: int
    height: int
    center_x: int
    center_y: int
    match_type: str
    original_query: str
    
    @property
    def center(self) -> tuple[int, int]:
        """Get center coordinates."""
        return (self.center_x, self.center_y)
    
    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """Get bounding box (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)


class SemanticLocator:
    """
    Intelligent UI element locator.
    
    Strategies (cascading):
    1. Exact Match - Case-insensitive exact match
    2. Fuzzy Match - Levenshtein, Jaro-Winkler, etc.
    3. Semantic Match - Synonym/translation awareness
    4. Contextual Match - "button to the right of X"
    
    Features:
    - Multi-language support
    - Abbreviation expansion
    - Synonym awareness
    """
    
    def __init__(self, fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD) -> None:
        """
        Initialize semantic locator.
        
        Args:
            fuzzy_threshold: Minimum fuzzy match score (0-1)
            
        Raises:
            ValueError: If threshold is out of range
        """
        if not MIN_THRESHOLD <= fuzzy_threshold <= MAX_THRESHOLD:
            raise ValueError(
                f"fuzzy_threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}, "
                f"got {fuzzy_threshold}"
            )
        
        self._fuzzy_threshold = fuzzy_threshold
        self._synonyms = self._build_synonym_dict()
        self._abbreviations = self._build_abbreviation_dict()
    
    def _build_synonym_dict(self) -> Dict[str, List[str]]:
        """Build synonym dictionary for common UI terms."""
        return {
            "save": ["salvar", "gravar", "guardar", "save as"],
            "open": ["abrir", "open file", "carregar"],
            "close": ["fechar", "sair", "exit", "quit"],
            "cancel": ["cancelar", "abort", "abortar"],
            "ok": ["confirmar", "aceitar", "confirm", "accept"],
            "yes": ["sim", "si"],
            "no": ["não", "nao"],
            "file": ["arquivo", "ficheiro"],
            "edit": ["editar", "edição"],
            "view": ["visualizar", "ver", "exibir"],
            "help": ["ajuda", "socorro"],
            "search": ["pesquisar", "buscar", "procurar"],
            "settings": ["configurações", "opções", "options", "preferences"],
            "next": ["próximo", "seguinte", "avançar"],
            "back": ["voltar", "anterior", "previous"],
            "new": ["novo", "criar", "create"],
            "delete": ["excluir", "apagar", "remover", "remove"],
            "copy": ["copiar"],
            "paste": ["colar"],
            "cut": ["recortar"],
            "undo": ["desfazer"],
            "redo": ["refazer"],
        }
    
    def _build_abbreviation_dict(self) -> Dict[str, str]:
        """Build abbreviation expansion dictionary."""
        return {
            "Arq.": "Arquivo",
            "Ed.": "Editar",
            "Vis.": "Visualizar",
            "Config.": "Configurações",
            "Pref.": "Preferências",
        }
    
    def find(
        self,
        query: str,
        elements: Union[List[OCRBox], List[Dict[str, Any]]],
        strategy: Literal["auto", "exact", "fuzzy", "semantic"] = "auto",
    ) -> Optional[LocatorMatch]:
        """
        Find element matching query.
        
        Args:
            query: Text to find
            elements: List of OCR boxes or dicts with text and bounds
            strategy: Matching strategy
            
        Returns:
            Best match or None
        """
        if not query or not query.strip():
            logger.warning("empty_query_provided")
            return None
        
        if not elements:
            return None
        
        normalized = self._normalize_elements(elements)
        
        if strategy in ("exact", "auto"):
            match = self._exact_match(query, normalized)
            if match or strategy == "exact":
                return match
        
        if strategy in ("fuzzy", "auto"):
            match = self._fuzzy_match(query, normalized)
            if match or strategy == "fuzzy":
                return match
        
        if strategy in ("semantic", "auto"):
            return self._semantic_match(query, normalized)
        
        return None
    
    def find_all(
        self,
        query: str,
        elements: Union[List[OCRBox], List[Dict[str, Any]]],
        threshold: Optional[float] = None,
    ) -> List[LocatorMatch]:
        """
        Find all elements matching query.
        
        Args:
            query: Text to find
            elements: OCR results
            threshold: Minimum match score (uses fuzzy_threshold if None)
            
        Returns:
            All matching elements sorted by confidence (descending)
        """
        if not query or not query.strip():
            return []
        
        threshold = threshold if threshold is not None else self._fuzzy_threshold
        normalized = self._normalize_elements(elements)
        
        matches = []
        query_lower = query.lower().strip()
        
        for elem in normalized:
            text_lower = elem["text"].lower().strip()
            
            # Calculate match score
            if text_lower == query_lower:
                score = 1.0
                match_type = "exact"
            else:
                score = fuzz.ratio(query_lower, text_lower) / 100.0
                match_type = "fuzzy"
            
            if score >= threshold:
                matches.append(self._create_match(elem, score, match_type, query))
        
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def _normalize_elements(
        self,
        elements: Union[List[OCRBox], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Normalize elements to common dict format."""
        normalized = []
        
        for elem in elements:
            if isinstance(elem, OCRBox):
                normalized.append({
                    "text": elem.text,
                    "x": elem.x,
                    "y": elem.y,
                    "width": elem.width,
                    "height": elem.height,
                    "confidence": elem.confidence,
                })
            elif isinstance(elem, dict):
                # Validate required keys
                if "text" in elem and "x" in elem and "y" in elem:
                    normalized.append({
                        "text": elem["text"],
                        "x": elem["x"],
                        "y": elem["y"],
                        "width": elem.get("width", 0),
                        "height": elem.get("height", 0),
                        "confidence": elem.get("confidence", 1.0),
                    })
        
        return normalized
    
    def _exact_match(
        self,
        query: str,
        elements: List[Dict[str, Any]],
    ) -> Optional[LocatorMatch]:
        """Find exact case-insensitive match."""
        query_lower = query.lower().strip()
        
        for elem in elements:
            if elem["text"].lower().strip() == query_lower:
                return self._create_match(elem, 1.0, "exact", query)
        
        return None
    
    def _fuzzy_match(
        self,
        query: str,
        elements: List[Dict[str, Any]],
    ) -> Optional[LocatorMatch]:
        """Find fuzzy match using multiple algorithms."""
        texts = [e["text"] for e in elements]
        
        if not texts:
            return None
        
        try:
            result = process.extractOne(
                query,
                texts,
                scorer=fuzz.WRatio,
                score_cutoff=self._fuzzy_threshold * 100,
            )
            
            if result:
                matched_text, score, index = result
                return self._create_match(
                    elements[index],
                    score / 100.0,
                    "fuzzy",
                    query,
                )
        except Exception as e:
            logger.error("fuzzy_match_error", error=str(e))
        
        return None
    
    def _semantic_match(
        self,
        query: str,
        elements: List[Dict[str, Any]],
    ) -> Optional[LocatorMatch]:
        """Find match using synonyms and semantic similarity."""
        query_lower = query.lower().strip()
        synonyms = self._get_synonyms(query_lower)
        
        for elem in elements:
            text_lower = elem["text"].lower().strip()
            
            # Check synonym match
            if text_lower in synonyms:
                return self._create_match(elem, 0.85, "semantic", query)
            
            # Check expanded abbreviations
            expanded = self._expand_abbreviation(elem["text"])
            if expanded.lower() == query_lower:
                return self._create_match(elem, 0.9, "semantic", query)
        
        return None
    
    def _get_synonyms(self, word: str) -> Set[str]:
        """Get synonyms for a word."""
        synonyms = {word}
        
        for key, values in self._synonyms.items():
            if word == key or word in values:
                synonyms.add(key)
                synonyms.update(values)
        
        return synonyms
    
    def _expand_abbreviation(self, text: str) -> str:
        """Expand known abbreviations in text."""
        for abbr, full in self._abbreviations.items():
            if abbr in text:
                text = text.replace(abbr, full)
        return text
    
    def _create_match(
        self,
        elem: Dict[str, Any],
        confidence: float,
        match_type: str,
        query: str,
    ) -> LocatorMatch:
        """Create a LocatorMatch from element dict."""
        return LocatorMatch(
            text=elem["text"],
            confidence=confidence,
            x=elem["x"],
            y=elem["y"],
            width=elem["width"],
            height=elem["height"],
            center_x=elem["x"] + elem["width"] // 2,
            center_y=elem["y"] + elem["height"] // 2,
            match_type=match_type,
            original_query=query,
        )
    
    # =========================================================================
    # Contextual Matching
    # =========================================================================
    
    def find_relative(
        self,
        anchor_query: str,
        direction: Literal["above", "below", "left", "right"],
        elements: Union[List[OCRBox], List[Dict[str, Any]]],
        target_query: Optional[str] = None,
    ) -> Optional[LocatorMatch]:
        """
        Find element relative to anchor.
        
        Args:
            anchor_query: Text of anchor element
            direction: Direction from anchor
            elements: OCR results
            target_query: Optional text filter for target
            
        Returns:
            Nearest element in given direction
        """
        normalized = self._normalize_elements(elements)
        
        # Find anchor
        anchor = self.find(anchor_query, normalized)
        if not anchor:
            logger.warning("anchor_not_found", query=anchor_query)
            return None
        
        # Filter elements by direction
        candidates = []
        for elem in normalized:
            if not self._is_in_direction(anchor, elem, direction):
                continue
            
            if target_query:
                # Check if element matches target query
                match_score = fuzz.ratio(
                    target_query.lower(), 
                    elem["text"].lower()
                )
                if match_score < DEFAULT_MATCH_CUTOFF:
                    continue
            
            candidates.append(elem)
        
        if not candidates:
            return None
        
        # Find nearest
        nearest = min(candidates, key=lambda e: self._distance(anchor, e))
        return self._create_match(
            nearest, 
            0.8, 
            "contextual", 
            f"{anchor_query} -> {direction}"
        )
    
    def _is_in_direction(
        self,
        anchor: LocatorMatch,
        elem: Dict[str, Any],
        direction: str,
    ) -> bool:
        """Check if element is in given direction from anchor."""
        elem_cx = elem["x"] + elem["width"] // 2
        elem_cy = elem["y"] + elem["height"] // 2
        
        direction_map = {
            "above": elem_cy < anchor.center_y,
            "below": elem_cy > anchor.center_y,
            "left": elem_cx < anchor.center_x,
            "right": elem_cx > anchor.center_x,
        }
        
        return direction_map.get(direction, False)
    
    def _distance(self, anchor: LocatorMatch, elem: Dict[str, Any]) -> float:
        """Calculate Euclidean distance between anchor and element."""
        elem_cx = elem["x"] + elem["width"] // 2
        elem_cy = elem["y"] + elem["height"] // 2
        
        dx = anchor.center_x - elem_cx
        dy = anchor.center_y - elem_cy
        
        return (dx * dx + dy * dy) ** 0.5
