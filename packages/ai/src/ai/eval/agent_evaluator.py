"""Agent Evaluation Engine for measuring agent reasoning, tool precision, and hallucination rates."""
from enum import Enum
import re
import time
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

from shared.logging import get_logger
from shared.types import JSONDict

logger = get_logger(__name__)


class AgentEvaluationMetric(str, Enum):
    PLAN_PRECISION = "plan_precision"
    TOOL_CALL_ACCURACY = "tool_call_accuracy"
    EVIDENCE_COVERAGE = "evidence_coverage"
    HALLUCINATION_RATE = "hallucination_rate"
    CONTRADICTION_RESILIENCE = "contradiction_resilience"
    SYNTHESIS_FIDELITY = "synthesis_fidelity"
    OVERALL_AGENT_SCORE = "overall_agent_score"


class AgentStepTelemetry(BaseModel):
    """Execution telemetry for a single agent action step."""
    model_config = ConfigDict(protected_namespaces=())

    step_index: int
    agent_type: str
    action_type: str
    tool_name: Optional[str] = None
    tool_args: JSONDict = Field(default_factory=dict)
    tool_output_length: int = 0
    success: bool = True
    error_message: Optional[str] = None
    latency_ms: int = 0
    tokens_consumed: int = 0


class AgentEvaluationScorecard(BaseModel):
    """Complete evaluation scorecard for an agent or research job execution."""
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: Optional[str] = None
    agent_name: str
    total_steps: int
    successful_steps: int
    failed_steps: int
    plan_precision: float
    tool_accuracy: float
    evidence_coverage: float
    hallucination_rate: float
    synthesis_fidelity: float
    overall_score: float
    execution_time_ms: int
    total_tokens: int
    estimated_cost_usd: float
    step_telemetry: List[AgentStepTelemetry] = Field(default_factory=list)
    findings_audit: JSONDict = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class AgentEvaluator:
    """Evaluates agent execution runs, assessing step efficacy and report faithfulness."""

    @staticmethod
    def evaluate_plan_precision(
        plan_tasks: List[Dict[str, Any]],
        research_objective: str,
    ) -> float:
        """Measure whether planned DAG tasks are relevant, non-empty, and comprehensive."""
        if not plan_tasks:
            return 0.0

        objective_words = set(re.findall(r"\w+", research_objective.lower()))
        stopwords = {"the", "a", "an", "is", "in", "of", "to", "for", "with", "and", "or"}
        content_objective_words = {w for w in objective_words if len(w) > 3 and w not in stopwords}

        if not content_objective_words:
            return 1.0

        matched_tasks = 0
        for task in plan_tasks:
            task_desc = (task.get("description") or task.get("title") or "").lower()
            task_words = set(re.findall(r"\w+", task_desc))
            if any(w in task_words for w in content_objective_words):
                matched_tasks += 1

        relevance_ratio = matched_tasks / len(plan_tasks)
        diversity_score = min(len(plan_tasks) / 3.0, 1.0)  # Reward balanced 3+ step plans
        return round(min((relevance_ratio * 0.7) + (diversity_score * 0.3), 1.0), 4)

    @staticmethod
    def evaluate_tool_accuracy(step_history: List[AgentStepTelemetry]) -> float:
        """Measure tool execution success rate without crashes or parameter failures."""
        if not step_history:
            return 1.0

        tool_steps = [s for s in step_history if s.tool_name]
        if not tool_steps:
            return 1.0

        successes = sum(1 for s in tool_steps if s.success and not s.error_message)
        return round(successes / len(tool_steps), 4)

    @staticmethod
    def evaluate_evidence_coverage(
        evidence_items: List[Dict[str, Any]],
        claims: List[str],
    ) -> float:
        """Assess the proportion of claims supported by grounded evidence items."""
        if not claims:
            return 1.0
        if not evidence_items:
            return 0.0

        all_evidence_text = " ".join(
            (e.get("content") or e.get("snippet") or e.get("text") or "").lower()
            for e in evidence_items
        )

        supported_claims = 0
        for claim in claims:
            words = [w for w in re.findall(r"\w+", claim.lower()) if len(w) > 3]
            if not words:
                supported_claims += 1
                continue
            matches = sum(1 for w in words if w in all_evidence_text)
            if (matches / len(words)) >= 0.5:
                supported_claims += 1

        return round(supported_claims / len(claims), 4)

    @staticmethod
    def evaluate_hallucination_rate(
        report_text: str,
        source_evidence: List[Dict[str, Any]],
    ) -> float:
        """Estimate hallucination rate based on ungrounded factual assertions [0.0 - 1.0]."""
        if not report_text.strip() or not source_evidence:
            return 0.0

        sentences = [s.strip() for s in re.split(r"[.!?]\s+", report_text) if len(s.strip()) > 20]
        if not sentences:
            return 0.0

        all_evidence_words = set(
            re.findall(r"\w+", " ".join(
                (e.get("content") or e.get("snippet") or e.get("text") or "").lower()
                for e in source_evidence
            ))
        )

        ungrounded_sentences = 0
        stopwords = {"this", "that", "these", "those", "have", "with", "from", "their", "which", "there", "about"}

        for sentence in sentences:
            words = [w for w in re.findall(r"\w+", sentence.lower()) if len(w) > 4 and w not in stopwords]
            if not words:
                continue
            grounded_ratio = sum(1 for w in words if w in all_evidence_words) / len(words)
            if grounded_ratio < 0.25:  # Less than 25% overlap with source evidence
                ungrounded_sentences += 1

        return round(ungrounded_sentences / len(sentences), 4)

    @classmethod
    def evaluate_job_execution(
        cls,
        job_id: str,
        agent_name: str,
        plan_tasks: List[Dict[str, Any]],
        research_objective: str,
        step_telemetry: List[AgentStepTelemetry],
        evidence_items: List[Dict[str, Any]],
        report_text: str,
        claims: Optional[List[str]] = None,
        execution_time_ms: int = 0,
        total_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> AgentEvaluationScorecard:
        """Perform full multi-dimensional evaluation scorecard computation."""
        extracted_claims = claims or [
            s.strip() for s in re.split(r"[.!?]\s+", report_text) if len(s.strip()) > 25
        ]

        plan_prec = cls.evaluate_plan_precision(plan_tasks, research_objective)
        tool_acc = cls.evaluate_tool_accuracy(step_telemetry)
        cov = cls.evaluate_evidence_coverage(evidence_items, extracted_claims)
        hallucination = cls.evaluate_hallucination_rate(report_text, evidence_items)
        synthesis_fid = round(max(1.0 - hallucination, 0.0), 4)

        # Composite score
        # 25% Plan + 25% Tool + 25% Coverage + 25% Synthesis Fidelity (with hallucination penalty)
        overall = round(
            (plan_prec * 0.25)
            + (tool_acc * 0.25)
            + (cov * 0.25)
            + (synthesis_fid * 0.25),
            4,
        )

        successful_steps = sum(1 for s in step_telemetry if s.success)
        failed_steps = len(step_telemetry) - successful_steps

        scorecard = AgentEvaluationScorecard(
            job_id=job_id,
            agent_name=agent_name,
            total_steps=len(step_telemetry),
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            plan_precision=plan_prec,
            tool_accuracy=tool_acc,
            evidence_coverage=cov,
            hallucination_rate=hallucination,
            synthesis_fidelity=synthesis_fid,
            overall_score=overall,
            execution_time_ms=execution_time_ms,
            total_tokens=total_tokens,
            estimated_cost_usd=cost_usd,
            step_telemetry=step_telemetry,
            findings_audit={
                "claims_evaluated": len(extracted_claims),
                "evidence_sources": len(evidence_items),
                "unsupported_claims": int(len(extracted_claims) * (1.0 - cov)),
            },
        )

        logger.info(
            "Agent execution evaluated",
            agent_name=agent_name,
            overall_score=scorecard.overall_score,
            tool_accuracy=scorecard.tool_accuracy,
            hallucination_rate=scorecard.hallucination_rate,
        )
        return scorecard
