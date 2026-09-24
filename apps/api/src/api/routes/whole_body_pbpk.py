"""API router for Whole-Body PBPK Digital Twin & Trans-Organ Pharmacokinetics."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.whole_body_pbpk_repo import WholeBodyPBPKRepository
from research.pbpk.whole_body_pbpk_engine import WholeBodyPBPKEngine

router = APIRouter(prefix="/pbpk", tags=["Whole-Body PBPK Digital Twin"])


class SimulatePBPKRequest(BaseModel):
    study_name: str = Field(..., description="Name of the PBPK simulation study")
    drug_candidate_name: str = Field(..., description="Identifier or name of the drug candidate")
    molecular_weight_da: float = Field(450.0, ge=10.0, le=10000.0, description="Molecular weight (Da)")
    logp: float = Field(2.5, ge=-5.0, le=10.0, description="Octanol-water partition coefficient LogP")
    plasma_protein_unbound_fraction: float = Field(0.08, ge=0.001, le=1.0, description="Fraction unbound in plasma (fu)")
    intrinsic_clearance_ml_min_kg: float = Field(15.0, ge=0.1, le=500.0, description="Intrinsic clearance (mL/min/kg)")
    species: str = Field("human", description="Target species (human, cynomolgus, rat)")
    administration_route: str = Field("oral", description="Route of administration (oral, iv_bolus, subcutaneous)")
    dose_mg_kg: float = Field(10.0, ge=0.01, le=2000.0, description="Administered dose (mg/kg)")
    simulation_time_hours: float = Field(24.0, ge=1.0, le=168.0, description="Simulation duration in hours")


class OrganCompartmentResponse(BaseModel):
    id: Optional[str] = None
    organ_name: str
    organ_volume_l_kg: float
    blood_flow_rate_l_h_kg: float
    tissue_plasma_partition_coefficient: float
    permeability_surface_area_product: float
    computed_cmax_ug_ml: float
    computed_auc_ug_h_ml: float
    computed_tmax_h: float


class ClearanceRateResponse(BaseModel):
    id: Optional[str] = None
    elimination_pathway: str
    organ_source: str
    clearance_rate_ml_min: float
    extraction_ratio: float
    fraction_metabolized: float


class PBPKStudyResponse(BaseModel):
    id: str
    study_name: str
    drug_candidate_name: str
    molecular_weight_da: float
    logp: float
    plasma_protein_unbound_fraction: float
    intrinsic_clearance_ml_min_kg: float
    species: str
    administration_route: str
    dose_mg_kg: float
    simulation_time_hours: float
    status: str
    summary_metrics: Optional[Dict[str, Any]] = None
    organ_compartments: List[OrganCompartmentResponse] = []
    clearance_rates: List[ClearanceRateResponse] = []
    created_at: str
    updated_at: str


def _serialize_study(study: Any) -> PBPKStudyResponse:
    return PBPKStudyResponse(
        id=str(study.id),
        study_name=study.study_name,
        drug_candidate_name=study.drug_candidate_name,
        molecular_weight_da=study.molecular_weight_da,
        logp=study.logp,
        plasma_protein_unbound_fraction=study.plasma_protein_unbound_fraction,
        intrinsic_clearance_ml_min_kg=study.intrinsic_clearance_ml_min_kg,
        species=study.species,
        administration_route=study.administration_route,
        dose_mg_kg=study.dose_mg_kg,
        simulation_time_hours=study.simulation_time_hours,
        status=study.status,
        summary_metrics=study.summary_metrics or {},
        organ_compartments=[
            OrganCompartmentResponse(
                id=str(c.id),
                organ_name=c.organ_name,
                organ_volume_l_kg=c.organ_volume_l_kg,
                blood_flow_rate_l_h_kg=c.blood_flow_rate_l_h_kg,
                tissue_plasma_partition_coefficient=c.tissue_plasma_partition_coefficient,
                permeability_surface_area_product=c.permeability_surface_area_product,
                computed_cmax_ug_ml=c.computed_cmax_ug_ml,
                computed_auc_ug_h_ml=c.computed_auc_ug_h_ml,
                computed_tmax_h=c.computed_tmax_h,
            )
            for c in (study.organ_compartments or [])
        ],
        clearance_rates=[
            ClearanceRateResponse(
                id=str(r.id),
                elimination_pathway=r.elimination_pathway,
                organ_source=r.organ_source,
                clearance_rate_ml_min=r.clearance_rate_ml_min,
                extraction_ratio=r.extraction_ratio,
                fraction_metabolized=r.fraction_metabolized,
            )
            for r in (study.clearance_rates or [])
        ],
        created_at=str(study.created_at),
        updated_at=str(study.updated_at),
    )


@router.post("/simulate", response_model=PBPKStudyResponse, status_code=status.HTTP_201_CREATED)
async def simulate_pbpk(
    payload: SimulatePBPKRequest,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> PBPKStudyResponse:
    """Run a whole-body physiologically based pharmacokinetic simulation."""
    engine = WholeBodyPBPKEngine()
    sim_result = engine.simulate_pharmacokinetics(
        study_name=payload.study_name,
        drug_candidate_name=payload.drug_candidate_name,
        molecular_weight_da=payload.molecular_weight_da,
        logp=payload.logp,
        plasma_protein_unbound_fraction=payload.plasma_protein_unbound_fraction,
        intrinsic_clearance_ml_min_kg=payload.intrinsic_clearance_ml_min_kg,
        species=payload.species,
        administration_route=payload.administration_route,
        dose_mg_kg=payload.dose_mg_kg,
        simulation_time_hours=payload.simulation_time_hours,
    )

    repo = WholeBodyPBPKRepository(session)
    study = await repo.create_study(
        study_name=sim_result["study_name"],
        drug_candidate_name=sim_result["drug_candidate_name"],
        molecular_weight_da=sim_result["molecular_weight_da"],
        logp=sim_result["logp"],
        plasma_protein_unbound_fraction=sim_result["plasma_protein_unbound_fraction"],
        intrinsic_clearance_ml_min_kg=sim_result["intrinsic_clearance_ml_min_kg"],
        species=sim_result["species"],
        administration_route=sim_result["administration_route"],
        dose_mg_kg=sim_result["dose_mg_kg"],
        simulation_time_hours=sim_result["simulation_time_hours"],
        summary_metrics=sim_result["summary_metrics"],
        compartments=sim_result["compartments"],
        clearance_rates=sim_result["clearance_rates"],
    )
    return _serialize_study(study)


@router.get("/studies", response_model=List[PBPKStudyResponse])
async def list_pbpk_studies(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> List[PBPKStudyResponse]:
    """List all saved PBPK studies."""
    repo = WholeBodyPBPKRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [_serialize_study(s) for s in studies]


@router.get("/studies/{study_id}", response_model=PBPKStudyResponse)
async def get_pbpk_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> PBPKStudyResponse:
    """Retrieve details and compartment kinetics for a specific PBPK study."""
    repo = WholeBodyPBPKRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PBPK study not found")
    return _serialize_study(study)


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pbpk_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> None:
    """Delete a PBPK study by ID."""
    repo = WholeBodyPBPKRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PBPK study not found")
