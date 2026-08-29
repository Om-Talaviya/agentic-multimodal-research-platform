"""Base protocols for AI providers."""

from typing import Protocol, AsyncIterator, runtime_checkable
from ai.schemas import (
    LLMRequest, LLMResponse, LLMMessage,
    VisionRequest, VisionResponse,
    EmbeddingRequest, EmbeddingResponse,
    RerankRequest, RerankResponse,
    ModelInfo, ModelCapability, ProviderHealth,
)
from shared.types import JSONDict


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM (text generation) providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def is_local(self) -> bool: ...
    
    @property
    def capabilities(self) -> set[ModelCapability]: ...
    
    @property
    def models(self) -> list[str]: ...
    
    async def complete(self, request: LLMRequest) -> LLMResponse: ...
    
    async def stream_complete(self, request: LLMRequest) -> AsyncIterator[str]: ...
    
    async def health_check(self) -> ProviderHealth: ...


@runtime_checkable
class VisionProvider(Protocol):
    """Protocol for vision-capable providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def is_local(self) -> bool: ...
    
    @property
    def supported_formats(self) -> list[str]: ...
    
    @property
    def capabilities(self) -> set[ModelCapability]: ...
    
    async def analyze(self, request: VisionRequest) -> VisionResponse: ...
    
    async def health_check(self) -> ProviderHealth: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def is_local(self) -> bool: ...
    
    @property
    def dimensions(self) -> int: ...
    
    @property
    def max_tokens(self) -> int: ...
    
    @property
    def capabilities(self) -> set[ModelCapability]: ...
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse: ...
    
    async def health_check(self) -> ProviderHealth: ...


@runtime_checkable
class RerankerProvider(Protocol):
    """Protocol for reranking providers."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def is_local(self) -> bool: ...
    
    @property
    def capabilities(self) -> set[ModelCapability]: ...
    
    async def rerank(self, request: RerankRequest) -> RerankResponse: ...
    
    async def health_check(self) -> ProviderHealth: ...