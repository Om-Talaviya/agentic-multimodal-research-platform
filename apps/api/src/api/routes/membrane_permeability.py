"""FastAPI Route for In-Silico Membrane Permeability (Phase 140)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.membrane_permeability_repo import MembranePermeabilityRepository
from research.chemistry.membrane_permeability_engine import (
    MembranePermeabilityEngine,
    PAMPAEvaluationRequest,
    PAMPAEvaluationResult,
)

router = APIRouter(prefix="/membrane-permeability", tags=["Membrane Permeability"])


@router.post("/evaluate", response_model=PAMPAEvaluationResult)
async def evaluate_membrane_permeability(
    payload: PAMPAEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = MembranePermeabilityEngine()
    result = engine.evaluate(payload)

    repo = MembranePermeabilityRepository(db)
    study = await repo.create_study(
        molecule_name=result.molecule_name,
        smiles=result.smiles,
        molecular_weight=payload.molecular_weight,
        logp=payload.logp,
        tpsa=payload.tpsa,
        papp_cm_per_s=result.papp_cm_per_s,
        permeability_class=result.permeability_class,
    )

    for pt in result.diffusivity_profile:
        await repo.add_diffusivity_record(
            study_id=study.id,
            bilayer_depth_angstrom=pt.depth_angstrom,
            free_energy_barrier_kcal_mol=pt.free_energy_barrier_kcal_mol,
            local_diffusion_coefficient=pt.diffusion_coeff,
        )

    await repo.add_qsar_profile(
        study_id=study.id,
        h_bond_donors=payload.h_bond_donors,
        h_bond_acceptors=payload.h_bond_acceptors,
        rotatable_bonds=payload.rotatable_bonds,
        predicted_pampa_score=result.qsar_score,
        is_blood_brain_barrier_permeable=result.bbb_permeable,
    )

    return result
