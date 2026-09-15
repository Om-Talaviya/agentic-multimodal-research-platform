"""Research debate package."""

from research.debate.models import (
    DebateConfig,
    ArgumentTurn,
    ArgumentCitation,
    RoundCritique,
    ClaimEloDelta,
    DebateConsensusPayload,
)
from research.debate.engine import DebateEngine, compute_elo_shift

__all__ = [
    "DebateConfig",
    "ArgumentTurn",
    "ArgumentCitation",
    "RoundCritique",
    "ClaimEloDelta",
    "DebateConsensusPayload",
    "DebateEngine",
    "compute_elo_shift",
]
