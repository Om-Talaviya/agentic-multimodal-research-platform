"""
Repository for Cryo-EM Density Map Fitting & Macromolecular Complexes.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.cryoem import DBCryoEMDensityMap, DBDensityMapFitting, DBMacromolecularComplex

class CryoEMRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_density_map(
        self,
        title: str,
        emdb_id: str = "EMD-30452",
        nominal_resolution: float = 2.4,
        voxel_size: float = 0.82,
        box_dimensions: str = "256x256x256",
        contour_level: float = 0.035,
        fsc_resolution: float = 2.35,
        fsc_curve_data: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> DBCryoEMDensityMap:
        density_map = DBCryoEMDensityMap(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            emdb_id=emdb_id,
            nominal_resolution_angstrom=nominal_resolution,
            voxel_size_angstrom=voxel_size,
            box_dimensions=box_dimensions,
            contour_level=contour_level,
            fsc_resolution_threshold=fsc_resolution,
            fsc_curve_data=fsc_curve_data or [],
            status="FITTED"
        )
        self.session.add(density_map)
        await self.session.commit()
        await self.session.refresh(density_map)
        return density_map

    async def get_density_map(self, map_id: uuid.UUID) -> Optional[DBCryoEMDensityMap]:
        query = (
            select(DBCryoEMDensityMap)
            .options(
                selectinload(DBCryoEMDensityMap.fittings),
                selectinload(DBCryoEMDensityMap.complexes)
            )
            .where(DBCryoEMDensityMap.id == map_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_density_maps(self, limit: int = 50) -> List[DBCryoEMDensityMap]:
        query = select(DBCryoEMDensityMap).order_by(DBCryoEMDensityMap.created_at.desc()).limit(limit)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_fitting(
        self,
        density_map_id: uuid.UUID,
        pdb_model_id: str,
        cross_correlation: float,
        molprobity_clashscore: float,
        ramachandran_favored_pct: float,
        rotamer_outliers_pct: float,
        alpha_helices: int,
        beta_sheets: int,
        fitting_log: Optional[str] = None
    ) -> DBDensityMapFitting:
        fitting = DBDensityMapFitting(
            id=uuid.uuid4(),
            density_map_id=density_map_id,
            pdb_model_id=pdb_model_id,
            cross_correlation_coefficient=cross_correlation,
            molprobity_clashscore=molprobity_clashscore,
            ramachandran_favored_pct=ramachandran_favored_pct,
            rotamer_outliers_pct=rotamer_outliers_pct,
            alpha_helices_count=alpha_helices,
            beta_sheets_count=beta_sheets,
            fitting_log=fitting_log
        )
        self.session.add(fitting)
        await self.session.commit()
        await self.session.refresh(fitting)
        return fitting

    async def add_macromolecular_complex(
        self,
        density_map_id: uuid.UUID,
        complex_name: str,
        stoichiometry: str,
        buried_surface_area: float,
        binding_free_energy: float,
        interface_residue_count: int,
        interaction_hotspots: List[Dict[str, Any]]
    ) -> DBMacromolecularComplex:
        comp = DBMacromolecularComplex(
            id=uuid.uuid4(),
            density_map_id=density_map_id,
            complex_name=complex_name,
            stoichiometry=stoichiometry,
            buried_surface_area_angstrom2=buried_surface_area,
            binding_free_energy_delta_g=binding_free_energy,
            interface_residue_count=interface_residue_count,
            interaction_hotspots=interaction_hotspots
        )
        self.session.add(comp)
        await self.session.commit()
        await self.session.refresh(comp)
        return comp
