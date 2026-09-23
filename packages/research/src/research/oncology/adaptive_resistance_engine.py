"""Adaptive Resistance & Clonal Fitness Dynamics Simulation Engine for Precision Oncology."""

import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClonalSpecification(BaseModel):
    """Specification of an initial tumor subclone."""
    clone_name: str
    driver_mutations: List[str] = Field(default_factory=list)
    initial_frequency: float = 0.1
    intrinsic_growth_rate: float = 0.05  # daily division rate
    ic50: float = 10.0  # uM or relative dose
    hill_coefficient: float = 1.5
    phenotype: str = "SENSITIVE"  # SENSITIVE, TOLERANT, MULTI_DRUG_RESISTANT


class DosingRegimenStep(BaseModel):
    """Chemotherapy dosing interval config."""
    drug_name: str = "Cisplatin"
    dosage: float = 50.0  # mg/m2 or concentration
    duration_days: int = 7
    holiday_days: int = 14


class SimulationResult(BaseModel):
    """Result of adaptive chemotherapy clonal dynamics simulation."""
    study_name: str
    cancer_type: str
    total_days: int
    trajectories: List[Dict[str, Any]]
    final_clones: List[Dict[str, Any]]
    summary_metrics: Dict[str, Any]
    recommendations: List[str]


class AdaptiveResistanceEngine:
    """Simulates evolutionary clonal dynamics under continuous vs adaptive chemotherapy dosing."""

    def __init__(self, carrying_capacity: float = 1e9):
        self.carrying_capacity = carrying_capacity

    def simulate_treatment_course(
        self,
        study_name: str,
        cancer_type: str,
        clones: List[ClonalSpecification],
        regimen: List[DosingRegimenStep],
        cycles: int = 6,
        adaptive_threshold: float = 0.5,  # tumor shrinkage ratio triggering dose modulation
    ) -> SimulationResult:
        """Run full forward longitudinal numerical simulation with competitive Lotka-Volterra + Hill killing."""
        # Normalize initial frequencies
        total_freq = sum(c.initial_frequency for c in clones) or 1.0
        active_clones = {
            c.clone_name: {
                "spec": c,
                "cells": max(100.0, (c.initial_frequency / total_freq) * 1e8),
            }
            for c in clones
        }

        trajectories: List[Dict[str, Any]] = []
        recommendations: List[str] = []
        day_counter = 0
        initial_tumor_burden = sum(v["cells"] for v in active_clones.values())

        for cycle_idx in range(cycles):
            for step in regimen:
                current_burden = sum(v["cells"] for v in active_clones.values())
                burden_ratio = current_burden / initial_tumor_burden if initial_tumor_burden > 0 else 1.0

                # Adaptive dosing decision rule
                applied_dose = step.dosage
                recommendation_action = "CONTINUE"
                if burden_ratio < adaptive_threshold:
                    applied_dose = step.dosage * 0.5
                    recommendation_action = "DOSE_MODULATE"
                    recommendations.append(f"Cycle {cycle_idx + 1}: Tumor burden reduced to {burden_ratio:.1%}, reduced dose to {applied_dose:.1f}")
                elif burden_ratio > 1.2:
                    applied_dose = step.dosage * 1.25
                    recommendation_action = "ESCALATE_OR_SWITCH"

                # On-drug phase
                for _ in range(step.duration_days):
                    day_counter += 1
                    tot_cells = sum(v["cells"] for v in active_clones.values())
                    for c_name, c_data in active_clones.items():
                        spec = c_data["spec"]
                        # Hill killing rate
                        kill_rate = (applied_dose ** spec.hill_coefficient) / (
                            (spec.ic50 ** spec.hill_coefficient) + (applied_dose ** spec.hill_coefficient) + 1e-9
                        )
                        # Net growth rate under carrying capacity
                        net_rate = spec.intrinsic_growth_rate * (1.0 - (tot_cells / self.carrying_capacity)) - kill_rate * 0.1
                        c_data["cells"] = max(1.0, c_data["cells"] * (1.0 + net_rate))

                # Drug Holiday Phase
                for _ in range(step.holiday_days):
                    day_counter += 1
                    tot_cells = sum(v["cells"] for v in active_clones.values())
                    for c_name, c_data in active_clones.items():
                        spec = c_data["spec"]
                        net_rate = spec.intrinsic_growth_rate * (1.0 - (tot_cells / self.carrying_capacity))
                        c_data["cells"] = max(1.0, c_data["cells"] * (1.0 + net_rate))

                # Record trajectory point at end of cycle segment
                cycle_burden = sum(v["cells"] for v in active_clones.values())
                clone_abundances = {
                    c_name: round(v["cells"] / cycle_burden, 4) if cycle_burden > 0 else 0.0
                    for c_name, v in active_clones.items()
                }

                # Compute resistance index: weighted fraction of non-sensitive cells
                res_idx = sum(
                    ab for c_name, ab in clone_abundances.items()
                    if active_clones[c_name]["spec"].phenotype != "SENSITIVE"
                )

                trajectories.append({
                    "time_step": cycle_idx * len(regimen) + len(trajectories),
                    "day": day_counter,
                    "cycle": cycle_idx + 1,
                    "drug_concentration": applied_dose,
                    "tumor_burden": round(cycle_burden / initial_tumor_burden, 4),
                    "clone_abundances": clone_abundances,
                    "resistance_index": round(res_idx, 4),
                    "adaptive_recommendation": recommendation_action,
                })

        # Calculate final state metrics
        final_clones_summary = []
        final_total_cells = sum(v["cells"] for v in active_clones.values())
        for c_name, v in active_clones.items():
            final_clones_summary.append({
                "clone_name": c_name,
                "driver_mutations": v["spec"].driver_mutations,
                "initial_frequency": v["spec"].initial_frequency,
                "final_frequency": round(v["cells"] / final_total_cells, 4) if final_total_cells > 0 else 0.0,
                "intrinsic_fitness": v["spec"].intrinsic_growth_rate,
                "phenotype": v["spec"].phenotype,
            })

        max_res_idx = max(t["resistance_index"] for t in trajectories) if trajectories else 0.0
        final_burden = trajectories[-1]["tumor_burden"] if trajectories else 1.0

        return SimulationResult(
            study_name=study_name,
            cancer_type=cancer_type,
            total_days=day_counter,
            trajectories=trajectories,
            final_clones=final_clones_summary,
            summary_metrics={
                "initial_burden": 1.0,
                "final_burden": final_burden,
                "max_resistance_index": max_res_idx,
                "total_cycles_simulated": cycles,
                "total_days_simulated": day_counter,
                "tumor_controlled": final_burden < 1.0,
            },
            recommendations=recommendations or ["Maintain standard monitoring protocol."],
        )
