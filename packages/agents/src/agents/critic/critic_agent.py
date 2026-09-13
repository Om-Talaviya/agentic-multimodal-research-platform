"""Critic and quality evaluation agent for evidence verification and factual grounding."""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4
from agents.base import Agent, AgentContext, AgentResult
from research.models import Evidence, ResearchTask
from ai.schemas import LLMMessage, LLMRequest, ModelCapabilities
from ai.providers.router import ModelRouter
from shared.logging import get_logger

logger = get_logger(__name__)


class CriticAgent(Agent):
    """Evaluates evidence validity, detects hallucinations/contradictions, and scores research output quality."""

    name = "critic"
    description = "Evaluates evidence validity, identifies contradictions, and verifies factual grounding"
    capabilities = {"verification", "critic", "fact_checking", "quality_assessment"}

    SYSTEM_PROMPT = """You are an advanced research critic, fact-checking, contradiction-detection, and deep gap analysis agent.
Your objective is to:
1. Evaluate research claims against supporting evidence, assign verification statuses, and validate citations.
2. Detect pairwise or multi-source CONTRADICTIONS, classifying them into:
   - "direct_conflict": Sources make incompatible factual claims.
   - "numerical_discrepancy": Discrepant statistics, percentages, dates, or measurements across sources.
   - "methodological_divergence": Differences resulting from distinct evaluation methodologies, sample sizes, or baseline definitions.
3. Identify UNRESOLVED GAPS in evidence or missing dimensions required to comprehensively answer the research inquiry.
4. Formulate precise GAP QUERIES and testable HYPOTHESES to guide recursive follow-up investigations.
5. Calculate an overall quantitative factual confidence score (0.0 to 1.0).

Verification statuses:
- "verified": The supporting text directly and unambiguously substantiates the claim.
- "refuted": The supporting text directly contradicts or disproves the claim.
- "inconclusive": The supporting text is insufficient, ambiguous, or only partially supports the claim.

Return your evaluation as a JSON object with this exact structure:
{
    "verifications": [
        {
            "evidence_id": "optional-id",
            "claim": "claim text",
            "verification_status": "verified|refuted|inconclusive",
            "confidence": 0.95,
            "source_reliability": 1.0,
            "verification_notes": "detailed explanation of why this status was assigned"
        }
    ],
    "contradictions": [
        {
            "topic": "topic or subject matter of conflict",
            "claim_a": "first claim statement",
            "source_a": "source / citation A identifier or title",
            "claim_b": "conflicting claim statement",
            "source_b": "source / citation B identifier or title",
            "conflict_type": "direct_conflict|numerical_discrepancy|methodological_divergence",
            "explanation": "concise explanation of the contradiction and root cause",
            "severity": "low|medium|high"
        }
    ],
    "unresolved_gaps": [
        "Description of missing data point or unverified area"
    ],
    "gap_queries": [
        "targeted search query to fill gap or resolve contradiction"
    ],
    "suggested_hypotheses": [
        "Testable hypothesis proposition explaining discrepancy"
    ],
    "confidence_score": 0.88,
    "quality_score": 0.85,
    "critique_summary": "Overall assessment of evidence reliability, contradictions found, gaps, and potential bias"
}
"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        """Run critic evaluation on research findings, claims, or raw evidence."""
        evidence_items = task.inputs.get("evidence", [])
        question = task.inputs.get("question") or task.objective

        if not evidence_items:
            logger.info("No evidence provided to CriticAgent, skipping verification", task_id=task.id)
            return AgentResult(
                success=True,
                output={
                    "verifications": [],
                    "contradictions": [],
                    "confidence_score": 1.0,
                    "quality_score": 1.0,
                    "critique_summary": "No evidence items to evaluate",
                },
                metadata={"evaluated_count": 0, "contradictions_count": 0},
            )

        # Prepare evidence prompt text
        formatted_evidence = []
        for i, ev in enumerate(evidence_items):
            if isinstance(ev, dict):
                ev_id = ev.get("id", f"ev_{i}")
                claim = ev.get("claim", "")
                text = ev.get("supporting_text", "")
                source_id = ev.get("source_id", "")
                reliability = ev.get("source_reliability", 1.0)
                coords = ev.get("citation_coordinates") or ev.get("coordinates") or {}
            elif hasattr(ev, "claim"):
                ev_id = str(getattr(ev, "id", f"ev_{i}"))
                claim = getattr(ev, "claim", "")
                text = getattr(ev, "supporting_text", "")
                source_id = str(getattr(ev, "source_id", ""))
                reliability = getattr(ev, "source_reliability", 1.0)
                coords = getattr(ev, "coordinates", None) or getattr(ev, "citation_coordinates", None) or {}
            else:
                continue

            coord_str = f" | Coordinates: {coords}" if coords else ""
            formatted_evidence.append(
                f"[Evidence #{i+1} | ID: {ev_id} | Source: {source_id} | Reliability: {reliability}{coord_str}]\n"
                f"Claim: {claim}\n"
                f"Supporting Text: {text[:2000]}\n"
            )

        user_content = (
            f"Research Question: {question}\n\n"
            f"Please verify the following {len(formatted_evidence)} evidence items and identify any contradictions among them:\n\n"
            + "\n---\n".join(formatted_evidence[:25])
        )

        try:
            response = await context.complete_llm(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=user_content),
                    ],
                    temperature=0.1,
                    json_mode=True,
                ),
                task="research",
            )

            raw_content = response.content.strip()
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            result_data = json.loads(raw_content)
            verifications = result_data.get("verifications", [])
            contradictions = result_data.get("contradictions", [])
            unresolved_gaps = result_data.get("unresolved_gaps", [])
            gap_queries = result_data.get("gap_queries", [])
            suggested_hypotheses = result_data.get("suggested_hypotheses", [])
            quality_score = float(result_data.get("quality_score", 0.8))
            confidence_score = float(result_data.get("confidence_score", quality_score))
            summary = result_data.get("critique_summary", "")

            # If gap_queries weren't provided but contradictions exist, generate targeted queries
            if not gap_queries and contradictions:
                for c in contradictions:
                    topic = c.get("topic", "")
                    if topic:
                        gap_queries.append(f"Resolve conflict in {topic} evidence")

            # Update working memory
            context.memory.set_working("last_critic_score", quality_score)
            context.memory.set_working("last_confidence_score", confidence_score)
            context.memory.set_working("last_contradictions", contradictions)
            context.memory.set_working("last_unresolved_gaps", unresolved_gaps)
            context.memory.set_working("last_gap_queries", gap_queries)
            context.memory.set_working("last_hypotheses", suggested_hypotheses)
            context.memory.set_working("last_critic_summary", summary)

            logger.info(
                "CriticAgent completed evaluation",
                task_id=task.id,
                evaluated_count=len(verifications),
                contradictions_count=len(contradictions),
                unresolved_gaps_count=len(unresolved_gaps),
                confidence_score=confidence_score,
                quality_score=quality_score,
            )

            return AgentResult(
                success=True,
                output={
                    "verifications": verifications,
                    "contradictions": contradictions,
                    "unresolved_gaps": unresolved_gaps,
                    "gap_queries": gap_queries,
                    "suggested_hypotheses": suggested_hypotheses,
                    "confidence_score": confidence_score,
                    "quality_score": quality_score,
                    "critique_summary": summary,
                },
                metadata={
                    "model": response.model,
                    "evaluated_count": len(verifications),
                    "contradictions_count": len(contradictions),
                    "unresolved_gaps_count": len(unresolved_gaps),
                    "confidence_score": confidence_score,
                    "quality_score": quality_score,
                },
            )

        except Exception as e:
            logger.error("CriticAgent evaluation failed", error=str(e), task_id=task.id)
            return AgentResult(
                success=False,
                errors=[f"Critic evaluation failed: {str(e)}"],
            )
