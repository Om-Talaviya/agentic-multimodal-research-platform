"""Tests for Model Evaluation Suite, Metrics Engine, and Benchmarking."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from ai.eval.metrics import EvaluationMetricsEngine
from ai.eval.evaluator import ModelEvaluator, EvaluationReport
from ai.eval.schemas import (
    BenchmarkCategory,
    BenchmarkDataset,
    BenchmarkSample,
    DEFAULT_RESEARCH_BENCHMARK,
    EvaluationMetric,
)
from ai.gateway.model_gateway import ModelGateway
from ai.schemas import LLMResponse


def test_benchmark_dataset_structure():
    """Verify default benchmark contains balanced research tasks."""
    assert len(DEFAULT_RESEARCH_BENCHMARK.samples) >= 4
    categories = {s.category for s in DEFAULT_RESEARCH_BENCHMARK.samples}
    assert BenchmarkCategory.FACTUAL_RETRIEVAL in categories
    assert BenchmarkCategory.REASONING in categories
    assert BenchmarkCategory.CITATION_ACCURACY in categories


def test_metrics_engine_factual_accuracy():
    """Verify factual accuracy calculation with keyword coverage."""
    sample = BenchmarkSample(
        id="sample_test",
        category=BenchmarkCategory.FACTUAL_RETRIEVAL,
        prompt="Explain PLA bioplastics degradation.",
        expected_keywords=["industrial composting", "58°C", "hydrolysis", "marine", "persistence"],
    )

    # High match
    score_high = EvaluationMetricsEngine.calculate_factual_accuracy(
        response_text="PLA requires industrial composting at >58°C for hydrolysis. In marine environments, persistence is high.",
        sample=sample,
    )
    assert score_high == 1.0

    # Partial match
    score_partial = EvaluationMetricsEngine.calculate_factual_accuracy(
        response_text="PLA bioplastics undergo hydrolysis under high temperature industrial composting.",
        sample=sample,
    )
    assert score_partial == 0.4


def test_metrics_engine_reasoning_depth():
    """Verify multi-step reasoning marker extraction."""
    sample = BenchmarkSample(
        id="sample_reason",
        category=BenchmarkCategory.REASONING,
        prompt="Compare battery architectures.",
        min_reasoning_steps=3,
    )

    multi_step_response = (
        "Let's evaluate the architecture step by step:\n"
        "1. First, we examine volumetric energy density.\n"
        "2. Therefore, solid-state electrolytes suppress dendrite formation.\n"
        "3. Consequently, thermal runaway thresholds are significantly higher.\n"
        "In comparison to conventional liquid cells, safety and performance show marked improvement across the entire operating cycle."
    )
    score_reasoning = EvaluationMetricsEngine.calculate_reasoning_depth(
        response_text=multi_step_response,
        sample=sample,
    )
    assert score_reasoning >= 0.70

    # Superficial short response
    score_simple = EvaluationMetricsEngine.calculate_reasoning_depth(
        response_text="Solid state is better.",
        sample=sample,
    )
    assert score_simple <= 0.40


def test_metrics_engine_retrieval_faithfulness():
    """Verify claim grounding against reference context."""
    sample = BenchmarkSample(
        id="sample_faith",
        category=BenchmarkCategory.FACTUAL_RETRIEVAL,
        prompt="Who flew Apollo 11?",
        context="The Apollo 11 spacecraft launched in July 1969 carrying Neil Armstrong and Buzz Aldrin to the Moon.",
    )

    grounded_ans = "The Apollo 11 spacecraft launched in July 1969 carrying Neil Armstrong and Buzz Aldrin."
    hallucinated_ans = "Elon Musk launched SpaceX Starship to Mars in 2024 with different astronauts."

    faith_high = EvaluationMetricsEngine.calculate_retrieval_faithfulness(grounded_ans, sample)
    faith_low = EvaluationMetricsEngine.calculate_retrieval_faithfulness(hallucinated_ans, sample)

    assert faith_high >= 0.70
    assert faith_low <= 0.40


def test_metrics_engine_citation_precision():
    """Verify citation marker extraction and precision scoring."""
    sample = BenchmarkSample(
        id="sample_cite",
        category=BenchmarkCategory.CITATION_ACCURACY,
        prompt="Extract findings with citations.",
        required_citations=["smith_2025_table_3"],
    )

    ans_with_citations = "According to smith_2025_table_3, membrane bioreactors reached 99.4% retention."
    cit_score = EvaluationMetricsEngine.calculate_citation_precision(ans_with_citations, sample)
    assert cit_score == 1.0

    no_cit = "Membrane bioreactors reached 99.4% retention."
    cit_score_zero = EvaluationMetricsEngine.calculate_citation_precision(no_cit, sample)
    assert cit_score_zero == 0.0


@pytest.mark.asyncio
async def test_model_evaluator_execution():
    """Verify end-to-end benchmark evaluation with mocked ModelGateway."""
    mock_gateway = MagicMock()
    mock_gateway.complete = AsyncMock()

    # Configure mock responses for samples
    mock_gateway.complete.return_value = LLMResponse(
        content="First, PLA requires industrial composting at >58°C for hydrolysis. Therefore, marine persistence is prolonged.",
        model="gemini-2.0-flash",
        usage={"prompt_tokens": 40, "completion_tokens": 30, "total_tokens": 70},
        metadata={"cost_usd": 0.00003},
    )

    mock_def = MagicMock()
    mock_def.provider_name = "gemini"
    mock_gateway.model_registry = MagicMock()
    mock_gateway.model_registry.get.return_value = mock_def

    evaluator = ModelEvaluator(mock_gateway)
    
    # Run against a subset benchmark
    test_benchmark = BenchmarkDataset(
        name="test_mini_bench",
        description="Mini test benchmark",
        samples=DEFAULT_RESEARCH_BENCHMARK.samples[:2],
    )

    report: EvaluationReport = await evaluator.evaluate_model(
        model_id="gemini-2.0-flash",
        benchmark=test_benchmark,
    )

    assert report.model_id == "gemini-2.0-flash"
    assert report.provider_name == "gemini"
    assert report.total_samples == 2
    assert report.overall_score > 0.0
    assert report.mean_latency_ms >= 0.0
    assert len(report.sample_results) == 2
