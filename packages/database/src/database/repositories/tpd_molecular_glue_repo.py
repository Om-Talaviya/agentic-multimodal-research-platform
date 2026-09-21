"""TPD Repo (Phase 121)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.tpd_molecular_glue import DBMolecularGlueScreen, DBTernaryComplexAffinity

class MolecularGlueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_screen(self, workspace_id: uuid.UUID, e3_ligase_name: str,
                            target_neo_substrate: str, screen_campaign_name: str,
                            total_screened_glues: int, top_glue_candidate: str) -> DBMolecularGlueScreen:
        s = DBMolecularGlueScreen(
            workspace_id=workspace_id,
            e3_ligase_name=e3_ligase_name,
            target_neo_substrate=target_neo_substrate,
            screen_campaign_name=screen_campaign_name,
            total_screened_glues=total_screened_glues,
            top_glue_candidate=top_glue_candidate,
        )
        self.db.add(s)
        await self.db.commit()
        await self.db.refresh(s)
        return s

    async def add_ternary_affinity(self, screen_id: uuid.UUID, glue_molecule_smiles: str,
                                   cooperativity_factor_alpha: float, ternary_kd_apparent_nm: float,
                                   dc50_degradation_potency_nm: float) -> DBTernaryComplexAffinity:
        t = DBTernaryComplexAffinity(
            screen_id=screen_id,
            glue_molecule_smiles=glue_molecule_smiles,
            cooperativity_factor_alpha=cooperativity_factor_alpha,
            ternary_kd_apparent_nm=ternary_kd_apparent_nm,
            dc50_degradation_potency_nm=dc50_degradation_potency_nm,
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        return t

    async def get_screen(self, screen_id: uuid.UUID) -> Optional[DBMolecularGlueScreen]:
        res = await self.db.execute(select(DBMolecularGlueScreen).where(DBMolecularGlueScreen.id == screen_id))
        return res.scalar_one_or_none()
