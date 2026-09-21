"""Spatial MSI Repo (Phase 116)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.spatial_metabolite_imaging import DBSpatialMSISample, DBTissueMetaboliteGradient

class SpatialMSIRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sample(self, workspace_id: uuid.UUID, tissue_section_name: str,
                            msi_modality: str, spatial_resolution_microns: float,
                            total_mz_features: int, warburg_lactate_gradient_ratio: float) -> DBSpatialMSISample:
        sample = DBSpatialMSISample(
            workspace_id=workspace_id,
            tissue_section_name=tissue_section_name,
            msi_modality=msi_modality,
            spatial_resolution_microns=spatial_resolution_microns,
            total_mz_features=total_mz_features,
            warburg_lactate_gradient_ratio=warburg_lactate_gradient_ratio,
        )
        self.db.add(sample)
        await self.db.commit()
        await self.db.refresh(sample)
        return sample

    async def add_gradient(self, msi_sample_id: uuid.UUID, metabolite_name: str,
                           mz_ratio: float, tumor_core_intensity: float,
                           stromal_border_intensity: float, core_to_border_ratio: float) -> DBTissueMetaboliteGradient:
        g = DBTissueMetaboliteGradient(
            msi_sample_id=msi_sample_id,
            metabolite_name=metabolite_name,
            mz_ratio=mz_ratio,
            tumor_core_intensity=tumor_core_intensity,
            stromal_border_intensity=stromal_border_intensity,
            core_to_border_ratio=core_to_border_ratio,
        )
        self.db.add(g)
        await self.db.commit()
        await self.db.refresh(g)
        return g

    async def get_sample(self, sample_id: uuid.UUID) -> Optional[DBSpatialMSISample]:
        res = await self.db.execute(select(DBSpatialMSISample).where(DBSpatialMSISample.id == sample_id))
        return res.scalar_one_or_none()
