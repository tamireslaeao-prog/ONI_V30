"""
UNIVERSAL SELF-HEALING WRAPPER
==============================
Provides decorators and wrappers that ANY service can use to automatically
enable self-healing on their execution methods.

Usage:
    from app.services.healing_wrapper import with_healing, wrap_executor

    # Decorator for methods
    @with_healing(app_context="photoshop")
    def run_jsx(self, code):
        ...

    # Or wrap any executor function
    result = wrap_executor(my_function, code, app_context="blender")
"""
import functools
import structlog
from typing import Callable, Dict, Any
from app.services.self_healing_executor import get_healing_engine

logger = structlog.get_logger()


def with_healing(app_context: str = "universal", max_retries: int = 3):
    """
    Decorator to wrap any code execution method with self-healing.
    
    The decorated function must:
    - Accept 'code' as first argument (after self)
    - Return dict with 'success' and 'error' keys
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self_or_code, *args, **kwargs):
            # Handle both instance methods and standalone functions
            if hasattr(self_or_code, '__class__') and not isinstance(self_or_code, str):
                # It's 'self' from a method
                instance = self_or_code
                code = args[0] if args else kwargs.get('code', '')
                remaining_args = args[1:]
                
                def executor(patched_code: str) -> Dict:
                    return func(instance, patched_code, *remaining_args, **kwargs)
            else:
                # It's standalone function, first arg is code
                code = self_or_code
                remaining_args = args
                
                def executor(patched_code: str) -> Dict:
                    return func(patched_code, *remaining_args, **kwargs)
            
            engine = get_healing_engine()
            return engine.execute_with_healing(
                code, 
                executor, 
                app_context=app_context,
                max_retries=max_retries
            )
        
        return wrapper
    return decorator


def wrap_executor(executor_fn: Callable[[str], Dict], 
                  code: str, 
                  app_context: str = "universal",
                  max_retries: int = 3) -> Dict:
    """
    Wrap any executor function with self-healing.
    
    Args:
        executor_fn: Function that takes code string and returns {'success': bool, 'error': str}
        code: The code to execute
        app_context: App name for context-specific fixes
        max_retries: Number of healing attempts
        
    Returns:
        Execution result
    """
    engine = get_healing_engine()
    return engine.execute_with_healing(code, executor_fn, app_context, max_retries)


class HealingMixin:
    """
    Mixin class that adds self-healing to any service.
    
    Usage:
        class MyService(HealingMixin):
            healing_context = "my_app"
            
            def execute(self, code):
                return self.heal_and_execute(code, self._raw_execute)
                
            def _raw_execute(self, code):
                # Your actual execution logic
                return {"success": True, "output": "..."}
    """
    healing_context: str = "universal"
    healing_max_retries: int = 3
    
    def heal_and_execute(self, code: str, executor_fn: Callable[[str], Dict]) -> Dict:
        """Execute code with self-healing enabled."""
        engine = get_healing_engine()
        return engine.execute_with_healing(
            code, 
            executor_fn, 
            app_context=getattr(self, 'healing_context', 'universal'),
            max_retries=getattr(self, 'healing_max_retries', 3)
        )
