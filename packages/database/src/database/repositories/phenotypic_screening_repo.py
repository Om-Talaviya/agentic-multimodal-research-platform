"""Repository for High-Content Phenotypic Screening & Cell Painting Assays."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.phenotypic_screening import (
    DBCellPaintingPlate,
    DBCellPaintingWell,
    DBSingleCellMorphometry,
)


class PhenotypicScreeningRepository:
    """Repository handling CRUD operations for Cell Painting plates and morphometry profiles."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_plate(
        self,
        workspace_id: UUID,
        plate_name: str,
        format: str = "384-well",
        cell_line: str = "U2OS",
        imaging_magnification: str = "20x",
        channels_profiled: Optional[List[str]] = None,
        total_wells: int = 384,
        plate_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBCellPaintingPlate:
        plate = DBCellPaintingPlate(
            workspace_id=workspace_id,
            plate_name=plate_name,
            format=format,
            cell_line=cell_line,
            imaging_magnification=imaging_magnification,
            channels_profiled=channels_profiled or ["DNA", "RNA", "ER", "AGP", "Mito"],
            total_wells=total_wells,
            plate_metadata=plate_metadata or {},
        )
        self.session.add(plate)
        await self.session.commit()
        await self.session.refresh(plate)
        return plate

    async def get_plate(self, plate_id: UUID) -> Optional[DBCellPaintingPlate]:
        query = (
            select(DBCellPaintingPlate)
            .where(DBCellPaintingPlate.id == plate_id)
            .options(
                selectinload(DBCellPaintingPlate.wells).selectinload(DBCellPaintingWell.single_cells)
            )
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_plates(self, workspace_id: UUID, limit: int = 50, offset: int = 0) -> List[DBCellPaintingPlate]:
        query = (
            select(DBCellPaintingPlate)
            .where(DBCellPaintingPlate.workspace_id == workspace_id)
            .order_by(desc(DBCellPaintingPlate.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_well_profile(
        self,
        plate_id: UUID,
        well_position: str,
        compound_name: str,
        concentration_uM: float = 10.0,
        is_control: bool = False,
        cell_count: int = 1500,
        viability_pct: float = 95.0,
        predicted_moa: str = "Unknown",
        moa_confidence: float = 0.85,
        phenotypic_activity_score: float = 0.0,
        morphological_profile: Optional[Dict[str, Any]] = None,
        single_cells: Optional[List[Dict[str, Any]]] = None,
    ) -> DBCellPaintingWell:
        well = DBCellPaintingWell(
            plate_id=plate_id,
            well_position=well_position,
            compound_name=compound_name,
            concentration_uM=concentration_uM,
            is_control=is_control,
            cell_count=cell_count,
            viability_pct=viability_pct,
            predicted_moa=predicted_moa,
            moa_confidence=moa_confidence,
            phenotypic_activity_score=phenotypic_activity_score,
            morphological_profile=morphological_profile or {},
        )
        self.session.add(well)
        await self.session.flush()

        if single_cells:
            for sc in single_cells:
                cell_morph = DBSingleCellMorphometry(
                    well_id=well.id,
                    cell_index=sc.get("cell_index", 0),
                    nuclear_area=sc.get("nuclear_area", 150.0),
                    nuclear_eccentricity=sc.get("nuclear_eccentricity", 0.45),
                    cytoplasm_area=sc.get("cytoplasm_area", 450.0),
                    er_intensity_mean=sc.get("er_intensity_mean", 1200.0),
                    mito_texture_contrast=sc.get("mito_texture_contrast", 35.0),
                    actin_alignment_index=sc.get("actin_alignment_index", 0.72),
                    zernike_moment_z20=sc.get("zernike_moment_z20", 0.15),
                    haralick_homogeneity=sc.get("haralick_homogeneity", 0.82),
                )
                self.session.add(cell_morph)

        await self.session.commit()
        await self.session.refresh(well)
        return well

    async def get_well(self, well_id: UUID) -> Optional[DBCellPaintingWell]:
        query = (
            select(DBCellPaintingWell)
            .where(DBCellPaintingWell.id == well_id)
            .options(selectinload(DBCellPaintingWell.single_cells))
        )
        res = await self.session.execute(query)
        return res.scalars().first()
