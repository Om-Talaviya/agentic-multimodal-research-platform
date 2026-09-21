"""Histone Repo (Phase 112)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.histone_epigenetics import DBHistoneChIPSample, DBSuperEnhancerLocus

class HistoneEpigeneticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sample(self, workspace_id: uuid.UUID, sample_name: str, histone_mark: str,
                            cell_line_or_tissue: str, total_aligned_peaks: int,
                            super_enhancer_count: int, frip_score: float) -> DBHistoneChIPSample:
        sample = DBHistoneChIPSample(
            workspace_id=workspace_id,
            sample_name=sample_name,
            histone_mark=histone_mark,
            cell_line_or_tissue=cell_line_or_tissue,
            total_aligned_peaks=total_aligned_peaks,
            super_enhancer_count=super_enhancer_count,
            frip_score=frip_score,
        )
        self.db.add(sample)
        await self.db.commit()
        await self.db.refresh(sample)
        return sample

    async def add_super_enhancer(self, chip_sample_id: uuid.UUID, locus_coordinates: str,
                                 associated_oncogene: str, rose_ranking_score: float,
                                 signal_intensity_rpm: float) -> DBSuperEnhancerLocus:
        locus = DBSuperEnhancerLocus(
            chip_sample_id=chip_sample_id,
            locus_coordinates=locus_coordinates,
            associated_oncogene=associated_oncogene,
            rose_ranking_score=rose_ranking_score,
            signal_intensity_rpm=signal_intensity_rpm,
        )
        self.db.add(locus)
        await self.db.commit()
        await self.db.refresh(locus)
        return locus

    async def get_sample(self, sample_id: uuid.UUID) -> Optional[DBHistoneChIPSample]:
        res = await self.db.execute(select(DBHistoneChIPSample).where(DBHistoneChIPSample.id == sample_id))
        return res.scalar_one_or_none()
