"""Unit tests for RagasEvaluationEngine."""
import pytest
from research.evaluations.ragas_engine import RagasEvaluationEngine


def test_ragas_engine_metrics_computation():
    engine = RagasEvaluationEngine()

    # 1. Faithfulness
    answer = "The platform strictly blocks SSRF attacks and loopback requests."
    contexts = ["WebFetchTool incorporates SSRF defenses blocking private IP addresses and loopback interfaces."]
    faith = engine.compute_faithfulness(answer, contexts)
    assert faith >= 0.70

    # 2. Answer Relevancy
    query = "How does the system prevent SSRF attacks?"
    relevancy = engine.compute_answer_relevancy(query, answer)
    assert relevancy >= 0.70

    # 3. Context Precision & Recall
    gt = "SSRF defenses prevent access to private IP addresses."
    cp = engine.compute_context_precision(contexts, gt)
    cr = engine.compute_context_recall(contexts, gt)
    assert cp > 0.0
    assert cr > 0.0

    # 4. Full Benchmark Evaluation
    sample = {
        "query": query,
        "generated_answer": answer,
        "ground_truth": gt,
        "retrieved_contexts": contexts,
    }
    result = engine.evaluate_benchmark_suite(
        name="Security & Groundedness Test",
        samples_data=[sample]
    )
    assert result["total_samples"] == 1
    assert result["avg_faithfulness"] >= 0.70
    assert result["red_team_defense_rate"] == 1.0
    assert len(result["probes"]) == 4
