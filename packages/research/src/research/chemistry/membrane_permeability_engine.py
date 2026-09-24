"""In-Silico Membrane Permeability & PAMPA QSAR Engine (Phase 140)."""

import math
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class PAMPAEvaluationRequest(BaseModel):
    molecule_name: str
    smiles: str
    molecular_weight: float = Field(..., gt=0)
    logp: float
    tpsa: float = Field(..., ge=0)
    h_bond_donors: int = Field(default=1, ge=0)
    h_bond_acceptors: int = Field(default=2, ge=0)
    rotatable_bonds: int = Field(default=4, ge=0)


class DiffusivityPoint(BaseModel):
    depth_angstrom: float
    free_energy_barrier_kcal_mol: float
    diffusion_coeff: float


class PAMPAEvaluationResult(BaseModel):
    molecule_name: str
    smiles: str
    papp_cm_per_s: float
    permeability_class: str
    qsar_score: float
    bbb_permeable: bool
    diffusivity_profile: List[DiffusivityPoint]
    status: str = "COMPLETED"


class MembranePermeabilityEngine:
    """Predicts artificial membrane permeability (Papp) using inhomogeneous solubility-diffusion models."""

    def evaluate(self, req: PAMPAEvaluationRequest) -> PAMPAEvaluationResult:
        # Inhomogeneous solubility-diffusion Papp estimation
        # Papp ~ exp(0.5 * logP - 0.03 * TPSA - 0.005 * MW) * 1e-6
        raw_exponent = 0.45 * req.logp - 0.025 * req.tpsa - 0.004 * req.molecular_weight
        papp = round(math.exp(max(-10.0, min(5.0, raw_exponent))) * 10.0 * 1e-6, 9)

        if papp >= 10.0e-6:
            perm_class = "High"
        elif papp >= 2.0e-6:
            perm_class = "Moderate"
        else:
            perm_class = "Low"

        # QSAR descriptor index
        qsar_score = round(1.0 / (1.0 + math.exp(-0.8 * req.logp + 0.03 * req.tpsa + 0.2 * req.h_bond_donors)), 4)
        bbb_permeable = bool(req.logp >= 1.5 and req.tpsa <= 90.0 and req.molecular_weight <= 450.0)

        # Depth-dependent free energy profile across 35 Angstrom bilayer
        depths = [-15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0]
        diff_profile = []
        for d in depths:
            # Hydrophobic core at d=0 has maximum barrier for polar groups, minimum for hydrophobic
            barrier = round(max(0.5, 3.5 - 0.8 * req.logp + 0.04 * req.tpsa * math.exp(-abs(d) / 5.0)), 2)
            d_coeff = round(1e-5 * math.exp(-abs(d) / 10.0), 7)
            diff_profile.append(
                DiffusivityPoint(
                    depth_angstrom=d,
                    free_energy_barrier_kcal_mol=barrier,
                    diffusion_coeff=d_coeff,
                )
            )

        return PAMPAEvaluationResult(
            molecule_name=req.molecule_name,
            smiles=req.smiles,
            papp_cm_per_s=papp,
            permeability_class=perm_class,
            qsar_score=qsar_score,
            bbb_permeable=bbb_permeable,
            diffusivity_profile=diff_profile,
        )
