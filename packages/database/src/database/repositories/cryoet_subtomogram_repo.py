"""Repository for Cryo-Electron Tomography (Cryo-ET) Subtomogram Averaging."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.cryoet_subtomogram import (
    DBCryoETDataset,
    DBSubtomogramParticle,
    DBAveragedStructureRefinement,
)


class CryoETSubtomogramRepository:
    """Handles async database operations for Cryo-ET subtomogram averaging."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(
        self,
        sample_name: str,
        specimen_organism: str,
        cellular_compartment: str = "CYTOSOL",
        tilt_angle_min: float = -60.0,
        tilt_angle_max: float = 60.0,
        total_tilt_images: int = 41,
        pixel_size_angstrom: float = 1.35,
        nominal_defocus_um: float = -2.5,
        tomogram_dimensions_json: Optional[Dict[str, int]] = None,
        dataset_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBCryoETDataset:
        dataset = DBCryoETDataset(
            sample_name=sample_name,
            specimen_organism=specimen_organism,
            cellular_compartment=cellular_compartment,
            tilt_angle_min=tilt_angle_min,
            tilt_angle_max=tilt_angle_max,
            total_tilt_images=total_tilt_images,
            pixel_size_angstrom=pixel_size_angstrom,
            nominal_defocus_um=nominal_defocus_um,
            tomogram_dimensions_json=tomogram_dimensions_json or {"x": 4096, "y": 4096, "z": 1024},
            dataset_metadata_json=dataset_metadata_json or {},
        )
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[DBCryoETDataset]:
        stmt = select(DBCryoETDataset).where(DBCryoETDataset.id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_datasets(self, limit: int = 50, offset: int = 0) -> List[DBCryoETDataset]:
        stmt = select(DBCryoETDataset).order_by(desc(DBCryoETDataset.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_particles(
        self,
        dataset_id: str,
        particles_data: List[Dict[str, Any]],
    ) -> List[DBSubtomogramParticle]:
        created = []
        for p in particles_data:
            item = DBSubtomogramParticle(
                dataset_id=dataset_id,
                particle_index=p["particle_index"],
                coord_x=p["coord_x"],
                coord_y=p["coord_y"],
                coord_z=p["coord_z"],
                euler_phi=p.get("euler_phi", 0.0),
                euler_theta=p.get("euler_theta", 0.0),
                euler_psi=p.get("euler_psi", 0.0),
                cross_correlation_score=p.get("cross_correlation_score", 0.75),
                class_assignment=p.get("class_assignment", "CLASS_1"),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_particles_by_dataset(self, dataset_id: str) -> List[DBSubtomogramParticle]:
        stmt = select(DBSubtomogramParticle).where(DBSubtomogramParticle.dataset_id == dataset_id).order_by(DBSubtomogramParticle.particle_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_refinement(
        self,
        dataset_id: str,
        class_name: str,
        particles_averaged_count: int,
        estimated_resolution_angstrom: float,
        fsc_0143_spatial_frequency: float,
        b_factor_sharpening: float = -120.0,
        fsc_curve_json: Optional[List[Dict[str, Any]]] = None,
    ) -> DBAveragedStructureRefinement:
        refinement = DBAveragedStructureRefinement(
            dataset_id=dataset_id,
            class_name=class_name,
            particles_averaged_count=particles_averaged_count,
            estimated_resolution_angstrom=estimated_resolution_angstrom,
            fsc_0143_spatial_frequency=fsc_0143_spatial_frequency,
            b_factor_sharpening=b_factor_sharpening,
            fsc_curve_json=fsc_curve_json or [],
        )
        self.session.add(refinement)
        await self.session.commit()
        await self.session.refresh(refinement)
        return refinement

    async def get_refinements_by_dataset(self, dataset_id: str) -> List[DBAveragedStructureRefinement]:
        stmt = select(DBAveragedStructureRefinement).where(DBAveragedStructureRefinement.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
