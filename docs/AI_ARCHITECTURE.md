# AI Architecture

## Overview

The AI architecture provides a clean abstraction layer between the application and model providers. This enables:
- Switching providers without code changes
- Capability-based model routing
- Local-first development with cloud fallback
- Consistent interfaces for all model interactions

## Provider Abstractions

### LLMProvider Protocol

```python
# packages/ai/providers/llm.py
from typing import Protocol, AsyncIterator
from packages.ai.schemas import LLMRequest, LLMResponse, LLMMessage

class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def capabilities(self) -> set[str]: ...
    
    @property
    def models(self) -> list[str]: ...
    
    async def complete(self, request: LLMRequest) -> LLMResponse: ...
    
    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]: ...
    
    async def health_check(self) -> bool: ...
```

### VisionProvider Protocol

```python
# packages/ai/providers/vision.py
from typing import Protocol
from packages.ai.schemas import VisionRequest, VisionResponse

class VisionProvider(Protocol):
    """Protocol for vision-capable models."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def supported_formats(self) -> list[str]: ...
    
    async def analyze(self, request: VisionRequest) -> VisionResponse: ...
    
    async def health_check(self) -> bool: ...
```

### EmbeddingProvider Protocol

```python
# packages/ai/providers/embeddings.py
from typing import Protocol
from packages.ai.schemas import EmbeddingRequest, EmbeddingResponse

class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def dimensions(self) -> int: ...
    
    @property
    def max_tokens(self) -> int: ...
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse: ...
    
    async def health_check(self) -> bool: ...
```

### RerankerProvider Protocol

```python
# packages/ai/providers/reranker.py
from typing import Protocol
from packages.ai.schemas import RerankRequest, RerankResponse

class RerankerProvider(Protocol):
    """Protocol for reranking providers."""
    
    @property
    def name(self) -> str: ...
    
    async def rerank(self, request: RerankRequest) -> RerankResponse: ...
    
    async def health_check(self) -> bool: ...
```

## Model Router

The `ModelRouter` selects appropriate models based on task requirements:

```python
# packages/ai/providers/router.py
from packages.ai.providers.llm import LLMProvider
from packages.ai.providers.vision import VisionProvider
from packages.ai.providers.embeddings import EmbeddingProvider
from packages.ai.providers.reranker import RerankerProvider
from packages.ai.schemas import ModelCapabilities

class ModelRouter:
    """Routes requests to appropriate model providers based on capabilities."""
    
    def __init__(
        self,
        llm_providers: list[LLMProvider],
        vision_providers: list[VisionProvider],
        embedding_providers: list[EmbeddingProvider],
        reranker_providers: list[RerankerProvider],
    ):
        self.llm_providers = llm_providers
        self.vision_providers = vision_providers
        self.embedding_providers = embedding_providers
        self.reranker_providers = reranker_providers
    
    def select_llm(
        self,
        capabilities: ModelCapabilities,
        prefer_local: bool = True,
    ) -> LLMProvider:
        """Select best LLM provider for given capabilities."""
        candidates = [
            p for p in self.llm_providers
            if capabilities.issubset(p.capabilities)
        ]
        if not candidates:
            raise NoSuitableModelError(f"No model supports {capabilities}")
        
        # Prefer local models
        if prefer_local:
            local = [p for p in candidates if p.is_local]
            if local:
                return local[0]
        
        return candidates[0]  # Fallback to first available
    
    def select_vision(self, prefer_local: bool = True) -> VisionProvider: ...
    def select_embedding(self, prefer_local: bool = True) -> EmbeddingProvider: ...
    def select_reranker(self, prefer_local: bool = True) -> RerankerProvider: ...
```

## Capability System

Models declare capabilities for intelligent routing:

```python
# packages/ai/schemas.py
from enum import Enum
from pydantic import BaseModel
from typing import Literal

class ModelCapability(str, Enum):
    REASONING = "reasoning"
    CODING = "coding"
    SUMMARIZATION = "summarization"
    VISION = "vision"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    TOOL_USE = "tool_use"
    JSON_MODE = "json_mode"

class ModelCapabilities(frozenset[ModelCapability]):
    """Immutable set of required capabilities."""
    
    @classmethod
    def for_task(cls, task_type: str) -> "ModelCapabilities":
        """Get required capabilities for a task type."""
        task_map = {
            "planning": {ModelCapability.REASONING, ModelCapability.TOOL_USE},
            "research": {ModelCapability.REASONING, ModelCapability.EXTRACTION},
            "synthesis": {ModelCapability.REASONING, ModelCapability.SUMMARIZATION},
            "report": {ModelCapability.SUMMARIZATION, ModelCapability.JSON_MODE},
            "vision": {ModelCapability.VISION, ModelCapability.EXTRACTION},
            "embedding": {ModelCapability.EMBEDDING},
        }
        return cls(task_map.get(task_type, {ModelCapability.REASONING}))
```

