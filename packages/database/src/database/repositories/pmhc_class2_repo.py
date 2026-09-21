"""MHC Class II Repo (Phase 118)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.pmhc_class2 import DBMHCClass2Screen, DBCD4NeoepitopeHit

class MHCClass2Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_screen(self, workspace_id: uuid.UUID, hla_class2_allele: str,
                            source_protein_antigen: str, total_screened_15mers: int,
                            immunogenic_hits_count: int) -> DBMHCClass2Screen:
        s = DBMHCClass2Screen(
            workspace_id=workspace_id,
            hla_class2_allele=hla_class2_allele,
            source_protein_antigen=source_protein_antigen,
            total_screened_15mers=total_screened_15mers,
            immunogenic_hits_count=immunogenic_hits_count,
        )
        self.db.add(s)
        await self.db.commit()
        await self.db.refresh(s)
        return s

    async def add_neoepitope(self, screen_id: uuid.UUID, peptide_15mer_sequence: str,
                            core_9mer_binding_motif: str, binding_affinity_ic50_nm: float,
                            cd4_immunogenicity_tier: str) -> DBCD4NeoepitopeHit:
        h = DBCD4NeoepitopeHit(
            screen_id=screen_id,
            peptide_15mer_sequence=peptide_15mer_sequence,
            core_9mer_binding_motif=core_9mer_binding_motif,
            binding_affinity_ic50_nm=binding_affinity_ic50_nm,
            cd4_immunogenicity_tier=cd4_immunogenicity_tier,
        )
        self.db.add(h)
        await self.db.commit()
        await self.db.refresh(h)
        return h

    async def get_screen(self, screen_id: uuid.UUID) -> Optional[DBMHCClass2Screen]:
        res = await self.db.execute(select(DBMHCClass2Screen).where(DBMHCClass2Screen.id == screen_id))
        return res.scalar_one_or_none()
