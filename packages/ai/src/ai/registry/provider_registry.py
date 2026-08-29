"""Provider registry managing model provider instances."""

from typing import Dict, List, Optional
from ai.providers.base import (
    EmbeddingProvider,
    LLMProvider,
    RerankerProvider,
    VisionProvider,
)
from ai.schemas import ProviderHealth
from shared.logging import get_logger

logger = get_logger(__name__)


class ProviderRegistry:
    """Central registry of all AI model provider instances."""

    def __init__(self) -> None:
        self._llm_providers: Dict[str, LLMProvider] = {}
        self._vision_providers: Dict[str, VisionProvider] = {}
        self._embedding_providers: Dict[str, EmbeddingProvider] = {}
        self._reranker_providers: Dict[str, RerankerProvider] = {}

    def register_llm(self, provider: LLMProvider) -> None:
        """Register an LLM provider."""
        self._llm_providers[provider.name] = provider
        logger.debug("Registered LLM provider", provider=provider.name)

    def register_vision(self, provider: VisionProvider) -> None:
        """Register a vision provider."""
        self._vision_providers[provider.name] = provider
        logger.debug("Registered Vision provider", provider=provider.name)

    def register_embedding(self, provider: EmbeddingProvider) -> None:
        """Register an embedding provider."""
        self._embedding_providers[provider.name] = provider
        logger.debug("Registered Embedding provider", provider=provider.name)

    def register_reranker(self, provider: RerankerProvider) -> None:
        """Register a reranker provider."""
        self._reranker_providers[provider.name] = provider
        logger.debug("Registered Reranker provider", provider=provider.name)

    def register_all_in_one(self, provider: any) -> None:
        """Register a provider that implements multiple protocols."""
        if isinstance(provider, LLMProvider):
            self.register_llm(provider)
        if isinstance(provider, VisionProvider):
            self.register_vision(provider)
        if isinstance(provider, EmbeddingProvider):
            self.register_embedding(provider)
        if isinstance(provider, RerankerProvider):
            self.register_reranker(provider)

    def get_llm(self, name: str) -> Optional[LLMProvider]:
        """Get LLM provider by name."""
        return self._llm_providers.get(name)

    def get_vision(self, name: str) -> Optional[VisionProvider]:
        """Get vision provider by name."""
        return self._vision_providers.get(name)

    def get_embedding(self, name: str) -> Optional[EmbeddingProvider]:
        """Get embedding provider by name."""
        return self._embedding_providers.get(name)

    def get_reranker(self, name: str) -> Optional[RerankerProvider]:
        """Get reranker provider by name."""
        return self._reranker_providers.get(name)

    def list_llm_providers(self) -> List[LLMProvider]:
        """List all registered LLM providers."""
        return list(self._llm_providers.values())

    def list_vision_providers(self) -> List[VisionProvider]:
        """List all registered vision providers."""
        return list(self._vision_providers.values())

    def list_embedding_providers(self) -> List[EmbeddingProvider]:
        """List all registered embedding providers."""
        return list(self._embedding_providers.values())

    def list_reranker_providers(self) -> List[RerankerProvider]:
        """List all registered reranker providers."""
        return list(self._reranker_providers.values())

    async def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Run health checks across all registered providers safely."""
        results: Dict[str, ProviderHealth] = {}

        for name, provider in self._llm_providers.items():
            key = f"llm:{name}"
            try:
                results[key] = await provider.health_check()
            except Exception as e:
                logger.warning("Provider health check failed", provider=name, error=str(e))
                results[key] = ProviderHealth(provider=name, healthy=False, error=str(e))

        for name, provider in self._vision_providers.items():
            key = f"vision:{name}"
            if key not in results:
                try:
                    results[key] = await provider.health_check()
                except Exception as e:
                    logger.warning("Vision provider health check failed", provider=name, error=str(e))
                    results[key] = ProviderHealth(provider=name, healthy=False, error=str(e))

        for name, provider in self._embedding_providers.items():
            key = f"embedding:{name}"
            try:
                results[key] = await provider.health_check()
            except Exception as e:
                logger.warning("Embedding provider health check failed", provider=name, error=str(e))
                results[key] = ProviderHealth(provider=name, healthy=False, error=str(e))

        for name, provider in self._reranker_providers.items():
            key = f"reranker:{name}"
            try:
                results[key] = await provider.health_check()
            except Exception as e:
                logger.warning("Reranker provider health check failed", provider=name, error=str(e))
                results[key] = ProviderHealth(provider=name, healthy=False, error=str(e))

        return results

    def clear(self) -> None:
        """Clear all registered providers."""
        self._llm_providers.clear()
        self._vision_providers.clear()
        self._embedding_providers.clear()
        self._reranker_providers.clear()
