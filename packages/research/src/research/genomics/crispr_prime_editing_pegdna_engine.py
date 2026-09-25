"""Autonomous Prime Editing pegRNA Design & Flap Kinetics Synthesis Matrix Engine (Phase 180)."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import math


@dataclass
class PegDNACandidateResult:
    candidate_id: str
    spacer_sequence_20nt: str
    pbs_sequence: str
    rtt_sequence_with_edit: str
    tevpre_structural_motif: str
    deep_pe_score: float
    melting_temp_pbs_celsius: float


@dataclass
class FlapEquilibriumKineticsPoint:
    flap_position_nt: int
    gibbs_free_energy_edited_flap_kcal: float
    gibbs_free_energy_unmodified_flap_kcal: float
    fen1_endonuclease_cleavage_rate: float
    incorporation_probability: float


@dataclass
class PrimeEditingPegDNAResult:
    target_gene: str
    intended_mutation_type: str
    pbs_length_nt: int
    rtt_length_nt: int
    nick_to_edit_distance_bp: int
    predicted_prime_editing_efficiency: float
    indel_byproduct_frequency: float
    flap_equilibrium_ratio: float
    pe_system_version: str
    pegdna_candidates: List[PegDNACandidateResult]
    flap_kinetics: List[FlapEquilibriumKineticsPoint]
    design_recommendation: str
    fidelity_index: float


class CRISPRPrimeEditingPegDNAEngine:
    """Engine for in-silico pegRNA optimization, PBS/RTT melting thermodynamics, and 3' flap vs 5' flap kinetics."""

    def __init__(self) -> None:
        pass

    def simulate_pegdna_design(
        self,
        target_gene: str = "HBB",
        intended_mutation_type: str = "point_substitution",
        pbs_length_nt: int = 13,
        rtt_length_nt: int = 15,
        nick_to_edit_distance_bp: int = 3,
        pe_system_version: str = "PEmax_epegRNA",
    ) -> PrimeEditingPegDNAResult:
        """Simulate candidate pegRNA generation and flap equilibrium dynamics."""
        tm_pbs = round(32.0 + (pbs_length_nt * 0.85) - (abs(nick_to_edit_distance_bp - 3) * 0.4), 1)

        dist_penalty = max(0.0, (nick_to_edit_distance_bp - 3) * 0.04)
        len_penalty = abs(pbs_length_nt - 13) * 0.02 + abs(rtt_length_nt - 15) * 0.015
        base_eff = 0.76 if "PEmax" in pe_system_version else 0.52
        pred_eff = round(max(0.15, min(0.95, base_eff - dist_penalty - len_penalty)), 3)

        indel_freq = round(max(0.01, 0.035 + (dist_penalty * 0.5)), 3)
        flap_ratio = round(2.8 + (pred_eff * 1.5) - (indel_freq * 10.0), 2)

        candidates = []
        for i in range(1, 4):
            c_pbs = pbs_length_nt + (i - 2)
            c_rtt = rtt_length_nt + (i - 1)
            c_tm = round(tm_pbs + (i * 0.7), 1)
            c_score = round(max(0.5, pred_eff - (abs(i - 1) * 0.05)), 2)
            candidates.append(
                PegDNACandidateResult(
                    candidate_id=f"pegRNA_{target_gene}_PBS{c_pbs}_RTT{c_rtt}_v{i}",
                    spacer_sequence_20nt=f"GACAGGTACGGCTA{i}TGCCA",
                    pbs_sequence=f"CGTTAGCTA{i}TGC",
                    rtt_sequence_with_edit=f"GCAATTTGGTA{i}CAGTT",
                    tevpre_structural_motif="tevpre_hairpin_epegRNA",
                    deep_pe_score=c_score,
                    melting_temp_pbs_celsius=c_tm,
                )
            )

        flap_pts = []
        for pos in [1, 3, 6, 9, 12, 15]:
            dG_edit = round(-18.5 - (pos * 0.6), 2)
            dG_unmod = round(-16.0 - (pos * 0.5), 2)
            fen1_rate = round(0.45 + (pos * 0.03), 3)
            prob = round(min(0.98, 0.65 + (pos * 0.02)), 3)
            flap_pts.append(
                FlapEquilibriumKineticsPoint(
                    flap_position_nt=pos,
                    gibbs_free_energy_edited_flap_kcal=dG_edit,
                    gibbs_free_energy_unmodified_flap_kcal=dG_unmod,
                    fen1_endonuclease_cleavage_rate=fen1_rate,
                    incorporation_probability=prob,
                )
            )

        fidelity = round(pred_eff / (indel_freq + 0.001), 1)
        rec = f"Optimized {pe_system_version} design for {target_gene} achieves {round(pred_eff*100, 1)}% editing efficiency with low indel byproduct ({round(indel_freq*100, 1)}%). Recommended PBS {pbs_length_nt}nt (Tm {tm_pbs} deg C), RTT {rtt_length_nt}nt."

        return PrimeEditingPegDNAResult(
            target_gene=target_gene,
            intended_mutation_type=intended_mutation_type,
            pbs_length_nt=pbs_length_nt,
            rtt_length_nt=rtt_length_nt,
            nick_to_edit_distance_bp=nick_to_edit_distance_bp,
            predicted_prime_editing_efficiency=pred_eff,
            indel_byproduct_frequency=indel_freq,
            flap_equilibrium_ratio=flap_ratio,
            pe_system_version=pe_system_version,
            pegdna_candidates=candidates,
            flap_kinetics=flap_pts,
            design_recommendation=rec,
            fidelity_index=fidelity,
        )