"""Autonomous CAR-T Cell Exhaustion Epigenetic State Transition & Persistence Simulator (Phase 183)."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import math


@dataclass
class DifferentiationStateResult:
    state_name: str
    population_percentage: float
    tcf7_expression_level: float
    proliferative_capacity_score: float
    cytolytic_granzyme_b_score: float


@dataclass
class CheckpointMarkerResult:
    marker_symbol: str
    surface_density_molecules: float
    epigenetic_chromatin_accessibility_score: float
    reversibility_potential_pct: float


@dataclass
class CARTExhaustionResult:
    car_construct_name: str
    costimulatory_domain: str
    antigen_density_per_tumor_cell: float
    tonic_signaling_level: str
    t_stem_cell_memory_pct: float
    tox_nr4a_epigenetic_exhaustion_score: float
    predicted_persistence_half_life_days: float
    in_vivo_antitumor_efficacy_score: float
    differentiation_states: List[DifferentiationStateResult]
    checkpoint_markers: List[CheckpointMarkerResult]
    therapeutic_recommendation: str
    memory_fitness_index: float


class CARTExhaustionKineticsEngine:
    """Engine for modeling CAR-T cell continuous phenotypic differentiation, TOX/NR4A exhaustion, and in-vivo persistence."""

    def __init__(self) -> None:
        pass

    def simulate_exhaustion_kinetics(
        self,
        car_construct_name: str = "anti-CD19-41BBz",
        costimulatory_domain: str = "4-1BB",
        antigen_density: float = 15000.0,
        tonic_signaling_level: str = "low",
        il2_il15_priming_ratio: float = 2.5,
    ) -> CARTExhaustionResult:
        """Simulate T-cell epigenetic transitions, TOX exhaustion, and clinical persistence."""
        # 4-1BB enhances mitochondrial biogenesis and Tscm fraction vs CD28
        is_41bb = "4-1bb" in costimulatory_domain.lower()
        tonic_factor = 1.6 if "high" in tonic_signaling_level.lower() else (1.2 if "med" in tonic_signaling_level.lower() else 0.9)

        base_tscm = 42.0 if is_41bb else 22.0
        tscm_pct = round(max(10.0, min(65.0, base_tscm * (il2_il15_priming_ratio / 2.0) / tonic_factor)), 1)
        tcm_pct = round(max(15.0, 32.0 / tonic_factor), 1)
        tem_pct = round(max(15.0, 24.0 * tonic_factor), 1)
        tex_pct = round(max(5.0, min(40.0, (100.0 - (tscm_pct + tcm_pct + tem_pct)))), 1)

        # TOX / NR4A epigenetic exhaustion score
        tox_score = round(min(0.95, max(0.08, (tex_pct * 0.02) * tonic_factor)), 3)

        # Persistence half-life in days (Tscm + 4-1BB drives longevity)
        half_life_days = round(max(30.0, min(365.0, (tscm_pct * 4.2) + (50.0 if is_41bb else 15.0) - (tox_score * 80.0))), 1)
        efficacy_score = round(min(0.98, max(0.40, 0.72 + (tscm_pct * 0.005) - (tox_score * 0.25))), 2)

        states = [
            DifferentiationStateResult(
                state_name="Tscm (Stem Memory)",
                population_percentage=tscm_pct,
                tcf7_expression_level=0.94,
                proliferative_capacity_score=0.96,
                cytolytic_granzyme_b_score=0.35,
            ),
            DifferentiationStateResult(
                state_name="Tcm (Central Memory)",
                population_percentage=tcm_pct,
                tcf7_expression_level=0.78,
                proliferative_capacity_score=0.82,
                cytolytic_granzyme_b_score=0.55,
            ),
            DifferentiationStateResult(
                state_name="Tem (Effector Memory)",
                population_percentage=tem_pct,
                tcf7_expression_level=0.45,
                proliferative_capacity_score=0.52,
                cytolytic_granzyme_b_score=0.88,
            ),
            DifferentiationStateResult(
                state_name="Tex (Exhausted State)",
                population_percentage=tex_pct,
                tcf7_expression_level=0.15,
                proliferative_capacity_score=0.18,
                cytolytic_granzyme_b_score=0.32,
            ),
        ]

        markers = [
            CheckpointMarkerResult(
                marker_symbol="PD-1",
                surface_density_molecules=round(1200.0 + (tox_score * 4500.0), 1),
                epigenetic_chromatin_accessibility_score=round(0.35 + (tox_score * 0.55), 2),
                reversibility_potential_pct=round(max(20.0, 85.0 - (tox_score * 60.0)), 1),
            ),
            CheckpointMarkerResult(
                marker_symbol="TOX",
                surface_density_molecules=round(800.0 + (tox_score * 3200.0), 1),
                epigenetic_chromatin_accessibility_score=round(tox_score, 2),
                reversibility_potential_pct=round(max(15.0, 70.0 - (tox_score * 50.0)), 1),
            ),
            CheckpointMarkerResult(
                marker_symbol="LAG-3",
                surface_density_molecules=round(950.0 + (tox_score * 2800.0), 1),
                epigenetic_chromatin_accessibility_score=round(0.28 + (tox_score * 0.48), 2),
                reversibility_potential_pct=round(max(30.0, 80.0 - (tox_score * 45.0)), 1),
            ),
        ]

        fitness_idx = round((tscm_pct / 50.0 * 0.4) + ((1.0 - tox_score) * 0.4) + (half_life_days / 250.0 * 0.2), 3)
        rec = f"Construct {car_construct_name} ({costimulatory_domain}) sustains high Tscm pool ({tscm_pct}%) with low TOX epigenetic exhaustion ({tox_score}). In-vivo persistence forecast: {half_life_days} days."

        return CARTExhaustionResult(
            car_construct_name=car_construct_name,
            costimulatory_domain=costimulatory_domain,
            antigen_density_per_tumor_cell=antigen_density,
            tonic_signaling_level=tonic_signaling_level,
            t_stem_cell_memory_pct=tscm_pct,
            tox_nr4a_epigenetic_exhaustion_score=tox_score,
            predicted_persistence_half_life_days=half_life_days,
            in_vivo_antitumor_efficacy_score=efficacy_score,
            differentiation_states=states,
            checkpoint_markers=markers,
            therapeutic_recommendation=rec,
            memory_fitness_index=fitness_idx,
        )