## Provider Implementations

### Ollama Provider (Local-First)

```python
# packages/ai/providers/ollama.py
import httpx
from packages.ai.providers.llm import LLMProvider
from packages.ai.providers.vision import VisionProvider
from packages.ai.providers.embeddings import EmbeddingProvider
from packages.ai.schemas import (
    LLMRequest, LLMResponse, LLMMessage,
    VisionRequest, VisionResponse,
    EmbeddingRequest, EmbeddingResponse,
)
from packages.shared.config import settings

class OllamaProvider(LLMProvider, VisionProvider, EmbeddingProvider):
    """Ollama local model provider."""
    
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def is_local(self) -> bool:
        return True
    
    @property
    def capabilities(self) -> set[ModelCapability]:
        # Dynamic based on available models
        return {
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.VISION,  # If vision model loaded
            ModelCapability.EXTRACTION,
            ModelCapability.TOOL_USE,
            ModelCapability.JSON_MODE,
        }
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model or settings.default_llm_model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        if request.json_mode:
            payload["format"] = "json"
        
        response = await self.client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return LLMResponse(
            content=data["message"]["content"],
            model=data["model"],
            usage=data.get("usage"),
        )
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        response = await self.client.post("/api/embed", json={
            "model": request.model or settings.default_embedding_model,
            "input": request.texts,
        })
        response.raise_for_status()
        data = response.json()
        
        return EmbeddingResponse(
            embeddings=data["embeddings"],
            model=data["model"],
        )
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
```

### OpenAI-Compatible Provider

```python
# packages/ai/providers/openai_compatible.py
import httpx
from packages.ai.providers.llm import LLMProvider
from packages.ai.schemas import LLMRequest, LLMResponse, LLMMessage
from packages.shared.config import settings

class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API provider (OpenAI, Anthropic, etc.)."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        name: str = "openai",
    ):
        self.api_key = api_key
        self.base_url = base_url
        self._name = name
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )
    
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
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model or "gpt-4o-mini",
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            usage=data.get("usage"),
        )
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/models", timeout=10.0)
            return response.status_code == 200
        except Exception:
            return False
```

## Schemas

```python
# packages/ai/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class LLMMessage(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None

class LLMRequest(BaseModel):
    messages: List[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    json_mode: bool = False
    tools: Optional[List[dict]] = None
    tool_choice: Optional[Literal["auto", "none", "required"]] = "auto"

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None
    tool_calls: Optional[List[dict]] = None
    finish_reason: Optional[str] = None

class VisionRequest(BaseModel):
    images: List[str]  # Base64 or URLs
    prompt: str
    model: Optional[str] = None

class VisionResponse(BaseModel):
    content: str
    model: str

class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = None

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    usage: Optional[dict] = None

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: Optional[str] = None
    top_k: int = 10

class RerankResponse(BaseModel):
    results: List[dict]  # {index, score, document}
    model: str
```

## Usage in Agents

```python
# Example agent using model router
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities, ModelCapability

class ResearchAgent:
    def __init__(self, router: ModelRouter):
        self.router = router
    
    async def research(self, query: str) -> str:
        # Select model with reasoning capability
        llm = self.router.select_llm(
            ModelCapabilities.for_task("research"),
            prefer_local=True,
        )
        
        response = await llm.complete(LLMRequest(
            messages=[
                LLMMessage(role="system", content="You are a research assistant..."),
                LLMMessage(role="user", content=query),
            ],
            temperature=0.3,
        ))
        return response.content
```

## Testing with Mocks

```python
# tests/unit/ai/test_mock_provider.py
from packages.ai.providers.llm import LLMProvider
from packages.ai.schemas import LLMRequest, LLMResponse, LLMMessage

class MockLLMProvider(LLMProvider):
    """Deterministic mock for testing."""
    
    def __init__(self, responses: dict[str, str]):
        self.responses = responses
        self.calls: list[LLMRequest] = []
    
    @property
    def name(self) -> str:
        return "mock"
    
    @property
    def capabilities(self) -> set:
        return {"reasoning", "coding", "summarization"}
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        key = request.messages[-1].content[:50]
        return LLMResponse(
            content=self.responses.get(key, "Mock response"),
            model="mock",
        )
    
    async def health_check(self) -> bool:
        return True
```

---

*This architecture enables testing without external API calls and seamless provider switching.*