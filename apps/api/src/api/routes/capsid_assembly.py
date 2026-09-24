"""FastAPI Route for AAV Viral Capsid Self-Assembly (Phase 151)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.viral_capsid_assembly_repo import CapsidAssemblyRepository
from research.virology.capsid_assembly_engine import (
    CapsidAssemblyEngine,
    CapsidAssemblyRequest,
    CapsidAssemblyResult,
)

router = APIRouter(prefix="/capsid-assembly", tags=["Capsid Assembly"])


@router.post("/simulate", response_model=CapsidAssemblyResult)
async def simulate_capsid_assembly(
    payload: CapsidAssemblyRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CapsidAssemblyEngine()
    result = engine.simulate(payload)

    repo = CapsidAssemblyRepository(db)
    study = await repo.create_study(
        serotype_name=result.serotype_name,
        triangulation_number=result.triangulation_number,
        vp_stoichiometry_ratio=result.vp_stoichiometry_ratio,
        assembly_yield_percent=result.assembly_yield_percent,
        gibbs_free_energy_kcal_mol=result.gibbs_free_energy_kcal_mol,
        critical_nucleus_size=result.critical_nucleus_size,
        full_empty_capsid_ratio=result.full_empty_capsid_ratio,
    )

    for i in result.interfaces:
        await repo.add_interface(
            study_id=study.id,
            symmetry_axis=i.symmetry_axis,
            delta_g_binding_kcal_mol=i.delta_g_binding_kcal_mol,
            buried_surface_area_a2=i.buried_surface_area_a2,
            hydrogen_bonds_count=i.hydrogen_bonds_count,
            salt_bridges_count=i.salt_bridges_count,
        )

    for t in result.trajectories:
        await repo.add_trajectory(
            study_id=study.id,
            oligomer_size=t.oligomer_size,
            forward_rate_k_on=t.forward_rate_k_on,
            reverse_rate_k_off=t.reverse_rate_k_off,
            fraction_assembled=t.fraction_assembled,
        )

    return result
