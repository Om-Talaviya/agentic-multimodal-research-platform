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
        user_id: Optional[str] = None,
    ) -> Tuple[ModelDefinition, LLMProvider]:
        """Select best matching (ModelDefinition, LLMProvider) pair.

        Routing logic (in order of application):
        1. Explicit model selection takes highest precedence (backward compatible)
        2. Determine target capabilities from task or explicit parameter
        3. Query candidate models from registry, filtered by:
           - Required capabilities
           - Vision support
           - Streaming support
           - Tier preference (FREE first if no task-specific policy)
           - Exclude models/providers
        4. Health/availability filtering
        5. Context window compatibility filtering
        6. Deterministic ranking
        7. Return selected (ModelDefinition, LLMProvider)
        """

        exclude_models = exclude_models or []
        exclude_providers = exclude_providers or []

        # =========================================================================
        # 1. Explicit model selection takes highest precedence (backward compatible)
        # =========================================================================
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
                    raise ModelNotFoundError(
                        "router", f"Requested model '{requested_model}' not found in registry"
                    )

            provider = self.provider_registry.get_llm(model_def.provider_name)
            if not provider:
                raise NoSuitableModelError(
                    f"Provider '{model_def.provider_name}' for model '{requested_model}' is not registered"
                )
            logger.debug(
                "Selected model and provider (explicit request)",
                model=model_def.model_id,
                provider=provider.name,
                task=task,
            )
            return model_def, provider

        # =========================================================================
        # 2. Determine target capabilities based on task or explicit parameter
        # =========================================================================
        target_caps: Set[ModelCapability] = set(required_capabilities or set())
        task_type_str: Optional[str] = None

        if task:
            normalized = normalize_task(task)
            task_type_str = normalized.value
            target_caps.update(get_required_capabilities(normalized))

        if requires_vision:
            target_caps.add(ModelCapability.VISION)

        # =========================================================================
        # 3. Query candidate models from registry, apply capability filtering
        # =========================================================================
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
        else:
            # Filter out excluded models/providers from the registry list
            filtered: List[ModelDefinition] = []
            for m in all_models:
                if m.model_id in exclude_models:
                    continue
                if m.provider_name in exclude_providers:
                    continue
                filtered.append(m)
            all_models = filtered

        # Capability filtering: model must support all required capabilities
        candidates: List[ModelDefinition] = []
        for m in all_models:
            if target_caps and not target_caps.issubset(m.capabilities):
                continue  # Model lacks required capability
            if requires_vision and not m.supports_vision:
                continue  # Model doesn't support vision
            if requires_streaming and not m.supports_streaming:
                continue  # Model doesn't support streaming
            candidates.append(m)

        if not candidates:
            raise NoSuitableModelError(
                f"No suitable model found for task={task}, capabilities={target_caps}. "
                f"Available: {[m.model_id for m in all_models]}"
            )

        # =========================================================================
        # 4. Tier preference filtering (FREE first, then PAID)
        # =========================================================================
        # Configurable policy: prefer free models unless task requires paid
        # This is a simple preference; deeper policy can be injected later
        free_candidates = [m for m in candidates if m.is_free()]
        paid_candidates = [m for m in candidates if m.is_paid()]

        # If we have free candidates, use those; otherwise fall back to paid
        filtered_by_tier: List[ModelDefinition]
        if free_candidates:
            filtered_by_tier = free_candidates
        else:
            filtered_by_tier = paid_candidates

        if not filtered_by_tier:
            # No candidates matching tier preference — fall back to all candidates
            filtered_by_tier = candidates

        # =========================================================================
        # 5. Health/availability filtering
        # =========================================================================
        import asyncio

        healthy_set: Set[str] = set()
        for m in filtered_by_tier:
            provider = self.provider_registry.get_llm(m.provider_name)
            if provider is None:
                continue
            try:
                health = asyncio.run(provider.health_check())
                if health.healthy:
                    healthy_set.add(m.model_id)
            except Exception:
                pass  # Skip unhealthy models

        # Re-filter: only keep models with healthy providers
        # But keep at least one candidate if nothing is healthy (degraded mode)
        final_candidates: List[ModelDefinition] = []
        for m in filtered_by_tier:
            if m.model_id in healthy_set:
                final_candidates.append(m)
            elif not healthy_set and m in filtered_by_tier:
                # No models healthy — include the least-unavailable as fallback
                final_candidates.append(m)

        if not final_candidates:
            # If we have candidates that failed health check, use those as last resort
            final_candidates = [m for m in filtered_by_tier if m not in final_candidates]

        if not final_candidates:
            raise NoSuitableModelError(
                f"No suitable model found for task={task}, capabilities={target_caps}. "
                f"Available: {[m.model_id for m in all_models]}"
            )

        # =========================================================================
        # 6. Context window compatibility filtering
        # =========================================================================
        # Determine the minimum context window needed for the task
        min_context = self._derive_min_context_for_task(task_type_str) if task_type_str else None

        context_filtered: List[ModelDefinition] = []
        for m in final_candidates:
            if min_context is None:
                # No minimum context required — accept all
                context_filtered.append(m)
            elif m.context_window and m.context_window >= min_context:
                context_filtered.append(m)
            elif m.context_window is None:
                # No context info — accept as possible fallback
                context_filtered.append(m)
            # else: context_window too small — skip

        if not context_filtered:
            # If context filtering eliminated all candidates, relax the filter
            context_filtered = final_candidates

        # =========================================================================
        # 7. Deterministic ranking (lower-is-better)
        # =========================================================================
        def ranking_key(m: ModelDefinition) -> Tuple[int, int, int, int, int]:
            """Ranking key: lower tuple = better rank.

            Components (lexicographic order, compared left-to-right):
            0. task_match: 0 if model matches task suitability, 1 if not
               (0 < 1, so matching models rank higher/better)
            1. local_match: 0 if local model preferred and model is local, 1 if not
            2. tier_priority: 0 if free (preferred), 1 if paid (fallback)
            3. cost_priority: 0 if no cost, 1 if has cost (lower cost preferred)
            4. model_priority: -m.priority (negate so higher numeric priority = better rank)
            """
            task_match_val = 0 if (task_type_str and task_type_str in m.task_suitability) else 1
            # task_match_val = 0 means model matches task (better rank since lower-is-better)
            # task_match_val = 1 means model does NOT match task (worse rank)

            local_match_val = 0 if (prefer_local and m.is_local) else 1

            tier_priority_val = 0 if m.is_free() else 1  # FREE=0 better (preferred)

            # Cost priority: 0 = no cost / free, 1 = has cost (higher cost = worse)
            cost_priority_val = 0 if (m.input_cost == 0 and m.output_cost == 0) else 1

            # Model priority: negate so higher numeric priority = better rank (lower number)
            model_priority_val = -m.priority

            return (task_match_val, local_match_val, tier_priority_val, cost_priority_val, model_priority_val)

        sorted_candidates = sorted(candidates, key=ranking_key)
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
            rationale=self._routing_rationale(
                selected_model, task_type_str, candidates
            ),
        )
        return selected_model, selected_provider

    def _derive_min_context_for_task(
        self, task_type_str: Optional[str]
    ) -> Optional[int]:
        """Derive minimum context window needed for a task type."""
        # Task-specific context requirements (tokens)
        context_map = {
            TaskType.LONG_FORM_RESEARCH.value: 100000,  # long research needs lots of context
            TaskType.VISION_ANALYSIS.value: 8192,  # vision typically moderate context
            TaskType.DEEP_REASONING.value: 32000,  # reasoning may need substantial context
        }
        if task_type_str and task_type_str in context_map:
            return context_map[task_type_str]
        return None

    def _routing_rationale(
        self, selected: ModelDefinition, task_type_str: Optional[str], all_candidates: List[ModelDefinition]
    ) -> str:
        """Generate a human-readable explanation of the routing decision."""
        reasons: List[str] = []

        if task_type_str and task_type_str in selected.task_suitability:
            reasons.append(f"supports task '{task_type_str}'")

        if ModelCapability.VISION in selected.capabilities:
            if selected.supports_vision:
                reasons.append("supports vision capability")

        if selected.is_free():
            reasons.append("free tier preference")
        else:
            reasons.append("paid tier")

        if selected.context_window:
            reasons.append(f"context window {selected.context_window // 1024}K tokens")

        if selected.priority:
            reasons.append(f"priority {selected.priority}")

        # Explain against what was filtered
        if all_candidates:
            reason_parts = []
            for c in all_candidates[:3]:  # Top 3 for context
                if c.is_free() and not selected.is_free():
                    reason_parts.append(f"chose over {c.model_id} (free→paid policy)")
                if c.task_suitability and task_type_str not in c.task_suitability:
                    reason_parts.append(f"filtered by task suitability (needs {task_type_str})")
            if reason_parts:
                reasons.append("; ".join(reason_parts))

        return "; ".join(reasons) if reasons else "model selected by default ranking"

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
                p
                for p in self.llm_providers
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