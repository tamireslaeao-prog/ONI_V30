"""
ONI v2.0 - Llama.cpp Engine
Primary LLM engine using llama-cpp-python
"""
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings
from app.core.exceptions import InferenceError, ModelNotFoundError
from app.infrastructure.llm.base import (
    GenerationConfig,
    GenerationResult,
    LLMProtocol,
    Message,
)
from app.infrastructure.llm.grammar import GrammarLoader

logger = structlog.get_logger()


class LlamaEngine:
    """
    LLM Engine using llama-cpp-python.
    
    Features:
    - GPU acceleration via CUDA
    - Grammar-guided generation (GBNF)
    - Async wrapper for thread safety
    - Token counting and context management
    """
    
    def __init__(
        self,
        model_path: Path | None = None,
        n_ctx: int | None = None,
        n_threads: int | None = None,
        n_gpu_layers: int | None = None,
    ) -> None:
        """
        Initialize the Llama engine.
        
        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: Number of CPU threads
            n_gpu_layers: Number of layers to offload to GPU
        """
        self._model_path = model_path or settings.llm.model_path
        self._n_ctx = n_ctx or settings.llm.context_size
        self._n_threads = n_threads or settings.llm.n_threads
        self._n_gpu_layers = n_gpu_layers or settings.llm.n_gpu_layers
        
        self._llm: Any = None
        self._grammar_loader = GrammarLoader()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="llm")
        self._lock = asyncio.Lock()
    
    @property
    def model_name(self) -> str:
        """Get the model name from path."""
        return self._model_path.stem
    
    @property
    def context_size(self) -> int:
        """Get the context window size."""
        return self._n_ctx
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._llm is not None
    
    async def load(self) -> None:
        """Load the model into memory."""
        if self.is_loaded:
            logger.warning("model_already_loaded", model=self.model_name)
            return
        
        if not self._model_path.exists():
            raise ModelNotFoundError(f"Model not found: {self._model_path}")
        
        logger.info(
            "loading_model",
            model=self.model_name,
            path=str(self._model_path),
            n_ctx=self._n_ctx,
            n_gpu_layers=self._n_gpu_layers,
        )
        
        start_time = time.perf_counter()
        
        # Load in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._load_model_sync)
        
        load_time = (time.perf_counter() - start_time) * 1000
        logger.info("model_loaded", model=self.model_name, load_time_ms=load_time)
    
    def _load_model_sync(self) -> None:
        """Synchronous model loading."""
        try:
            from llama_cpp import Llama
            
            self._llm = Llama(
                model_path=str(self._model_path),
                n_ctx=self._n_ctx,
                n_threads=self._n_threads,
                n_gpu_layers=self._n_gpu_layers,
                verbose=False,
            )
        except Exception as e:
            raise ModelNotFoundError(f"Failed to load model: {e}")
    
    async def unload(self) -> None:
        """Unload the model from memory."""
        if self._llm is not None:
            del self._llm
            self._llm = None
            logger.info("model_unloaded", model=self.model_name)
    
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
        if not self.is_loaded:
            raise InferenceError("Model not loaded")
        
        config = config or GenerationConfig()
        
        async with self._lock:
            loop = asyncio.get_event_loop()
            start_time = time.perf_counter()
            
            result = await loop.run_in_executor(
                self._executor,
                lambda: self._generate_sync(prompt, config)
            )
            
            generation_time = (time.perf_counter() - start_time) * 1000
            result.generation_time_ms = generation_time
            
            logger.debug(
                "generation_complete",
                tokens=result.tokens_generated,
                time_ms=generation_time,
            )
            
            return result
    
    def _generate_sync(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        """Synchronous text generation."""
        # Load grammar if specified
        grammar = None
        if config.grammar:
            grammar = self._grammar_loader.load_grammar(config.grammar)
        
        try:
            output = self._llm(
                prompt,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                repeat_penalty=config.repeat_penalty,
                stop=config.stop_sequences or None,
                grammar=grammar,
            )
            
            text = output["choices"][0]["text"]
            finish_reason = output["choices"][0].get("finish_reason", "unknown")
            
            return GenerationResult(
                text=text,
                tokens_generated=output["usage"]["completion_tokens"],
                tokens_prompt=output["usage"]["prompt_tokens"],
                generation_time_ms=0.0,  # Will be set by async wrapper
                finish_reason=finish_reason,
                metadata={
                    "model": self.model_name,
                    "temperature": config.temperature,
                }
            )
            
        except Exception as e:
            raise InferenceError(f"Generation failed: {e}")
    
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
        if not self.is_loaded:
            raise InferenceError("Model not loaded")
        
        config = config or GenerationConfig()
        
        async with self._lock:
            loop = asyncio.get_event_loop()
            start_time = time.perf_counter()
            
            result = await loop.run_in_executor(
                self._executor,
                lambda: self._chat_sync(messages, config)
            )
            
            generation_time = (time.perf_counter() - start_time) * 1000
            result.generation_time_ms = generation_time
            
            return result
    
    def _chat_sync(
        self,
        messages: list[Message],
        config: GenerationConfig,
    ) -> GenerationResult:
        """Synchronous chat completion."""
        # Convert to llama-cpp format
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Load grammar if specified
        grammar = None
        if config.grammar:
            grammar = self._grammar_loader.load_grammar(config.grammar)
        
        try:
            output = self._llm.create_chat_completion(
                messages=formatted_messages,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                repeat_penalty=config.repeat_penalty,
                stop=config.stop_sequences or None,
                grammar=grammar,
            )
            
            text = output["choices"][0]["message"]["content"]
            finish_reason = output["choices"][0].get("finish_reason", "unknown")
            
            return GenerationResult(
                text=text,
                tokens_generated=output["usage"]["completion_tokens"],
                tokens_prompt=output["usage"]["prompt_tokens"],
                generation_time_ms=0.0,
                finish_reason=finish_reason,
                metadata={
                    "model": self.model_name,
                    "messages_count": len(messages),
                }
            )
            
        except Exception as e:
            raise InferenceError(f"Chat completion failed: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the model's tokenizer.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        if not self.is_loaded:
            # Fallback estimate
            return len(text) // 4
        
        try:
            tokens = self._llm.tokenize(text.encode("utf-8"))
            return len(tokens)
        except Exception:
            return len(text) // 4
    
    async def get_embedding(self, text: str) -> list[float]:
        """
        Get text embedding.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not self.is_loaded:
            raise InferenceError("Model not loaded")
        
        async with self._lock:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._executor,
                lambda: self._llm.embed(text)
            )
