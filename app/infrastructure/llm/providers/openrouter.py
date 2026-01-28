"""
ONI LLM - OpenRouter Provider
OpenRouter API with key rotation.
"""
import os
from typing import List
import httpx
import structlog
from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from .base_provider import LLMProvider
from .api_key_pool import APIKeyPool

logger = structlog.get_logger()


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider with key rotation."""
    
    FREE_MODELS = [
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-7b-it:free", 
        "meta-llama/llama-3-8b-instruct:free",
    ]
    
    def __init__(self, api_keys: List[str] | None = None, model: str | None = None):
        self._key_pool = APIKeyPool()
        self._model = model or os.getenv("OPENROUTER_MODEL", self.FREE_MODELS[0])
        self._base_url = "https://openrouter.ai/api/v1"
        
        for suffix in ["", "_1", "_2", "_3", "_4", "_5"]:
            key = os.getenv(f"OPENROUTER_API_KEY{suffix}", "")
            if key:
                self._key_pool.add_key(key)
        
        for key in (api_keys or []):
            self._key_pool.add_key(key)
        
        logger.info("openrouter_provider_init", keys_loaded=len(self._key_pool.keys))
    
    @property
    def name(self) -> str:
        return f"OpenRouter ({self._model})"
    
    @property
    def is_available(self) -> bool:
        return self._key_pool.has_keys and not self._key_pool.all_keys_exhausted
    
    async def generate(self, prompt: str, config: GenerationConfig | None = None, **kwargs) -> GenerationResult:
        config = config or GenerationConfig()
        api_key = self._key_pool.get_current_key()
        if not api_key:
            raise RuntimeError("No OpenRouter API keys available")
        
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://oni.local",
            "X-Title": "ONI Desktop Agent"
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return GenerationResult(
                text=text,
                tokens_generated=usage.get("completion_tokens", len(text) // 4),
                tokens_prompt=usage.get("prompt_tokens", len(prompt) // 4),
                generation_time_ms=0, finish_reason=data["choices"][0].get("finish_reason", "stop"),
                metadata={"provider": "openrouter", "model": self._model}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [429, 401, 403]:
                self._key_pool.mark_failed(api_key)
            raise
