"""CTC Repo (Phase 111)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.ctc_metastasis import DBCirculatingTumorCellSample, DBMetastaticColonizationSite

class CTCRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sample(self, workspace_id: uuid.UUID, patient_id: str, primary_tumor_type: str,
                            ctc_enumeration_per_7_5ml: int, emt_hybrid_score: float,
                            metastatic_tropism_primary: str, capture_technology: str = "Microfluidic Vortex Chip") -> DBCirculatingTumorCellSample:
        sample = DBCirculatingTumorCellSample(
            workspace_id=workspace_id,
            patient_id=patient_id,
            primary_tumor_type=primary_tumor_type,
            ctc_enumeration_per_7_5ml=ctc_enumeration_per_7_5ml,
            emt_hybrid_score=emt_hybrid_score,
            metastatic_tropism_primary=metastatic_tropism_primary,
            capture_technology=capture_technology,
        )
        self.db.add(sample)
        await self.db.commit()
        await self.db.refresh(sample)
        return sample

    async def add_colonization_site(self, ctc_sample_id: uuid.UUID, target_organ: str,
                                   colonization_probability: float, seed_soil_compatibility_score: float,
                                   chemokine_gradient_strength: float) -> DBMetastaticColonizationSite:
        site = DBMetastaticColonizationSite(
            ctc_sample_id=ctc_sample_id,
            target_organ=target_organ,
            colonization_probability=colonization_probability,
            seed_soil_compatibility_score=seed_soil_compatibility_score,
            chemokine_gradient_strength=chemokine_gradient_strength,
        )
        self.db.add(site)
        await self.db.commit()
        await self.db.refresh(site)
        return site

    async def get_sample(self, sample_id: uuid.UUID) -> Optional[DBCirculatingTumorCellSample]:
        res = await self.db.execute(select(DBCirculatingTumorCellSample).where(DBCirculatingTumorCellSample.id == sample_id))
        return res.scalar_one_or_none()
