"""
ONI LLM - Base Provider
Abstract base class for LLM providers.
"""
from abc import ABC, abstractmethod
from app.infrastructure.llm.base import GenerationConfig, GenerationResult


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, config: GenerationConfig | None = None) -> GenerationResult:
        """Generate text completion."""
        pass
