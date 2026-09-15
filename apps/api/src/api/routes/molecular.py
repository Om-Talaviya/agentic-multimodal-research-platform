"""Autonomous Bio-Molecular Structure & Protein Folding API Routes (Phase 38)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.molecular_repo import MolecularStructureRepository
from research.structure_engine import (
    BindingPocketSpec,
    StructurePredictionEngine,
)
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/molecular", tags=["molecular-structure"])
engine = StructurePredictionEngine()


# --- Pydantic Request / Response Schemas ---

class StructurePredictRequest(BaseModel):
    uniprot_id: str = Field(..., description="UniProt Accession ID (e.g. Q9BYF1, Q99250, P02766)")
    gene_name: Optional[str] = Field(None, description="Gene symbol (e.g. PCSK9, Cas9_Sp, TTR)")
    sequence: Optional[str] = Field(None, description="FASTA amino acid sequence")
    structure_source: str = Field("AlphaFold3", description="AlphaFold3, ESMFold, PDB_Experimental")
    organism: str = Field("Homo sapiens", description="Host organism")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class LigandDockRequest(BaseModel):
    pocket_id: uuid.UUID
    ligand_name: str = Field(..., description="Name of small molecule ligand or inhibitor")
    ligand_smiles: Optional[str] = None


class MutateRequest(BaseModel):
    wildtype_residue: str = Field(..., max_length=1, description="Single letter wildtype AA (e.g. D)")
    position: int = Field(..., ge=1, description="Residue sequence position")
    mutant_residue: str = Field(..., max_length=1, description="Single letter mutant AA (e.g. Y)")


# --- Endpoint Implementations ---

@router.post("/predict", status_code=status.HTTP_201_CREATED)
async def predict_molecular_structure(
    payload: StructurePredictRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Predict 3D protein structure coordinates, pLDDT spectrum, and active binding pockets."""
    pred = engine.predict_structure(
        uniprot_id=payload.uniprot_id,
        gene_name=payload.gene_name,
        sequence=payload.sequence,
        structure_source=payload.structure_source,
        organism=payload.organism,
    )

    repo = MolecularStructureRepository(session)
    structure = await repo.create_structure(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        uniprot_id=pred.uniprot_id,
        gene_name=pred.gene_name,
        sequence=pred.sequence,
        pdb_coordinate_data=pred.pdb_coordinate_data,
        mean_plddt_score=pred.mean_plddt_score,
        resolution_angstrom=pred.resolution_angstrom,
        structure_source=pred.structure_source,
        organism=pred.organism,
        secondary_structure_summary=pred.secondary_structure_summary,
    )

    # Persist binding pockets
    pockets = await repo.add_binding_pockets(
        structure_id=structure.id,
        pockets_data=[p.model_dump() for p in pred.binding_pockets],
    )

    await session.commit()
    logger.info("molecular_structure_persisted", structure_id=str(structure.id), uniprot=structure.uniprot_id)

    return {
        "id": str(structure.id),
        "uniprot_id": structure.uniprot_id,
        "gene_name": structure.gene_name,
        "organism": structure.organism,
        "mean_plddt_score": structure.mean_plddt_score,
        "resolution_angstrom": structure.resolution_angstrom,
        "structure_source": structure.structure_source,
        "sequence": structure.sequence,
        "secondary_structure_summary": structure.secondary_structure_summary,
        "binding_pockets": [
            {
                "id": str(p.id),
                "pocket_index": p.pocket_index,
                "druggability_score": p.druggability_score,
                "volume_cubic_angstrom": p.volume_cubic_angstrom,
                "surface_area_angstrom2": p.surface_area_angstrom2,
                "key_residues_json": p.key_residues_json,
                "center_coordinates_json": p.center_coordinates_json,
            }
            for p in pockets
        ],
        "created_at": structure.created_at.isoformat(),
    }


