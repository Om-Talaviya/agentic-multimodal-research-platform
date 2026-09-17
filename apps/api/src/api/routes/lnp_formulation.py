"""REST API endpoints for Synthetic Cell Membrane Dynamics & LNP Formulation Simulator."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.lnp_formulation_repo import LNPFormulationRepository
from research.lnp.lnp_engine import LNPFormulationSimulatorEngine

router = APIRouter(prefix="/api/v1/lnp", tags=["LNP Formulation Simulator"])
engine = LNPFormulationSimulatorEngine()


class LipidComponentInput(BaseModel):
    component_name: str
    lipid_category: str
    molar_percentage: float = 25.0
    molecular_weight_g_mol: float = 700.0
    charge_at_ph7: float = 0.0


class LNPFormulationRequest(BaseModel):
    formulation_name: str
    cargo_type: str = "mRNA"
    ionizable_lipid_name: str = "ALC-0315"
    np_ratio: float = Field(6.0, ge=1.0, le=20.0)
    flow_rate_ratio_aqueous_organic: float = Field(3.0, ge=1.0, le=10.0)
    total_flow_rate_ml_min: float = Field(12.0, ge=0.5, le=50.0)
    components: Optional[List[LipidComponentInput]] = None


@router.post("/formulations/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_lnp_formulation(
    req: LNPFormulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulates LNP self-assembly biophysics, size distribution, and synthetic membrane dynamics."""
    repo = LNPFormulationRepository(db)

    components_dict = [c.model_dump() for c in req.components] if req.components else None
    eval_res = engine.simulate_formulation(req.model_dump(), components_dict)

    study = await repo.create_formulation(
        formulation_name=eval_res["formulation_name"],
        cargo_type=eval_res["cargo_type"],
        ionizable_lipid_name=eval_res["ionizable_lipid_name"],
        lipid_ratio_molar_json=eval_res["lipid_ratio_molar_json"],
        np_ratio=eval_res["np_ratio"],
        encapsulation_efficiency_pct=eval_res["encapsulation_efficiency_pct"],
        mean_diameter_nm=eval_res["mean_diameter_nm"],
        pdi_polydispersity_index=eval_res["pdi_polydispersity_index"],
        zeta_potential_mv=eval_res["zeta_potential_mv"],
        apparent_pka=eval_res["apparent_pka"],
        simulation_metadata_json=eval_res["simulation_metadata_json"],
    )

    created_components = await repo.add_components(study.id, eval_res["components"])
    created_profile = await repo.add_membrane_profile(study.id, eval_res["membrane_profile"])

    return {
        "id": study.id,
        "formulation_name": study.formulation_name,
        "cargo_type": study.cargo_type,
        "ionizable_lipid_name": study.ionizable_lipid_name,
        "lipid_ratio_molar": study.lipid_ratio_molar_json,
        "np_ratio": study.np_ratio,
        "encapsulation_efficiency_pct": study.encapsulation_efficiency_pct,
        "mean_diameter_nm": study.mean_diameter_nm,
        "pdi_polydispersity_index": study.pdi_polydispersity_index,
        "zeta_potential_mv": study.zeta_potential_mv,
        "apparent_pka": study.apparent_pka,
        "metadata": study.simulation_metadata_json,
        "components": [
            {
                "id": c.id,
                "component_name": c.component_name,
                "lipid_category": c.lipid_category,
                "molar_percentage": c.molar_percentage,
                "molecular_weight_g_mol": c.molecular_weight_g_mol,
                "charge_at_ph7": c.charge_at_ph7,
            }
            for c in created_components
        ],
        "membrane_profile": {
            "id": created_profile.id,
            "membrane_thickness_angstrom": created_profile.membrane_thickness_angstrom,
            "area_per_lipid_angstrom2": created_profile.area_per_lipid_angstrom2,
            "order_parameter_s2": created_profile.order_parameter_s2,
            "bending_modulus_kc_kbt": created_profile.bending_modulus_kc_kbt,
            "endosomal_escape_efficiency_pct": created_profile.endosomal_escape_efficiency_pct,
            "cytotoxicity_score": created_profile.cytotoxicity_score,
        }
    }


@router.get("/formulations")
async def list_formulations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists LNP formulation studies."""
    repo = LNPFormulationRepository(db)
    formulations = await repo.list_formulations(limit=limit, offset=offset)
    return [
        {
            "id": f.id,
            "formulation_name": f.formulation_name,
            "cargo_type": f.cargo_type,
            "ionizable_lipid_name": f.ionizable_lipid_name,
            "mean_diameter_nm": f.mean_diameter_nm,
            "encapsulation_efficiency_pct": f.encapsulation_efficiency_pct,
            "apparent_pka": f.apparent_pka,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in formulations
    ]


@router.get("/formulations/{formulation_id}")
async def get_formulation_details(
    formulation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed LNP formulation study with components and membrane dynamics."""
    repo = LNPFormulationRepository(db)
    formulation = await repo.get_formulation(formulation_id)
    if not formulation:
        raise HTTPException(status_code=404, detail="LNP formulation study not found")

    components = await repo.get_components_by_formulation(formulation_id)
    membrane = await repo.get_membrane_profile_by_formulation(formulation_id)

    return {
        "id": formulation.id,
        "formulation_name": formulation.formulation_name,
        "cargo_type": formulation.cargo_type,
        "ionizable_lipid_name": formulation.ionizable_lipid_name,
        "lipid_ratio_molar": formulation.lipid_ratio_molar_json,
        "np_ratio": formulation.np_ratio,
        "encapsulation_efficiency_pct": formulation.encapsulation_efficiency_pct,
        "mean_diameter_nm": formulation.mean_diameter_nm,
        "pdi_polydispersity_index": formulation.pdi_polydispersity_index,
        "zeta_potential_mv": formulation.zeta_potential_mv,
        "apparent_pka": formulation.apparent_pka,
        "metadata": formulation.simulation_metadata_json,
        "components": [
            {
                "id": c.id,
                "component_name": c.component_name,
                "lipid_category": c.lipid_category,
                "molar_percentage": c.molar_percentage,
                "molecular_weight_g_mol": c.molecular_weight_g_mol,
                "charge_at_ph7": c.charge_at_ph7,
            }
            for c in components
        ],
        "membrane_profile": {
            "id": membrane.id if membrane else None,
            "membrane_thickness_angstrom": membrane.membrane_thickness_angstrom if membrane else None,
            "area_per_lipid_angstrom2": membrane.area_per_lipid_angstrom2 if membrane else None,
            "order_parameter_s2": membrane.order_parameter_s2 if membrane else None,
            "bending_modulus_kc_kbt": membrane.bending_modulus_kc_kbt if membrane else None,
            "endosomal_escape_efficiency_pct": membrane.endosomal_escape_efficiency_pct if membrane else None,
            "cytotoxicity_score": membrane.cytotoxicity_score if membrane else None,
        } if membrane else None
    }
