"""
ONI LLM - Local Llama Provider
"""
from typing import Any
from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from .base_provider import LLMProvider


class LocalLlamaProvider(LLMProvider):
    """Local llama.cpp provider wrapper."""
    
    def __init__(self, llama_engine: Any = None):
        self._engine = llama_engine
    
    @property
    def name(self) -> str:
        if self._engine:
            return f"Local ({self._engine.model_name})"
        return "Local (not loaded)"
    
    @property
    def is_available(self) -> bool:
        return self._engine is not None and self._engine.is_loaded
    
    async def generate(self, prompt: str, config: GenerationConfig | None = None) -> GenerationResult:
        if not self._engine:
            raise RuntimeError("Local LLM engine not loaded")
        return await self._engine.generate(prompt, config)
