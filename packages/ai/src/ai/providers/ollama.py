"""Ollama provider implementation."""

import httpx
import base64
import json
from typing import Optional, AsyncIterator
from ai.providers.base import LLMProvider, VisionProvider, EmbeddingProvider
from ai.schemas import (
    LLMRequest, LLMResponse, LLMMessage,
    VisionRequest, VisionResponse,
    EmbeddingRequest, EmbeddingResponse,
    ModelInfo, ModelCapability, ProviderHealth,
)
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider(LLMProvider, VisionProvider, EmbeddingProvider):
    """Ollama local model provider."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 120.0):
        self.base_url = base_url or settings.ollama_base_url
        self.timeout = timeout
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)
        self._models_cache: list[str] = []
        self._capabilities_cache: dict[str, set[ModelCapability]] = {}
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def is_local(self) -> bool:
        return True
    
    @property
    def capabilities(self) -> set[ModelCapability]:
        # Return union of all model capabilities
        all_caps = set()
        for caps in self._capabilities_cache.values():
            all_caps.update(caps)
        if not all_caps:
            # Default capabilities if not loaded
            all_caps = {
                ModelCapability.REASONING,
                ModelCapability.CODING,
                ModelCapability.SUMMARIZATION,
                ModelCapability.EXTRACTION,
                ModelCapability.TOOL_USE,
                ModelCapability.JSON_MODE,
            }
        return all_caps
    
    @property
    def models(self) -> list[str]:
        return self._models_cache
    
    @property
    def dimensions(self) -> int:
        return 768  # nomic-embed-text default
    
    @property
    def max_tokens(self) -> int:
        return 8192
    
    @property
    def supported_formats(self) -> list[str]:
        return ["image/png", "image/jpeg", "image/webp"]
    
    async def _load_models(self) -> None:
        """Load available models from Ollama."""
        try:
            response = await self._client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            self._models_cache = [m["name"] for m in data.get("models", [])]
            
            # Determine capabilities per model
            for model in self._models_cache:
                caps = {ModelCapability.REASONING, ModelCapability.CODING, ModelCapability.SUMMARIZATION}
                model_lower = model.lower()
                if any(v in model_lower for v in ["llava", "vision", "bakllava", "moondream"]):
                    caps.add(ModelCapability.VISION)
                if "embed" in model_lower:
                    caps = {ModelCapability.EMBEDDING}
                if "rerank" in model_lower:
                    caps = {ModelCapability.CLASSIFICATION}
                self._capabilities_cache[model] = caps
                
        except Exception as e:
            logger.warning("Failed to load Ollama models", error=str(e))
            self._models_cache = []
    
    def _get_model_caps(self, model: Optional[str]) -> set[ModelCapability]:
        if model and model in self._capabilities_cache:
            return self._capabilities_cache[model]
        return self.capabilities
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        model = request.model or settings.default_llm_model
        
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["num_predict"] = request.max_tokens
        
        if request.json_mode:
            payload["format"] = "json"
        
        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = request.tool_choice
        
        logger.debug("Ollama completion request", model=model, messages=len(request.messages))
        
        try:
            response = await self._client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["message"]["content"],
                model=data["model"],
                usage=data.get("usage"),
                tool_calls=data["message"].get("tool_calls"),
                finish_reason=data.get("done_reason"),
            )
        except httpx.HTTPStatusError as e:
            logger.error("Ollama completion failed", status=e.response.status_code, error=e.response.text)
            raise
        except Exception as e:
            logger.error("Ollama completion error", error=str(e))
            raise
    
    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]:
        model = request.model or settings.default_llm_model
        
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        
        if request.max_tokens:
            payload["num_predict"] = request.max_tokens
        
        async with self._client.stream("POST", "/api/chat", json=payload, timeout=self.timeout) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done"):
                        break
    
    async def analyze(self, request: VisionRequest) -> VisionResponse:
        model = request.model or settings.default_vision_model
        
        # Prepare images - ensure they're data URLs
        images = []
        for img in request.images:
            if img.startswith("http"):
                images.append(img)
            elif img.startswith("data:"):
                images.append(img)
            else:
                # Assume base64
                images.append(f"data:image/png;base64,{img}")
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "images": images,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["num_predict"] = request.max_tokens
        
        logger.debug("Ollama vision request", model=model, image_count=len(images))
        
        try:
            response = await self._client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return VisionResponse(
                content=data["response"],
                model=model,
                usage=data.get("usage"),
            )
        except Exception as e:
            logger.error("Ollama vision failed", error=str(e))
            raise
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or settings.default_embedding_model
        
        payload = {
            "model": model,
            "input": request.texts,
        }
        
        logger.debug("Ollama embedding request", model=model, text_count=len(request.texts))
        
        try:
            response = await self._client.post("/api/embed", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return EmbeddingResponse(
                embeddings=data["embeddings"],
                model=data["model"],
                usage=data.get("usage"),
                dimensions=len(data["embeddings"][0]) if data["embeddings"] else None,
            )
        except Exception as e:
            logger.error("Ollama embedding failed", error=str(e))
            raise
    
    async def health_check(self) -> ProviderHealth:
        try:
            await self._load_models()
            response = await self._client.get("/api/tags", timeout=5.0)
            healthy = response.status_code == 200
            
            models = [
                ModelInfo(
                    name=m,
                    provider="ollama",
                    capabilities=list(self._get_model_caps(m)),
                    is_local=True,
                )
                for m in self._models_cache
            ]
            
            return ProviderHealth(
                provider="ollama",
                healthy=healthy,
                models=models,
            )
        except Exception as e:
            return ProviderHealth(
                provider="ollama",
                healthy=False,
                error=str(e),
            )
    
    async def close(self) -> None:
        await self._client.aclose()