"""
ONI v6.5 - Quality Verification Service
Compares before/after screenshots to verify action quality.
Implements self-correction loop when quality is unsatisfactory.
"""
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class QualityLevel(Enum):
    EXCELLENT = "excellent"  # 9-10
    GOOD = "good"            # 7-8
    ACCEPTABLE = "acceptable" # 5-6
    POOR = "poor"            # 3-4
    FAILED = "failed"        # 1-2


class MeetsExpectation(Enum):
    YES = "yes"
    PARTIAL = "partial"
    NO = "no"


@dataclass
class QualityResult:
    """Result of quality verification."""
    quality_score: float  # 1-10
    quality_level: QualityLevel
    meets_expectation: MeetsExpectation
    issues: List[str] = field(default_factory=list)
    corrections_needed: List[str] = field(default_factory=list)
    should_retry: bool = False
    retry_with_changes: List[str] = field(default_factory=list)
    raw_vlm_response: Optional[str] = None


class QualityVerificationService:
    """
    Compares before/after screenshots and evaluates quality.
    Decides if action was successful or needs retry.
    """
    
    # Minimum acceptable quality scores by task type
    MIN_QUALITY_THRESHOLDS = {
        "drawing": 6.0,
        "text_editing": 7.0,
        "file_operation": 8.0,
        "navigation": 5.0,
        "default": 6.0
    }
    
    @classmethod
    def get_comparison_prompt(cls, expected_result: str, task_type: str = "drawing") -> str:
        """
        Generate prompt for VLM to compare before/after images.
        """
        return f"""
Você está avaliando o resultado de uma ação automatizada.

**Tarefa executada:** {task_type}
**Resultado esperado:** {expected_result}

Compare a imagem ANTES e DEPOIS e responda em JSON:
{{
    "quality_score": <número de 1 a 10>,
    "meets_expectation": "<yes/partial/no>",
    "visual_changes": ["<lista de mudanças visuais detectadas>"],
    "issues_found": ["<problemas identificados>"],
    "specific_problems": {{
        "brush_too_thick": <true/false>,
        "wrong_color": <true/false>,
        "wrong_position": <true/false>,
        "incomplete_drawing": <true/false>,
        "artifacts_noise": <true/false>
    }},
    "corrections_needed": ["<ações para corrigir problemas>"],
    "should_undo": <true/false>,
    "retry_suggestions": ["<sugestões para tentar novamente>"]
}}

IMPORTANTE:
- quality_score 1-3: resultado muito ruim (borrado, errado)
- quality_score 4-5: resultado abaixo do esperado
- quality_score 6-7: resultado aceitável com pequenos problemas
- quality_score 8-10: resultado bom ou excelente
"""
    
    @classmethod
    def get_quality_level(cls, score: float) -> QualityLevel:
        """Convert numeric score to quality level."""
        if score >= 9:
            return QualityLevel.EXCELLENT
        elif score >= 7:
            return QualityLevel.GOOD
        elif score >= 5:
            return QualityLevel.ACCEPTABLE
        elif score >= 3:
            return QualityLevel.POOR
        else:
            return QualityLevel.FAILED
    
    @classmethod
    async def compare_before_after(
        cls,
        before_path: str,
        after_path: str,
        expected_result: str,
        task_type: str = "drawing",
        vlm_service = None
    ) -> QualityResult:
        """
        Compare before and after screenshots to verify quality.
        
        Args:
            before_path: Path to screenshot taken BEFORE action
            after_path: Path to screenshot taken AFTER action
            expected_result: Description of expected outcome
            task_type: Type of task for threshold lookup
            vlm_service: VLM service for image comparison
            
        Returns:
            QualityResult with detailed assessment
        """
        min_threshold = cls.MIN_QUALITY_THRESHOLDS.get(task_type, cls.MIN_QUALITY_THRESHOLDS["default"])
        
        if vlm_service is None:
            # Fallback: basic file size comparison
            logger.warning("vlm_not_available_for_quality_check")
            return cls._fallback_comparison(before_path, after_path, min_threshold)
        
        prompt = cls.get_comparison_prompt(expected_result, task_type)
        
        try:
            # Call VLM with both images
            response = await vlm_service.compare_images(before_path, after_path, prompt)
            
            # Parse response
            result_data = json.loads(response) if isinstance(response, str) else response
            
            score = float(result_data.get("quality_score", 5.0))
            meets_exp_str = result_data.get("meets_expectation", "partial")
            meets_exp = MeetsExpectation.YES if meets_exp_str == "yes" else (
                MeetsExpectation.PARTIAL if meets_exp_str == "partial" else MeetsExpectation.NO
            )
            
            issues = result_data.get("issues_found", [])
            corrections = result_data.get("corrections_needed", [])
            should_undo = result_data.get("should_undo", False)
            retry_suggestions = result_data.get("retry_suggestions", [])
            
            # Determine if retry is needed
            should_retry = score < min_threshold or meets_exp == MeetsExpectation.NO or should_undo
            
            return QualityResult(
                quality_score=score,
                quality_level=cls.get_quality_level(score),
                meets_expectation=meets_exp,
                issues=issues,
                corrections_needed=corrections,
                should_retry=should_retry,
                retry_with_changes=retry_suggestions,
                raw_vlm_response=str(result_data)
            )
            
        except Exception as e:
            logger.error("quality_verification_failed", error=str(e))
            return QualityResult(
                quality_score=0,
                quality_level=QualityLevel.FAILED,
                meets_expectation=MeetsExpectation.NO,
                issues=[f"Verification error: {str(e)}"],
                should_retry=True,
                retry_with_changes=["Fix VLM service and retry"]
            )
    
    @classmethod
    def _fallback_comparison(cls, before_path: str, after_path: str, min_threshold: float) -> QualityResult:
        """
        Fallback comparison when VLM is not available.
        Uses file size difference as a rough indicator.
        """
        import os
        
        try:
            before_size = os.path.getsize(before_path)
            after_size = os.path.getsize(after_path)
            size_diff = abs(after_size - before_size)
            
            # If there's significant change, assume something happened
            if size_diff > 10000:  # More than 10KB difference
                return QualityResult(
                    quality_score=6.0,
                    quality_level=QualityLevel.ACCEPTABLE,
                    meets_expectation=MeetsExpectation.PARTIAL,
                    issues=["VLM not available - using file size comparison"],
                    should_retry=False,
                    retry_with_changes=["Enable VLM for proper quality assessment"]
                )
            else:
                return QualityResult(
                    quality_score=3.0,
                    quality_level=QualityLevel.POOR,
                    meets_expectation=MeetsExpectation.NO,
                    issues=["No significant visual change detected", "VLM not available for detailed analysis"],
                    should_retry=True,
                    retry_with_changes=["Verify action was executed", "Check tool configuration"]
                )
                
        except Exception as e:
            return QualityResult(
                quality_score=0,
                quality_level=QualityLevel.FAILED,
                meets_expectation=MeetsExpectation.NO,
                issues=[f"Fallback comparison failed: {str(e)}"],
                should_retry=True
            )
    
    @classmethod
    def should_undo_and_retry(cls, result: QualityResult) -> Tuple[bool, int]:
        """
        Determine if we should undo and how many steps.
        
        Returns:
            Tuple of (should_undo, num_steps_to_undo)
        """
        if not result.should_retry:
            return False, 0
            
        if result.quality_level == QualityLevel.FAILED:
            return True, 1
        elif result.quality_level == QualityLevel.POOR:
            return True, 1
        elif result.quality_level == QualityLevel.ACCEPTABLE and result.meets_expectation == MeetsExpectation.NO:
            return True, 1
            
        return False, 0
    
    @classmethod
    def get_retry_strategy(cls, result: QualityResult) -> Dict[str, Any]:
        """
        Get recommended retry strategy based on quality result.
        """
        strategy = {
            "undo_first": result.should_retry,
            "num_undos": 1 if result.should_retry else 0,
            "config_changes": [],
            "approach_changes": []
        }
        
        # Analyze specific problems if available
        if "brush_too_thick" in str(result.raw_vlm_response):
            strategy["config_changes"].append({
                "issue": "brush_too_thick",
                "action": "Reduzir tamanho do pincel",
                "keys": "[",  # Photoshop shortcut to reduce brush size
                "repeat": 10
            })
        
        if "wrong_color" in str(result.raw_vlm_response):
            strategy["config_changes"].append({
                "issue": "wrong_color",
                "action": "Selecionar cor correta",
                "method": "color_picker"
            })
        
        if "wrong_position" in str(result.raw_vlm_response):
            strategy["approach_changes"].append("Recalcular coordenadas de desenho")
        
        strategy["corrections"] = result.corrections_needed
        strategy["suggestions"] = result.retry_with_changes
        
        return strategy
