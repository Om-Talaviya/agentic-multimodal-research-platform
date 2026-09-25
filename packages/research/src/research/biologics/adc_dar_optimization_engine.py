"""Autonomous ADC DAR Optimization & Aggregation Predictor Engine (Phase 178)."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import math


@dataclass
class DARSpeciesDistributionResult:
    dar_species: int
    molar_fraction: float
    retention_time_min: float
    mass_shift_da: float
    relative_clearance_rate: float


@dataclass
class AggregationKineticsPoint:
    incubation_hours: float
    monomer_percentage: float
    high_molecular_weight_pct: float
    low_molecular_weight_pct: float
    turbidity_od350: float


@dataclass
class ADCDAROptimizationResult:
    antibody_name: str
    payload_name: str
    linker_type: str
    conjugation_chemistry: str
    target_dar: float
    calculated_mean_dar: float
    aggregation_propensity_score: float
    hydrophobicity_index: float
    unconjugated_antibody_pct: float
    high_dar_overload_pct: float
    species_distribution: List[DARSpeciesDistributionResult]
    aggregation_kinetics: List[AggregationKineticsPoint]
    optimization_recommendation: str
    therapeutic_index_multiplier: float


class ADCDAROptimizationEngine:
    """Engine for in-silico ADC DAR optimization, Poisson/Binomial distribution modeling, and aggregation prediction."""

    def __init__(self, default_payload_mw: float = 718.0) -> None:
        self.default_payload_mw = default_payload_mw

    def calculate_binomial_dar_distribution(self, n_sites: int, p_conjugation: float) -> Dict[int, float]:
        """Compute DAR species probabilities using binomial distribution."""
        dist = {}
        for k in range(0, n_sites + 1):
            comb = math.comb(n_sites, k)
            prob = comb * (p_conjugation ** k) * ((1.0 - p_conjugation) ** (n_sites - k))
            dist[k] = prob
        return dist

    def simulate_dar_optimization(
        self,
        antibody_name: str,
        payload_name: str,
        target_dar: float = 4.0,
        linker_type: str = "cleavable_val_cit",
        conjugation_chemistry: str = "cysteine_maleimide",
        payload_logp: float = 2.8,
        reaction_stoichiometry: float = 4.5,
    ) -> ADCDAROptimizationResult:
        """Run full ADC DAR optimization simulation."""
        n_sites = 8 if "cysteine" in conjugation_chemistry.lower() else 12
        p_conj = min(0.95, max(0.05, (target_dar / n_sites) * (reaction_stoichiometry / 4.0)))

        binom_dist = self.calculate_binomial_dar_distribution(n_sites, p_conj)

        species_results = []
        weighted_dar_sum = 0.0

        for dar, fraction in binom_dist.items():
            if fraction < 0.001:
                continue
            weighted_dar_sum += dar * fraction
            retention_time = 12.0 + (dar * 1.85) * (1.0 + (payload_logp * 0.1))
            mass_shift = dar * self.default_payload_mw
            clearance_rate = 1.0 + (dar * 0.22) + (0.05 * (dar ** 1.5))
            species_results.append(
                DARSpeciesDistributionResult(
                    dar_species=dar,
                    molar_fraction=round(fraction * 100.0, 2),
                    retention_time_min=round(retention_time, 2),
                    mass_shift_da=round(mass_shift, 2),
                    relative_clearance_rate=round(clearance_rate, 3),
                )
            )

        mean_dar = round(weighted_dar_sum, 2)
        unconjugated_pct = round(binom_dist.get(0, 0.0) * 100.0, 2)
        high_dar_overload = round(sum(frac for dar, frac in binom_dist.items() if dar >= 6) * 100.0, 2)

        # Hydrophobicity index & aggregation propensity
        hydrophobicity_index = round(1.2 + (mean_dar * 0.38) + (payload_logp * 0.45), 2)
        aggregation_propensity = round(min(1.0, 0.04 + (mean_dar * 0.025) + (high_dar_overload * 0.008)), 3)

        # Aggregation kinetics over 72 hours
        kinetics = []
        for hour in [0.0, 12.0, 24.0, 48.0, 72.0]:
            decay = math.exp(-0.003 * hour * (hydrophobicity_index / 2.0))
            monomer = round(98.5 * decay, 2)
            hmw = round((100.0 - monomer) * 0.85, 2)
            lmw = round((100.0 - monomer) * 0.15, 2)
            turbidity = round(0.015 + (100.0 - monomer) * 0.012, 4)
            kinetics.append(
                AggregationKineticsPoint(
                    incubation_hours=hour,
                    monomer_percentage=monomer,
                    high_molecular_weight_pct=hmw,
                    low_molecular_weight_pct=lmw,
                    turbidity_od350=turbidity,
                )
            )

        rec = f"Optimal stoichiometry {round(reaction_stoichiometry, 1)}x achieved DAR {mean_dar} (Target: {target_dar}). High DAR species constrained to {high_dar_overload}%."
        ti_multiplier = round(max(1.1, 3.2 - (aggregation_propensity * 2.0) - (high_dar_overload * 0.05)), 2)

        return ADCDAROptimizationResult(
            antibody_name=antibody_name,
            payload_name=payload_name,
            linker_type=linker_type,
            conjugation_chemistry=conjugation_chemistry,
            target_dar=target_dar,
            calculated_mean_dar=mean_dar,
            aggregation_propensity_score=aggregation_propensity,
            hydrophobicity_index=hydrophobicity_index,
            unconjugated_antibody_pct=unconjugated_pct,
            high_dar_overload_pct=high_dar_overload,
            species_distribution=species_results,
            aggregation_kinetics=kinetics,
            optimization_recommendation=rec,
            therapeutic_index_multiplier=ti_multiplier,
        )
