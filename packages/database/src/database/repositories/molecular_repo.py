"""Autonomous Bio-Molecular Structure & Protein Folding Repository (Phase 38)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.molecular import (
    DBBindingPocket,
    DBDockingPose,
    DBMolecularStructure,
    DBMutationStability,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class MolecularStructureRepository:
    """Async repository for 3D molecular structures, binding pockets, docking poses, and mutational stability scans."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_structure(
        self,
        user_id: uuid.UUID | str,
        uniprot_id: str,
        gene_name: str,
        sequence: str,
        pdb_coordinate_data: str,
        mean_plddt_score: float = 88.5,
        resolution_angstrom: Optional[float] = 1.85,
        structure_source: str = "AlphaFold3",
        organism: str = "Homo sapiens",
        secondary_structure_summary: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
    ) -> DBMolecularStructure:
        """Create and persist a new 3D bio-molecular structure specification."""
        structure = DBMolecularStructure(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            uniprot_id=uniprot_id.upper(),
            gene_name=gene_name,
            organism=organism,
            sequence=sequence,
            mean_plddt_score=mean_plddt_score,
            resolution_angstrom=resolution_angstrom,
            structure_source=structure_source,
            pdb_coordinate_data=pdb_coordinate_data,
            secondary_structure_summary=secondary_structure_summary or {},
        )
        self._session.add(structure)
        await self._session.flush()
        logger.info(
            "molecular_structure_created",
            structure_id=str(structure.id),
            uniprot_id=uniprot_id,
            gene=gene_name,
            plddt=mean_plddt_score,
        )
        return structure

    async def get_structure(self, structure_id: uuid.UUID | str) -> Optional[DBMolecularStructure]:
        """Fetch a molecular structure by ID with all binding pockets, docking poses, and mutations."""
        stmt = (
            select(DBMolecularStructure)
            .where(DBMolecularStructure.id == structure_id)
            .options(
                selectinload(DBMolecularStructure.binding_pockets),
                selectinload(DBMolecularStructure.docking_poses),
                selectinload(DBMolecularStructure.mutations),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_structures(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        uniprot_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBMolecularStructure]:
        """List molecular structures filtered by user, workspace, project, or UniProt ID."""
        stmt = (
            select(DBMolecularStructure)
            .options(
                selectinload(DBMolecularStructure.binding_pockets),
                selectinload(DBMolecularStructure.docking_poses),
                selectinload(DBMolecularStructure.mutations),
            )
            .order_by(desc(DBMolecularStructure.created_at))
            .limit(limit)
            .offset(offset)
        )

        if project_id:
            stmt = stmt.where(DBMolecularStructure.project_id == project_id)
        elif workspace_id:
            stmt = stmt.where(DBMolecularStructure.workspace_id == workspace_id)
        elif user_id:
            stmt = stmt.where(DBMolecularStructure.user_id == user_id)

        if uniprot_id:
            stmt = stmt.where(DBMolecularStructure.uniprot_id == uniprot_id.upper())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_binding_pocket(
        self,
        structure_id: uuid.UUID | str,
        pocket_index: int,
        druggability_score: float = 0.82,
        volume_cubic_angstrom: float = 650.0,
        surface_area_angstrom2: float = 420.0,
        key_residues_json: Optional[List[str]] = None,
        center_coordinates_json: Optional[Dict[str, float]] = None,
    ) -> DBBindingPocket:
        """Add a single predicted binding pocket to a structure."""
        pocket = DBBindingPocket(
            id=uuid.uuid4(),
            structure_id=structure_id,
            pocket_index=pocket_index,
            druggability_score=druggability_score,
            volume_cubic_angstrom=volume_cubic_angstrom,
            surface_area_angstrom2=surface_area_angstrom2,
            key_residues_json=key_residues_json or [],
            center_coordinates_json=center_coordinates_json or {},
        )
        self._session.add(pocket)
        await self._session.flush()
        return pocket

    async def add_binding_pockets(
        self,
        structure_id: uuid.UUID | str,
        pockets_data: List[Dict[str, Any]],
    ) -> List[DBBindingPocket]:
        """Batch add predicted binding pockets to a structure."""
        created = []
        for p in pockets_data:
            pocket = DBBindingPocket(
                id=uuid.uuid4(),
                structure_id=structure_id,
                pocket_index=int(p.get("pocket_index", len(created) + 1)),
                druggability_score=float(p.get("druggability_score", 0.82)),
                volume_cubic_angstrom=float(p.get("volume_cubic_angstrom", 650.0)),
                surface_area_angstrom2=float(p.get("surface_area_angstrom2", 420.0)),
                key_residues_json=p.get("key_residues_json", []),
                center_coordinates_json=p.get("center_coordinates_json", {}),
            )
            self._session.add(pocket)
            created.append(pocket)
        await self._session.flush()
        return created

    async def add_docking_pose(
        self,
        structure_id: uuid.UUID | str,
        pocket_id: uuid.UUID | str,
        ligand_name: str,
        binding_affinity_kcal_mol: float,
        rmsd_angstrom: float = 1.0,
        hydrogen_bonds_count: int = 4,
        pi_stacking_interactions: int = 2,
        pose_coordinates_json: Optional[Dict[str, Any]] = None,
    ) -> DBDockingPose:
        """Add a ligand docking pose within a predicted binding pocket."""
        pose = DBDockingPose(
            id=uuid.uuid4(),
            structure_id=structure_id,
            pocket_id=pocket_id,
            ligand_name=ligand_name,
            binding_affinity_kcal_mol=binding_affinity_kcal_mol,
            rmsd_angstrom=rmsd_angstrom,
            hydrogen_bonds_count=hydrogen_bonds_count,
            pi_stacking_interactions=pi_stacking_interactions,
            pose_coordinates_json=pose_coordinates_json or {},
        )
        self._session.add(pose)
        await self._session.flush()
        logger.info(
            "docking_pose_added",
            structure_id=str(structure_id),
            ligand=ligand_name,
            affinity=binding_affinity_kcal_mol,
        )
        return pose

    async def add_mutation_stability(
        self,
        structure_id: uuid.UUID | str,
        wildtype_residue: str,
        position: int,
        mutant_residue: str,
        delta_delta_g_kcal_mol: float,
        stability_verdict: str = "stabilizing",
        pathogenicity_score: float = 0.5,
    ) -> DBMutationStability:
        """Add a single mutational stability scan result."""
        mutation = DBMutationStability(
            id=uuid.uuid4(),
            structure_id=structure_id,
            wildtype_residue=wildtype_residue.upper(),
            position=position,
            mutant_residue=mutant_residue.upper(),
            delta_delta_g_kcal_mol=delta_delta_g_kcal_mol,
            stability_verdict=stability_verdict,
            pathogenicity_score=pathogenicity_score,
        )
        self._session.add(mutation)
        await self._session.flush()
        return mutation

    async def add_mutation_stabilities(
        self,
        structure_id: uuid.UUID | str,
        mutations_data: List[Dict[str, Any]],
    ) -> List[DBMutationStability]:
        """Batch add mutational stability scan results."""
        created = []
        for m in mutations_data:
            mutation = DBMutationStability(
                id=uuid.uuid4(),
                structure_id=structure_id,
                wildtype_residue=str(m["wildtype_residue"]).upper(),
                position=int(m["position"]),
                mutant_residue=str(m["mutant_residue"]).upper(),
                delta_delta_g_kcal_mol=float(m["delta_delta_g_kcal_mol"]),
                stability_verdict=str(m.get("stability_verdict", "neutral")),
                pathogenicity_score=float(m.get("pathogenicity_score", 0.5)),
            )
            self._session.add(mutation)
            created.append(mutation)
        await self._session.flush()
        return created
