"""Model evaluation engine for automated benchmarking across providers."""
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

from ai.eval.metrics import EvaluationMetricsEngine
from ai.eval.schemas import (
    BenchmarkDataset,
    BenchmarkSample,
    DEFAULT_RESEARCH_BENCHMARK,
    EvaluationMetric,
)
from ai.gateway.model_gateway import ModelGateway
from ai.registry.model_registry import ModelDefinition
from ai.schemas import LLMMessage, LLMRequest, MessageRole
from shared.logging import get_logger

logger = get_logger(__name__)


class SampleEvaluationResult(BaseModel):
    """Detailed score report for a single benchmark test case."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    category: str
    prompt: str
    response_text: str
    metrics: Dict[str, float]
    passed: bool
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    error: Optional[str] = None


class EvaluationReport(BaseModel):
    """Comprehensive evaluation summary for a model across a benchmark dataset."""
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(default_factory=lambda: str(uuid4()))
    model_id: str
    provider_name: str
    benchmark_name: str
    total_samples: int
    passed_samples: int
    pass_rate: float
    overall_score: float
    mean_accuracy: float
    mean_reasoning: float
    mean_faithfulness: float
    mean_citation_precision: float
    mean_latency_ms: float
    total_cost_usd: float
    category_scores: Dict[str, float] = Field(default_factory=dict)
    sample_results: List[SampleEvaluationResult] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class LeaderboardEntry(BaseModel):
    """Summary record for competitive model leaderboard ranking."""
    model_config = ConfigDict(protected_namespaces=())

    rank: int
    model_id: str
    provider_name: str
    overall_score: float
    factual_accuracy: float
    reasoning_depth: float
    retrieval_faithfulness: float
    mean_latency_ms: float
    cost_per_1k_usd: float
    tier: str
    is_local: bool
    is_pareto_optimal: bool = False
    last_evaluated: float


class ModelEvaluator:
    """Orchestrates benchmark evaluation runs and leaderboard generation."""

    def __init__(self, gateway: ModelGateway) -> None:
        self.gateway = gateway

    async def evaluate_model(
        self,
        model_id: str,
        benchmark: Optional[BenchmarkDataset] = None,
    ) -> EvaluationReport:
        """Run all test samples in a benchmark suite against target model."""
        target_benchmark = benchmark or DEFAULT_RESEARCH_BENCHMARK
        logger.info(
            "Starting model benchmark evaluation",
            model_id=model_id,
            benchmark=target_benchmark.name,
            samples=len(target_benchmark.samples),
        )

        sample_results: List[SampleEvaluationResult] = []
        category_totals: Dict[str, List[float]] = {}
        total_cost = 0.0

        for sample in target_benchmark.samples:
            prompt_content = sample.prompt
            if sample.context:
                prompt_content = f"Context:\n{sample.context}\n\nQuestion:\n{sample.prompt}"

            request = LLMRequest(
                model=model_id,
                messages=[
                    LLMMessage(role=MessageRole.USER, content=prompt_content),
                ],
                temperature=0.1,  # Low temperature for deterministic evaluation
            )

            start_t = time.perf_counter()
            response_text = ""
            error_msg: Optional[str] = None
            prompt_tokens = 0
            completion_tokens = 0
            cost_usd = 0.0

            try:
                resp = await self.gateway.complete(request, fallback_enabled=False)
                response_text = resp.content
                if resp.usage and isinstance(resp.usage, dict):
                    prompt_tokens = int(resp.usage.get("prompt_tokens") or resp.usage.get("input_tokens") or 0)
                    completion_tokens = int(resp.usage.get("completion_tokens") or resp.usage.get("output_tokens") or 0)
                cost_usd = resp.metadata.get("cost_usd", 0.0)
            except Exception as exc:
                error_msg = str(exc)
                logger.warning("Evaluation sample execution failed", model_id=model_id, sample_id=sample.id, error=str(exc))
                response_text = ""

            latency_ms = int((time.perf_counter() - start_t) * 1000)
            total_cost += cost_usd

            metrics = EvaluationMetricsEngine.evaluate_sample(
                response_text=response_text,
                sample=sample,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost_usd,
            )

            passed = metrics[EvaluationMetric.OVERALL_SCORE.value] >= 0.5 and not error_msg
            category_totals.setdefault(sample.category.value, []).append(metrics[EvaluationMetric.OVERALL_SCORE.value])

            sample_results.append(
                SampleEvaluationResult(
                    sample_id=sample.id,
                    category=sample.category.value,
                    prompt=sample.prompt,
                    response_text=response_text,
                    metrics=metrics,
                    passed=passed,
                    latency_ms=latency_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=cost_usd,
                    error=error_msg,
                )
            )

        # Aggregate metrics
        n = len(sample_results)
        passed_count = sum(1 for s in sample_results if s.passed)
        mean_acc = sum(s.metrics[EvaluationMetric.FACTUAL_ACCURACY.value] for s in sample_results) / n if n else 0.0
        mean_reason = sum(s.metrics[EvaluationMetric.REASONING_DEPTH.value] for s in sample_results) / n if n else 0.0
        mean_faith = sum(s.metrics[EvaluationMetric.RETRIEVAL_FAITHFULNESS.value] for s in sample_results) / n if n else 0.0
        mean_cite = sum(s.metrics[EvaluationMetric.CITATION_PRECISION.value] for s in sample_results) / n if n else 0.0
        mean_lat = sum(s.latency_ms for s in sample_results) / n if n else 0.0
        overall = sum(s.metrics[EvaluationMetric.OVERALL_SCORE.value] for s in sample_results) / n if n else 0.0

        cat_scores = {
            cat: round(sum(scores) / len(scores), 4)
            for cat, scores in category_totals.items()
        }

        # Lookup provider name from registry
        model_def = self.gateway.model_registry.get(model_id)
        prov_name = model_def.provider_name if model_def else "unknown"

        report = EvaluationReport(
            model_id=model_id,
            provider_name=prov_name,
            benchmark_name=target_benchmark.name,
            total_samples=n,
            passed_samples=passed_count,
            pass_rate=round(passed_count / n, 4) if n else 0.0,
            overall_score=round(overall, 4),
            mean_accuracy=round(mean_acc, 4),
            mean_reasoning=round(mean_reason, 4),
            mean_faithfulness=round(mean_faith, 4),
            mean_citation_precision=round(mean_cite, 4),
            mean_latency_ms=round(mean_lat, 1),
            total_cost_usd=round(total_cost, 6),
            category_scores=cat_scores,
            sample_results=sample_results,
        )

        logger.info(
            "Model benchmark evaluation completed",
            model_id=model_id,
            overall_score=report.overall_score,
            pass_rate=report.pass_rate,
        )
        return report
