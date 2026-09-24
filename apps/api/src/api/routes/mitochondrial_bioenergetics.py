"""FastAPI Route for Mitochondrial Bioenergetics (Phase 144)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.mitochondrial_bioenergetics_repo import MitochondrialBioenergeticsRepository
from research.cellular.mitochondrial_bioenergetics_engine import (
    MitochondrialBioenergeticsEngine,
    BioenergeticsSimulationRequest,
    BioenergeticsSimulationResult,
)

router = APIRouter(prefix="/mitochondrial-bioenergetics", tags=["Mitochondrial Bioenergetics"])


@router.post("/simulate", response_model=BioenergeticsSimulationResult)
async def simulate_mitochondrial_oxphos(
    payload: BioenergeticsSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = MitochondrialBioenergeticsEngine()
    result = engine.simulate(payload)

    repo = MitochondrialBioenergeticsRepository(db)
    study = await repo.create_study(
        cell_line_or_tissue=result.cell_line,
        oxygen_consumption_rate_pmol_min=result.basal_ocr_pmol_min,
        extracellular_acidification_rate=35.0,
        respiratory_control_ratio=round(result.maximal_respiratory_capacity / max(1.0, result.proton_leak), 2),
        membrane_potential_delta_psi_mv=result.delta_psi_mv,
    )

    for c in result.etc_complexes:
        await repo.add_complex_record(
            study_id=study.id,
            complex_name=c.complex_id,
            relative_activity_pct=c.activity_pct,
            proton_pumping_stoichiometry=4.0,
            inhibitor_sensitivity="Rotenone/Antimycin",
        )

    await repo.add_ros_profile(
        study_id=study.id,
        superoxide_flux_uM_s=result.superoxide_emission_rate,
        h2o2_emission_rate=result.superoxide_emission_rate * 0.5,
        mptp_opening_probability=0.04,
        glutathione_redox_ratio=55.0,
    )

    return result
