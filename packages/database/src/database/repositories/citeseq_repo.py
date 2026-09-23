"""
Phase 128: Autonomous Single-Cell Spatial CITE-seq Multi-Modal Surface Protein & mRNA Co-Mapping Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.citeseq import (
    DBCITEseqDataset,
    DBAntibodyDerivedTag,
    DBCellSurfaceProteinExpression,
)


class CITEseqRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(
        self,
        sample_name: str,
        tissue_origin: str = "Tumor-Infiltrating Lymphocytes",
        total_cells_profiled: int = 14500,
        adt_panel_size: int = 54,
        rna_features_count: int = 24500,
        dsb_background_ambient_mean: float = 1.85,
        wNN_modality_weight_protein: float = 0.58,
        wNN_modality_weight_rna: float = 0.42,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBCITEseqDataset:
        dataset = DBCITEseqDataset(
            id=uuid.uuid4(),
            project_id=project_id,
            sample_name=sample_name,
            tissue_origin=tissue_origin,
            total_cells_profiled=total_cells_profiled,
            adt_panel_size=adt_panel_size,
            rna_features_count=rna_features_count,
            dsb_background_ambient_mean=dsb_background_ambient_mean,
            wNN_modality_weight_protein=wNN_modality_weight_protein,
            wNN_modality_weight_rna=wNN_modality_weight_rna,
            metadata_json=metadata_json or {},
        )
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[DBCITEseqDataset]:
        stmt = (
            select(DBCITEseqDataset)
            .options(
                selectinload(DBCITEseqDataset.antibodies),
                selectinload(DBCITEseqDataset.expressions),
            )
            .where(DBCITEseqDataset.id == dataset_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datasets(self, limit: int = 50) -> List[DBCITEseqDataset]:
        stmt = (
            select(DBCITEseqDataset)
            .options(
                selectinload(DBCITEseqDataset.antibodies),
                selectinload(DBCITEseqDataset.expressions),
            )
            .order_by(desc(DBCITEseqDataset.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_antibody_tag(
        self,
        dataset_id: uuid.UUID,
        tag_barcode: str,
        marker_name: str,
        clone_id: str,
        isotype_control: str = "IgG1-k",
        signal_to_noise_ratio: float = 14.8,
    ) -> DBAntibodyDerivedTag:
        tag = DBAntibodyDerivedTag(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            tag_barcode=tag_barcode,
            marker_name=marker_name,
            clone_id=clone_id,
            isotype_control=isotype_control,
            signal_to_noise_ratio=signal_to_noise_ratio,
        )
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def add_protein_expression(
        self,
        dataset_id: uuid.UUID,
        cell_cluster_id: str,
        marker_name: str,
        dsb_normalized_expression: float = 4.82,
        corresponding_rna_tpm: float = 128.4,
        concordance_spearman_rho: float = 0.78,
        discordance_pvalue: float = 0.0001,
    ) -> DBCellSurfaceProteinExpression:
        exp = DBCellSurfaceProteinExpression(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            cell_cluster_id=cell_cluster_id,
            marker_name=marker_name,
            dsb_normalized_expression=dsb_normalized_expression,
            corresponding_rna_tpm=corresponding_rna_tpm,
            concordance_spearman_rho=concordance_spearman_rho,
            discordance_pvalue=discordance_pvalue,
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp
