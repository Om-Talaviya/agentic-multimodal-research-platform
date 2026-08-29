"""Model router for capability and task-based provider selection."""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from ai.providers.base import (
    EmbeddingProvider,
    LLMProvider,
    RerankerProvider,
    VisionProvider,
)
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.router.tasks import TaskType, get_required_capabilities, normalize_task
from ai.schemas import ModelCapabilities, ModelCapability, ProviderHealth
from shared.exceptions import ModelNotFoundError, ProviderError
from shared.logging import get_logger

logger = get_logger(__name__)


class NoSuitableModelError(Exception):
    """Raised when no provider or model supports required capabilities."""

    pass


class ModelRouter:
    """Routes requests to appropriate model providers based on capabilities, tasks, or explicit selection."""

    def __init__(
        self,
        llm_providers: Optional[List[LLMProvider]] = None,
        vision_providers: Optional[List[VisionProvider]] = None,
        embedding_providers: Optional[List[EmbeddingProvider]] = None,
        reranker_providers: Optional[List[RerankerProvider]] = None,
        model_registry: Optional[ModelRegistry] = None,
        provider_registry: Optional[ProviderRegistry] = None,
    ) -> None:
        self.provider_registry = provider_registry or ProviderRegistry()
        self.model_registry = model_registry or ModelRegistry()

        # Wire legacy provider lists into provider_registry if passed
        if llm_providers:
            for p in llm_providers:
                self.provider_registry.register_llm(p)
        if vision_providers:
            for p in vision_providers:
                self.provider_registry.register_vision(p)
        if embedding_providers:
            for p in embedding_providers:
                self.provider_registry.register_embedding(p)
        if reranker_providers:
            for p in reranker_providers:
                self.provider_registry.register_reranker(p)

    @property
    def llm_providers(self) -> List[LLMProvider]:
        return self.provider_registry.list_llm_providers()

    @property
    def vision_providers(self) -> List[VisionProvider]:
        return self.provider_registry.list_vision_providers()

    @property
    def embedding_providers(self) -> List[EmbeddingProvider]:
        return self.provider_registry.list_embedding_providers()

    @property
    def reranker_providers(self) -> List[RerankerProvider]:
        return self.provider_registry.list_reranker_providers()

    def select_model_and_provider(
        self,
        requested_model: Optional[str] = None,
        task: Optional[Union[str, TaskType]] = None,
        required_capabilities: Optional[Set[ModelCapability]] = None,
        prefer_local: bool = True,
        exclude_models: Optional[List[str]] = None,
        exclude_providers: Optional[List[str]] = None,
        requires_vision: bool = False,
        requires_streaming: bool = False,
    ) -> Tuple[ModelDefinition, LLMProvider]:
        """Select best matching (ModelDefinition, LLMProvider) pair."""
        exclude_models = exclude_models or []
        exclude_providers = exclude_providers or []

        # 1. Explicit model selection takes highest precedence
        if requested_model:
            model_def = self.model_registry.get(requested_model)
            if not model_def:
                # If model is not in model_registry, check if any registered provider hosts it
                for p in self.llm_providers:
                    if requested_model in p.models or requested_model == p.name:
                        # Synthesize minimal ModelDefinition
                        model_def = ModelDefinition(
                            model_id=requested_model,
                            provider_name=p.name,
                            capabilities=set(p.capabilities),
                            is_local=p.is_local,
                            supports_streaming=True,
                            supports_vision=isinstance(p, VisionProvider),
                        )
                        break

            if not model_def:
                # Fallback: if we have providers, check if any can handle requested_model
                if self.llm_providers:
                    provider = self.llm_providers[0]
                    model_def = ModelDefinition(
                        model_id=requested_model,
                        provider_name=provider.name,
                        capabilities=set(provider.capabilities),
                        is_local=provider.is_local,
                    )
                else:
                    raise ModelNotFoundError("router", f"Requested model '{requested_model}' not found in registry")

            provider = self.provider_registry.get_llm(model_def.provider_name)
            if not provider:
                raise NoSuitableModelError(
                    f"Provider '{model_def.provider_name}' for model '{requested_model}' is not registered"
                )
            return model_def, provider

        # 2. Determine capabilities based on task or explicit parameter
        target_caps: Set[ModelCapability] = set(required_capabilities or set())
        task_type_str: Optional[str] = None
        if task:
            normalized = normalize_task(task)
            task_type_str = normalized.value
            target_caps.update(get_required_capabilities(normalized))

        if requires_vision:
            target_caps.add(ModelCapability.VISION)

        # 3. Query candidate models from registry
        all_models = self.model_registry.list_models()
        if not all_models:
            # If model registry is empty, construct candidates from provider registry
            for p in self.llm_providers:
                if p.name in exclude_providers:
                    continue
                for m_id in (p.models or [p.name]):
                    if m_id not in exclude_models:
                        all_models.append(
                            ModelDefinition(
                                model_id=m_id,
                                provider_name=p.name,
                                capabilities=set(p.capabilities),
                                is_local=p.is_local,
                                priority=5,
                                supports_streaming=True,
                                supports_vision=isinstance(p, VisionProvider),
                            )
                        )

        candidates: List[ModelDefinition] = []
        for m in all_models:
            if m.model_id in exclude_models:
                continue
            if m.provider_name in exclude_providers:
                continue
            if target_caps and not target_caps.issubset(m.capabilities):
                continue
            if requires_vision and not m.supports_vision:
                continue
            if requires_streaming and not m.supports_streaming:
                continue
            candidates.append(m)

        if not candidates:
            raise NoSuitableModelError(
                f"No suitable model found for task={task}, capabilities={target_caps}. "
                f"Available: {[m.model_id for m in all_models]}"
            )

        # 4. Rank candidates by (task_suitability, is_local if preferred, priority)
        def score_candidate(m: ModelDefinition) -> Tuple[int, int, int]:
            task_match = 1 if (task_type_str and task_type_str in m.task_suitability) else 0
            local_match = 1 if (prefer_local and m.is_local) else 0
            return (task_match, local_match, m.priority)

        sorted_candidates = sorted(candidates, key=score_candidate, reverse=True)
        selected_model = sorted_candidates[0]
        selected_provider = self.provider_registry.get_llm(selected_model.provider_name)

        if not selected_provider:
            raise NoSuitableModelError(
                f"Provider '{selected_model.provider_name}' for model '{selected_model.model_id}' is not registered"
            )

        logger.debug(
            "Selected model and provider",
            model=selected_model.model_id,
            provider=selected_provider.name,
            task=task,
        )
        return selected_model, selected_provider

    def select_llm(
        self,
        capabilities: Optional[ModelCapabilities] = None,
        task: Optional[Union[str, TaskType]] = None,
        prefer_local: bool = True,
        exclude: Optional[List[str]] = None,
    ) -> LLMProvider:
        """Select best LLM provider for given capabilities or task (backward-compatible)."""
        exclude = exclude or []
        caps_set = set(capabilities) if capabilities else None

        # Try registry-based resolution first
        try:
            _, provider = self.select_model_and_provider(
                task=task,
                required_capabilities=caps_set,
                prefer_local=prefer_local,
                exclude_providers=exclude,
            )
            return provider
        except Exception:
            # Fall back to legacy provider capability lookup
            candidates = [
                p for p in self.llm_providers
                if p.name not in exclude
                and (not caps_set or caps_set.issubset(p.capabilities))
            ]

            if not candidates:
                raise NoSuitableModelError(
                    f"No LLM provider supports capabilities: {capabilities}. "
                    f"Available: {[(p.name, p.capabilities) for p in self.llm_providers]}"
                )

            if prefer_local:
                local = [p for p in candidates if p.is_local]
                if local:
                    return local[0]

            return candidates[0]

    def select_vision(
        self,
        prefer_local: bool = True,
        exclude: Optional[List[str]] = None,
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
        exclude: Optional[List[str]] = None,
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
        exclude: Optional[List[str]] = None,
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

    async def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Check health of all providers."""
        return await self.provider_registry.health_check_all()

    def get_all_models(self) -> Dict[str, Any]:
        """Get all available models grouped by provider."""
        return {
            "llm": {p.name: p.models for p in self.llm_providers},
            "vision": {p.name: p.models for p in self.vision_providers},
            "embedding": {p.name: p.models for p in self.embedding_providers},
            "reranker": {p.name: p.models for p in self.reranker_providers},
            "catalog": [m.model_dump() for m in self.model_registry.list_models()],
        }