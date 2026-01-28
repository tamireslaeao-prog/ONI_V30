"""
ONI v2.0 - GBNF Grammar Loader
Manages GBNF grammars for structured output
"""
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings
from app.core.exceptions import GrammarError

logger = structlog.get_logger()


class GrammarLoader:
    """
    Loads and caches GBNF grammars for structured LLM output.
    
    Features:
    - LRU caching of parsed grammars
    - Grammar validation
    - Dynamic grammar generation
    """
    
    def __init__(self, grammar_dir: Path | None = None) -> None:
        """
        Initialize grammar loader.
        
        Args:
            grammar_dir: Directory containing grammar files
        """
        self._grammar_dir = grammar_dir or settings.llm.grammar_dir
        self._grammar_cache: dict[str, Any] = {}
    
    def load_grammar(self, grammar_name: str) -> Any:
        """
        Load a grammar by name.
        
        Args:
            grammar_name: Name of grammar (e.g., "action_schema")
            
        Returns:
            Compiled LlamaGrammar object
        """
        # Check cache
        if grammar_name in self._grammar_cache:
            return self._grammar_cache[grammar_name]
        
        # Find grammar file
        grammar_path = self._find_grammar_file(grammar_name)
        if grammar_path is None:
            raise GrammarError(f"Grammar not found: {grammar_name}")
        
        # Load and compile
        try:
            grammar_text = grammar_path.read_text(encoding="utf-8")
            compiled = self._compile_grammar(grammar_text)
            self._grammar_cache[grammar_name] = compiled
            
            logger.debug("grammar_loaded", name=grammar_name, path=str(grammar_path))
            return compiled
            
        except Exception as e:
            raise GrammarError(f"Failed to load grammar {grammar_name}: {e}")
    
    def _find_grammar_file(self, grammar_name: str) -> Path | None:
        """Find grammar file by name."""
        # Try exact path first
        if grammar_name.endswith(".gbnf"):
            path = Path(grammar_name)
            if path.exists():
                return path
        
        # Try in grammar directory
        for extension in [".gbnf", ""]:
            path = self._grammar_dir / f"{grammar_name}{extension}"
            if path.exists():
                return path
        
        return None
    
    def _compile_grammar(self, grammar_text: str) -> Any:
        """
        Compile grammar text.
        
        Args:
            grammar_text: Raw GBNF grammar text
            
        Returns:
            Compiled LlamaGrammar object
        """
        try:
            from llama_cpp import LlamaGrammar
            return LlamaGrammar.from_string(grammar_text)
        except ImportError:
            # If llama_cpp not installed, return raw text
            logger.warning("llama_cpp_not_installed_using_raw_grammar")
            return grammar_text
        except Exception as e:
            raise GrammarError(f"Grammar compilation failed: {e}")
    
    def load_grammar_from_string(self, grammar_text: str, name: str = "inline") -> Any:
        """
        Load grammar from string.
        
        Args:
            grammar_text: GBNF grammar text
            name: Optional name for caching
            
        Returns:
            Compiled grammar
        """
        cache_key = f"inline_{hash(grammar_text)}"
        
        if cache_key in self._grammar_cache:
            return self._grammar_cache[cache_key]
        
        compiled = self._compile_grammar(grammar_text)
        self._grammar_cache[cache_key] = compiled
        return compiled
    
    def list_available_grammars(self) -> list[str]:
        """List all available grammar files."""
        if not self._grammar_dir.exists():
            return []
        
        return [
            p.stem for p in self._grammar_dir.glob("*.gbnf")
        ]
    
    def clear_cache(self) -> None:
        """Clear the grammar cache."""
        self._grammar_cache.clear()
        logger.debug("grammar_cache_cleared")


# =============================================================================
# Common Grammar Templates
# =============================================================================

class GrammarTemplates:
    """Pre-defined grammar templates for common use cases."""
    
    @staticmethod
    def json_object() -> str:
        """Grammar for generic JSON object."""
        return '''
root ::= object
object ::= "{" ws (pair ("," ws pair)*)? ws "}"
pair ::= string ws ":" ws value
value ::= string | number | boolean | "null" | object | array
array ::= "[" ws (value ("," ws value)*)? ws "]"
string ::= "\\"" ([^"\\\\] | "\\\\" .)* "\\""
number ::= "-"? ("0" | [1-9] [0-9]*) ("." [0-9]+)? ([eE] [+-]? [0-9]+)?
boolean ::= "true" | "false"
ws ::= [ \\t\\n\\r]*
'''
    
    @staticmethod
    def yes_no() -> str:
        """Grammar for yes/no response."""
        return '''
root ::= response
response ::= "yes" | "no"
'''
    
    @staticmethod
    def number_only() -> str:
        """Grammar for number-only response."""
        return '''
root ::= number
number ::= "-"? ("0" | [1-9] [0-9]*) ("." [0-9]+)?
'''
    
    @staticmethod
    def coordinate() -> str:
        """Grammar for x,y coordinate."""
        return '''
root ::= coordinate
coordinate ::= "{" ws "\\"x\\":" ws number "," ws "\\"y\\":" ws number ws "}"
number ::= [0-9]+
ws ::= [ \\t\\n\\r]*
'''
    
    @staticmethod
    def action_simple() -> str:
        """Grammar for simple action selection."""
        return '''
root ::= action
action ::= "\\"click\\"" | "\\"type\\"" | "\\"scroll\\"" | "\\"wait\\"" | "\\"done\\""
'''
