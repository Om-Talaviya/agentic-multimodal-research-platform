"""Intelligent Model Ecosystem Optimizer.

Provides multi-parameter routing optimization, Pareto-frontier analysis,
and customizable profile-based model scoring across Quality, Speed, Cost, and Locality.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from ai.registry.model_registry import ModelDefinition
from ai.schemas import ModelCapability
from shared.logging import get_logger

logger = get_logger(__name__)


class ProfileType(str, Enum):
    """Preset optimization profiles for routing decisions."""
    BALANCED = "balanced"
    COST_MINIMIZED = "cost_minimized"
    SPEED_MAXIMIZED = "speed_maximized"
    QUALITY_MAXIMIZED = "quality_maximized"
    CUSTOM = "custom"


class OptimizationProfile(BaseModel):
    """Configuration weights and constraint thresholds for multi-parameter routing."""
    name: str = "Balanced"
    profile_type: ProfileType = ProfileType.BALANCED
    quality_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    speed_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    cost_weight: float = Field(default=0.30, ge=0.0, le=1.0)
    locality_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    max_latency_ms: Optional[int] = Field(default=None, description="Max acceptable latency SLA in ms")
    max_cost_per_1k: Optional[float] = Field(default=None, description="Max acceptable USD cost per 1k tokens")
    require_local: bool = Field(default=False, description="Strictly mandate local on-premise execution")
    prefer_local: bool = Field(default=True, description="Prefer local model if scores are comparable")
    description: Optional[str] = None

    def normalized_weights(self) -> Tuple[float, float, float, float]:
        """Return normalized weights summing to 1.0."""
        total = self.quality_weight + self.speed_weight + self.cost_weight + self.locality_weight
        if total <= 0:
            return 0.35, 0.25, 0.30, 0.10
        return (
            self.quality_weight / total,
            self.speed_weight / total,
            self.cost_weight / total,
            self.locality_weight / total,
        )


PRESET_PROFILES: Dict[ProfileType, OptimizationProfile] = {
    ProfileType.BALANCED: OptimizationProfile(
        name="Balanced Ecosystem",
        profile_type=ProfileType.BALANCED,
        quality_weight=0.35,
        speed_weight=0.25,
        cost_weight=0.30,
        locality_weight=0.10,
        description="Even trade-off between reasoning quality, execution speed, and token cost.",
    ),
    ProfileType.COST_MINIMIZED: OptimizationProfile(
        name="Cost Minimized",
        profile_type=ProfileType.COST_MINIMIZED,
        quality_weight=0.20,
        speed_weight=0.15,
        cost_weight=0.55,
        locality_weight=0.10,
        description="Prioritizes free tiers and low-cost models to maximize budget efficiency.",
    ),
    ProfileType.SPEED_MAXIMIZED: OptimizationProfile(
        name="Speed Maximized",
        profile_type=ProfileType.SPEED_MAXIMIZED,
        quality_weight=0.20,
        speed_weight=0.55,
        cost_weight=0.10,
        locality_weight=0.15,
        description="Prioritizes fast inference, lightweight models, and local low-latency engines.",
    ),
    ProfileType.QUALITY_MAXIMIZED: OptimizationProfile(
        name="Quality & Reasoning Maximized",
        profile_type=ProfileType.QUALITY_MAXIMIZED,
        quality_weight=0.75,
        speed_weight=0.10,
        cost_weight=0.10,
        locality_weight=0.05,
        prefer_local=False,
        description="Selects the highest capability frontier models for deep reasoning and synthesis.",
    ),
}


class ModelScore(BaseModel):
    """Detailed multi-parameter evaluation score for a candidate model."""
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    provider_name: str
    total_score: float
    quality_score: float
    speed_score: float
    cost_score: float
    locality_score: float
    is_pareto_optimal: bool = False
    rank: int = 1
    tier: str = "paid"
    is_local: bool = False
    estimated_cost_per_1k: float = 0.0
    rationale: str = ""


class OptimizationResult(BaseModel):
    """Full ranking and trade-off analysis from multi-parameter optimization."""
    selected_model_id: str
    selected_provider: str
    profile_used: OptimizationProfile
    ranked_candidates: List[ModelScore]
    pareto_frontier: List[str]
    tradeoff_analysis: str


class ModelEcosystemOptimizer:
    """Multi-parameter model optimization engine with Pareto-frontier sorting."""

    @staticmethod
    def compute_quality_score(model: ModelDefinition, task: Optional[str] = None) -> float:
        """Compute normalized quality score in [0.0, 1.0]."""
        # Base priority contribution (0 to 10 -> 0.0 to 0.5)
        base = min(max(model.priority / 20.0, 0.05), 0.5)

        # Task suitability bonus (+0.25)
        task_bonus = 0.0
        if task and task in model.task_suitability:
            task_bonus = 0.25
        elif not task and model.task_suitability:
            task_bonus = 0.15

        # Capability breadth bonus (+0.15)
        cap_bonus = min(len(model.capabilities) * 0.04, 0.15)

        # Context window bonus (+0.10)
        context_bonus = 0.0
        if model.context_window:
            if model.context_window >= 128000:
                context_bonus = 0.10
            elif model.context_window >= 32000:
                context_bonus = 0.06
            elif model.context_window >= 8000:
                context_bonus = 0.03

        return min(round(base + task_bonus + cap_bonus + context_bonus, 4), 1.0)

    @staticmethod
    def compute_speed_score(model: ModelDefinition) -> float:
        """Compute normalized speed score in [0.0, 1.0]."""
        score = 0.5
        if model.is_local:
            score += 0.3  # Local engines have near-zero network latency
        else:
            score += 0.1

        if model.supports_streaming:
            score += 0.1

        # Smaller models generally yield higher tokens/sec
        if model.priority <= 5:
            score += 0.1
        elif model.priority >= 9:
            score -= 0.05

        return min(max(round(score, 4), 0.05), 1.0)

    @staticmethod
    def compute_cost_score(model: ModelDefinition) -> float:
        """Compute normalized cost efficiency score in [0.0, 1.0] (1.0 = Free/cheapest)."""
        if model.is_free() or (model.input_cost == 0.0 and model.output_cost == 0.0):
            return 1.0

        avg_cost_per_1k = (model.input_cost + model.output_cost) / 2.0
        # Cost decay function: 1.0 / (1.0 + cost * 200)
        score = 1.0 / (1.0 + (avg_cost_per_1k * 200.0))
        return min(max(round(score, 4), 0.01), 0.95)

    @staticmethod
    def compute_locality_score(model: ModelDefinition, prefer_local: bool = True) -> float:
        """Compute locality score in [0.0, 1.0]."""
        if model.is_local:
            return 1.0
        return 0.3 if prefer_local else 0.8

    @classmethod
    def find_pareto_frontier(cls, candidates: List[ModelDefinition], task: Optional[str] = None) -> Set[str]:
        """Compute non-dominated Pareto frontier across (Quality, Speed, Cost Efficiency)."""
        if not candidates:
            return set()

        metrics = {}
        for m in candidates:
            q = cls.compute_quality_score(m, task)
            s = cls.compute_speed_score(m)
            c = cls.compute_cost_score(m)
            metrics[m.model_id] = (q, s, c)

        frontier = set()
        model_ids = list(metrics.keys())

        for m_id in model_ids:
            q_a, s_a, c_a = metrics[m_id]
            dominated = False
            for other_id in model_ids:
                if m_id == other_id:
                    continue
                q_b, s_b, c_b = metrics[other_id]
                # other dominates m if other >= m in all and other > m in at least one
                if (q_b >= q_a and s_b >= s_a and c_b >= c_a) and (q_b > q_a or s_b > s_a or c_b > c_a):
                    dominated = True
                    break
            if not dominated:
                frontier.add(m_id)

        return frontier

    @classmethod
    def optimize(
        cls,
        candidates: List[ModelDefinition],
        profile: Optional[OptimizationProfile] = None,
        task: Optional[str] = None,
        required_capabilities: Optional[Set[ModelCapability]] = None,
    ) -> OptimizationResult:
        """Score, filter, and rank candidate models using multi-parameter utility optimization."""
        if not candidates:
            raise ValueError("No candidate models provided for optimization")

        opt_profile = profile or PRESET_PROFILES[ProfileType.BALANCED]
        w_q, w_s, w_c, w_l = opt_profile.normalized_weights()

        # 1. Hard SLA & constraint filtering
        filtered: List[ModelDefinition] = []
        for m in candidates:
            if opt_profile.require_local and not m.is_local:
                continue
            if opt_profile.max_cost_per_1k is not None:
                avg_cost = (m.input_cost + m.output_cost) / 2.0
                if avg_cost > opt_profile.max_cost_per_1k:
                    continue
            if required_capabilities and not required_capabilities.issubset(m.capabilities):
                continue
            filtered.append(m)

        if not filtered:
            # Fallback to original candidates if constraints over-filtered
            filtered = candidates

        # 2. Pareto Frontier
        pareto_ids = cls.find_pareto_frontier(filtered, task)

        # 3. Multi-parameter scoring
        scores: List[ModelScore] = []
        for m in filtered:
            q = cls.compute_quality_score(m, task)
            s = cls.compute_speed_score(m)
            c = cls.compute_cost_score(m)
            l = cls.compute_locality_score(m, opt_profile.prefer_local)

            total = round((w_q * q) + (w_s * s) + (w_c * c) + (w_l * l), 4)
            avg_cost = (m.input_cost + m.output_cost) / 2.0

            # Generate itemized rationale
            is_pareto = m.model_id in pareto_ids
            reasons = []
            if is_pareto:
                reasons.append("Pareto-optimal trade-off")
            if m.is_free():
                reasons.append("Zero token cost")
            if m.is_local:
                reasons.append("On-premise zero latency")
            if task and task in m.task_suitability:
                reasons.append(f"Specialized for '{task}'")
            if q >= 0.7:
                reasons.append("High reasoning score")

            rationale = ", ".join(reasons) if reasons else "Standard capability match"

            scores.append(
                ModelScore(
                    model_id=m.model_id,
                    provider_name=m.provider_name,
                    total_score=total,
                    quality_score=q,
                    speed_score=s,
                    cost_score=c,
                    locality_score=l,
                    is_pareto_optimal=is_pareto,
                    tier=m.tier,
                    is_local=m.is_local,
                    estimated_cost_per_1k=avg_cost,
                    rationale=rationale,
                )
            )

        # 4. Sort descending by total score, then pareto optimality, then quality
        scores.sort(key=lambda s: (-s.total_score, -int(s.is_pareto_optimal), -s.quality_score))

        for idx, item in enumerate(scores):
            item.rank = idx + 1

        selected = scores[0]

        # 5. Build trade-off analysis explanation
        analysis = (
            f"Selected '{selected.model_id}' via {opt_profile.name} (Score: {selected.total_score:.3f}). "
            f"Quality: {selected.quality_score:.2f}, Speed: {selected.speed_score:.2f}, "
            f"Cost Efficiency: {selected.cost_score:.2f}, Locality: {selected.locality_score:.2f}. "
            f"{'Model is on the non-dominated Pareto frontier.' if selected.is_pareto_optimal else ''}"
        )

        return OptimizationResult(
            selected_model_id=selected.model_id,
            selected_provider=selected.provider_name,
            profile_used=opt_profile,
            ranked_candidates=scores,
            pareto_frontier=list(pareto_ids),
            tradeoff_analysis=analysis,
        )
