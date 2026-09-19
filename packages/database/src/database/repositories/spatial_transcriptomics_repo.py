"""Repository for Spatial Transcriptomics & TME Deconvolution data access."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.spatial_transcriptomics import (
    DBSpatialTranscriptomicsSlice,
    DBCellTypeProportion,
    DBSpatialLigandReceptor,
)


class SpatialTranscriptomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_slice(
        self,
        workspace_id: uuid.UUID,
        sample_name: str,
        tissue_type: str,
        platform: str = "10x Visium HD",
        total_spots: int = 4992,
        median_genes_per_spot: float = 3200.0,
        deconvolution_algorithm: str = "Spatial-Bayes-Deconv",
        spatial_entropy_score: float = 0.74,
        analysis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBSpatialTranscriptomicsSlice:
        slice_obj = DBSpatialTranscriptomicsSlice(
            workspace_id=workspace_id,
            sample_name=sample_name,
            tissue_type=tissue_type,
            platform=platform,
            total_spots=total_spots,
            median_genes_per_spot=median_genes_per_spot,
            deconvolution_algorithm=deconvolution_algorithm,
            spatial_entropy_score=spatial_entropy_score,
            analysis_metadata=analysis_metadata or {},
        )
        self.session.add(slice_obj)
        await self.session.commit()
        await self.session.refresh(slice_obj)
        return slice_obj

    async def add_cell_proportion(
        self,
        slice_id: uuid.UUID,
        cell_type: str,
        mean_abundance_fraction: float,
        spatial_enrichment_zone: str = "Tumor Core",
        marker_genes: Optional[List[str]] = None,
    ) -> DBCellTypeProportion:
        prop = DBCellTypeProportion(
            slice_id=slice_id,
            cell_type=cell_type,
            mean_abundance_fraction=mean_abundance_fraction,
            spatial_enrichment_zone=spatial_enrichment_zone,
            marker_genes=marker_genes or [],
        )
        self.session.add(prop)
        await self.session.commit()
        await self.session.refresh(prop)
        return prop

    async def add_ligand_receptor(
        self,
        slice_id: uuid.UUID,
        ligand_gene: str,
        receptor_gene: str,
        sender_cell_type: str,
        receiver_cell_type: str,
        communication_score: float = 0.85,
        p_value: float = 0.001,
        spatial_colocalization_score: float = 0.78,
    ) -> DBSpatialLigandReceptor:
        lr = DBSpatialLigandReceptor(
            slice_id=slice_id,
            ligand_gene=ligand_gene,
            receptor_gene=receptor_gene,
            sender_cell_type=sender_cell_type,
            receiver_cell_type=receiver_cell_type,
            communication_score=communication_score,
            p_value=p_value,
            spatial_colocalization_score=spatial_colocalization_score,
        )
        self.session.add(lr)
        await self.session.commit()
        await self.session.refresh(lr)
        return lr

    async def get_slice(self, slice_id: uuid.UUID) -> Optional[DBSpatialTranscriptomicsSlice]:
        stmt = (
            select(DBSpatialTranscriptomicsSlice)
            .options(
                selectinload(DBSpatialTranscriptomicsSlice.cell_proportions),
                selectinload(DBSpatialTranscriptomicsSlice.ligand_receptors),
            )
            .where(DBSpatialTranscriptomicsSlice.id == slice_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_slices_by_workspace(
        self, workspace_id: uuid.UUID
    ) -> List[DBSpatialTranscriptomicsSlice]:
        stmt = (
            select(DBSpatialTranscriptomicsSlice)
            .options(
                selectinload(DBSpatialTranscriptomicsSlice.cell_proportions),
                selectinload(DBSpatialTranscriptomicsSlice.ligand_receptors),
            )
            .where(DBSpatialTranscriptomicsSlice.workspace_id == workspace_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
