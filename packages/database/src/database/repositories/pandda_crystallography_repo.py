"""
Phase 129: Autonomous High-Throughput Crystallography Fragment Screening & PanDDA Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.pandda_crystallography import (
    DBCrystallographyFragmentScreen,
    DBFragmentHit,
    DBPanDDABackgroundDensityMap,
)


class PanDDACrystallographyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        campaign_name: str,
        target_protein: str,
        crystal_space_group: str = "P 21 21 21",
        high_resolution_cutoff_angstrom: float = 1.45,
        total_crystals_soaked: int = 320,
        pandda_events_detected: int = 14,
        background_model_r_free: float = 0.185,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBCrystallographyFragmentScreen:
        screen = DBCrystallographyFragmentScreen(
            id=uuid.uuid4(),
            project_id=project_id,
            campaign_name=campaign_name,
            target_protein=target_protein,
            crystal_space_group=crystal_space_group,
            high_resolution_cutoff_angstrom=high_resolution_cutoff_angstrom,
            total_crystals_soaked=total_crystals_soaked,
            pandda_events_detected=pandda_events_detected,
            background_model_r_free=background_model_r_free,
            metadata_json=metadata_json or {},
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def get_screen(self, screen_id: uuid.UUID) -> Optional[DBCrystallographyFragmentScreen]:
        stmt = (
            select(DBCrystallographyFragmentScreen)
            .options(
                selectinload(DBCrystallographyFragmentScreen.hits),
                selectinload(DBCrystallographyFragmentScreen.density_maps),
            )
            .where(DBCrystallographyFragmentScreen.id == screen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(self, limit: int = 50) -> List[DBCrystallographyFragmentScreen]:
        stmt = (
            select(DBCrystallographyFragmentScreen)
            .options(
                selectinload(DBCrystallographyFragmentScreen.hits),
                selectinload(DBCrystallographyFragmentScreen.density_maps),
            )
            .order_by(desc(DBCrystallographyFragmentScreen.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_fragment_hit(
        self,
        screen_id: uuid.UUID,
        hit_id: str,
        fragment_smiles: str,
        binding_site_name: str,
        event_b_factor: float = 24.5,
        event_occupancy: float = 0.78,
        z_peak_score: float = 6.45,
        ligand_efficiency_le: float = 0.48,
    ) -> DBFragmentHit:
        hit = DBFragmentHit(
            id=uuid.uuid4(),
            screen_id=screen_id,
            hit_id=hit_id,
            fragment_smiles=fragment_smiles,
            binding_site_name=binding_site_name,
            event_b_factor=event_b_factor,
            event_occupancy=event_occupancy,
            z_peak_score=z_peak_score,
            ligand_efficiency_le=ligand_efficiency_le,
        )
        self.session.add(hit)
        await self.session.commit()
        await self.session.refresh(hit)
        return hit

    async def add_density_map(
        self,
        screen_id: uuid.UUID,
        map_id: str,
        resolution_angstrom: float = 1.45,
        statistical_outlier_noise_sigma: float = 0.12,
        mean_density_value: float = 0.98,
    ) -> DBPanDDABackgroundDensityMap:
        dmap = DBPanDDABackgroundDensityMap(
            id=uuid.uuid4(),
            screen_id=screen_id,
            map_id=map_id,
            resolution_angstrom=resolution_angstrom,
            statistical_outlier_noise_sigma=statistical_outlier_noise_sigma,
            mean_density_value=mean_density_value,
        )
        self.session.add(dmap)
        await self.session.commit()
        await self.session.refresh(dmap)
        return dmap
