"""
Repository for Virtual High-Throughput Screening (vHTS) (Phase 54).
Handles CRUD for vHTS screens, docking hits, and chemical scaffold clusters.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.vhts import (
    DBVirtualHTSScreen,
    DBVirtualHTSHit,
    DBHTSClusterGroup,
)


class VirtualHTSRepository:
    """Repository handling persistence for vHTS campaigns, docking poses, and clusters."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        target_protein_name: str,
        pdb_id: str,
        binding_pocket_box: Optional[Dict[str, Any]] = None,
        library_source: str = "Enamine_REAL_10M",
        total_screened: int = 1000000,
        top_hits_count: int = 0,
        best_affinity: float = 0.0,
    ) -> DBVirtualHTSScreen:
        """Create a new vHTS screen record."""
        screen = DBVirtualHTSScreen(
            target_protein_name=target_protein_name,
            pdb_id=pdb_id,
            binding_pocket_box=binding_pocket_box or {"center": [12.4, -4.2, 28.1], "size": [20.0, 20.0, 20.0]},
            library_source=library_source,
            total_screened_compounds=total_screened,
            top_hits_count=top_hits_count,
            best_affinity_kcal_mol=best_affinity,
            status="COMPLETED",
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def get_screen(self, screen_id: str) -> Optional[DBVirtualHTSScreen]:
        """Fetch screen with hits and clusters loaded."""
        stmt = (
            select(DBVirtualHTSScreen)
            .where(DBVirtualHTSScreen.id == screen_id)
            .options(
                selectinload(DBVirtualHTSScreen.hits),
                selectinload(DBVirtualHTSScreen.clusters),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(self, limit: int = 50) -> List[DBVirtualHTSScreen]:
        """List all vHTS screens."""
        stmt = (
            select(DBVirtualHTSScreen)
            .options(
                selectinload(DBVirtualHTSScreen.hits),
                selectinload(DBVirtualHTSScreen.clusters),
            )
            .order_by(DBVirtualHTSScreen.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_hit(
        self,
        screen_id: str,
        compound_id: str,
        smiles: str,
        docking_score_kcal_mol: float,
        cwas_energy: float = 0.0,
        pains_filter_passed: bool = True,
        rmsd_to_reference: float = 0.0,
        pose_coordinates_json: Optional[Dict[str, Any]] = None,
    ) -> DBVirtualHTSHit:
        """Add a screening hit and update screen metrics."""
        hit = DBVirtualHTSHit(
            screen_id=screen_id,
            compound_id=compound_id,
            smiles=smiles,
            docking_score_kcal_mol=docking_score_kcal_mol,
            cwas_energy=cwas_energy,
            pains_filter_passed=pains_filter_passed,
            rmsd_to_reference=rmsd_to_reference,
            pose_coordinates_json=pose_coordinates_json or {},
        )
        self.session.add(hit)

        # Update screen best affinity
        screen = await self.get_screen(screen_id)
        if screen:
            screen.top_hits_count += 1
            if screen.best_affinity_kcal_mol == 0.0 or docking_score_kcal_mol < screen.best_affinity_kcal_mol:
                screen.best_affinity_kcal_mol = docking_score_kcal_mol

        await self.session.commit()
        await self.session.refresh(hit)
        return hit

    async def list_hits(self, screen_id: str, limit: int = 100) -> List[DBVirtualHTSHit]:
        """List hits for a screen ordered by binding energy (best first)."""
        stmt = (
            select(DBVirtualHTSHit)
            .where(DBVirtualHTSHit.screen_id == screen_id)
            .order_by(DBVirtualHTSHit.docking_score_kcal_mol.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_cluster(
        self,
        screen_id: str,
        cluster_label: str,
        scaffold_smiles: str,
        member_hits_count: int,
        mean_affinity_kcal_mol: float,
    ) -> DBHTSClusterGroup:
        """Add a chemical scaffold cluster."""
        cluster = DBHTSClusterGroup(
            screen_id=screen_id,
            cluster_label=cluster_label,
            scaffold_smiles=scaffold_smiles,
            member_hits_count=member_hits_count,
            mean_affinity_kcal_mol=mean_affinity_kcal_mol,
        )
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def list_clusters(self, screen_id: str) -> List[DBHTSClusterGroup]:
        """List scaffold clusters for a screen."""
        stmt = (
            select(DBHTSClusterGroup)
            .where(DBHTSClusterGroup.screen_id == screen_id)
            .order_by(DBHTSClusterGroup.mean_affinity_kcal_mol.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_metrics(self) -> Dict[str, Any]:
        """Get aggregate statistics for vHTS pipeline."""
        total_scr = (await self.session.execute(select(func.count(DBVirtualHTSScreen.id)))).scalar() or 0
        total_compounds = (await self.session.execute(select(func.sum(DBVirtualHTSScreen.total_screened_compounds)))).scalar() or 0
        total_hits = (await self.session.execute(select(func.count(DBVirtualHTSHit.id)))).scalar() or 0
        best_overall = (await self.session.execute(select(func.min(DBVirtualHTSScreen.best_affinity_kcal_mol)))).scalar() or 0.0

        return {
            "total_screens": total_scr,
            "total_screened_compounds": int(total_compounds),
            "total_hits_discovered": total_hits,
            "best_affinity_kcal_mol": best_overall,
            "gpu_acceleration": "AutoDock Vina GPU & GNINA 1.3 Active",
        }
