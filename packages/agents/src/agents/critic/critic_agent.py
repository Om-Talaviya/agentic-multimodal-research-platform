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

    SYSTEM_PROMPT = """You are a rigorous research critic and fact-checking agent.
Your objective is to evaluate research claims against supporting evidence, detect contradictions, and assign an accurate verification status.

Verification statuses:
- "verified": The supporting text directly and unambiguously substantiates the claim.
- "refuted": The supporting text directly contradicts or disproves the claim.
- "inconclusive": The supporting text is insufficient, ambiguous, or only partially supports the claim.

Return your evaluation as a JSON object with this structure:
{
    "verifications": [
        {
            "evidence_id": "optional-id",
            "claim": "claim text",
            "verification_status": "verified|refuted|inconclusive",
            "confidence": 0.95,
            "verification_notes": "detailed explanation of why this status was assigned"
        }
    ],
    "quality_score": 0.85,
    "critique_summary": "Overall assessment of evidence reliability, gaps, and potential bias"
}
"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        """Run critic evaluation on research findings, claims, or raw evidence."""
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("research"))

        evidence_items = task.inputs.get("evidence", [])
        question = task.inputs.get("question") or task.objective

        if not evidence_items:
            logger.info("No evidence provided to CriticAgent, skipping verification", task_id=task.id)
            return AgentResult(
                success=True,
                output={
                    "verifications": [],
                    "quality_score": 1.0,
                    "critique_summary": "No evidence items to evaluate",
                },
                metadata={"evaluated_count": 0},
            )

        # Prepare evidence prompt text
        formatted_evidence = []
        for i, ev in enumerate(evidence_items):
            if isinstance(ev, dict):
                ev_id = ev.get("id", f"ev_{i}")
                claim = ev.get("claim", "")
                text = ev.get("supporting_text", "")
            elif hasattr(ev, "claim"):
                ev_id = str(getattr(ev, "id", f"ev_{i}"))
                claim = getattr(ev, "claim", "")
                text = getattr(ev, "supporting_text", "")
            else:
                continue

            formatted_evidence.append(
                f"[Evidence #{i+1} | ID: {ev_id}]\nClaim: {claim}\nSupporting Text: {text[:2000]}\n"
            )

        user_content = (
            f"Research Question: {question}\n\n"
            f"Please verify the following {len(formatted_evidence)} evidence items:\n\n"
            + "\n---\n".join(formatted_evidence[:20])
        )

        try:
            response = await llm.complete(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=user_content),
                    ],
                    temperature=0.1,
                    json_mode=True,
                )
            )

            result_data = json.loads(response.content)
            verifications = result_data.get("verifications", [])
            quality_score = float(result_data.get("quality_score", 0.8))
            summary = result_data.get("critique_summary", "")

            # Update working memory
            context.memory.set_working("last_critic_score", quality_score)
            context.memory.set_working("last_critic_summary", summary)

            logger.info(
                "CriticAgent completed evaluation",
                task_id=task.id,
                evaluated_count=len(verifications),
                quality_score=quality_score,
            )

            return AgentResult(
                success=True,
                output={
                    "verifications": verifications,
                    "quality_score": quality_score,
                    "critique_summary": summary,
                },
                metadata={
                    "model": response.model,
                    "evaluated_count": len(verifications),
                    "quality_score": quality_score,
                },
            )

        except Exception as e:
            logger.error("CriticAgent evaluation failed", error=str(e), task_id=task.id)
            return AgentResult(
                success=False,
                errors=[f"Critic evaluation failed: {str(e)}"],
            )
