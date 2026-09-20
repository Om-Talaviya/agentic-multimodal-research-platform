"""
FastAPI route for Phase 105: Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS).
"""
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.hdx_ms_repo import HDXMassSpecRepository
from research.structural.hdx_engine import HDXDynamicsEngine

router = APIRouter(prefix="/hdx-ms", tags=["Phase 105: HDX-MS Conformational Dynamics"])

class PeptideInput(BaseModel):
    peptide_sequence: str
    start_res: int
    end_res: int
    is_binding_site: bool = False

class HDXSimulationRequest(BaseModel):
    protein_name: str
    uniprot_id: Optional[str] = None
    state_condition: str = "LIGAND_BOUND"
    peptides: List[PeptideInput]
    timepoints: Optional[List[float]] = None

class HDXExperimentResponse(BaseModel):
    id: str
    protein_name: str
    uniprot_id: Optional[str] = None
    state_condition: str
    total_peptides: int
    sequence_coverage_pct: float
    redundancy_score: float
    status: str
    uptake_curves: List[Dict[str, Any]] = []
    protection_maps: List[Dict[str, Any]] = []

@router.post("/simulate", response_model=HDXExperimentResponse, status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_hdx(
    request: HDXSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = HDXDynamicsEngine()
    raw_peptides = [p.model_dump() for p in request.peptides]
    sim = engine.simulate_experiment(
        protein_name=request.protein_name,
        peptides=raw_peptides,
        state_condition=request.state_condition,
        timepoints=request.timepoints
    )

    repo = HDXMassSpecRepository(db)
    exp = await repo.create_experiment(
        protein_name=sim["protein_name"],
        uniprot_id=request.uniprot_id,
        state_condition=sim["state_condition"],
        sequence_coverage_pct=sim["sequence_coverage_pct"],
        redundancy_score=sim["redundancy_score"]
    )

    await repo.add_uptake_curves(exp.id, sim["uptake_curves"])
    await repo.add_protection_maps(exp.id, sim["protection_maps"])

    hydrated = await repo.get_experiment(exp.id)
    if not hydrated:
        raise HTTPException(status_code=500, detail="Failed to retrieve HDX experiment")

    return HDXExperimentResponse(
        id=str(hydrated.id),
        protein_name=hydrated.protein_name,
        uniprot_id=hydrated.uniprot_id,
        state_condition=hydrated.state_condition,
        total_peptides=hydrated.total_peptides,
        sequence_coverage_pct=hydrated.sequence_coverage_pct,
        redundancy_score=hydrated.redundancy_score,
        status=hydrated.status,
        uptake_curves=[{
            "peptide_sequence": c.peptide_sequence,
            "start_res": c.start_res,
            "end_res": c.end_res,
            "timepoint_seconds": c.timepoint_seconds,
            "deuterium_uptake_da": c.deuterium_uptake_da,
            "fractional_uptake_pct": c.fractional_uptake_pct,
            "protection_factor_ln_p": c.protection_factor_ln_p
        } for c in hydrated.uptake_curves],
        protection_maps=[{
            "residue_number": m.residue_number,
            "amino_acid": m.amino_acid,
            "protection_factor": m.protection_factor,
            "solvent_accessibility_level": m.solvent_accessibility_level,
            "delta_uptake_apo_vs_bound": m.delta_uptake_apo_vs_bound
        } for m in hydrated.protection_maps]
    )

@router.get("/experiments", response_model=List[HDXExperimentResponse])
async def list_hdx_experiments(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    repo = HDXMassSpecRepository(db)
    experiments = await repo.list_experiments(limit=limit, offset=offset)
    return [
        HDXExperimentResponse(
            id=str(e.id),
            protein_name=e.protein_name,
            uniprot_id=e.uniprot_id,
            state_condition=e.state_condition,
            total_peptides=e.total_peptides,
            sequence_coverage_pct=e.sequence_coverage_pct,
            redundancy_score=e.redundancy_score,
            status=e.status,
            uptake_curves=[],
            protection_maps=[]
        )
        for e in experiments
    ]

@router.get("/experiments/{experiment_id}", response_model=HDXExperimentResponse)
async def get_hdx_experiment_detail(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = HDXMassSpecRepository(db)
    hydrated = await repo.get_experiment(experiment_id)
    if not hydrated:
        raise HTTPException(status_code=404, detail="HDX experiment not found")

    return HDXExperimentResponse(
        id=str(hydrated.id),
        protein_name=hydrated.protein_name,
        uniprot_id=hydrated.uniprot_id,
        state_condition=hydrated.state_condition,
        total_peptides=hydrated.total_peptides,
        sequence_coverage_pct=hydrated.sequence_coverage_pct,
        redundancy_score=hydrated.redundancy_score,
        status=hydrated.status,
        uptake_curves=[{
            "peptide_sequence": c.peptide_sequence,
            "start_res": c.start_res,
            "end_res": c.end_res,
            "timepoint_seconds": c.timepoint_seconds,
            "deuterium_uptake_da": c.deuterium_uptake_da,
            "fractional_uptake_pct": c.fractional_uptake_pct,
            "protection_factor_ln_p": c.protection_factor_ln_p
        } for c in hydrated.uptake_curves],
        protection_maps=[{
            "residue_number": m.residue_number,
            "amino_acid": m.amino_acid,
            "protection_factor": m.protection_factor,
            "solvent_accessibility_level": m.solvent_accessibility_level,
            "delta_uptake_apo_vs_bound": m.delta_uptake_apo_vs_bound
        } for m in hydrated.protection_maps]
    )
