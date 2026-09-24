"""Phase 156: Autonomous PROTAC Ternary Complex Degradation Kinetics Engine."""

import math
from typing import List, Optional
from pydantic import BaseModel, Field


class E3BindingDto(BaseModel):
    domain_type: str
    kd_binary_nM: float
    kd_ternary_nM: float
    delta_g_formation_kcal_mol: float


class DoseResponseKineticPointDto(BaseModel):
    protac_dose_nM: float
    ternary_fraction: float
    degradation_rate_pct: float
    ubiquitination_flux: float


class PROTACKineticsRequest(BaseModel):
    protac_compound_name: str = "ARV-110 (Bavdegalutamide Analogue)"
    target_protein_name: str = "Androgen Receptor (AR / AR-T878A)"
    e3_ligase_name: str = "VHL (Von Hippel-Lindau)"
    linker_type: str = "PEG3-Triazole Linker"
    target_kd_binary_nM: float = 18.5
    e3_kd_binary_nM: float = 35.0


class PROTACKineticsResult(BaseModel):
    protac_compound_name: str
    target_protein_name: str
    e3_ligase_name: str
    linker_type: str
    cooperativity_alpha: float
    dc50_nM: float
    dmax_percent: float
    hook_effect_threshold_uM: float
    e3_profiles: List[E3BindingDto]
    dose_response_curve: List[DoseResponseKineticPointDto]


class PROTACKineticsEngine:
    def simulate_degradation(self, req: PROTACKineticsRequest) -> PROTACKineticsResult:
        alpha = 4.5  # Positive cooperativity
        kd_ternary_poi = round(req.target_kd_binary_nM / alpha, 2)
        kd_ternary_e3 = round(req.e3_kd_binary_nM / alpha, 2)

        profiles = [
            E3BindingDto(
                domain_type="Target POI Binding Warhead",
                kd_binary_nM=req.target_kd_binary_nM,
                kd_ternary_nM=kd_ternary_poi,
                delta_g_formation_kcal_mol=-10.8,
            ),
            E3BindingDto(
                domain_type="E3 Ligase Recruitment Domain",
                kd_binary_nM=req.e3_kd_binary_nM,
                kd_ternary_nM=kd_ternary_e3,
                delta_g_formation_kcal_mol=-9.9,
            ),
        ]

        # Generate bell-shaped Hook effect curve
        doses = [0.1, 1.0, 10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0, 10000.0]
        points: List[DoseResponseKineticPointDto] = []

        for d in doses:
            # Bell curve model for ternary fraction
            x = math.log10(d)
            bell = math.exp(-((x - 1.7) ** 2) / 1.2)
            ternary = round(bell * 0.88, 3)
            deg = round(ternary * 96.5, 1)
            flux = round(ternary * 14.2, 2)
            points.append(
                DoseResponseKineticPointDto(
                    protac_dose_nM=d,
                    ternary_fraction=ternary,
                    degradation_rate_pct=deg,
                    ubiquitination_flux=flux,
                )
            )

        return PROTACKineticsResult(
            protac_compound_name=req.protac_compound_name,
            target_protein_name=req.target_protein_name,
            e3_ligase_name=req.e3_ligase_name,
            linker_type=req.linker_type,
            cooperativity_alpha=alpha,
            dc50_nM=2.8,
            dmax_percent=95.4,
            hook_effect_threshold_uM=2.5,
            e3_profiles=profiles,
            dose_response_curve=points,
        )
