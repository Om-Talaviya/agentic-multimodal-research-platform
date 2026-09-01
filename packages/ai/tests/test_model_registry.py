"""Unit tests for ModelRegistry and ModelDefinition."""

import pytest
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.schemas import ModelCapability


def test_model_definition_creation():
    """Test creating ModelDefinition with metadata."""
    model = ModelDefinition(
        model_id="test-model",
        provider_name="test-provider",
        capabilities={ModelCapability.REASONING, ModelCapability.VISION},
        context_window=128000,
        supports_streaming=True,
        supports_vision=True,
        task_suitability=["deep_reasoning", "vision_analysis"],
        priority=10,
        is_local=True,
    )

    assert model.model_id == "test-model"
    assert model.provider_name == "test-provider"
    assert ModelCapability.REASONING in model.capabilities
    assert model.supports_vision is True
    assert model.supports_streaming is True
    assert model.priority == 10
    assert model.is_local is True


def test_model_registry_crud():
    """Test register, get, contains, unregister, clear operations."""
    registry = ModelRegistry()
    assert len(registry.list_models()) == 0

    m1 = ModelDefinition(
        model_id="gemini-2.0-flash",
        provider_name="gemini",
        capabilities={ModelCapability.REASONING},
        priority=10,
    )
    m2 = ModelDefinition(
        model_id="gemini-1.5-pro",
        provider_name="gemini",
        capabilities={ModelCapability.REASONING},
        priority=8,
    )

    registry.register(m1)
    registry.register(m2)

    assert registry.contains("gemini-2.0-flash") is True
    assert registry.contains("non-existent") is False
    assert registry.get("gemini-2.0-flash") == m1

    models = registry.list_models()
    assert len(models) == 2
    # Ordered by priority descending
    assert models[0].model_id == "gemini-2.0-flash"
    assert models[1].model_id == "gemini-1.5-pro"

    # Unregister
    assert registry.unregister("gemini-2.0-flash") is True
    assert registry.contains("gemini-2.0-flash") is False
    assert len(registry.list_models()) == 1

    # Clear
    registry.clear()
    assert len(registry.list_models()) == 0


def test_model_registry_filtering():
    """Test filtering models by provider, capability, task, vision, streaming."""
    registry = ModelRegistry()

    m_fast = ModelDefinition(
        model_id="fast-model",
        provider_name="prov-a",
        capabilities={ModelCapability.SUMMARIZATION},
        task_suitability=["fast_text_generation"],
        supports_vision=False,
        supports_streaming=True,
        priority=5,
    )
    m_vision = ModelDefinition(
        model_id="vision-model",
        provider_name="prov-b",
        capabilities={ModelCapability.VISION, ModelCapability.REASONING},
        task_suitability=["vision_analysis"],
        supports_vision=True,
        supports_streaming=True,
        priority=8,
    )

    registry.register(m_fast)
    registry.register(m_vision)

    # Filter by provider
    assert len(registry.list_models(provider_name="prov-a")) == 1
    assert registry.list_models(provider_name="prov-a")[0].model_id == "fast-model"

    # Filter by capability
    assert len(registry.list_models(capability=ModelCapability.VISION)) == 1
    assert registry.list_models(capability=ModelCapability.VISION)[0].model_id == "vision-model"

    # Filter by task
    assert len(registry.list_models(task="fast_text_generation")) == 1
    assert registry.list_models(task="fast_text_generation")[0].model_id == "fast-model"

    # Filter by vision support
    assert len(registry.list_models(supports_vision=True)) == 1
    assert len(registry.list_models(supports_vision=False)) == 1
