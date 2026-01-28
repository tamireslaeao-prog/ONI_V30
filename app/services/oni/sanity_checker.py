"""
ONI v7.0 - Sanity Checker Service
Pre-action sanity checks to prevent obvious errors.
"""

import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SanityCheckResult:
    """Result of sanity checks."""
    passed: bool
    checks_run: int
    checks_passed: int
    failed_checks: List[str]
    warnings: List[str]
    confidence: float


class SanityCheckerService:
    """
    Pre-Action Sanity Checker.
    
    Performs quick sanity checks before critical actions:
    1. Window match - Is the correct window in focus?
    2. Cursor position - Is mouse in expected region?
    3. No blocking dialogs - Are there popups blocking?
    4. Element visible - Is target element present?
    """
    
    # Screen regions (for cursor position check)
    REGIONS = {
        "toolbar": (0, 0, 1920, 100),
        "canvas": (200, 100, 1720, 900),
        "sidebar": (0, 100, 200, 1080),
        "statusbar": (0, 1000, 1920, 1080),
    }
    
    @classmethod
    def check_window_match(
        cls,
        expected_app: str,
        active_window_title: str,
        active_process: str
    ) -> Tuple[bool, str]:
        """Check if the correct window is in focus."""
        expected_lower = expected_app.lower()
        title_lower = active_window_title.lower()
        process_lower = active_process.lower()
        
        # Check process name first (more reliable)
        if expected_lower in process_lower:
            return True, f"Process matches: {active_process}"
        
        # Check window title
        if expected_lower in title_lower:
            return True, f"Title matches: {active_window_title}"
        
        # Known mappings
        app_mappings = {
            "photoshop": ["photoshop", "adobe photoshop", "ps"],
            "coreldraw": ["coreldraw", "corel draw", "coreldrw"],
            "explorer": ["explorer", "file explorer", "windows explorer"],
            "chrome": ["chrome", "google chrome"],
            "vscode": ["code", "visual studio code"],
        }
        
        for app, variants in app_mappings.items():
            if expected_lower in variants or app in expected_lower:
                if any(v in title_lower or v in process_lower for v in variants):
                    return True, f"Mapped match: {app}"
        
        return False, f"Expected '{expected_app}', got '{active_window_title}' ({active_process})"
    
    @classmethod
    def check_cursor_position(
        cls,
        x: int,
        y: int,
        expected_region: str = None,
        in_primary_monitor: bool = True
    ) -> Tuple[bool, str]:
        """Check if cursor is in expected region."""
        if not in_primary_monitor:
            return False, f"Cursor at ({x}, {y}) is NOT in primary monitor!"
        
        # Check if in screen bounds
        if x < 0 or x > 1920 or y < 0 or y > 1080:
            return False, f"Cursor at ({x}, {y}) is OUT OF BOUNDS!"
        
        # If specific region expected, check it
        if expected_region and expected_region in cls.REGIONS:
            x1, y1, x2, y2 = cls.REGIONS[expected_region]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True, f"Cursor in {expected_region} region"
            else:
                return False, f"Cursor at ({x}, {y}) not in {expected_region} region"
        
        return True, f"Cursor at ({x}, {y}) in valid position"
    
    @classmethod
    def check_no_dialogs(
        cls,
        ocr_text: str = ""
    ) -> Tuple[bool, str]:
        """Check for blocking dialogs based on OCR text."""
        blocking_indicators = [
            "do you want to save",
            "save changes",
            "are you sure",
            "confirm",
            "warning",
            "error",
            "failed",
            "cannot",
            "unable to",
            "access denied",
            "permission",
        ]
        
        ocr_lower = ocr_text.lower()
        
        for indicator in blocking_indicators:
            if indicator in ocr_lower:
                return False, f"Possible blocking dialog detected: '{indicator}'"
        
        return True, "No blocking dialogs detected"
    
    @classmethod
    def check_element_visible(
        cls,
        target_element: str,
        ocr_text: str = "",
        screen_elements: List[Dict] = None
    ) -> Tuple[bool, str]:
        """Check if target element is visible."""
        target_lower = target_element.lower()
        
        # Check OCR text
        if ocr_text and target_lower in ocr_text.lower():
            return True, f"Element '{target_element}' found in OCR text"
        
        # Check screen elements
        if screen_elements:
            for elem in screen_elements:
                elem_text = elem.get("text", "").lower()
                if target_lower in elem_text:
                    return True, f"Element '{target_element}' found in screen elements"
        
        # Can't confirm but not necessarily failing
        return True, f"Element '{target_element}' not confirmed but proceeding"
    
    @classmethod
    async def run_all_checks(
        cls,
        expected_app: str = None,
        active_window_title: str = "",
        active_process: str = "",
        cursor_x: int = 0,
        cursor_y: int = 0,
        in_primary_monitor: bool = True,
        expected_region: str = None,
        target_element: str = None,
        ocr_text: str = "",
        screen_elements: List[Dict] = None
    ) -> SanityCheckResult:
        """
        Run all applicable sanity checks.
        
        Returns SanityCheckResult with pass/fail status.
        """
        checks_run = 0
        checks_passed = 0
        failed = []
        warnings = []
        
        # 1. Window match check
        if expected_app:
            checks_run += 1
            passed, msg = cls.check_window_match(expected_app, active_window_title, active_process)
            if passed:
                checks_passed += 1
            else:
                failed.append(f"WINDOW: {msg}")
        
        # 2. Cursor position check
        if cursor_x > 0 or cursor_y > 0:
            checks_run += 1
            passed, msg = cls.check_cursor_position(cursor_x, cursor_y, expected_region, in_primary_monitor)
            if passed:
                checks_passed += 1
            else:
                if not in_primary_monitor:
                    failed.append(f"CURSOR: {msg}")
                else:
                    warnings.append(f"CURSOR: {msg}")
        
        # 3. Blocking dialogs check
        if ocr_text:
            checks_run += 1
            passed, msg = cls.check_no_dialogs(ocr_text)
            if passed:
                checks_passed += 1
            else:
                warnings.append(f"DIALOG: {msg}")
        
        # 4. Element visible check
        if target_element:
            checks_run += 1
            passed, msg = cls.check_element_visible(target_element, ocr_text, screen_elements)
            if passed:
                checks_passed += 1
            else:
                warnings.append(f"ELEMENT: {msg}")
        
        # Calculate overall result
        all_passed = len(failed) == 0
        confidence = checks_passed / checks_run if checks_run > 0 else 1.0
        
        result = SanityCheckResult(
            passed=all_passed,
            checks_run=checks_run,
            checks_passed=checks_passed,
            failed_checks=failed,
            warnings=warnings,
            confidence=round(confidence, 2)
        )
        
        if not all_passed:
            logger.warning("sanity_check_failed", 
                          failed=failed, 
                          warnings=warnings)
        else:
            logger.debug("sanity_check_passed", 
                        checks=checks_run, 
                        confidence=confidence)
        
        return result
    
    @classmethod
    def quick_check(
        cls,
        active_window: Dict[str, Any],
        expected_app: str = None
    ) -> bool:
        """
        Quick sanity check (synchronous, minimal).
        
        Args:
            active_window: Dict with 'title', 'process_name'
            expected_app: Expected app name
            
        Returns:
            True if basic checks pass
        """
        if not expected_app:
            return True
        
        title = active_window.get("title", "")
        process = active_window.get("process_name", "")
        
        passed, _ = cls.check_window_match(expected_app, title, process)
        return passed
