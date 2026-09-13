"""Official Google Gemini API provider implementation.

Communicates with the Google Gemini API using OpenAI-compatible endpoints or Google AI Studio endpoints.
"""

import asyncio
import json
import time
from typing import AsyncIterator, List, Optional, Set

import httpx

from ai.providers.base import LLMProvider, VisionProvider
from ai.schemas import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    ModelCapability,
    ModelInfo,
    ProviderHealth,
    VisionRequest,
    VisionResponse,
)
from shared.config import settings
from shared.exceptions import (
    ModelNotFoundError,
    ProviderError,
    ProviderUnavailableError,
)
from shared.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-pro-exp",
]


class GeminiProvider(LLMProvider, VisionProvider):
    """Official Google Gemini API provider supporting multimodal and reasoning models."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        client: Optional[httpx.AsyncClient] = None,
        name: str = "gemini",
    ):
        self._name = name
        self.base_url = (base_url or settings.gemini_base_url).rstrip("/")
        self.api_key = api_key or settings.gemini_api_key
        self.default_model = default_model or settings.gemini_default_model
        self.timeout = timeout or settings.gemini_timeout
        self.max_retries = max_retries if max_retries is not None else settings.gemini_max_retries

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = client or httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )
        self._models_cache: List[str] = list(SUPPORTED_GEMINI_MODELS)

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_local(self) -> bool:
        return False

    @property
    def capabilities(self) -> Set[ModelCapability]:
        return {
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.VISION,
            ModelCapability.EXTRACTION,
            ModelCapability.CLASSIFICATION,
            ModelCapability.TOOL_USE,
            ModelCapability.JSON_MODE,
        }

    @property
    def models(self) -> List[str]:
        return list(self._models_cache)

    @property
    def supported_formats(self) -> List[str]:
        return ["image/png", "image/jpeg", "image/webp", "image/gif"]

    async def _load_models(self) -> List[str]:
        """Fetch available models from Gemini API models endpoint."""
        try:
            response = await self._client.get("models")
            if response.status_code == 200:
                data = response.json()
                raw_models = data.get("data", [])
                fetched_ids = [m["id"] for m in raw_models if "id" in m]
                if fetched_ids:
                    self._models_cache = fetched_ids
                    return self._models_cache
        except Exception as exc:
            logger.debug("Could not fetch remote Gemini model list, using defaults", error=str(exc))
        return self._models_cache

    def _resolve_model(self, requested_model: Optional[str]) -> str:
        model = requested_model or self.default_model
        return model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a standard chat completion request."""
        model = self._resolve_model(request.model)
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        start_time = time.perf_counter()
        retries = 0
        while True:
            try:
                res = await self._client.post("chat/completions", json=payload)
                if res.status_code == 404:
                    raise ModelNotFoundError(self.name, model)
                if res.status_code != 200:
                    raise ProviderError(
                        self.name,
                        f"Gemini API returned error {res.status_code}: {res.text}",
                        details={"status_code": res.status_code, "body": res.text},
                    )

                data = res.json()
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "")
                finish_reason = choice.get("finish_reason", "stop")

                usage = data.get("usage", {})
                latency_ms = (time.perf_counter() - start_time) * 1000

                return LLMResponse(
                    content=content,
                    model=model,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    finish_reason=finish_reason,
                    metadata={"provider": self.name, "latency_ms": latency_ms},
                )
            except httpx.RequestError as exc:
                if retries < self.max_retries:
                    retries += 1
                    await asyncio.sleep(0.5 * retries)
                    continue
                raise ProviderUnavailableError(self.name)

    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Alias for complete."""
        return await self.complete(request)

    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream chunks from chat completion."""
        model = self._resolve_model(request.model)
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        try:
            async with self._client.stream("POST", "chat/completions", json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    raise ProviderError(self.name, f"Gemini streaming error: {err_body.decode('utf-8', errors='ignore')}")

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
        except httpx.RequestError:
            raise ProviderUnavailableError(self.name)

    async def chat_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Alias for stream_complete."""
        async for chunk in self.stream_complete(request):
            yield chunk

    async def analyze(self, request: VisionRequest) -> VisionResponse:
        """Send multimodal vision analysis request."""
        model = self._resolve_model(request.model)
        content_items = [{"type": "text", "text": request.prompt}]

        for img in request.images:
            if img.startswith("data:") or img.startswith("http"):
                url = img
            else:
                url = f"data:image/png;base64,{img}"
            content_items.append({"type": "image_url", "image_url": {"url": url}})

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content_items,
                }
            ],
            "stream": False,
        }

        start_time = time.perf_counter()
        try:
            res = await self._client.post("chat/completions", json=payload)
            if res.status_code != 200:
                raise ProviderError(self.name, f"Gemini Vision API error: {res.text}")

            data = res.json()
            content = data["choices"][0]["message"]["content"]
            latency_ms = (time.perf_counter() - start_time) * 1000

            return VisionResponse(
                content=content,
                model=model,
                usage=data.get("usage"),
                metadata={"provider": self.name, "latency_ms": latency_ms},
            )
        except httpx.RequestError:
            raise ProviderUnavailableError(self.name)

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Alias for analyze."""
        return await self.analyze(request)

    async def health_check(self) -> ProviderHealth:
        """Query Gemini endpoint health status."""
        try:
            res = await self._client.get("models")
            healthy = res.status_code == 200
            model_infos = [
                ModelInfo(
                    name=m,
                    provider=self.name,
                    capabilities=list(self.capabilities),
                    context_window=1048576,
                    is_local=False,
                )
                for m in self.models
            ]
            return ProviderHealth(provider=self.name, healthy=healthy, models=model_infos)
        except Exception as exc:
            return ProviderHealth(
                provider=self.name,
                healthy=False,
                models=[],
                error=f"Gemini health check failed: {str(exc)}",
            )

    async def close(self) -> None:
        await self._client.aclose()
