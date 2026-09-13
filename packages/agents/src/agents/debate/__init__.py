"""Debate agents package."""

from agents.debate.proposer_agent import ProposerAgent
from agents.debate.opposer_agent import OpposerAgent
from agents.debate.consensus_arbiter import ConsensusArbiter

__all__ = [
    "ProposerAgent",
    "OpposerAgent",
    "ConsensusArbiter",
]