@router.get("/structures")
async def list_structures(
    uniprot_id: Optional[str] = Query(None, description="Filter by UniProt ID"),
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List 3D molecular structures with pocket counts and pLDDT scores."""
    repo = MolecularStructureRepository(session)
    structures = await repo.list_structures(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        uniprot_id=uniprot_id,
        limit=limit,
        offset=offset,
    )

    return [
        {
            "id": str(s.id),
            "uniprot_id": s.uniprot_id,
            "gene_name": s.gene_name,
            "organism": s.organism,
            "mean_plddt_score": s.mean_plddt_score,
            "resolution_angstrom": s.resolution_angstrom,
            "structure_source": s.structure_source,
            "binding_pockets_count": len(s.binding_pockets),
            "docking_poses_count": len(s.docking_poses),
            "mutations_count": len(s.mutations),
            "created_at": s.created_at.isoformat(),
        }
        for s in structures
    ]


@router.get("/structures/{structure_id}")
async def get_structure(
    structure_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve full molecular structure with 3D coordinates, pockets, docking poses, and mutations."""
    repo = MolecularStructureRepository(session)
    structure = await repo.get_structure(structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Molecular structure '{structure_id}' not found.",
        )

    return {
        "id": str(structure.id),
        "uniprot_id": structure.uniprot_id,
        "gene_name": structure.gene_name,
        "organism": structure.organism,
        "sequence": structure.sequence,
        "mean_plddt_score": structure.mean_plddt_score,
        "resolution_angstrom": structure.resolution_angstrom,
        "structure_source": structure.structure_source,
        "pdb_coordinate_data": structure.pdb_coordinate_data,
        "secondary_structure_summary": structure.secondary_structure_summary,
        "binding_pockets": [
            {
                "id": str(p.id),
                "pocket_index": p.pocket_index,
                "druggability_score": p.druggability_score,
                "volume_cubic_angstrom": p.volume_cubic_angstrom,
                "surface_area_angstrom2": p.surface_area_angstrom2,
                "key_residues_json": p.key_residues_json,
                "center_coordinates_json": p.center_coordinates_json,
            }
            for p in structure.binding_pockets
        ],
        "docking_poses": [
            {
                "id": str(dp.id),
                "pocket_id": str(dp.pocket_id),
                "ligand_name": dp.ligand_name,
                "binding_affinity_kcal_mol": dp.binding_affinity_kcal_mol,
                "rmsd_angstrom": dp.rmsd_angstrom,
                "hydrogen_bonds_count": dp.hydrogen_bonds_count,
                "pi_stacking_interactions": dp.pi_stacking_interactions,
                "pose_coordinates_json": dp.pose_coordinates_json,
                "created_at": dp.created_at.isoformat(),
            }
            for dp in structure.docking_poses
        ],
        "mutations": [
            {
                "id": str(m.id),
                "wildtype_residue": m.wildtype_residue,
                "position": m.position,
                "mutant_residue": m.mutant_residue,
                "delta_delta_g_kcal_mol": m.delta_delta_g_kcal_mol,
                "stability_verdict": m.stability_verdict,
                "pathogenicity_score": m.pathogenicity_score,
            }
            for m in structure.mutations
        ],
        "created_at": structure.created_at.isoformat(),
    }


@router.post("/structures/{structure_id}/dock")
async def dock_ligand_to_pocket(
    structure_id: uuid.UUID,
    payload: LigandDockRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute in-silico ligand docking against predicted binding pocket."""
    repo = MolecularStructureRepository(session)
    structure = await repo.get_structure(structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Molecular structure '{structure_id}' not found.",
        )

    target_pocket = next((p for p in structure.binding_pockets if p.id == payload.pocket_id), None)
    if not target_pocket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Binding pocket '{payload.pocket_id}' not found in structure.",
        )

    pocket_spec = BindingPocketSpec(
        pocket_index=target_pocket.pocket_index,
        druggability_score=target_pocket.druggability_score,
        volume_cubic_angstrom=target_pocket.volume_cubic_angstrom,
        surface_area_angstrom2=target_pocket.surface_area_angstrom2,
        key_residues_json=target_pocket.key_residues_json,
        center_coordinates_json=target_pocket.center_coordinates_json,
    )

    dock_res = engine.evaluate_docking(
        pocket=pocket_spec,
        ligand_name=payload.ligand_name,
        ligand_smiles=payload.ligand_smiles,
    )

    pose = await repo.add_docking_pose(
        structure_id=structure.id,
        pocket_id=target_pocket.id,
        ligand_name=dock_res.ligand_name,
        binding_affinity_kcal_mol=dock_res.binding_affinity_kcal_mol,
        rmsd_angstrom=dock_res.rmsd_angstrom,
        hydrogen_bonds_count=dock_res.hydrogen_bonds_count,
        pi_stacking_interactions=dock_res.pi_stacking_interactions,
        pose_coordinates_json=dock_res.pose_coordinates_json,
    )

    await session.commit()

    return {
        "id": str(pose.id),
        "structure_id": str(structure.id),
        "pocket_id": str(target_pocket.id),
        "ligand_name": pose.ligand_name,
        "binding_affinity_kcal_mol": pose.binding_affinity_kcal_mol,
        "rmsd_angstrom": pose.rmsd_angstrom,
        "hydrogen_bonds_count": pose.hydrogen_bonds_count,
        "pi_stacking_interactions": pose.pi_stacking_interactions,
        "pose_coordinates_json": pose.pose_coordinates_json,
    }


@router.post("/structures/{structure_id}/mutate")
async def scan_mutation_stability(
    structure_id: uuid.UUID,
    payload: MutateRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute thermodynamic mutational stability scan (Delta Delta G)."""
    repo = MolecularStructureRepository(session)
    structure = await repo.get_structure(structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Molecular structure '{structure_id}' not found.",
        )

    mut_res = engine.scan_mutational_stability(
        wildtype_residue=payload.wildtype_residue,
        position=payload.position,
        mutant_residue=payload.mutant_residue,
    )

    mutation = await repo.add_mutation_stability(
        structure_id=structure.id,
        wildtype_residue=mut_res.wildtype_residue,
        position=mut_res.position,
        mutant_residue=mut_res.mutant_residue,
        delta_delta_g_kcal_mol=mut_res.delta_delta_g_kcal_mol,
        stability_verdict=mut_res.stability_verdict,
        pathogenicity_score=mut_res.pathogenicity_score,
    )

    await session.commit()

    return {
        "id": str(mutation.id),
        "structure_id": str(structure.id),
        "wildtype_residue": mutation.wildtype_residue,
        "position": mutation.position,
        "mutant_residue": mutation.mutant_residue,
        "delta_delta_g_kcal_mol": mutation.delta_delta_g_kcal_mol,
        "stability_verdict": mutation.stability_verdict,
        "pathogenicity_score": mutation.pathogenicity_score,
    }


@router.get("/structures/{structure_id}/export-pdb")
async def export_pdb_file(
    structure_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Download 3D PDB coordinate file."""
    repo = MolecularStructureRepository(session)
    structure = await repo.get_structure(structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Molecular structure '{structure_id}' not found.",
        )

    return Response(
        content=structure.pdb_coordinate_data,
        media_type="chemical/x-pdb",
        headers={"Content-Disposition": f'attachment; filename="{structure.gene_name}_{structure.uniprot_id}.pdb"'},
    )
