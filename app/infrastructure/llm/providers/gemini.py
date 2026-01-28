"""
ONI LLM - Gemini Provider
Google Gemini API with key rotation.
"""
import os
from typing import List
import httpx
import structlog
from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from .base_provider import LLMProvider
from .api_key_pool import APIKeyPool

logger = structlog.get_logger()


class GeminiProvider(LLMProvider):
    """Google Gemini API provider with key rotation."""
    
    def __init__(self, api_keys: List[str] | None = None, model: str = "gemini-2.0-flash-exp"):
        self._key_pool = APIKeyPool()
        self._model = os.getenv("GEMINI_MODEL", model)
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        for suffix in ["", "_1", "_2", "_3", "_4", "_5"]:
            key = os.getenv(f"GEMINI_API_KEY{suffix}", "")
            if key:
                self._key_pool.add_key(key)
        
        for key in (api_keys or []):
            self._key_pool.add_key(key)
        
        logger.info("gemini_provider_init", keys_loaded=len(self._key_pool.keys), model=self._model)
    
    @property
    def name(self) -> str:
        return f"Gemini ({self._model})"
    
    @property
    def is_available(self) -> bool:
        return self._key_pool.has_keys and not self._key_pool.all_keys_exhausted
    
    async def generate(self, prompt: str, config: GenerationConfig | None = None, **kwargs) -> GenerationResult:
        config = config or GenerationConfig()
        api_key = self._key_pool.get_current_key()
        if not api_key:
            raise RuntimeError("No Gemini API keys available")
        
        url = f"{self._base_url}/models/{self._model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens,
                "topP": config.top_p,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, params={"key": api_key}, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                data = response.json()
            
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return GenerationResult(
                text=text, tokens_generated=len(text) // 4, tokens_prompt=len(prompt) // 4,
                generation_time_ms=0, finish_reason="stop", metadata={"provider": "gemini", "model": self._model}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [429, 401, 403, 404]:
                self._key_pool.mark_failed(api_key)
            raise
