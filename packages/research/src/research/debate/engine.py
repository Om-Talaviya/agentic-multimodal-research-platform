"""Adversarial Debate Execution Engine managing multi-round dialectics and Elo tracking."""

from typing import Any, Dict, List, Optional, Tuple
import uuid

from agents.base import AgentContext
from agents.debate.proposer_agent import ProposerAgent
from agents.debate.opposer_agent import OpposerAgent
from agents.debate.consensus_arbiter import ConsensusArbiter
from database.repositories.debate_repo import DebateRepository
from research.debate.models import (
    ArgumentTurn,
    DebateConfig,
    DebateConsensusPayload,
    RoundCritique,
)
from shared.logging import get_logger

logger = get_logger(__name__)


def compute_elo_shift(
    rating_a: float,
    rating_b: float,
    score_a: float,
    score_b: float,
    k_factor: float = 32.0,
) -> Tuple[float, float, float]:
    """Compute Elo rating update given ratings and round performance scores.

    Returns:
        Tuple of (delta_a, new_rating_a, new_rating_b)
    """
    expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    # Actual outcome S_A based on score differential
    if score_a > score_b:
        actual_a = 1.0
    elif score_a < score_b:
        actual_a = 0.0
    else:
        actual_a = 0.5

    delta_a = k_factor * (actual_a - expected_a)
    new_a = max(100.0, rating_a + delta_a)
    new_b = max(100.0, rating_b - delta_a)
    return round(delta_a, 2), round(new_a, 1), round(new_b, 1)


