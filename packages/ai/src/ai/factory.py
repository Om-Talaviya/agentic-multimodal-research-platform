"""Factory functions for assembling default ModelGateway and registries."""

from typing import Optional
from ai.gateway.model_gateway import ModelGateway
from ai.providers.gemini_web2api import GeminiWeb2APIProvider
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

# Pre-defined catalog of Gemini Web2API models
DEFAULT_GEMINI_MODEL_DEFINITIONS = [
    ModelDefinition(
        model_id="gemini-3.7-flash",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=10,
        is_local=True,
        task_suitability=[
            "fast_text_generation",
            "vision_analysis",
            "long_form_research",
            "streaming_response",
            "planning",
            "synthesis",
            "report",
        ],
        metadata={"description": "Latest all-around model (Gemini 3.7 Flash)"},
    ),
    ModelDefinition(
        model_id="gemini-3.6-flash",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=8,
        is_local=True,
        task_suitability=[
            "fast_text_generation",
            "vision_analysis",
            "long_form_research",
            "streaming_response",
        ],
        metadata={"description": "All-around model (Gemini 3.6 Flash)"},
    ),
    ModelDefinition(
        model_id="gemini-3.5-flash",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=7,
        is_local=True,
        task_suitability=[
            "fast_text_generation",
            "vision_analysis",
            "streaming_response",
        ],
        metadata={"description": "Alias for gemini-3.6-flash (backend upgraded)"},
    ),
    ModelDefinition(
        model_id="gemini-3.5-flash-thinking",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=10,
        is_local=True,
        task_suitability=[
            "deep_reasoning",
            "long_form_research",
            "planning",
            "synthesis",
        ],
        metadata={"description": "Deep thinking mode, longest output (~20k chars)"},
    ),
    ModelDefinition(
        model_id="gemini-3.1-pro",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=9,
        is_local=True,
        task_suitability=[
            "deep_reasoning",
            "long_form_research",
            "coding",
            "planning",
        ],
        metadata={"description": "Pro model (requires cookie for real routing)"},
    ),
    ModelDefinition(
        model_id="gemini-auto",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=6,
        is_local=True,
        task_suitability=[
            "fast_text_generation",
        ],
        metadata={"description": "Auto model selection"},
    ),
    ModelDefinition(
        model_id="gemini-3.5-flash-thinking-lite",
        provider_name="gemini-web2api",
        capabilities=ALL_GEMINI_CAPS,
        context_window=1048576,
        supports_streaming=True,
        supports_vision=True,
        priority=8,
        is_local=True,
        task_suitability=[
            "deep_reasoning",
            "fast_text_generation",
        ],
        metadata={"description": "Dynamic thinking with adaptive depth"},
    ),
    ModelDefinition(
        model_id="gemini-flash-lite",
        provider_name="gemini-web2api",
        capabilities={
            ModelCapability.REASONING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.EXTRACTION,
            ModelCapability.CLASSIFICATION,
        },
        context_window=524288,
        supports_streaming=True,
        supports_vision=False,
        priority=9,
        is_local=True,
        task_suitability=[
            "fast_text_generation",
            "streaming_response",
        ],
        metadata={"description": "Lightweight fast model"},
    ),
]


def create_default_gateway(
    gemini_provider: Optional[GeminiWeb2APIProvider] = None,
    custom_model_registry: Optional[ModelRegistry] = None,
    custom_provider_registry: Optional[ProviderRegistry] = None,
) -> ModelGateway:
    """Construct and configure a default ModelGateway instance."""
    provider_registry = custom_provider_registry or ProviderRegistry()
    model_registry = custom_model_registry or ModelRegistry()

    # 1. Register Gemini Web2API Provider
    if gemini_provider is None and settings.gemini_web2api_base_url:
        gemini_provider = GeminiWeb2APIProvider(
            base_url=settings.gemini_web2api_base_url,
            api_key=settings.gemini_web2api_api_key,
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
