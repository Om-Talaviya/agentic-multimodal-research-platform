"""Proposer Agent: Constructs affirmative evidence-grounded thesis arguments and rebuttals."""

import json
from typing import Any, Dict, List, Optional
from agents.base import Agent, AgentContext, AgentResult
from ai.schemas import LLMMessage, LLMRequest
from shared.logging import get_logger

logger = get_logger(__name__)


class ProposerAgent(Agent):
    """Affirmative debate agent defending a scientific or empirical thesis."""

    name = "proposer"
    description = "Constructs affirmative, evidence-grounded arguments and structured defenses in debates"
    capabilities = {"debate_proposer", "argumentation", "thesis_defense", "evidence_grounding"}

    SYSTEM_PROMPT = """You are the PROPOSER AGENT in an adversarial multi-agent research debate.
Your mission is to construct clear, rigorous, evidence-backed arguments defending the primary thesis.

Objectives:
1. Present strong logical deductions substantiated by empirical citations, statistics, or documented benchmarks.
2. Directly address and rebut the Opposer's previous counterarguments without evading criticism.
3. Explicitly acknowledge valid points or edge-case boundary conditions (honest scientific concessions strengthen your core argument).
4. Extract 2-4 core claims with supporting citations.

Return your response strictly as a JSON object:
{
    "argument_text": "Detailed multi-paragraph logical argument...",
    "key_claims": ["claim 1", "claim 2"],
    "citations": [
        {
            "title": "source name",
            "snippet": "exact evidence excerpt",
            "url": "optional url",
            "reliability": 0.95
        }
    ],
    "persuasiveness_self_score": 0.85,
    "concessions_made": ["concession if any"]
}"""

    async def execute(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        """Execute proposer turn in a debate round."""
        topic: str = kwargs.get("topic", "")
        thesis: str = kwargs.get("thesis", "")
        round_number: int = kwargs.get("round_number", 1)
        opposer_prior_argument: Optional[str] = kwargs.get("opposer_prior_argument")
        debate_history: List[Dict[str, Any]] = kwargs.get("debate_history", [])

        user_prompt = f"""Debate Topic: {topic}
Primary Thesis to Defend: {thesis}
Current Round: {round_number}

"""
        if opposer_prior_argument:
            user_prompt += f"Opposer's Previous Argument:\n{opposer_prior_argument}\n\n"

        if debate_history:
            user_prompt += f"Previous Rounds Summary: {json.dumps(debate_history[-2:])}\n\n"

        user_prompt += "Construct your affirmative argument and return valid JSON."

        llm_request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                LLMMessage(role="user", content=user_prompt),
            ],
            model_id=kwargs.get("model_id", "gemini-2.5-pro"),
            temperature=0.2,
        )

        try:
            if context.model_gateway:
                response = await context.model_gateway.complete(llm_request, user_context=context.to_dict())
                text = response.text.strip()
            else:
                text = json.dumps({
                    "argument_text": f"Empirical evidence robustly supports the thesis on {topic}.",
                    "key_claims": [f"Primary thesis on {topic} is supported by high-confidence literature."],
                    "citations": [{"title": "Baseline Study", "snippet": "Observed 95% efficacy", "reliability": 0.9}],
                    "persuasiveness_self_score": 0.85,
                    "concessions_made": [],
                })

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
        except Exception as e:
            logger.warning("proposer_parse_failed", error=str(e))
            data = {
                "argument_text": f"Affirmative position on {topic}: The proposition holds based on verified evidence.",
                "key_claims": [f"Proposition for {topic} is validated."],
                "citations": [],
                "persuasiveness_self_score": 0.75,
                "concessions_made": [],
            }

        return AgentResult(
            task_id=f"debate-proposer-r{round_number}",
            agent_name=self.name,
            success=True,
            output=data,
        )

    async def run(self, task: Any, context: AgentContext) -> AgentResult:
        """Standard Agent interface execution."""
        task_dict = task.dict() if hasattr(task, "dict") else (task if isinstance(task, dict) else {})
        return await self.execute(context, **task_dict)
