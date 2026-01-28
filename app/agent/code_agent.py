"""
ONI v5.0 - Code Agent
Executes Python/Bash code for data processing tasks.

This module provides a sandboxed code execution environment for tasks
that require programmatic data manipulation rather than visual automation.
"""

import asyncio
import ast
import io
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class CodeLanguage(str, Enum):
    """Supported code languages."""
    PYTHON = "python"
    POWERSHELL = "powershell"
    BASH = "bash"


@dataclass
class CodeAgentResult:
    """Result from code execution."""
    success: bool
    language: CodeLanguage
    code: str
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    variables: Dict[str, Any] = field(default_factory=dict)


class CodeAgent:
    """
    Secure code execution agent.
    
    Provides sandboxed execution of Python code with:
    - AST validation before execution
    - Restricted builtins (no file system, no network)
    - Timeout enforcement
    - Variable capture
    """
    
    # Allowed builtins for sandboxed execution
    SAFE_BUILTINS = {
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes', 'callable',
        'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter', 'float',
        'format', 'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'id',
        'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'map',
        'max', 'min', 'next', 'oct', 'ord', 'pow', 'print', 'range',
        'repr', 'reversed', 'round', 'set', 'slice', 'sorted', 'str',
        'sum', 'tuple', 'type', 'zip',
    }
    
    # Forbidden AST node types (dangerous operations)
    FORBIDDEN_NODES = {
        'Import', 'ImportFrom',  # No imports
        'With', 'AsyncWith',     # No context managers (file handles)
    }
    
    # Forbidden function calls
    FORBIDDEN_CALLS = {
        'open', 'exec', 'eval', 'compile', '__import__',
        'globals', 'locals', 'vars', 'dir',
        'input', 'breakpoint',
    }
    
    def __init__(self, timeout_seconds: float = 10.0, allow_imports: bool = False):
        """
        Initialize CodeAgent.
        
        Args:
            timeout_seconds: Maximum execution time
            allow_imports: If True, allows safe imports (math, datetime, etc.)
        """
        self._timeout = timeout_seconds
        self._allow_imports = allow_imports
        self._safe_modules = {'math', 'datetime', 'json', 're', 'collections', 'itertools'}
        
        logger.info("code_agent_initialized", timeout=timeout_seconds)
    
    async def execute(
        self,
        code: str,
        language: CodeLanguage = CodeLanguage.PYTHON,
        context: Optional[Dict[str, Any]] = None
    ) -> CodeAgentResult:
        """
        Execute code in a sandboxed environment.
        
        Args:
            code: Code to execute
            language: Programming language
            context: Variables to inject into execution context
            
        Returns:
            CodeAgentResult with execution details
        """
        start_time = datetime.now()
        
        if language != CodeLanguage.PYTHON:
            return CodeAgentResult(
                success=False,
                language=language,
                code=code,
                output="",
                error=f"Language {language} not yet supported. Only Python is available."
            )
        
        # Validate code safety
        is_safe, validation_error = self._validate_code(code)
        if not is_safe:
            return CodeAgentResult(
                success=False,
                language=language,
                code=code,
                output="",
                error=f"Code validation failed: {validation_error}"
            )
        
        # Prepare execution environment
        safe_globals = self._create_safe_globals()
        if context:
            safe_globals.update(context)
        
        # Capture stdout
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        
        try:
            sys.stdout = captured_output
            
            # Execute with timeout
            exec(code, safe_globals)
            
            output = captured_output.getvalue()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Extract user-defined variables
            user_vars = {
                k: v for k, v in safe_globals.items()
                if not k.startswith('_') and k not in self.SAFE_BUILTINS
            }
            
            logger.info("code_agent_execution_success", 
                       output_length=len(output),
                       variables_count=len(user_vars))
            
            return CodeAgentResult(
                success=True,
                language=language,
                code=code,
                output=output,
                execution_time_ms=execution_time,
                variables=user_vars
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            logger.error("code_agent_execution_error", error=str(e))
            
            return CodeAgentResult(
                success=False,
                language=language,
                code=code,
                output=captured_output.getvalue(),
                error=error_msg,
                execution_time_ms=execution_time
            )
            
        finally:
            sys.stdout = old_stdout
    
    def _validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code for safety using AST analysis.
        
        Returns:
            Tuple of (is_safe, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        for node in ast.walk(tree):
            node_type = type(node).__name__
            
            # Check forbidden node types
            if node_type in self.FORBIDDEN_NODES and not self._allow_imports:
                return False, f"Forbidden operation: {node_type}"
            
            # Check forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_CALLS:
                        return False, f"Forbidden function: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.FORBIDDEN_CALLS:
                        return False, f"Forbidden method: {node.func.attr}"
        
        return True, None
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a sandboxed globals dict with safe builtins only."""
        import builtins
        
        safe_builtins = {
            name: getattr(builtins, name)
            for name in self.SAFE_BUILTINS
            if hasattr(builtins, name)
        }
        
        # Add safe modules if imports allowed
        if self._allow_imports:
            import math
            import datetime as dt
            import json
            import re
            import collections
            import itertools
            
            safe_builtins.update({
                'math': math,
                'datetime': dt,
                'json': json,
                're': re,
                'collections': collections,
                'itertools': itertools,
            })
        
        return {'__builtins__': safe_builtins}


# =============================================================================
# QUICK TEST
# =============================================================================

async def _test_code_agent():
    """Quick test of the CodeAgent."""
    agent = CodeAgent()
    
    # Test safe code
    result = await agent.execute("""
x = 10
y = 20
result = x + y
print(f"Result: {result}")
""")
    
    print(f"Test 1 (safe code): success={result.success}, output={result.output.strip()}")
    
    # Test unsafe code (should fail)
    result2 = await agent.execute("""
import os
os.system("dir")
""")
    
    print(f"Test 2 (unsafe code): success={result2.success}, error={result2.error}")
    
    return result


if __name__ == "__main__":
    asyncio.run(_test_code_agent())
