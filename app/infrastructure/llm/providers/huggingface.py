"""
ONI LLM - HuggingFace Provider
"""
import os
import httpx
from app.infrastructure.llm.base import GenerationConfig, GenerationResult
from .base_provider import LLMProvider


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API provider."""
    
    FREE_MODELS = ["mistralai/Mistral-7B-Instruct-v0.2", "meta-llama/Llama-2-7b-chat-hf"]
    
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self._model = model or os.getenv("HUGGINGFACE_MODEL", self.FREE_MODELS[0])
        self._base_url = "https://api-inference.huggingface.co/models"
    
    @property
    def name(self) -> str:
        return f"HuggingFace ({self._model.split('/')[-1]})"
    
    @property
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    async def generate(self, prompt: str, config: GenerationConfig | None = None, **kwargs) -> GenerationResult:
        config = config or GenerationConfig()
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": config.max_tokens, "temperature": config.temperature, "top_p": config.top_p, "return_full_text": False}}
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self._base_url}/{self._model}", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        text = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
        return GenerationResult(text=text, tokens_generated=len(text) // 4, tokens_prompt=len(prompt) // 4, generation_time_ms=0, finish_reason="stop", metadata={"provider": "huggingface", "model": self._model})
