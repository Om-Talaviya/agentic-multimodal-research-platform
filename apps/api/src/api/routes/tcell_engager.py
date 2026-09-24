"""FastAPI Route for Multispecific T-Cell Engagers (Phase 158)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.multispecific_tcell_engager_repo import MultispecificTCellEngagerRepository
from research.immunology.tcell_engager_geometry_engine import (
    TCellEngagerGeometryEngine,
    TCellEngagerRequest,
    TCellEngagerResult,
)

router = APIRouter(prefix="/tcell-engager", tags=["T-Cell Engager Geometry"])


@router.post("/model-geometry", response_model=TCellEngagerResult)
async def model_tcell_engager(
    payload: TCellEngagerRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = TCellEngagerGeometryEngine()
    result = engine.model_synapse_geometry(payload)

    repo = MultispecificTCellEngagerRepository(db)
    study = await repo.create_study(
        construct_name=result.construct_name,
        modality_format=result.modality_format,
        primary_tumor_antigen=result.primary_tumor_antigen,
        tcell_activation_arm=result.tcell_activation_arm,
        synaptic_cleft_distance_a=result.synaptic_cleft_distance_a,
        cytolytic_potency_ec50_pm=result.cytolytic_potency_ec50_pm,
        perforin_granzyme_flux=result.perforin_granzyme_flux,
        crs_cytokine_risk_score=result.crs_cytokine_risk_score,
    )

    for b in result.binding_domains:
        await repo.add_binding_domain(
            study_id=study.id,
            arm_designation=b.arm_designation,
            target_epitope=b.target_epitope,
            kd_affinity_nM=b.kd_affinity_nM,
            arm_length_angstrom=b.arm_length_angstrom,
            rotational_flexibility_deg=b.rotational_flexibility_deg,
        )

    for s in result.synapse_profiles:
        await repo.add_synapse_profile(
            study_id=study.id,
            intermembrane_distance_nm=s.intermembrane_distance_nm,
            synapse_maturation_time_min=s.synapse_maturation_time_min,
            lytic_granule_polarization_pct=s.lytic_granule_polarization_pct,
            tumor_lysis_percentage=s.tumor_lysis_percentage,
        )

    return result
