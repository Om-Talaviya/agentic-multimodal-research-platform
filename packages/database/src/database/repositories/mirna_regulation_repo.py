"""miRNA Repo (Phase 115)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.mirna_regulation import DBMiRNARegulatoryNetwork, DBMiRNATargetRepression

class MiRNARepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_network(self, workspace_id: uuid.UUID, mirna_id: str, seed_sequence: str,
                             disease_context: str, total_predicted_targets: int,
                             network_density: float) -> DBMiRNARegulatoryNetwork:
        net = DBMiRNARegulatoryNetwork(
            workspace_id=workspace_id,
            mirna_id=mirna_id,
            seed_sequence=seed_sequence,
            disease_context=disease_context,
            total_predicted_targets=total_predicted_targets,
            network_density=network_density,
        )
        self.db.add(net)
        await self.db.commit()
        await self.db.refresh(net)
        return net

    async def add_target(self, network_id: uuid.UUID, target_gene: str, seed_match_type: str,
                         binding_free_energy_kcal_mol: float, predicted_repression_fold: float) -> DBMiRNATargetRepression:
        t = DBMiRNATargetRepression(
            network_id=network_id,
            target_gene=target_gene,
            seed_match_type=seed_match_type,
            binding_free_energy_kcal_mol=binding_free_energy_kcal_mol,
            predicted_repression_fold=predicted_repression_fold,
        )
        self.db.add(t)
        await self.db.commit()
        await self.db.refresh(t)
        return t

    async def get_network(self, network_id: uuid.UUID) -> Optional[DBMiRNARegulatoryNetwork]:
        res = await self.db.execute(select(DBMiRNARegulatoryNetwork).where(DBMiRNARegulatoryNetwork.id == network_id))
        return res.scalar_one_or_none()
