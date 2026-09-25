"""API Router for AlphaFold Multimeric Complex & Co-Evolutionary Contact Forecaster."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.alphafold_complex_docking_repo import AlphaFoldComplexRepository
from research.structural.alphafold_complex_docking_engine import AlphaFoldComplexDockingEngine

router = APIRouter(prefix="/alphafold-complex-docking", tags=["AlphaFold Complex Docking"])


class ContactResidueInput(BaseModel):
    chain_a_residue: str = Field("Tyr68", description="Chain A contact residue")
    chain_b_residue: str = Field("Glu121", description="Chain B contact residue")
    inter_residue_distance_angstrom: float = Field(2.74, description="Inter-residue distance in Angstroms")
    predicted_aligned_error_angstrom: float = Field(1.45, description="PAE in Angstroms")
    interaction_type: str = Field("salt_bridge", description="Biochemical interaction category")
    contact_plddt: float = Field(93.4, description="Residue confidence score (0-100)")


class PredictComplexDockingRequest(BaseModel):
    study_name: str = Field(..., description="Name for the complex docking experiment")
    target_complex_name: str = Field("PD-1 / PD-L1 Complex", description="Target multimer complex identifier")
    chain_a_name: str = Field("PDCD1_HUMAN (Chain A)", description="Primary receptor protein chain")
    chain_b_name: str = Field("CD274_HUMAN (Chain B)", description="Interacting ligand/binder chain")
    custom_contacts: Optional[List[ContactResidueInput]] = None


@router.post("/predict", status_code=status.HTTP_201_CREATED)
async def predict_complex_docking(
    payload: PredictComplexDockingRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Run AlphaFold-Multimer contact prediction and interface energetics scoring."""
    engine = AlphaFoldComplexDockingEngine()
    contacts_data = [c.model_dump() for c in payload.custom_contacts] if payload.custom_contacts else None

    result = engine.predict_complex_docking(
        study_name=payload.study_name,
        target_complex_name=payload.target_complex_name,
        chain_a_name=payload.chain_a_name,
        chain_b_name=payload.chain_b_name,
        custom_contacts=contacts_data,
    )

    repo = AlphaFoldComplexRepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        target_complex_name=result["target_complex_name"],
        chain_a_name=result["chain_a_name"],
        chain_b_name=result["chain_b_name"],
        mean_iptm_score=result["mean_iptm_score"],
        mean_plddt_interface=result["mean_plddt_interface"],
        buried_surface_area_angstrom2=result["buried_surface_area_angstrom2"],
        summary_metrics=result["summary_metrics"],
        contacts=result["contacts"],
        energy_metrics=result["energy_metrics"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "target_complex_name": saved_study.target_complex_name,
        "chain_a_name": saved_study.chain_a_name,
        "chain_b_name": saved_study.chain_b_name,
        "mean_iptm_score": saved_study.mean_iptm_score,
        "mean_plddt_interface": saved_study.mean_plddt_interface,
        "buried_surface_area_angstrom2": saved_study.buried_surface_area_angstrom2,
        "summary_metrics": saved_study.summary_metrics,
        "contacts": [
            {
                "id": str(c.id),
                "chain_a_residue": c.chain_a_residue,
                "chain_b_residue": c.chain_b_residue,
                "inter_residue_distance_angstrom": c.inter_residue_distance_angstrom,
                "predicted_aligned_error_angstrom": c.predicted_aligned_error_angstrom,
                "interaction_type": c.interaction_type,
                "contact_plddt": c.contact_plddt,
            }
            for c in saved_study.contacts
        ],
        "energy_metrics": [
            {
                "id": str(e.id),
                "energy_component": e.energy_component,
                "value_kcal_mol": e.value_kcal_mol,
                "favorable_flag": e.favorable_flag,
            }
            for e in saved_study.energy_metrics
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_complex_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent AlphaFold multimer complex studies."""
    repo = AlphaFoldComplexRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "target_complex_name": s.target_complex_name,
            "chain_a_name": s.chain_a_name,
            "chain_b_name": s.chain_b_name,
            "mean_iptm_score": s.mean_iptm_score,
            "mean_plddt_interface": s.mean_plddt_interface,
            "buried_surface_area_angstrom2": s.buried_surface_area_angstrom2,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_complex_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details for a specific AlphaFold complex docking study."""
    repo = AlphaFoldComplexRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complex docking study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "target_complex_name": study.target_complex_name,
        "chain_a_name": study.chain_a_name,
        "chain_b_name": study.chain_b_name,
        "mean_iptm_score": study.mean_iptm_score,
        "mean_plddt_interface": study.mean_plddt_interface,
        "buried_surface_area_angstrom2": study.buried_surface_area_angstrom2,
        "summary_metrics": study.summary_metrics,
        "contacts": [
            {
                "id": str(c.id),
                "chain_a_residue": c.chain_a_residue,
                "chain_b_residue": c.chain_b_residue,
                "inter_residue_distance_angstrom": c.inter_residue_distance_angstrom,
                "predicted_aligned_error_angstrom": c.predicted_aligned_error_angstrom,
                "interaction_type": c.interaction_type,
                "contact_plddt": c.contact_plddt,
            }
            for c in study.contacts
        ],
        "energy_metrics": [
            {
                "id": str(e.id),
                "energy_component": e.energy_component,
                "value_kcal_mol": e.value_kcal_mol,
                "favorable_flag": e.favorable_flag,
            }
            for e in study.energy_metrics
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complex_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a complex docking study record by ID."""
    repo = AlphaFoldComplexRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complex docking study with ID '{study_id}' not found.",
        )