class DebateEngine:
    """Orchestrates adversarial multi-agent research debates and dialectical consensus synthesis."""

    def __init__(
        self,
        debate_repo: DebateRepository,
        proposer_agent: Optional[ProposerAgent] = None,
        opposer_agent: Optional[OpposerAgent] = None,
        arbiter_agent: Optional[ConsensusArbiter] = None,
    ):
        self.debate_repo = debate_repo
        self.proposer = proposer_agent or ProposerAgent()
        self.opposer = opposer_agent or OpposerAgent()
        self.arbiter = arbiter_agent or ConsensusArbiter()

    async def execute_round(
        self,
        debate_id: uuid.UUID,
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Execute the next chronological round in a debate session."""
        debate = await self.debate_repo.get_debate(debate_id, include_rounds=True)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found.")

        if debate.status != "active":
            raise ValueError(f"Debate {debate_id} is already {debate.status}.")

        next_round_number = debate.current_round + 1
        if next_round_number > debate.max_rounds:
            raise ValueError(f"Debate {debate_id} has already completed all {debate.max_rounds} rounds.")

        # Gather previous rounds context
        previous_rounds = [
            {
                "round_number": r.round_number,
                "proposer_argument": r.proposer_argument,
                "opposer_argument": r.opposer_argument,
                "round_winner": r.round_winner,
            }
            for r in (debate.rounds or [])
        ]
        last_opposer_arg = previous_rounds[-1]["opposer_argument"] if previous_rounds else None

        # 1. Proposer Turn
        proposer_res = await self.proposer.execute(
            context,
            topic=debate.topic,
            thesis=debate.initial_thesis,
            round_number=next_round_number,
            opposer_prior_argument=last_opposer_arg,
            debate_history=previous_rounds,
            model_id=debate.proposer_model,
        )
        proposer_out = proposer_res.output or {}
        proposer_text = proposer_out.get("argument_text", "")
        proposer_claims = proposer_out.get("key_claims", [])
        proposer_cites = proposer_out.get("citations", [])

        # 2. Opposer Turn
        opposer_res = await self.opposer.execute(
            context,
            topic=debate.topic,
            thesis=debate.initial_thesis,
            counter_thesis=debate.counter_thesis,
            round_number=next_round_number,
            proposer_argument=proposer_text,
            proposer_claims=proposer_claims,
            debate_history=previous_rounds,
            model_id=debate.opposer_model,
        )
        opposer_out = opposer_res.output or {}
        opposer_text = opposer_out.get("argument_text", "")
        opposer_cites = opposer_out.get("citations", [])

        # 3. Arbiter Round Evaluation
        round_eval = await self.arbiter.evaluate_round(
            context=context,
            topic=debate.topic,
            round_number=next_round_number,
            proposer_turn=proposer_out,
            opposer_turn=opposer_out,
            model_id=debate.arbiter_model,
        )

        p_score = float(round_eval.get("proposer_score", 0.8))
        o_score = float(round_eval.get("opposer_score", 0.8))
        round_winner = round_eval.get("round_winner", "draw")
        critique = round_eval.get("critique", "")

        # 4. Compute Elo Shift
        elo_delta, new_p_elo, new_o_elo = compute_elo_shift(
            rating_a=debate.proposer_elo,
            rating_b=debate.opposer_elo,
            score_a=p_score,
            score_b=o_score,
        )

        # 5. Persist Round
        saved_round = await self.debate_repo.add_debate_round(
            debate_id=debate_id,
            round_number=next_round_number,
            proposer_argument=proposer_text,
            opposer_argument=opposer_text,
            proposer_citations=proposer_cites,
            opposer_citations=opposer_cites,
            proposer_score=p_score,
            opposer_score=o_score,
            arbiter_critique=critique,
            round_winner=round_winner,
            elo_delta=elo_delta,
            round_telemetry={
                "proposer_claims": proposer_claims,
                "opposer_flaws": opposer_out.get("flaws_identified", []),
                "proposer_concessions": proposer_out.get("concessions_made", []),
                "opposer_concessions": opposer_out.get("concessions_made", []),
            },
        )

        # 6. Update Debate current round and Elo
        await self.debate_repo.update_debate_status(
            debate_id=debate_id,
            status="active" if next_round_number < debate.max_rounds else "concluded",
            current_round=next_round_number,
            proposer_elo=new_p_elo,
            opposer_elo=new_o_elo,
        )

        # 7. If max rounds reached, auto-synthesize consensus
        consensus_record = None
        if next_round_number >= debate.max_rounds:
            consensus_record = await self.synthesize_and_save_consensus(debate_id, context)

        return {
            "round_number": next_round_number,
            "round_id": str(saved_round.id),
            "round_winner": round_winner,
            "proposer_score": p_score,
            "opposer_score": o_score,
            "elo_delta": elo_delta,
            "proposer_elo_after": new_p_elo,
            "opposer_elo_after": new_o_elo,
            "is_concluded": next_round_number >= debate.max_rounds,
            "consensus": consensus_record,
        }

    async def synthesize_and_save_consensus(
        self,
        debate_id: uuid.UUID,
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Synthesize and persist dialectical consensus for a completed debate."""
        debate = await self.debate_repo.get_debate(debate_id, include_rounds=True)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found.")

        rounds_data = [
            {
                "round_number": r.round_number,
                "proposer_argument": r.proposer_argument,
                "opposer_argument": r.opposer_argument,
                "proposer_citations": r.proposer_citations,
                "opposer_citations": r.opposer_citations,
                "proposer_score": r.proposer_score,
                "opposer_score": r.opposer_score,
                "round_winner": r.round_winner,
                "arbiter_critique": r.arbiter_critique,
            }
            for r in (debate.rounds or [])
        ]

        consensus_data = await self.arbiter.synthesize_consensus(
            context=context,
            topic=debate.topic,
            initial_thesis=debate.initial_thesis,
            rounds_history=rounds_data,
            model_id=debate.arbiter_model,
        )

        consensus_stmt = consensus_data.get("consensus_statement", "")
        accepted = consensus_data.get("accepted_claims", [])
        refuted = consensus_data.get("refuted_claims", [])
        concessions = consensus_data.get("concessions", [])
        uncertainties = consensus_data.get("remaining_uncertainties", [])
        confidence = float(consensus_data.get("overall_confidence", 0.85))
        winner_overall = consensus_data.get("winner_overall", "balanced_consensus")

        consensus_obj = await self.debate_repo.record_consensus(
            debate_id=debate_id,
            consensus_statement=consensus_stmt,
            accepted_claims=accepted,
            refuted_claims=refuted,
            concessions=concessions,
            remaining_uncertainties=uncertainties,
            overall_confidence=confidence,
            winner_overall=winner_overall,
            final_proposer_elo=debate.proposer_elo,
            final_opposer_elo=debate.opposer_elo,
            synthesis_metadata={"total_rounds_analyzed": len(rounds_data)},
        )

        return {
            "consensus_id": str(consensus_obj.id),
            "consensus_statement": consensus_stmt,
            "accepted_claims": accepted,
            "refuted_claims": refuted,
            "concessions": concessions,
            "remaining_uncertainties": uncertainties,
            "overall_confidence": confidence,
            "winner_overall": winner_overall,
            "final_proposer_elo": debate.proposer_elo,
            "final_opposer_elo": debate.opposer_elo,
        }

    async def execute_full_debate(
        self,
        debate_id: uuid.UUID,
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Execute all remaining rounds in a debate to completion."""
        debate = await self.debate_repo.get_debate(debate_id)
        if not debate:
            raise ValueError(f"Debate {debate_id} not found.")

        rounds_completed = []
        while debate.current_round < debate.max_rounds and debate.status == "active":
            round_res = await self.execute_round(debate_id, context)
            rounds_completed.append(round_res)
            debate = await self.debate_repo.get_debate(debate_id)

        consensus = await self.debate_repo.get_consensus(debate_id)
        return {
            "debate_id": str(debate_id),
            "status": debate.status,
            "rounds_completed": rounds_completed,
            "consensus_id": str(consensus.id) if consensus else None,
        }
