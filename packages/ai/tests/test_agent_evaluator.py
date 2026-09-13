"""Unit tests for Agent Evaluator Engine and Metrics."""

import pytest
from ai.eval.agent_evaluator import (
    AgentEvaluator,
    AgentEvaluationScorecard,
    AgentStepTelemetry,
    AgentEvaluationMetric,
)


def test_agent_evaluation_metrics_enum():
    """Verify standard AgentEvaluationMetric enum keys."""
    assert AgentEvaluationMetric.PLAN_PRECISION.value == "plan_precision"
    assert AgentEvaluationMetric.TOOL_CALL_ACCURACY.value == "tool_call_accuracy"
    assert AgentEvaluationMetric.EVIDENCE_COVERAGE.value == "evidence_coverage"
    assert AgentEvaluationMetric.HALLUCINATION_RATE.value == "hallucination_rate"
    assert AgentEvaluationMetric.CONTRADICTION_RESILIENCE.value == "contradiction_resilience"
    assert AgentEvaluationMetric.SYNTHESIS_FIDELITY.value == "synthesis_fidelity"
    assert AgentEvaluationMetric.OVERALL_AGENT_SCORE.value == "overall_agent_score"


def test_evaluate_plan_precision():
    """Test plan precision scoring based on task relevance and diversity."""
    objective = "Investigate quantum computing superconducting qubits error correction"
    plan_tasks = [
        {"title": "Search superconducting qubits architecture"},
        {"title": "Retrieve quantum error correction schemes"},
        {"title": "Synthesize fault-tolerant quantum computing report"},
    ]
    precision = AgentEvaluator.evaluate_plan_precision(plan_tasks, objective)
    assert precision > 0.8

    # Empty plan test
    assert AgentEvaluator.evaluate_plan_precision([], objective) == 0.0


def test_evaluate_tool_accuracy():
    """Test tool execution telemetry accuracy scoring."""
    telemetries = [
        AgentStepTelemetry(
            step_index=0,
            agent_type="web_agent",
            action_type="tool_execution",
            tool_name="web_search",
            success=True,
            latency_ms=100,
        ),
        AgentStepTelemetry(
            step_index=1,
            agent_type="web_agent",
            action_type="tool_execution",
            tool_name="web_fetch",
            success=True,
            latency_ms=200,
        ),
        AgentStepTelemetry(
            step_index=2,
            agent_type="web_agent",
            action_type="tool_execution",
            tool_name="doc_reader",
            success=False,
            error_message="Connection timed out",
            latency_ms=5000,
        ),
    ]

    accuracy = AgentEvaluator.evaluate_tool_accuracy(telemetries)
    assert accuracy == round(2 / 3, 4)

    # Empty telemetries should return 1.0 default
    assert AgentEvaluator.evaluate_tool_accuracy([]) == 1.0


def test_evaluate_evidence_coverage():
    """Test claim grounding coverage against source evidence."""
    evidence = [
        {"content": "Quantum error correction utilizes surface codes to achieve fault-tolerant thresholds."},
        {"content": "Superconducting circuits operate at millikelvin temperatures."},
    ]
    claims = [
        "Quantum error correction employs surface code topologies.",
        "Cryogenic dilution refrigerators keep qubits at millikelvin temperatures.",
    ]
    coverage = AgentEvaluator.evaluate_evidence_coverage(evidence, claims)
    assert coverage >= 0.5

    # Empty claims should yield 1.0, empty evidence should yield 0.0
    assert AgentEvaluator.evaluate_evidence_coverage(evidence, []) == 1.0
    assert AgentEvaluator.evaluate_evidence_coverage([], claims) == 0.0


def test_evaluate_hallucination_rate():
    """Test hallucination detection on grounded vs ungrounded text."""
    evidence = [
        {"content": "Transformer architectures utilize self-attention mechanisms to process sequential data."}
    ]
    grounded_report = "Transformer architectures utilize self-attention mechanisms to process data sequences."
    ungrounded_report = "Magical crystals transmit quantum psychic signals across parallel dimensions instantly."

    hallucination_grounded = AgentEvaluator.evaluate_hallucination_rate(grounded_report, evidence)
    assert hallucination_grounded == 0.0

    hallucination_ungrounded = AgentEvaluator.evaluate_hallucination_rate(ungrounded_report, evidence)
    assert hallucination_ungrounded > 0.5


def test_evaluate_job_execution_composite_scorecard():
    """Test end-to-end scorecard generation."""
    steps = [
        AgentStepTelemetry(
            step_index=0,
            agent_type="planner",
            action_type="plan_generation",
            tool_name=None,
            success=True,
        ),
        AgentStepTelemetry(
            step_index=1,
            agent_type="web_agent",
            action_type="tool_execution",
            tool_name="web_search",
            success=True,
            latency_ms=150,
            tokens_consumed=80,
        ),
    ]
    plan_tasks = [{"title": "Explore transformer scaling laws"}]
    evidence = [{"content": "Transformer scaling laws demonstrate compute optimal training."}]
    report = "Transformer scaling laws demonstrate compute optimal training curves."

    scorecard = AgentEvaluator.evaluate_job_execution(
        job_id="job_test_001",
        agent_name="research_pipeline",
        plan_tasks=plan_tasks,
        research_objective="transformer scaling laws",
        step_telemetry=steps,
        evidence_items=evidence,
        report_text=report,
        execution_time_ms=1200,
        total_tokens=500,
        cost_usd=0.0001,
    )

    assert isinstance(scorecard, AgentEvaluationScorecard)
    assert scorecard.job_id == "job_test_001"
    assert scorecard.total_steps == 2
    assert scorecard.successful_steps == 2
    assert scorecard.failed_steps == 0
    assert scorecard.tool_accuracy == 1.0
    assert scorecard.overall_score > 0.8
