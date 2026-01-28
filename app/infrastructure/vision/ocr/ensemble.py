"""
ONI v2.0 - OCR Ensemble (ROVER Fusion)
Multi-engine OCR with voting-based fusion
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import structlog
from rapidfuzz import fuzz

from app.core.exceptions import OCRError
from app.infrastructure.vision.ocr.tesseract import OCRBox, OCRResult, TesseractOCR
from app.infrastructure.vision.ocr.easyocr_engine import EasyOCREngine

logger = structlog.get_logger()


@dataclass
class FusedBox:
    """OCR box with multi-engine confidence."""
    text: str
    confidence: float
    x: int
    y: int
    width: int
    height: int
    sources: list[str] = field(default_factory=list)
    votes: int = 1


class OCROrchestrator:
    """
    Multi-engine OCR with ROVER-style fusion.
    
    Features:
    - Parallel execution of multiple OCR engines
    - ROVER (Recognizer Output Voting Error Reduction)
    - Confidence-weighted voting
    - Spatial alignment of results
    """
    
    def __init__(
        self,
        engines: list[str] | None = None,
    ) -> None:
        """
        Initialize OCR orchestrator.
        
        Args:
            engines: List of engines to use ["tesseract", "easyocr"]
        """
        self._engine_names = engines or ["tesseract", "easyocr"]
        self._engines: dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all OCR engines."""
        if self._initialized:
            return
        
        init_tasks = []
        
        if "tesseract" in self._engine_names:
            engine = TesseractOCR()
            self._engines["tesseract"] = engine
            init_tasks.append(engine.initialize())
        
        if "easyocr" in self._engine_names:
            engine = EasyOCREngine()
            self._engines["easyocr"] = engine
            init_tasks.append(engine.initialize())
        
        await asyncio.gather(*init_tasks, return_exceptions=True)
        self._initialized = True
        
        logger.info("ocr_ensemble_initialized", engines=list(self._engines.keys()))
    
    async def extract(
        self,
        image: np.ndarray,
        use_voting: bool = True,
    ) -> OCRResult:
        """
        Extract text using all engines and fuse results.
        
        Args:
            image: Input image
            use_voting: Use ROVER voting (if False, just concatenate)
            
        Returns:
            Fused OCR result
        """
        if not self._initialized:
            await self.initialize()
        
        import time
        start_time = time.perf_counter()
        
        # Run all engines in parallel
        tasks = []
        for name, engine in self._engines.items():
            tasks.append(self._extract_with_engine(name, engine, image))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failures
        valid_results: list[tuple[str, OCRResult]] = []
        for name, result in zip(self._engines.keys(), results):
            if isinstance(result, Exception):
                logger.warning("ocr_engine_failed", engine=name, error=str(result))
            else:
                valid_results.append((name, result))
        
        if not valid_results:
            raise OCRError("All OCR engines failed")
        
        # Fuse results
        if use_voting and len(valid_results) > 1:
            fused = self._rover_fusion(valid_results)
        else:
            # Use best single result
            fused = max(valid_results, key=lambda x: x[1].confidence)[1]
        
        fused.processing_time_ms = (time.perf_counter() - start_time) * 1000
        fused.engine = "ensemble"
        
        return fused
    
    async def _extract_with_engine(
        self,
        name: str,
        engine: Any,
        image: np.ndarray,
    ) -> OCRResult:
        """Extract with a single engine."""
        return await engine.extract(image)
    
    def _rover_fusion(
        self,
        results: list[tuple[str, OCRResult]],
    ) -> OCRResult:
        """
        ROVER-style fusion of multiple OCR results.
        
        Aligns results by position and votes on text.
        """
        # Collect all boxes with source info
        all_boxes: list[tuple[str, OCRBox]] = []
        for engine_name, result in results:
            for box in result.boxes:
                all_boxes.append((engine_name, box))
        
        if not all_boxes:
            return OCRResult(boxes=[], full_text="", confidence=0.0, engine="ensemble")
        
        # Cluster boxes by spatial overlap
        clusters = self._cluster_boxes(all_boxes)
        
        # Vote within each cluster
        fused_boxes = []
        for cluster in clusters:
            fused_box = self._vote_cluster(cluster)
            if fused_box:
                fused_boxes.append(fused_box)
        
        # Sort by position (top-left to bottom-right)
        fused_boxes.sort(key=lambda b: (b.y, b.x))
        
        # Build full text
        full_text = " ".join(box.text for box in fused_boxes)
        
        # Calculate average confidence
        avg_conf = sum(b.confidence for b in fused_boxes) / len(fused_boxes) if fused_boxes else 0.0
        
        # Convert to OCRBox
        final_boxes = [
            OCRBox(
                text=b.text,
                confidence=b.confidence,
                x=b.x,
                y=b.y,
                width=b.width,
                height=b.height,
            )
            for b in fused_boxes
        ]
        
        return OCRResult(
            boxes=final_boxes,
            full_text=full_text,
            confidence=avg_conf,
            engine="ensemble",
        )
    
    def _cluster_boxes(
        self,
        boxes: list[tuple[str, OCRBox]],
        iou_threshold: float = 0.3,
    ) -> list[list[tuple[str, OCRBox]]]:
        """Cluster boxes by spatial overlap (IoU)."""
        if not boxes:
            return []
        
        clusters: list[list[tuple[str, OCRBox]]] = []
        used = set()
        
        for i, (name1, box1) in enumerate(boxes):
            if i in used:
                continue
            
            cluster = [(name1, box1)]
            used.add(i)
            
            for j, (name2, box2) in enumerate(boxes):
                if j in used:
                    continue
                
                if self._calculate_iou(box1, box2) >= iou_threshold:
                    cluster.append((name2, box2))
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_iou(self, box1: OCRBox, box2: OCRBox) -> float:
        """Calculate Intersection over Union."""
        x1 = max(box1.x, box2.x)
        y1 = max(box1.y, box2.y)
        x2 = min(box1.x + box1.width, box2.x + box2.width)
        y2 = min(box1.y + box1.height, box2.y + box2.height)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = box1.width * box1.height
        area2 = box2.width * box2.height
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _vote_cluster(
        self,
        cluster: list[tuple[str, OCRBox]],
    ) -> FusedBox | None:
        """Vote on text within a cluster."""
        if not cluster:
            return None
        
        # Collect texts with confidence weights
        votes: dict[str, float] = {}
        for engine_name, box in cluster:
            text = box.text.strip()
            if text:
                # Weight by confidence
                votes[text] = votes.get(text, 0) + box.confidence
        
        if not votes:
            return None
        
        # Find winner (also consider fuzzy matches)
        winner_text = max(votes.keys(), key=lambda t: votes[t])
        winner_conf = votes[winner_text] / len(cluster)
        
        # Average bounding box
        avg_x = int(sum(b.x for _, b in cluster) / len(cluster))
        avg_y = int(sum(b.y for _, b in cluster) / len(cluster))
        avg_w = int(sum(b.width for _, b in cluster) / len(cluster))
        avg_h = int(sum(b.height for _, b in cluster) / len(cluster))
        
        sources = list(set(name for name, _ in cluster))
        
        return FusedBox(
            text=winner_text,
            confidence=min(winner_conf, 1.0),
            x=avg_x,
            y=avg_y,
            width=avg_w,
            height=avg_h,
            sources=sources,
            votes=len(cluster),
        )
