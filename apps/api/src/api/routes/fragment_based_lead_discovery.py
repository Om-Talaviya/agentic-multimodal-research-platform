"""FastAPI routes for Phase 184: Fragment-Based Drug Discovery Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.fragment_based_lead_discovery_repo import FBDDLeadDiscoveryRepository
from research.chemistry.fragment_based_lead_discovery_engine import FBDDLeadDiscoveryEngine

router = APIRouter(prefix="/fragment-based-lead-discovery", tags=["Fragment-Based Lead Discovery"])


class SimulateFBDDRequest(BaseModel):
    name: str = Field(..., example="KRAS-G12D Switch-II Fragment Linking Campaign")
    target_protein_pocket: str = Field(..., example="KRAS-G12D Switch-II Pocket")
    fragment_library_size: int = Field(default=1500, ge=100, le=50000)
    linker_growth_strategy: str = Field(default="fragment_linking_rigid")
    target_subpockets_count: int = Field(default=2, ge=1, le=5)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_fbdd(
    req: SimulateFBDDRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = FBDDLeadDiscoveryEngine()
    result = engine.simulate_fbdd_pipeline(
        target_protein_pocket=req.target_protein_pocket,
        fragment_library_size=req.fragment_library_size,
        linker_growth_strategy=req.linker_growth_strategy,
        target_subpockets_count=req.target_subpockets_count,
    )

    repo = FBDDLeadDiscoveryRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_protein_pocket=result.target_protein_pocket,
        fragment_library_size=result.fragment_library_size,
        top_fragment_kd_micromolar=result.top_fragment_kd_micromolar,
        mean_ligand_efficiency=result.mean_ligand_efficiency,
        linker_growth_strategy=result.linker_growth_strategy,
        optimized_lead_predicted_pic50=result.optimized_lead_predicted_pic50,
        lipinski_rule_of_three_compliance_pct=result.lipinski_rule_of_three_compliance_pct,
        status="completed",
        parameters={
            "lead_optimization_index": result.lead_optimization_index,
        },
        summary_report=result.medicinal_chemistry_recommendation,
    )

    for h in result.fragment_hits:
        await repo.add_fragment_hit(
            study_id=study.id,
            fragment_id=h.fragment_id,
            smiles_representation=h.smiles_representation,
            heavy_atom_count=h.heavy_atom_count,
            molecular_weight_da=h.molecular_weight_da,
            dissociation_constant_kd_um=h.dissociation_constant_kd_um,
            ligand_efficiency_le=h.ligand_efficiency_le,
            subpocket_binding_site=h.subpocket_binding_site,
        )

    for c in result.linker_candidates:
        await repo.add_linker_candidate(
            study_id=study.id,
            lead_id=c.lead_id,
            combined_smiles=c.combined_smiles,
            linker_type=c.linker_type,
            predicted_affinity_kd_nm=c.predicted_affinity_kd_nm,
            binding_delta_g_kcal_mol=c.binding_delta_g_kcal_mol,
            synthetic_accessibility_sa_score=c.synthetic_accessibility_sa_score,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "target_protein_pocket": study.target_protein_pocket,
        "mean_ligand_efficiency": study.mean_ligand_efficiency,
        "optimized_lead_predicted_pic50": study.optimized_lead_predicted_pic50,
        "lead_optimization_index": result.lead_optimization_index,
        "recommendation": result.medicinal_chemistry_recommendation,
        "fragment_hits": [
            {
                "fragment_id": fh.fragment_id,
                "smiles_representation": fh.smiles_representation,
                "molecular_weight_da": fh.molecular_weight_da,
                "dissociation_constant_kd_um": fh.dissociation_constant_kd_um,
                "ligand_efficiency_le": fh.ligand_efficiency_le,
                "subpocket_binding_site": fh.subpocket_binding_site,
            }
            for fh in result.fragment_hits
        ],
        "linker_candidates": [
            {
                "lead_id": lc.lead_id,
                "combined_smiles": lc.combined_smiles,
                "linker_type": lc.linker_type,
                "predicted_affinity_kd_nm": lc.predicted_affinity_kd_nm,
                "binding_delta_g_kcal_mol": lc.binding_delta_g_kcal_mol,
                "synthetic_accessibility_sa_score": lc.synthetic_accessibility_sa_score,
            }
            for lc in result.linker_candidates
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = FBDDLeadDiscoveryRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_protein_pocket": s.target_protein_pocket,
            "mean_ligand_efficiency": s.mean_ligand_efficiency,
            "optimized_lead_predicted_pic50": s.optimized_lead_predicted_pic50,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]