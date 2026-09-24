"""Phase 157: Autonomous Cell-Free Protein Synthesis (CFPS) TX-TL Kinetics Engine."""

import math
from typing import List, Optional
from pydantic import BaseModel, Field


class YieldTrajectoryPointDto(BaseModel):
    time_elapsed_hours: float
    mrna_concentration_uM: float
    protein_concentration_mg_ml: float
    ribosome_active_fraction: float


class SubstrateKineticsDto(BaseModel):
    substrate_name: str
    initial_concentration_mM: float
    final_concentration_mM: float
    consumption_rate_mM_h: float


class CFPSTXTLRequest(BaseModel):
    target_protein_name: str = "De-Novo Designed Neutralizing Nanobody"
    extract_system_type: str = "E. coli BL21 Star (DE3) Lysate"
    reaction_mode: str = "Continuous Exchange Cell-Free (CECF)"
    dna_template_concentration_nM: float = 10.0
    reaction_temperature_celsius: float = 30.0


class CFPSTXTLResult(BaseModel):
    target_protein_name: str
    extract_system_type: str
    reaction_mode: str
    reaction_time_hours: float
    final_protein_yield_mg_ml: float
    transcription_rate_nt_s: float
    translation_rate_aa_s: float
    energy_regeneration_efficiency: float
    yield_trajectories: List[YieldTrajectoryPointDto]
    substrate_depletions: List[SubstrateKineticsDto]


class CFPSTXTLEngine:
    def simulate_tx_tl(self, req: CFPSTXTLRequest) -> CFPSTXTLResult:
        tx_rate = 42.5  # T7 RNAP nt/sec
        tl_rate = 1.8   # Ribosome aa/sec

        time_points = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
        trajectories: List[YieldTrajectoryPointDto] = []

        for t in time_points:
            mrna = round(15.0 * (1.0 - math.exp(-t / 2.0)), 2)
            yield_val = round(2.8 * (1.0 / (1.0 + math.exp(-(t - 4.5) / 1.5))), 2)
            ribosome_act = round(max(0.2, 0.98 * math.exp(-t / 14.0)), 3)
            trajectories.append(
                YieldTrajectoryPointDto(
                    time_elapsed_hours=t,
                    mrna_concentration_uM=mrna,
                    protein_concentration_mg_ml=yield_val,
                    ribosome_active_fraction=ribosome_act,
                )
            )

        substrates = [
            SubstrateKineticsDto(substrate_name="ATP / GTP Energy Pool", initial_concentration_mM=4.0, final_concentration_mM=1.2, consumption_rate_mM_h=0.23),
            SubstrateKineticsDto(substrate_name="20 Standard Amino Acids", initial_concentration_mM=1.5, final_concentration_mM=0.35, consumption_rate_mM_h=0.095),
            SubstrateKineticsDto(substrate_name="PEP (Phosphoenolpyruvate)", initial_concentration_mM=30.0, final_concentration_mM=4.5, consumption_rate_mM_h=2.12),
        ]

        final_yield = trajectories[-1].protein_concentration_mg_ml

        return CFPSTXTLResult(
            target_protein_name=req.target_protein_name,
            extract_system_type=req.extract_system_type,
            reaction_mode=req.reaction_mode,
            reaction_time_hours=12.0,
            final_protein_yield_mg_ml=final_yield,
            transcription_rate_nt_s=tx_rate,
            translation_rate_aa_s=tl_rate,
            energy_regeneration_efficiency=0.91,
            yield_trajectories=trajectories,
            substrate_depletions=substrates,
        )
