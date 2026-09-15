"""Model Gateway providing high-level abstraction, fallback, telemetry, and health management."""
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from uuid import UUID
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
    QuotaExceededError,
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
        max_fallback_attempts: int = 3,
        session_factory: Optional[Any] = None,
    ) -> None:
        self.router = router
        self.model_registry = model_registry or router.model_registry
        self.provider_registry = provider_registry or router.provider_registry
        self.max_fallback_attempts = max_fallback_attempts
        self.session_factory = session_factory

    async def _check_user_quota(
        self,
        user_id: UUID,
        model_def: Optional[ModelDefinition] = None,
        estimated_tokens: int = 1000,
    ) -> bool:
        """Check if user has remaining quota for this model request."""
        try:
            from database.connection import get_session
            from database.repositories.quota_repo import UserQuotaRepository

            estimated_cost = 0.0
            if model_def:
                estimated_cost = model_def.estimated_cost(estimated_tokens, 500)

            session_cm = self.session_factory() if self.session_factory else get_session()
            async with session_cm as session:
                quota_repo = UserQuotaRepository(session)
                return await quota_repo.check_quota(
                    user_id=user_id,
                    estimated_tokens=estimated_tokens,
                    estimated_cost=estimated_cost,
                )
        except Exception as exc:
            logger.warning("Quota check failed, defaulting to allowed", error=str(exc))
            return True

    async def _record_usage(
        self,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: int,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        request_type: str = "complete",
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Persist model usage telemetry to the database asynchronously. Best-effort persistence."""
        try:
            from database.connection import get_session
            from database.repositories.usage_repo import UsageRepository
            from database.repositories.quota_repo import UserQuotaRepository

            session_cm = self.session_factory() if self.session_factory else get_session()
            async with session_cm as session:
                usage_repo = UsageRepository(session)
                await usage_repo.record_usage(
                    provider=provider_name,
                    model=model_name,
                    user_id=user_id,
                    job_id=job_id,
                    request_type=request_type,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    cost_usd=cost_usd,
                    success=success,
                    error_message=error_message,
                    latency_ms=latency_ms,
                )
                if user_id and success:
                    quota_repo = UserQuotaRepository(session)
                    try:
                        await quota_repo.reserve_or_consume_quota(
                            user_id=user_id,
                            tokens=prompt_tokens + completion_tokens,
                            cost=cost_usd,
                            with_for_update=True,
                        )
                    except Exception as q_err:
                        logger.warning("Could not update user quota consumption", user_id=str(user_id), error=str(q_err))
        except Exception as exc:
            logger.warning("Failed to persist model usage record to database", error=str(exc))

    async def complete(
        self,
        request: LLMRequest,
        task: Optional[Union[str, TaskType]] = None,
        fallback_enabled: bool = True,
        routing_profile: Optional[Union[str, Any]] = None,
    ) -> LLMResponse:
        """Execute text completion with capability routing, safe fallback, and telemetry."""
        start_time = time.perf_counter()
        requested_model = request.model
        fallback_occurred = False
        original_model_id: Optional[str] = None
        attempted_models: List[str] = []
        attempted_providers: List[str] = []
        last_error: Optional[Exception] = None

        # Extract user_id, job_id, and routing_profile from request metadata if present
        req_meta = getattr(request, "metadata", {}) or {}
        user_id_raw = req_meta.get("user_id")
        job_id_raw = req_meta.get("job_id")
        effective_profile = routing_profile or req_meta.get("routing_profile")

        user_id: Optional[UUID] = None
        if user_id_raw:
            try:
                user_id = UUID(str(user_id_raw))
            except Exception:
                user_id = None

        job_id: Optional[UUID] = None
        if job_id_raw:
            try:
                job_id = UUID(str(job_id_raw))
            except Exception:
                job_id = None

        # -------------------------------------------------------------------------
        # 1. Select initial model & provider via Router
        # -------------------------------------------------------------------------
        try:
            model_def, provider = self.router.select_model_and_provider(
                requested_model=requested_model,
                task=task,
                requires_streaming=False,
                user_id=str(user_id) if user_id else None,
                routing_profile=effective_profile,
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
        # 2. Check quota on initial selection if user_id is present
        # -------------------------------------------------------------------------
        if user_id:
            has_quota = await self._check_user_quota(user_id, model_def)
            while not has_quota:
                attempted_models.append(target_model)
                logger.info("Model exceeds user quota, falling back", model=target_model, user_id=str(user_id))
                try:
                    fallback_def, fallback_prov = self.router.select_model_and_provider(
                        task=task,
                        required_capabilities=model_def.capabilities,
                        exclude_models=attempted_models,
                        exclude_providers=attempted_providers,
                        routing_profile=effective_profile,
                    )
                    model_def = fallback_def
                    target_model = fallback_def.model_id
                    target_provider = fallback_prov
                    fallback_occurred = True
                    has_quota = await self._check_user_quota(user_id, model_def)
                except Exception:
                    raise QuotaExceededError(f"All available models exceed quota limits for user {user_id}")

        # -------------------------------------------------------------------------
        # 3. Attempt invocation with fallback support
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

                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                if response.usage and isinstance(response.usage, dict):
                    prompt_tokens = int(response.usage.get("prompt_tokens") or response.usage.get("input_tokens") or 0)
                    completion_tokens = int(response.usage.get("completion_tokens") or response.usage.get("output_tokens") or 0)
                    total_tokens = int(response.usage.get("total_tokens") or (prompt_tokens + completion_tokens))
                elif hasattr(response, "usage") and response.usage:
                    prompt_tokens = int(getattr(response.usage, "prompt_tokens", 0) or getattr(response.usage, "input_tokens", 0) or 0)
                    completion_tokens = int(getattr(response.usage, "completion_tokens", 0) or getattr(response.usage, "output_tokens", 0) or 0)
                    total_tokens = int(getattr(response.usage, "total_tokens", prompt_tokens + completion_tokens) or (prompt_tokens + completion_tokens))

                # Cost calculation: (input_cost / 1000 * prompt_tokens) + (output_cost / 1000 * completion_tokens)
                cost_usd = 0.0
                active_model_def = self.model_registry.get(response.model or target_model) or model_def
                if active_model_def:
                    cost_usd = active_model_def.estimated_cost(prompt_tokens, completion_tokens)

                # Attach observability telemetry
                telemetry = {
                    "provider": target_provider.name,
                    "model": response.model or target_model,
                    "requested_model": requested_model,
                    "requested_task": str(task) if task else None,
                    "routing_profile": str(effective_profile) if effective_profile else "default",
                    "latency_ms": latency_ms,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": cost_usd,
                    "fallback_occurred": fallback_occurred,
                    "original_model": original_model_id if fallback_occurred else None,
                    "attempts": attempt + 1,
                }
                response.metadata.setdefault("telemetry", telemetry)
                response.metadata["provider"] = target_provider.name
                response.metadata["fallback_occurred"] = fallback_occurred
                response.metadata["cost_usd"] = cost_usd
                response.metadata["total_tokens"] = total_tokens
                response.metadata["routing_profile"] = str(effective_profile) if effective_profile else "default"
                if fallback_occurred:
                    response.metadata["original_model"] = original_model_id
                    if last_error:
                        response.metadata["primary_error"] = str(last_error)

                # Persist usage telemetry asynchronously
                await self._record_usage(
                    provider_name=target_provider.name,
                    model_name=response.model or target_model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=cost_usd,
                    latency_ms=latency_ms,
                    user_id=user_id,
                    job_id=job_id,
                    request_type="complete",
                    success=True,
                )

                logger.info(
                    "Gateway completion succeeded",
                    model=response.model or target_model,
                    provider=target_provider.name,
                    latency_ms=latency_ms,
                    fallback=fallback_occurred,
                    tokens=total_tokens,
                    cost_usd=cost_usd,
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
                    if user_id:
                        while not await self._check_user_quota(user_id, fallback_model_def):
                            attempted_models.append(fallback_model_def.model_id)
                            fallback_model_def, fallback_provider = self.router.select_model_and_provider(
                                task=task,
                                required_capabilities=model_def.capabilities,
                                exclude_models=attempted_models,
                                exclude_providers=attempted_providers,
                            )

                    target_model = fallback_model_def.model_id
                    target_provider = fallback_provider
                    model_def = fallback_model_def
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
        # 4. All attempts exhausted — raise last error or generic unavailable
        # -------------------------------------------------------------------------
        if last_error:
            raise last_error
        raise ProviderUnavailableError("gateway")

    async def stream_complete(
        self,
        request: LLMRequest,
        task: Optional[Union[str, TaskType]] = None,
        fallback_enabled: bool = True,
        routing_profile: Optional[Union[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Stream completion tokens through the model gateway."""
        requested_model = request.model
        req_meta = getattr(request, "metadata", {}) or {}
        effective_profile = routing_profile or req_meta.get("routing_profile")

        model_def, provider = self.router.select_model_and_provider(
            requested_model=requested_model,
            task=task or TaskType.STREAMING_RESPONSE,
            requires_streaming=True,
            routing_profile=effective_profile,
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
                    routing_profile=effective_profile,
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

        req_meta = getattr(request, "metadata", {}) or {}
        user_id_raw = req_meta.get("user_id")
        job_id_raw = req_meta.get("job_id")

        user_id: Optional[UUID] = None
        if user_id_raw:
            try:
                user_id = UUID(str(user_id_raw))
            except Exception:
                user_id = None

        job_id: Optional[UUID] = None
        if job_id_raw:
            try:
                job_id = UUID(str(job_id_raw))
            except Exception:
                job_id = None

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
            await self._record_usage(
                provider_name=vision_provider.name,
                model_name=response.model or model_def.model_id,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                user_id=user_id,
                job_id=job_id,
                request_type="vision",
                success=True,
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
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            await self._record_usage(
                provider_name=fallback_prov.name,
                model_name=response.model or model_def.model_id,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                user_id=user_id,
                job_id=job_id,
                request_type="vision",
                success=True,
            )
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