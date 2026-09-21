"""Multiome Repo (Phase 120)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.multiome_joint import DBSingleCellMultiomeDataset, DBCisRegulatoryLinkage

class MultiomeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dataset(self, workspace_id: uuid.UUID, sample_identifier: str,
                             total_joint_cells: int, wnn_modality_weight_rna: float,
                             wnn_modality_weight_atac: float) -> DBSingleCellMultiomeDataset:
        d = DBSingleCellMultiomeDataset(
            workspace_id=workspace_id,
            sample_identifier=sample_identifier,
            total_joint_cells=total_joint_cells,
            wnn_modality_weight_rna=wnn_modality_weight_rna,
            wnn_modality_weight_atac=wnn_modality_weight_atac,
        )
        self.db.add(d)
        await self.db.commit()
        await self.db.refresh(d)
        return d

    async def add_linkage(self, dataset_id: uuid.UUID, target_gene: str,
                         accessible_peak_locus: str, peak_to_gene_correlation: float,
                         binding_transcription_factor: str) -> DBCisRegulatoryLinkage:
        l = DBCisRegulatoryLinkage(
            dataset_id=dataset_id,
            target_gene=target_gene,
            accessible_peak_locus=accessible_peak_locus,
            peak_to_gene_correlation=peak_to_gene_correlation,
            binding_transcription_factor=binding_transcription_factor,
        )
        self.db.add(l)
        await self.db.commit()
        await self.db.refresh(l)
        return l

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[DBSingleCellMultiomeDataset]:
        res = await self.db.execute(select(DBSingleCellMultiomeDataset).where(DBSingleCellMultiomeDataset.id == dataset_id))
        return res.scalar_one_or_none()
