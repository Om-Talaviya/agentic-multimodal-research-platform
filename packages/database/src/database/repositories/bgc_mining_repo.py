"""BGC Repo (Phase 123)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.bgc_mining import DBMicrobialBGCGenome, DBBiosyntheticClusterCluster

class BGCRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_genome(self, workspace_id: uuid.UUID, organism_species_name: str,
                            genome_size_mbp: float, total_detected_bgcs: int,
                            novel_scaffold_fraction: float) -> DBMicrobialBGCGenome:
        g = DBMicrobialBGCGenome(
            workspace_id=workspace_id,
            organism_species_name=organism_species_name,
            genome_size_mbp=genome_size_mbp,
            total_detected_bgcs=total_detected_bgcs,
            novel_scaffold_fraction=novel_scaffold_fraction,
        )
        self.db.add(g)
        await self.db.commit()
        await self.db.refresh(g)
        return g

    async def add_cluster(self, genome_id: uuid.UUID, bgc_type: str,
                          core_synthetase_genes: str, predicted_chemical_class: str,
                          mibiig_known_homology_pct: float) -> DBBiosyntheticClusterCluster:
        c = DBBiosyntheticClusterCluster(
            genome_id=genome_id,
            bgc_type=bgc_type,
            core_synthetase_genes=core_synthetase_genes,
            predicted_chemical_class=predicted_chemical_class,
            mibiig_known_homology_pct=mibiig_known_homology_pct,
        )
        self.db.add(c)
        await self.db.commit()
        await self.db.refresh(c)
        return c

    async def get_genome(self, genome_id: uuid.UUID) -> Optional[DBMicrobialBGCGenome]:
        res = await self.db.execute(select(DBMicrobialBGCGenome).where(DBMicrobialBGCGenome.id == genome_id))
        return res.scalar_one_or_none()
