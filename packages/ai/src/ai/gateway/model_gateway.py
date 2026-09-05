"""Model Gateway providing high-level abstraction, fallback, telemetry, and health management."""
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from ai.providers.base import LLMProvider, VisionProvider
from ai.providers.router import ModelRouter, NoSuitableModelError
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.router.tasks import TaskType
from ai.schemas import (
    LLMRequest,
    LLMResponse,
    ProviderHealth,
    VisionRequest,
    VisionResponse,
)
from shared.exceptions import (
    ModelNotFoundError,
    ProviderError,
    ProviderUnavailableError,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class GatewayHealth(BaseModel):
    """Unified health status of the Model Gateway."""

    healthy: bool
    total_models: int
    active_providers: List[str]
    provider_health: Dict[str, ProviderHealth] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelGateway:
    """Central Model Gateway through which application code interacts with all AI models."""

    def __init__(
        self,
        router: ModelRouter,
        model_registry: Optional[ModelRegistry] = None,
        provider_registry: Optional[ProviderRegistry] = None,
        max_fallback_attempts: int = 3,  # PHASE 8A: configurable fallback depth
    ) -> None:
        self.router = router
        self.model_registry = model_registry or router.model_registry
        self.provider_registry = provider_registry or router.provider_registry
        self.max_fallback_attempts = max_fallback_attempts

    async def complete(
        self,
        request: LLMRequest,
        task: Optional[Union[str, TaskType]] = None,
        fallback_enabled: bool = True,
    ) -> LLMResponse:
        """Execute text completion with capability routing, safe fallback, and telemetry.

        Routing pipeline:
        1. Select initial model/provider via ModelRouter (capability-aware, tier-aware, health-aware)
        2. Attempt invocation
        3. OnProviderUnavailableError/ProviderError: attempt fallback (up to max_fallback_attempts)
        4. Return LLMResponse with full telemetry metadata
        """
        start_time = time.perf_counter()
        requested_model = request.model
        fallback_occurred = False
        original_model_id: Optional[str] = None
        attempted_models: List[str] = []
        attempted_providers: List[str] = []
        last_error: Optional[Exception] = None

        # -------------------------------------------------------------------------
        # 1. Select initial model & provider via Router
        # -------------------------------------------------------------------------
        try:
            model_def, provider = self.router.select_model_and_provider(
                requested_model=requested_model,
                task=task,
                requires_streaming=False,
                user_id=getattr(request, "metadata", {}).get("user_id"),
            )
        except Exception as e:
            logger.error(
                "Failed to route request to any model",
                error=str(e),
                task=task,
                requested_model=requested_model,
            )
            raise

        original_model_id = model_def.model_id
        target_model = model_def.model_id
        target_provider = provider

        # -------------------------------------------------------------------------
        # 2. Attempt invocation with fallback support
        # -------------------------------------------------------------------------
        for attempt in range(self.max_fallback_attempts + 1):
            attempted_models.append(target_model)
            attempted_providers.append(target_provider.name)

            # Ensure request object carries selected model
            current_request = request.model_copy(update={"model": target_model})

            try:
                logger.debug(
                    "Executing completion via gateway",
                    model=target_model,
                    provider=target_provider.name,
                    task=str(task) if task else None,
                    attempt=attempt,
                )
                response = await target_provider.complete(current_request)
                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Attach observability telemetry
                telemetry = {
                    "provider": target_provider.name,
                    "model": response.model or target_model,
                    "requested_model": requested_model,
                    "requested_task": str(task) if task else None,
                    "latency_ms": latency_ms,
                    "fallback_occurred": fallback_occurred,
                    "original_model": original_model_id if fallback_occurred else None,
                    "attempts": attempt + 1,
                }
                response.metadata.setdefault("telemetry", telemetry)
                response.metadata["provider"] = target_provider.name
                response.metadata["fallback_occurred"] = fallback_occurred
                if fallback_occurred:
                    response.metadata["original_model"] = original_model_id
                    if last_error:
                        response.metadata["primary_error"] = str(last_error)

                logger.info(
                    "Gateway completion succeeded",
                    model=response.model or target_model,
                    provider=target_provider.name,
                    latency_ms=latency_ms,
                    fallback=fallback_occurred,
                )
                return response

            except (ProviderUnavailableError, ProviderError) as e:
                last_error = e
                logger.warning(
                    "Provider invocation failed during gateway complete",
                    model=target_model,
                    provider=target_provider.name,
                    error=str(e),
                    attempt=attempt,
                )

                if not fallback_enabled or attempt >= self.max_fallback_attempts:
                    # No more retries — break and raise
                    break

                # Attempt finding alternative model via router
                try:
                    fallback_model_def, fallback_provider = self.router.select_model_and_provider(
                        task=task,
                        required_capabilities=model_def.capabilities,
                        exclude_models=attempted_models,
                        exclude_providers=attempted_providers,
                    )
                    target_model = fallback_model_def.model_id
                    target_provider = fallback_provider
                    fallback_occurred = True
                    logger.info(
                        "Switching to fallback model",
                        original_model=original_model_id,
                        fallback_model=target_model,
                        fallback_provider=target_provider.name,
                    )
                except Exception as route_err:
                    logger.warning("No compatible fallback model available", error=str(route_err))
                    break

        # -------------------------------------------------------------------------
        # 3. All attempts exhausted — raise last error or generic unavailable
        # -------------------------------------------------------------------------
        if last_error:
            raise last_error
        raise ProviderUnavailableError("gateway")

    async def stream_complete(
        self,
        request: LLMRequest,
        task: Optional[Union[str, TaskType]] = None,
        fallback_enabled: bool = True,
    ) -> AsyncIterator[str]:
        """Stream completion tokens through the model gateway."""
        requested_model = request.model

        model_def, provider = self.router.select_model_and_provider(
            requested_model=requested_model,
            task=task or TaskType.STREAMING_RESPONSE,
            requires_streaming=True,
        )

        current_request = request.model_copy(update={"model": model_def.model_id})

        logger.debug(
            "Executing stream completion via gateway",
            model=model_def.model_id,
            provider=provider.name,
        )

        try:
            async for token in provider.stream_complete(current_request):
                yield token
        except (ProviderUnavailableError, ProviderError) as e:
            if not fallback_enabled:
                raise
            logger.warning("Stream failed, attempting fallback stream", model=model_def.model_id, error=str(e))
            try:
                fallback_def, fallback_provider = self.router.select_model_and_provider(
                    task=task or TaskType.STREAMING_RESPONSE,
                    required_capabilities=model_def.capabilities,
                    exclude_models=[model_def.model_id],
                    exclude_providers=[provider.name],
                    requires_streaming=True,
                )
                fallback_req = request.model_copy(update={"model": fallback_def.model_id})
                async for token in fallback_provider.stream_complete(fallback_req):
                    yield token
            except Exception:
                raise e

    async def analyze_vision(
        self,
        request: VisionRequest,
        fallback_enabled: bool = True,
    ) -> VisionResponse:
        """Execute vision analysis request through the gateway."""
        start_time = time.perf_counter()
        requested_model = request.model

        model_def, provider = self.router.select_model_and_provider(
            requested_model=requested_model,
            task=TaskType.VISION_ANALYSIS,
            requires_vision=True,
        )

        if not isinstance(provider, VisionProvider):
            # Lookup vision provider
            vision_provider = self.provider_registry.get_vision(provider.name)
            if not vision_provider:
                vision_provider = self.router.select_vision()
            else:
                vision_provider = provider
        else:
            vision_provider = provider

        current_request = request.model_copy(update={"model": model_def.model_id})

        try:
            response = await vision_provider.analyze(current_request)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            response.metadata.setdefault(
                "telemetry",
                {
                    "provider": vision_provider.name,
                    "model": response.model or model_def.model_id,
                    "latency_ms": latency_ms,
                    "fallback_occurred": False,
                },
            )
            return response
        except Exception as e:
            logger.warning("Vision analysis failed", provider=vision_provider.name, error=str(e))
            if not fallback_enabled:
                raise
            # Attempt fallback vision provider
            fallback_prov = self.router.select_vision(exclude=[vision_provider.name])
            current_request = request.model_copy(update={"model": model_def.model_id})
            response = await fallback_prov.analyze(current_request)
            response.metadata["fallback_occurred"] = True
            return response

    async def health_check(self) -> GatewayHealth:
        """Get comprehensive health status of gateway, providers, and models."""
        provider_health = await self.provider_registry.health_check_all()
        models = self.model_registry.list_models()
        active_providers = [p.name for p in self.provider_registry.list_llm_providers()]

        # Gateway is considered healthy if at least one LLM provider is healthy
        any_healthy = any(h.healthy for h in provider_health.values())

        return GatewayHealth(
            healthy=any_healthy,
            total_models=len(models),
            active_providers=active_providers,
            provider_health=provider_health,
            metadata={"total_registered_models": len(models)},
        )

    def get_available_models(self) -> List[ModelDefinition]:
        """List all models in the catalog."""
        return self.model_registry.list_models()