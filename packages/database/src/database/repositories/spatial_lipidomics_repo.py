"""
Repository for Phase 106: Spatial Lipidomics & Multi-Isotope Imaging Mass Spectrometry.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.spatial_lipidomics import DBSpatialLipidomicsDataset, DBLipidSpeciesIdentification, DBSpatialIonIntensityMap

class SpatialLipidomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(
        self,
        sample_name: str,
        user_id: Optional[uuid.UUID] = None,
        tissue_type: str = "Brain Sagittal Section",
        matrix_type: str = "DHB",
        laser_spatial_resolution_um: float = 20.0,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBSpatialLipidomicsDataset:
        ds = DBSpatialLipidomicsDataset(
            id=uuid.uuid4(),
            user_id=user_id,
            sample_name=sample_name,
            tissue_type=tissue_type,
            matrix_type=matrix_type,
            laser_spatial_resolution_um=laser_spatial_resolution_um,
            metadata_json=metadata_json or {},
            status="COMPLETED"
        )
        self.session.add(ds)
        await self.session.commit()
        await self.session.refresh(ds)
        return ds

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[DBSpatialLipidomicsDataset]:
        stmt = (
            select(DBSpatialLipidomicsDataset)
            .options(selectinload(DBSpatialLipidomicsDataset.lipid_species), selectinload(DBSpatialLipidomicsDataset.spatial_spots))
            .where(DBSpatialLipidomicsDataset.id == dataset_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datasets(self, limit: int = 50, offset: int = 0) -> List[DBSpatialLipidomicsDataset]:
        stmt = (
            select(DBSpatialLipidomicsDataset)
            .order_by(desc(DBSpatialLipidomicsDataset.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_lipid_species(
        self,
        dataset_id: uuid.UUID,
        species_data: List[Dict[str, Any]]
    ) -> List[DBLipidSpeciesIdentification]:
        entities = []
        for s in species_data:
            species_id = s.get("id") or uuid.uuid4()
            if isinstance(species_id, str):
                species_id = uuid.UUID(species_id)

            entity = DBLipidSpeciesIdentification(
                id=species_id,
                dataset_id=dataset_id,
                mz_ratio=s["mz_ratio"],
                lipid_species=s["lipid_species"],
                lipid_class=s["lipid_class"],
                adduct_type=s.get("adduct_type", "[M+H]+"),
                structural_formula=s.get("structural_formula"),
                mean_intensity=s.get("mean_intensity", 0.0)
            )
            entities.append(entity)
            self.session.add(entity)

        ds = await self.session.get(DBSpatialLipidomicsDataset, dataset_id)
        if ds:
            classes = {s["lipid_class"] for s in species_data}
            ds.detected_lipid_classes = len(classes)

        await self.session.commit()
        return entities

    async def add_spatial_spots(
        self,
        dataset_id: uuid.UUID,
        spots_data: List[Dict[str, Any]]
    ) -> List[DBSpatialIonIntensityMap]:
        entities = []
        for sp in spots_data:
            lipid_sp_id = sp["lipid_species_id"]
            if isinstance(lipid_sp_id, str):
                lipid_sp_id = uuid.UUID(lipid_sp_id)

            entity = DBSpatialIonIntensityMap(
                id=uuid.uuid4(),
                dataset_id=dataset_id,
                lipid_species_id=lipid_sp_id,
                x_coord=sp["x_coord"],
                y_coord=sp["y_coord"],
                normalized_intensity=sp.get("normalized_intensity", 0.0),
                region_annotation=sp.get("region_annotation", "Cortex")
            )
            entities.append(entity)
            self.session.add(entity)

        ds = await self.session.get(DBSpatialLipidomicsDataset, dataset_id)
        if ds:
            unique_spots = {(sp["x_coord"], sp["y_coord"]) for sp in spots_data}
            ds.total_spots = len(unique_spots)

        await self.session.commit()
        return entities
