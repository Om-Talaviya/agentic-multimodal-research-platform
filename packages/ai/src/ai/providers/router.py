"""Model router for capability-based provider selection."""

from typing import Optional
from ai.providers.base import LLMProvider, VisionProvider, EmbeddingProvider, RerankerProvider
from ai.schemas import ModelCapabilities, ModelCapability, ProviderHealth
from shared.logging import get_logger

logger = get_logger(__name__)


class NoSuitableModelError(Exception):
    """Raised when no provider supports required capabilities."""
    pass


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
        exclude: list[str] | None = None,
    ) -> LLMProvider:
        """Select best LLM provider for given capabilities."""
        exclude = exclude or []
        
        candidates = [
            p for p in self.llm_providers
            if p.name not in exclude
            and capabilities.issubset(p.capabilities)
        ]
        
        if not candidates:
            raise NoSuitableModelError(
                f"No LLM provider supports capabilities: {capabilities}. "
                f"Available: {[(p.name, p.capabilities) for p in self.llm_providers]}"
            )
        
        if prefer_local:
            local = [p for p in candidates if p.is_local]
            if local:
                logger.debug("Selected local LLM provider", provider=local[0].name)
                return local[0]
        
        logger.debug("Selected LLM provider", provider=candidates[0].name)
        return candidates[0]
    
    def select_vision(
        self,
        prefer_local: bool = True,
        exclude: list[str] | None = None,
    ) -> VisionProvider:
        """Select best vision provider."""
        exclude = exclude or []
        
        candidates = [p for p in self.vision_providers if p.name not in exclude]
        
        if not candidates:
            raise NoSuitableModelError("No vision provider available")
        
        if prefer_local:
            local = [p for p in candidates if p.is_local]
            if local:
                return local[0]
        
        return candidates[0]
    
    def select_embedding(
        self,
        prefer_local: bool = True,
        exclude: list[str] | None = None,
    ) -> EmbeddingProvider:
        """Select best embedding provider."""
        exclude = exclude or []
        
        candidates = [p for p in self.embedding_providers if p.name not in exclude]
        
        if not candidates:
            raise NoSuitableModelError("No embedding provider available")
        
        if prefer_local:
            local = [p for p in candidates if p.is_local]
            if local:
                return local[0]
        
        return candidates[0]
    
    def select_reranker(
        self,
        prefer_local: bool = True,
        exclude: list[str] | None = None,
    ) -> RerankerProvider:
        """Select best reranker provider."""
        exclude = exclude or []
        
        candidates = [p for p in self.reranker_providers if p.name not in exclude]
        
        if not candidates:
            raise NoSuitableModelError("No reranker provider available")
        
        if prefer_local:
            local = [p for p in candidates if p.is_local]
            if local:
                return local[0]
        
        return candidates[0]
    
    async def health_check_all(self) -> dict[str, ProviderHealth]:
        """Check health of all providers."""
        results = {}
        
        for provider in self.llm_providers:
            results[f"llm:{provider.name}"] = await provider.health_check()
        
        for provider in self.vision_providers:
            results[f"vision:{provider.name}"] = await provider.health_check()
        
        for provider in self.embedding_providers:
            results[f"embedding:{provider.name}"] = await provider.health_check()
        
        for provider in self.reranker_providers:
            results[f"reranker:{provider.name}"] = await provider.health_check()
        
        return results
    
    def get_all_models(self) -> dict[str, list[str]]:
        """Get all available models grouped by provider."""
        return {
            "llm": {p.name: p.models for p in self.llm_providers},
            "vision": {p.name: p.models for p in self.vision_providers},
            "embedding": {p.name: p.models for p in self.embedding_providers},
            "reranker": {p.name: p.models for p in self.reranker_providers},
        }