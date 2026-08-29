"""Gemini Web2API provider implementation.

Communicates with the local Gemini Web2API service exposed via OpenAI-compatible endpoints.
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

# Supported models exposed by Gemini Web2API
SUPPORTED_GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-thinking",
    "gemini-3.1-pro",
    "gemini-auto",
    "gemini-3.5-flash-thinking-lite",
    "gemini-flash-lite",
]


class GeminiWeb2APIProvider(LLMProvider, VisionProvider):
    """Gemini Web2API provider using OpenAI-compatible API endpoints."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = (base_url or settings.gemini_web2api_base_url).rstrip("/")
        self.api_key = api_key or settings.gemini_web2api_api_key
        self.default_model = default_model or settings.gemini_default_model
        self.timeout = timeout if timeout is not None else settings.gemini_web2api_timeout
        self.max_retries = (
            max_retries if max_retries is not None else settings.gemini_web2api_max_retries
        )
        self._name = "gemini-web2api"
        self._models_cache: List[str] = list(SUPPORTED_GEMINI_MODELS)

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = client or httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_local(self) -> bool:
        return True

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

    async def _load_models(self) -> None:
        """Load available models from the Web2API endpoint."""
        try:
            response = await self._client.get("/models", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                model_ids = [m["id"] for m in data.get("data", []) if "id" in m]
                if model_ids:
                    self._models_cache = model_ids
        except Exception as e:
            logger.warning(
                "Failed to refresh models from Gemini Web2API",
                provider=self._name,
                error=str(e),
            )

    def _map_messages(self, messages: List[LLMMessage]) -> List[dict]:
        """Format domain messages into OpenAI-compatible format."""
        formatted = []
        for msg in messages:
            item = {"role": msg.role.value if hasattr(msg.role, "value") else str(msg.role), "content": msg.content}
            if msg.name:
                item["name"] = msg.name
            if msg.tool_calls:
                item["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            formatted.append(item)
        return formatted

    async def _send_request_with_retries(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Send HTTP request with timeout handling, error mapping, and retries."""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, endpoint, **kwargs)
                if response.status_code >= 500 and attempt < self.max_retries:
                    logger.warning(
                        "Gemini Web2API returned server error, retrying...",
                        status_code=response.status_code,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(0.5 * (2**attempt))
                    continue

                if response.status_code == 404 or (
                    response.status_code == 400 and "Unknown model" in response.text
                ):
                    error_msg = response.text
                    try:
                        error_json = response.json()
                        error_msg = error_json.get("error", {}).get("message", error_msg)
                    except Exception:
                        pass
                    raise ModelNotFoundError(self._name, error_msg)

                if response.status_code >= 400:
                    error_msg = response.text
                    try:
                        error_json = response.json()
                        error_msg = error_json.get("error", {}).get("message", error_msg)
                    except Exception:
                        pass
                    raise ProviderError(
                        self._name,
                        f"HTTP {response.status_code}: {error_msg}",
                        details={"status_code": response.status_code, "response": error_msg},
                    )

                return response

            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        "Gemini Web2API connection error, retrying...",
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    await asyncio.sleep(0.5 * (2**attempt))
                    continue
                raise ProviderUnavailableError(self._name) from e
            except (ModelNotFoundError, ProviderError):
                raise
            except Exception as e:
                raise ProviderError(self._name, f"Unexpected error: {str(e)}") from e

        if last_exception:
            raise ProviderUnavailableError(self._name) from last_exception
        raise ProviderUnavailableError(self._name)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute chat completion and normalize response into LLMResponse."""
        model = request.model or self.default_model

        payload = {
            "model": model,
            "messages": self._map_messages(request.messages),
            "temperature": request.temperature,
            "stream": False,
        }

        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        if request.tools:
            payload["tools"] = request.tools
            if request.tool_choice:
                payload["tool_choice"] = request.tool_choice

        logger.debug("Gemini Web2API completion request", model=model, provider=self._name)

        response = await self._send_request_with_retries("POST", "/chat/completions", json=payload)
        data = response.json()

        if not data.get("choices") or len(data["choices"]) == 0:
            raise ProviderError(self._name, "Empty choices returned in completion response", details={"data": data})

        choice = data["choices"][0]
        message = choice.get("message", {})
        content = message.get("content") or ""
        finish_reason = choice.get("finish_reason")
        tool_calls = message.get("tool_calls")
        usage = data.get("usage")

        return LLMResponse(
            content=content,
            model=data.get("model", model),
            usage=usage,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            metadata={"provider": self._name, "raw_id": data.get("id")},
        )

    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream tokens from chat completion endpoint."""
        model = request.model or self.default_model

        payload = {
            "model": model,
            "messages": self._map_messages(request.messages),
            "temperature": request.temperature,
            "stream": True,
        }

        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        try:
            async with self._client.stream(
                "POST", "/chat/completions", json=payload, timeout=self.timeout
            ) as response:
                if response.status_code >= 400:
                    error_text = await response.aread()
                    raise ProviderError(
                        self._name,
                        f"Stream request failed: HTTP {response.status_code}",
                        details={"status_code": response.status_code, "response": error_text.decode("utf-8", errors="ignore")},
                    )

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as e:
            logger.error("Gemini Web2API stream connection failed", error=str(e))
            raise ProviderUnavailableError(self._name) from e
        except ProviderError:
            raise
        except Exception as e:
            logger.error("Gemini Web2API stream error", error=str(e))
            raise ProviderError(self._name, str(e)) from e

    async def analyze(self, request: VisionRequest) -> VisionResponse:
        """Execute vision analysis request and normalize response into VisionResponse."""
        model = request.model or self.default_model

        content_parts = [{"type": "text", "text": request.prompt}]
        for img in request.images:
            content_parts.append({"type": "image_url", "image_url": {"url": img}})

        messages = [{"role": "user", "content": content_parts}]

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        logger.debug("Gemini Web2API vision request", model=model, provider=self._name)

        response = await self._send_request_with_retries("POST", "/chat/completions", json=payload)
        data = response.json()

        if not data.get("choices") or len(data["choices"]) == 0:
            raise ProviderError(self._name, "Empty choices returned in vision response", details={"data": data})

        choice = data["choices"][0]
        message = choice.get("message", {})
        content = message.get("content") or ""
        usage = data.get("usage")

        return VisionResponse(
            content=content,
            model=data.get("model", model),
            usage=usage,
            metadata={"provider": self._name, "raw_id": data.get("id")},
        )

    async def health_check(self) -> ProviderHealth:
        """Check health status of Gemini Web2API endpoint gracefully without throwing."""
        start_time = time.perf_counter()
        try:
            response = await self._client.get("/models", timeout=5.0)
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                model_ids = [m["id"] for m in data.get("data", []) if "id" in m]
                if model_ids:
                    self._models_cache = model_ids

                models = [
                    ModelInfo(
                        name=m,
                        provider=self._name,
                        capabilities=list(self.capabilities),
                        is_local=True,
                    )
                    for m in self._models_cache
                ]

                return ProviderHealth(
                    provider=self._name,
                    healthy=True,
                    latency_ms=latency_ms,
                    models=models,
                )

            return ProviderHealth(
                provider=self._name,
                healthy=False,
                latency_ms=latency_ms,
                error=f"HTTP {response.status_code}: {response.text}",
            )
        except Exception as e:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            return ProviderHealth(
                provider=self._name,
                healthy=False,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def close(self) -> None:
        """Close HTTP client session."""
        await self._client.aclose()
