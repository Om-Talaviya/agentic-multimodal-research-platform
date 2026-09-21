"""DDR Repo (Phase 119)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.ddr_pathways import DBDDRPathwayProfile, DBSyntheticViabilityInteraction

class DDRPathwayRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(self, workspace_id: uuid.UUID, cancer_type: str,
                             primary_ddr_defect: str, hrd_genomic_scar_score: float,
                             replication_stress_index: float) -> DBDDRPathwayProfile:
        p = DBDDRPathwayProfile(
            workspace_id=workspace_id,
            cancer_type=cancer_type,
            primary_ddr_defect=primary_ddr_defect,
            hrd_genomic_scar_score=hrd_genomic_scar_score,
            replication_stress_index=replication_stress_index,
        )
        self.db.add(p)
        await self.db.commit()
        await self.db.refresh(p)
        return p

    async def add_interaction(self, ddr_profile_id: uuid.UUID, therapeutic_target_gene: str,
                              synthetic_lethal_potency_score: float,
                              recommended_inhibitor_class: str) -> DBSyntheticViabilityInteraction:
        i = DBSyntheticViabilityInteraction(
            ddr_profile_id=ddr_profile_id,
            therapeutic_target_gene=therapeutic_target_gene,
            synthetic_lethal_potency_score=synthetic_lethal_potency_score,
            recommended_inhibitor_class=recommended_inhibitor_class,
        )
        self.db.add(i)
        await self.db.commit()
        await self.db.refresh(i)
        return i

    async def get_profile(self, profile_id: uuid.UUID) -> Optional[DBDDRPathwayProfile]:
        res = await self.db.execute(select(DBDDRPathwayProfile).where(DBDDRPathwayProfile.id == profile_id))
        return res.scalar_one_or_none()
