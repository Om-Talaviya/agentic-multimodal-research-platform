"""Opposer Agent: Probes edge cases, tests assumptions, and formulates rigorous counterarguments."""

import json
from typing import Any, Dict, List, Optional
from agents.base import Agent, AgentContext, AgentResult
from ai.schemas import LLMMessage, LLMRequest
from shared.logging import get_logger

logger = get_logger(__name__)


class OpposerAgent(Agent):
    """Skeptical adversarial agent probing weaknesses and constructing counter-theses."""

    name = "opposer"
    description = "Formulates rigorous counterarguments, surfaces methodological flaws, and challenges assumptions in debates"
    capabilities = {"debate_opposer", "counterargumentation", "critical_scrutiny", "fallacy_detection"}

    SYSTEM_PROMPT = """You are the OPPOSER AGENT in an adversarial multi-agent research debate.
Your mission is to rigorously test, scrutinize, and challenge the Proposer's thesis and arguments.

Objectives:
1. Identify logical fallacies, unproven assumptions, survivorship biases, or methodological weaknesses.
2. Introduce counter-evidence, boundary failure conditions, edge cases, and alternative explanations.
3. Attack the specific claims made by the Proposer in their latest argument.
4. Concede points where empirical evidence is undeniable, but isolate the remaining limits of validity.

Return your response strictly as a JSON object:
{
    "argument_text": "Detailed multi-paragraph logical counterargument...",
    "counter_claims": ["counter claim 1", "counter claim 2"],
    "citations": [
        {
            "title": "counter source name",
            "snippet": "contradictory or limiting evidence excerpt",
            "url": "optional url",
            "reliability": 0.92
        }
    ],
    "flaws_identified": ["flaw in proposer reasoning 1", "unsupported assumption 2"],
    "persuasiveness_self_score": 0.88,
    "concessions_made": ["concession if any"]
}"""

    async def execute(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        """Execute opposer turn in a debate round."""
        topic: str = kwargs.get("topic", "")
        thesis: str = kwargs.get("thesis", "")
        counter_thesis: Optional[str] = kwargs.get("counter_thesis")
        round_number: int = kwargs.get("round_number", 1)
        proposer_argument: str = kwargs.get("proposer_argument", "")
        proposer_claims: List[str] = kwargs.get("proposer_claims", [])
        debate_history: List[Dict[str, Any]] = kwargs.get("debate_history", [])

        user_prompt = f"""Debate Topic: {topic}
Primary Thesis Being Challenged: {thesis}
Counter-Thesis: {counter_thesis or "Skeptical Antithesis"}
Current Round: {round_number}

Proposer's Argument in This Round:
{proposer_argument}

Proposer's Stated Key Claims:
{json.dumps(proposer_claims)}

"""
        if debate_history:
            user_prompt += f"Previous Rounds Summary: {json.dumps(debate_history[-2:])}\n\n"

        user_prompt += "Construct your adversarial counterargument and return valid JSON."

        llm_request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                LLMMessage(role="user", content=user_prompt),
            ],
            model_id=kwargs.get("model_id", "gemini-2.5-pro"),
            temperature=0.3,
        )

        try:
            if context.model_gateway:
                response = await context.model_gateway.complete(llm_request, user_context=context.to_dict())
                text = response.text.strip()
            else:
                text = json.dumps({
                    "argument_text": f"The proposition regarding {topic} oversimplifies critical edge cases and lacks universal generalizability.",
                    "counter_claims": [f"Conditions exist where the primary thesis on {topic} breaks down."],
                    "citations": [{"title": "Counter Experiment", "snippet": "Observed failure under stress testing", "reliability": 0.88}],
                    "flaws_identified": ["Omission of boundary constraints", "Extrapolation beyond test domain"],
                    "persuasiveness_self_score": 0.82,
                    "concessions_made": [],
                })

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
        except Exception as e:
            logger.warning("opposer_parse_failed", error=str(e))
            data = {
                "argument_text": f"Adversarial counter-position on {topic}: The proposition must be qualified with stricter operational constraints.",
                "counter_claims": [f"The thesis on {topic} is subject to significant boundary limitations."],
                "citations": [],
                "flaws_identified": ["Potential over-generalization"],
                "persuasiveness_self_score": 0.75,
                "concessions_made": [],
            }

        return AgentResult(
            task_id=f"debate-opposer-r{round_number}",
            agent_name=self.name,
            success=True,
            output=data,
        )

    async def run(self, task: Any, context: AgentContext) -> AgentResult:
        """Standard Agent interface execution."""
        task_dict = task.dict() if hasattr(task, "dict") else (task if isinstance(task, dict) else {})
        return await self.execute(context, **task_dict)
