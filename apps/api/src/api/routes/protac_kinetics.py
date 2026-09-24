"""FastAPI Route for PROTAC Ternary Complex Kinetics (Phase 156)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.protac_ternary_complex_repo import PROTACKineticsRepository
from research.targeted_degradation.protac_kinetics_engine import (
    PROTACKineticsEngine,
    PROTACKineticsRequest,
    PROTACKineticsResult,
)

router = APIRouter(prefix="/protac-kinetics", tags=["PROTAC Kinetics"])


@router.post("/simulate", response_model=PROTACKineticsResult)
async def simulate_protac_kinetics(
    payload: PROTACKineticsRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = PROTACKineticsEngine()
    result = engine.simulate_degradation(payload)

    repo = PROTACKineticsRepository(db)
    study = await repo.create_study(
        protac_compound_name=result.protac_compound_name,
        target_protein_name=result.target_protein_name,
        e3_ligase_name=result.e3_ligase_name,
        linker_type=result.linker_type,
        cooperativity_alpha=result.cooperativity_alpha,
        dc50_nM=result.dc50_nM,
        dmax_percent=result.dmax_percent,
        hook_effect_threshold_uM=result.hook_effect_threshold_uM,
    )

    for p in result.e3_profiles:
        await repo.add_e3_profile(
            study_id=study.id,
            domain_type=p.domain_type,
            kd_binary_nM=p.kd_binary_nM,
            kd_ternary_nM=p.kd_ternary_nM,
            delta_g_formation_kcal_mol=p.delta_g_formation_kcal_mol,
        )

    for d in result.dose_response_curve:
        await repo.add_degradation_point(
            study_id=study.id,
            protac_dose_nM=d.protac_dose_nM,
            ternary_fraction=d.ternary_fraction,
            degradation_rate_pct=d.degradation_rate_pct,
            ubiquitination_flux=d.ubiquitination_flux,
        )

    return result
