"""Factory functions for assembling default ModelGateway and registries."""
from typing import Optional
from ai.gateway.model_gateway import ModelGateway
from ai.providers.gemini import GeminiProvider
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import ModelCapability
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)

# Standard Gemini capabilities
ALL_GEMINI_CAPS = {
    ModelCapability.REASONING,
    ModelCapability.CODING,
    ModelCapability.SUMMARIZATION,
    ModelCapability.VISION,
    ModelCapability.EXTRACTION,
    ModelCapability.CLASSIFICATION,
    ModelCapability.TOOL_USE,
    ModelCapability.JSON_MODE,
}

# Pre-defined catalog of official Gemini models
# Tier set to "free" since these are the platform's default models;
# pricing can be configured independently via input_cost/output_cost
DEFAULT_GEMINI_MODEL_DEFINITIONS = [
    ModelDefinition(
        model_id="gemini-2.0-flash",
        provider_name="gemini",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=10,
        is_local=False,
        tier="free",  # Phase 8A: default to free for platform models
        input_cost=0.0,
        output_cost=0.0,
        task_suitability=[
            "fast_text_generation",
            "vision_analysis",
            "long_form_research",
            "streaming_response",
            "planning",
            "synthesis",
            "report",
        ],
        metadata={"description": "Next-generation multimodal flagship (Gemini 2.0 Flash)"},
    ),
    ModelDefinition(
        model_id="gemini-2.0-flash-lite",
        provider_name="gemini",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=9,
        is_local=False,
        tier="free",  # Phase 8A: default to free for platform models
        input_cost=0.0,
        output_cost=0.0,
        task_suitability=[
            "fast_text_generation",
            "streaming_response",
        ],
        metadata={"description": "Cost-efficient lightweight model (Gemini 2.0 Flash Lite)"},
    ),
    ModelDefinition(
        model_id="gemini-1.5-pro",
        provider_name="gemini",
        capabilities=ALL_GEMINI_CAPS,
        context_window=2097152,
        supports_streaming=True,
        supports_vision=True,
        priority=9,
        is_local=False,
        tier="free",  # Phase 8A: default to free for platform models
        input_cost=0.0,
        output_cost=0.0,
        task_suitability=[
            "deep_reasoning",
            "long_form_research",
            "coding",
            "planning",
            "synthesis",
        ],
        metadata={"description": "Complex reasoning model with 2M context (Gemini 1.5 Pro)"},
    ),
    ModelDefinition(
        model_id="gemini-1.5-flash",
        provider_name="gemini",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=8,
        is_local=False,
        tier="free",  # Phase 8A: default to free for platform models
        input_cost=0.0,
        output_cost=0.0,
        task_suitability=[
            "fast_text_generation",
            "vision_analysis",
            "long_form_research",
            "streaming_response",
        ],
        metadata={"description": "Fast and versatile multimodal model (Gemini 1.5 Flash)"},
    ),
]


def create_default_gateway(
    gemini_provider: Optional[GeminiProvider] = None,
    custom_model_registry: Optional[ModelRegistry] = None,
    custom_provider_registry: Optional[ProviderRegistry] = None,
) -> ModelGateway:
    """Construct and configure a default ModelGateway instance."""
    provider_registry = custom_provider_registry or ProviderRegistry()
    model_registry = custom_model_registry or ModelRegistry()

    # 1. Register Gemini Provider if configured
    if gemini_provider is None and (settings.gemini_api_key or settings.gemini_base_url):
        gemini_provider = GeminiProvider(
            base_url=settings.gemini_base_url,
            api_key=settings.gemini_api_key,
            default_model=settings.gemini_default_model,
        )

    if gemini_provider is not None:
        provider_registry.register_all_in_one(gemini_provider)

        # 2. Register standard Gemini models into model_registry
        for model_def in DEFAULT_GEMINI_MODEL_DEFINITIONS:
            model_registry.register(model_def)

    # 3. Build Router and Gateway
    router = ModelRouter(
        model_registry=model_registry,
        provider_registry=provider_registry,
    )

    gateway = ModelGateway(
        router=router,
        model_registry=model_registry,
        provider_registry=provider_registry,
    )

    return gateway