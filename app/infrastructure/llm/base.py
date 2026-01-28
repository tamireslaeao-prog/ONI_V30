"""
ONI v2.0 - LLM Base Protocol
Abstract interface for LLM engines
"""
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    stop_sequences: list[str] = field(default_factory=list)
    grammar: str | None = None


@dataclass
class GenerationResult:
    """Result of text generation."""
    text: str
    tokens_generated: int
    tokens_prompt: int
    generation_time_ms: float
    finish_reason: str  # "stop", "length", "grammar"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Chat message."""
    role: str  # "system", "user", "assistant"
    content: str


@runtime_checkable
class LLMProtocol(Protocol):
    """
    Protocol defining the interface for LLM engines.
    
    Any LLM implementation must provide these methods:
    - generate: Raw text completion
    - chat: Chat-style conversation
    - get_embedding: Text embeddings (optional)
    """
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        ...
    
    @property
    def context_size(self) -> int:
        """Get the maximum context size."""
        ...
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        ...
    
    @abstractmethod
    async def load(self) -> None:
        """Load the model into memory."""
        ...
    
    @abstractmethod
    async def unload(self) -> None:
        """Unload the model from memory."""
        ...
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        config: GenerationConfig | None = None,
    ) -> GenerationResult:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Returns:
            Generation result with text and metadata
        """
        ...
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        config: GenerationConfig | None = None,
    ) -> GenerationResult:
        """
        Chat-style conversation.
        
        Args:
            messages: List of conversation messages
            config: Generation configuration
            
        Returns:
            Generation result with assistant response
        """
        ...
    
    async def get_embedding(self, text: str) -> list[float]:
        """
        Get text embedding (optional).
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        raise NotImplementedError("Embeddings not supported by this model")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        # Default rough estimate: ~4 chars per token
        return len(text) // 4
