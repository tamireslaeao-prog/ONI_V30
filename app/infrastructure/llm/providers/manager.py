"""
ONI LLM - Manager with Fallback
"""
import os
from typing import Any, List
import structlog
from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from .base_provider import LLMProvider
from .rate_limiter import IntelligentRateLimiter
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider
from .huggingface import HuggingFaceProvider
from .local_llama import LocalLlamaProvider

logger = structlog.get_logger()


class LLMManagerWithFallback:
    """Manager for multiple LLM providers with intelligent fallback."""
    
    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._fallback_order: List[str] = ["openrouter", "gemini", "local"]
        self._current_provider: str | None = None
        self._rate_limiter = IntelligentRateLimiter(requests_per_minute=10)
    
    def register_provider(self, name: str, provider: LLMProvider) -> None:
        self._providers[name] = provider
        logger.info("llm_provider_registered", name=name, available=provider.is_available, provider_name=provider.name)
    
    def set_fallback_order(self, order: List[str]) -> None:
        self._fallback_order = order
        logger.info("fallback_order_set", order=order)
    
    @property
    def available_providers(self) -> list[str]:
        return [name for name, p in self._providers.items() if p.is_available]
    
    def get_provider(self, name: str | None = None) -> LLMProvider | None:
        if name and name in self._providers:
            return self._providers[name] if self._providers[name].is_available else None
        for provider_name in self._fallback_order:
            if provider_name in self._providers and self._providers[provider_name].is_available:
                return self._providers[provider_name]
        return None
    
    async def generate(self, prompt: str, config: GenerationConfig | None = None, **kwargs) -> GenerationResult:
        await self._rate_limiter.wait_if_needed()
        errors = []
        
        for provider_name in self._fallback_order:
            if provider_name not in self._providers:
                continue
            provider = self._providers[provider_name]
            if not provider.is_available:
                continue
            
            try:
                result = await provider.generate(prompt, config, **kwargs)
                self._rate_limiter.on_success()
                if self._current_provider != provider_name:
                    self._current_provider = provider_name
                    logger.info("llm_provider_active", provider=provider_name)
                return result
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)[:50]}")
                if "429" in str(e):
                    self._rate_limiter.on_429_error()
                continue
        
        raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")


llm_manager = LLMManagerWithFallback()


def setup_providers(local_engine: Any = None, fallback_order: List[str] | None = None) -> LLMManagerWithFallback:
    """Setup all LLM providers with automatic key loading."""
    if local_engine:
        llm_manager.register_provider("local", LocalLlamaProvider(local_engine))
    else:
        llm_manager.register_provider("local", LocalLlamaProvider(None))
    
    gemini = GeminiProvider()
    if gemini.is_available:
        llm_manager.register_provider("gemini", gemini)
    
    openrouter = OpenRouterProvider()
    if openrouter.is_available:
        llm_manager.register_provider("openrouter", openrouter)
    
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        llm_manager.register_provider("huggingface", HuggingFaceProvider(hf_key))
    
    order = fallback_order or ["local", "openrouter", "gemini", "huggingface"]
    llm_manager.set_fallback_order(order)
    logger.info("llm_providers_ready", available=llm_manager.available_providers, fallback_order=order)
    return llm_manager
