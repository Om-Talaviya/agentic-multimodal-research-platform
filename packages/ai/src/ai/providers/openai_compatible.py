"""OpenAI-compatible provider implementation."""

import httpx
import json
from typing import Optional, AsyncIterator
from ai.providers.base import LLMProvider, VisionProvider
from ai.schemas import (
    LLMRequest, LLMResponse, LLMMessage,
    VisionRequest, VisionResponse,
    ModelInfo, ModelCapability, ProviderHealth,
)
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(LLMProvider, VisionProvider):
    """OpenAI-compatible API provider (OpenAI, Anthropic, etc.)."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        name: str = "openai",
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._name = name
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        self._models_cache: list[str] = []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def is_local(self) -> bool:
        return False
    
    @property
    def capabilities(self) -> set[ModelCapability]:
        return {
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.VISION,
            ModelCapability.EXTRACTION,
            ModelCapability.TOOL_USE,
            ModelCapability.JSON_MODE,
        }
    
    @property
    def models(self) -> list[str]:
        return self._models_cache
    
    @property
    def supported_formats(self) -> list[str]:
        return ["image/png", "image/jpeg", "image/webp", "image/gif"]
    
    async def _load_models(self) -> None:
        try:
            response = await self._client.get("/models")
            response.raise_for_status()
            data = response.json()
            self._models_cache = [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.warning("Failed to load models", provider=self._name, error=str(e))
            self._models_cache = []
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        model = request.model or "gpt-4o-mini"
        
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = request.tool_choice
        
        logger.debug("OpenAI completion request", model=model, provider=self._name)
        
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            return LLMResponse(
                content=choice["message"]["content"] or "",
                model=data["model"],
                usage=data.get("usage"),
                tool_calls=choice["message"].get("tool_calls"),
                finish_reason=choice.get("finish_reason"),
            )
        except httpx.HTTPStatusError as e:
            logger.error("OpenAI completion failed", status=e.response.status_code, error=e.response.text)
            raise
        except Exception as e:
            logger.error("OpenAI completion error", error=str(e))
            raise
    
    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]:
        model = request.model or "gpt-4o-mini"
        
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        async with self._client.stream("POST", "/chat/completions", json=payload, timeout=self._timeout) as response:
            response.raise_for_status()
            lines = response.aiter_lines()
            try:
                async for line in lines:
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
            finally:
                await lines.aclose()
    
    async def analyze(self, request: VisionRequest) -> VisionResponse:
        model = request.model or "gpt-4o-mini"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": request.prompt},
                    *[{"type": "image_url", "image_url": {"url": img}} for img in request.images],
                ],
            }
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        logger.debug("OpenAI vision request", model=model, provider=self._name)
        
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return VisionResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                usage=data.get("usage"),
            )
        except Exception as e:
            logger.error("OpenAI vision failed", error=str(e))
            raise
    
    async def health_check(self) -> ProviderHealth:
        try:
            await self._load_models()
            response = await self._client.get("/models", timeout=10.0)
            healthy = response.status_code == 200
            
            models = [
                ModelInfo(
                    name=m,
                    provider=self._name,
                    capabilities=list(self.capabilities),
                    is_local=False,
                )
                for m in self._models_cache
            ]
            
            return ProviderHealth(
                provider=self._name,
                healthy=healthy,
                models=models,
            )
        except Exception as e:
            return ProviderHealth(
                provider=self._name,
                healthy=False,
                error=str(e),
            )
    
    async def close(self) -> None:
        await self._client.aclose()