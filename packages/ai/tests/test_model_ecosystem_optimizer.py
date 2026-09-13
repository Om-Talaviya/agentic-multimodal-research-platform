"""Unit tests for ModelEcosystemOptimizer, Pareto-frontier sorting, and profile routing."""
import pytest
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.router.optimizer import (
    ModelEcosystemOptimizer,
    OptimizationProfile,
    PRESET_PROFILES,
    ProfileType,
)
from ai.schemas import ModelCapability
from ai.providers.router import ModelRouter
from ai.providers.base import LLMProvider
from ai.schemas import LLMRequest, LLMResponse, MessageRole


class DummyLLM(LLMProvider):
    name = "dummy"
    models = ["model-fast", "model-smart", "model-free"]
    capabilities = [ModelCapability.REASONING, ModelCapability.SUMMARIZATION]
    is_local = True

    async def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="dummy response",
            role=MessageRole.ASSISTANT,
            model=request.model or "model-fast",
        )

    async def stream_complete(self, request: LLMRequest):
        yield "dummy"

    async def health_check(self):
        return True


@pytest.fixture
def sample_models():
    return [
        ModelDefinition(
            model_id="gemini-2.5-pro",
            provider_name="gemini",
            capabilities={ModelCapability.REASONING, ModelCapability.SUMMARIZATION, ModelCapability.VISION},
            priority=10,
            tier="paid",
            input_cost=0.00125,
            output_cost=0.005,
            context_window=1000000,
            is_local=False,
            task_suitability=["long_form_research", "deep_reasoning"],
        ),
        ModelDefinition(
            model_id="gemini-2.5-flash",
            provider_name="gemini",
            capabilities={ModelCapability.SUMMARIZATION, ModelCapability.VISION},
            priority=8,
            tier="paid",
            input_cost=0.00015,
            output_cost=0.0006,
            context_window=1000000,
            is_local=False,
            task_suitability=["quick_answer", "summarization"],
        ),
        ModelDefinition(
            model_id="ollama-llama3.3:70b",
            provider_name="ollama",
            capabilities={ModelCapability.REASONING, ModelCapability.SUMMARIZATION},
            priority=7,
            tier="free",
            input_cost=0.0,
            output_cost=0.0,
            context_window=128000,
            is_local=True,
            task_suitability=["deep_reasoning", "long_form_research"],
        ),
        ModelDefinition(
            model_id="ollama-qwen2.5:7b",
            provider_name="ollama",
            capabilities={ModelCapability.SUMMARIZATION},
            priority=4,
            tier="free",
            input_cost=0.0,
            output_cost=0.0,
            context_window=32000,
            is_local=True,
            task_suitability=["quick_answer"],
        ),
    ]


def test_pareto_frontier_identification(sample_models):
    frontier = ModelEcosystemOptimizer.find_pareto_frontier(sample_models, task="deep_reasoning")
    assert len(frontier) >= 1
    # ollama-llama3.3:70b has 0 cost + local speed + high reasoning, should be Pareto-optimal
    assert "ollama-llama3.3:70b" in frontier


def test_cost_minimized_profile(sample_models):
    result = ModelEcosystemOptimizer.optimize(
        candidates=sample_models,
        profile=PRESET_PROFILES[ProfileType.COST_MINIMIZED],
        task="long_form_research",
    )
    # Under cost minimization, free tier models should top the list
    assert result.selected_model_id.startswith("ollama-")
    assert result.ranked_candidates[0].cost_score == 1.0


def test_quality_maximized_profile(sample_models):
    result = ModelEcosystemOptimizer.optimize(
        candidates=sample_models,
        profile=PRESET_PROFILES[ProfileType.QUALITY_MAXIMIZED],
        task="deep_reasoning",
    )
    # gemini-2.5-pro has highest quality and context window
    assert result.selected_model_id == "gemini-2.5-pro"
    assert result.ranked_candidates[0].quality_score >= 0.7


def test_speed_maximized_profile(sample_models):
    result = ModelEcosystemOptimizer.optimize(
        candidates=sample_models,
        profile=PRESET_PROFILES[ProfileType.SPEED_MAXIMIZED],
        task="quick_answer",
    )
    # Local lightweight model should be heavily favored
    assert result.selected_model_id == "ollama-qwen2.5:7b"
    assert result.ranked_candidates[0].is_local is True


def test_router_with_optimization_profile(sample_models):
    registry = ModelRegistry()
    for m in sample_models:
        registry.register(m)

    router = ModelRouter(
        llm_providers=[DummyLLM()],
        model_registry=registry,
    )

    # Test optimize_routing method
    res = router.optimize_routing(
        task="deep_reasoning",
        profile=ProfileType.QUALITY_MAXIMIZED,
    )
    assert res.selected_model_id == "gemini-2.5-pro"
    assert "Pareto" in res.tradeoff_analysis or "Selected" in res.tradeoff_analysis
