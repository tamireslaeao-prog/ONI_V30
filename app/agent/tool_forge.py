"""
ONI v5.0 - Tool Forge
Creates and manages dynamically generated automation tools.

The ANT (Adaptive Networked Toolkit) component that can create
new tools on-the-fly when existing approaches fail.
"""

import asyncio
import ast
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ForgedTool:
    """A dynamically created tool."""
    name: str
    description: str
    code: str
    created_at: datetime = field(default_factory=datetime.now)
    success_count: int = 0
    failure_count: int = 0
    is_validated: bool = False
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class ToolForge:
    """
    Tool Forge - ANT's tool creation system.
    
    Creates automation tools dynamically when standard approaches fail.
    Uses LLM to generate Python code that accomplishes failed steps.
    """
    
    # Safe functions that can be used in forged tools
    ALLOWED_MODULES = {
        'pyautogui',  # Mouse/keyboard
        'time',       # Delays
        'asyncio',    # Async operations
    }
    
    def __init__(self, llm_provider: Any = None, cache_size: int = 100):
        """
        Initialize ToolForge.
        
        Args:
            llm_provider: LLM for generating tool code
            cache_size: Max number of tools to cache
        """
        self._llm = llm_provider
        self._cache: Dict[str, ForgedTool] = {}
        self._cache_size = cache_size
        
        logger.info("tool_forge_initialized")
    
    async def create_fix(self, error_context: Dict[str, Any]) -> Optional[str]:
        """
        Create a fix for a failed step.
        
        Args:
            error_context: Context about the failure including:
                - step: The step that failed
                - attempts: Number of attempts made
                - previous_errors: List of previous error messages
                
        Returns:
            Python code string that might fix the issue, or None
        """
        step = error_context.get("step", "")
        attempts = error_context.get("attempts", 0)
        errors = error_context.get("previous_errors", [])
        
        # Check cache first
        cache_key = self._generate_cache_key(step)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached.success_rate > 0.5:
                logger.info("tool_forge_cache_hit", step=step[:50])
                return cached.code
        
        # Generate new fix
        if self._llm:
            code = await self._generate_with_llm(step, errors)
        else:
            code = self._generate_heuristic_fix(step, errors)
        
        if code:
            # Validate generated code
            if self._validate_code(code):
                # Cache the tool
                tool = ForgedTool(
                    name=f"fix_{cache_key[:20]}",
                    description=f"Fix for: {step[:50]}",
                    code=code,
                    is_validated=True
                )
                self._cache[cache_key] = tool
                
                logger.info("tool_forge_created_tool", step=step[:50])
                return code
            else:
                logger.warning("tool_forge_validation_failed", step=step[:50])
        
        return None
    
    async def _generate_with_llm(self, step: str, errors: List[str]) -> Optional[str]:
        """Generate fix code using LLM."""
        prompt = f"""You are an automation expert. Generate Python code to accomplish this step that previously failed.

FAILED STEP: {step}

PREVIOUS ERRORS:
{chr(10).join(errors[-3:]) if errors else "No error details available"}

REQUIREMENTS:
1. Use pyautogui for mouse/keyboard automation
2. Include error handling (try/except)
3. Add small delays between actions (time.sleep)
4. Define a function called 'fix' that takes no arguments
5. The function must return True on success, False on failure
6. DO NOT use: open(), exec(), eval(), import os, import subprocess

EXAMPLE FORMAT:
def fix():
    try:
        import pyautogui
        import time
        # Your automation code here
        return True
    except Exception:
        return False

Return ONLY the Python code, nothing else.
"""
        
        try:
            if hasattr(self._llm, "generate"):
                response = await self._llm.generate(prompt)
            elif hasattr(self._llm, "chat"):
                response = await self._llm.chat(prompt)
            else:
                response = str(self._llm(prompt))
            
            # Extract code from response
            code = self._extract_code(response)
            return code
            
        except Exception as e:
            logger.error("tool_forge_llm_error", error=str(e))
            return None
    
    def _generate_heuristic_fix(self, step: str, errors: List[str]) -> Optional[str]:
        """Generate fix code using heuristics."""
        step_lower = step.lower()
        
        # Common fixes based on step type
        if "click" in step_lower:
            return self._generate_click_fix(step)
        elif "type" in step_lower or "digitar" in step_lower:
            return self._generate_type_fix(step)
        elif "save" in step_lower or "salvar" in step_lower:
            return self._generate_save_fix()
        elif "open" in step_lower or "abrir" in step_lower:
            return self._generate_open_fix(step)
        elif "wait" in step_lower or "esperar" in step_lower:
            return self._generate_wait_fix()
        
        # Generic retry fix
        return self._generate_generic_fix(step)
    
    def _generate_click_fix(self, step: str) -> str:
        """Generate a fix for click operations."""
        return '''def fix():
    try:
        import pyautogui
        import time
        
        # Wait for UI to stabilize
        time.sleep(0.5)
        
        # Try clicking at current mouse position (assuming user positioned it)
        pyautogui.click()
        time.sleep(0.3)
        
        return True
    except Exception:
        return False
'''
    
    def _generate_type_fix(self, step: str) -> str:
        """Generate a fix for typing operations."""
        # Extract text to type
        match = re.search(r'"([^"]+)"', step)
        text = match.group(1) if match else "text"
        
        return f'''def fix():
    try:
        import pyautogui
        import time
        
        # Ensure focus is on input field
        pyautogui.click()
        time.sleep(0.2)
        
        # Clear existing content
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Type the text slowly
        pyautogui.typewrite("{text}", interval=0.05)
        time.sleep(0.2)
        
        return True
    except Exception:
        return False
'''
    
    def _generate_save_fix(self) -> str:
        """Generate a fix for save operations."""
        return '''def fix():
    try:
        import pyautogui
        import time
        
        # Try Ctrl+S first
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)
        
        # If save dialog appeared, press Enter to confirm
        pyautogui.press('enter')
        time.sleep(0.3)
        
        return True
    except Exception:
        return False
'''
    
    def _generate_open_fix(self, step: str) -> str:
        """Generate a fix for open operations."""
        # Extract app name
        match = re.search(r'(?:open|abrir)\s+(.+)', step, re.IGNORECASE)
        app = match.group(1).strip() if match else "notepad"
        
        return f'''def fix():
    try:
        import pyautogui
        import time
        
        # Use Windows Run dialog
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        
        # Type app name
        pyautogui.typewrite("{app}", interval=0.02)
        time.sleep(0.2)
        
        # Press Enter to run
        pyautogui.press('enter')
        time.sleep(1.0)
        
        return True
    except Exception:
        return False
'''
    
    def _generate_wait_fix(self) -> str:
        """Generate a fix for wait operations."""
        return '''def fix():
    try:
        import time
        
        # Just wait a bit
        time.sleep(2.0)
        
        return True
    except Exception:
        return False
'''
    
    def _generate_generic_fix(self, step: str) -> str:
        """Generate a generic retry fix."""
        return '''def fix():
    try:
        import pyautogui
        import time
        
        # Press Escape to clear any dialogs
        pyautogui.press('escape')
        time.sleep(0.3)
        
        # Wait for UI to stabilize
        time.sleep(0.5)
        
        return True
    except Exception:
        return False
'''
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response."""
        # Try to find code block
        code_match = re.search(r'```(?:python)?\n?(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # If no code block, assume entire response is code
        return response.strip()
    
    def _validate_code(self, code: str) -> bool:
        """Validate that code is safe to execute."""
        try:
            # Parse as AST
            tree = ast.parse(code)
            
            # Check for forbidden patterns
            forbidden = {'open', 'exec', 'eval', 'compile', '__import__'}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in forbidden:
                            return False
                
                # Check for dangerous imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        name = alias.name.split('.')[0]
                        if name not in self.ALLOWED_MODULES:
                            return False
            
            return True
            
        except SyntaxError:
            return False
    
    def _generate_cache_key(self, step: str) -> str:
        """Generate cache key from step description."""
        # Normalize step
        normalized = step.lower().strip()
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def record_result(self, step: str, success: bool) -> None:
        """Record whether a forged tool succeeded or failed."""
        cache_key = self._generate_cache_key(step)
        if cache_key in self._cache:
            if success:
                self._cache[cache_key].success_count += 1
            else:
                self._cache[cache_key].failure_count += 1
    
    def get_tool(self, step: str) -> Optional[ForgedTool]:
        """Get a cached tool for a step, if available."""
        cache_key = self._generate_cache_key(step)
        return self._cache.get(cache_key)
    
    def clear_cache(self) -> None:
        """Clear the tool cache."""
        self._cache.clear()
        logger.info("tool_forge_cache_cleared")


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_tool_forge():
    """Quick test of the ToolForge."""
    forge = ToolForge()
    
    # Test heuristic generation
    error_context = {
        "step": "Click the Save button",
        "attempts": 3,
        "previous_errors": ["Element not found", "Click failed"]
    }
    
    code = await forge.create_fix(error_context)
    print(f"Generated fix:\n{code}")
    
    # Test if code is valid Python
    try:
        ast.parse(code)
        print("\n✅ Code is valid Python")
    except SyntaxError as e:
        print(f"\n❌ Syntax error: {e}")
    
    return code


if __name__ == "__main__":
    asyncio.run(_test_tool_forge())
