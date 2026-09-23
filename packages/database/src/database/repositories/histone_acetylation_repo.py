"""
Repository for Phase 136: Epigenetic Histone Acetylation Dynamics & HAT/HDAC Chromatin Remodeling Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.histone_acetylation import (
    DBHistoneAcetylationModel,
    DBHATHDACKinetics,
    DBChromatinOpennessProfile,
)


class HistoneAcetylationRepository:
    """Repository handling CRUD operations for histone acetylation models, enzyme kinetics, and chromatin openness profiles."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_model(
        self,
        locus_name: str,
        genomic_coordinates: str,
        cell_line_or_tissue: str,
        initial_h3k27ac_enrichment: float = 12.4,
        hdac_inhibitor_name: Optional[str] = "Vorinostat (SAHA)",
        predicted_enhancer_activation_fold: float = 4.8,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBHistoneAcetylationModel:
        """Create a new histone acetylation dynamics model."""
        model = DBHistoneAcetylationModel(
            id=uuid.uuid4(),
            project_id=project_id,
            locus_name=locus_name,
            genomic_coordinates=genomic_coordinates,
            cell_line_or_tissue=cell_line_or_tissue,
            initial_h3k27ac_enrichment=initial_h3k27ac_enrichment,
            hdac_inhibitor_name=hdac_inhibitor_name,
            predicted_enhancer_activation_fold=predicted_enhancer_activation_fold,
            metadata_json=metadata_json or {},
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_model(self, model_id: uuid.UUID) -> Optional[DBHistoneAcetylationModel]:
        """Get histone acetylation model with kinetics and chromatin profiles."""
        stmt = (
            select(DBHistoneAcetylationModel)
            .options(
                selectinload(DBHistoneAcetylationModel.enzyme_kinetics),
                selectinload(DBHistoneAcetylationModel.chromatin_profiles),
            )
            .where(DBHistoneAcetylationModel.id == model_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_models(self, limit: int = 50, offset: int = 0) -> List[DBHistoneAcetylationModel]:
        """List all histone acetylation models."""
        stmt = (
            select(DBHistoneAcetylationModel)
            .order_by(desc(DBHistoneAcetylationModel.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_enzyme_kinetics(
        self,
        model_id: uuid.UUID,
        enzyme_type: str,
        catalytic_rate_kcat: float,
        michaelis_constant_km_um: float,
        inhibition_constant_ki_nm: Optional[float] = None,
    ) -> DBHATHDACKinetics:
        """Add enzyme kinetic parameters."""
        kinetics = DBHATHDACKinetics(
            id=uuid.uuid4(),
            model_id=model_id,
            enzyme_type=enzyme_type,
            catalytic_rate_kcat=catalytic_rate_kcat,
            michaelis_constant_km_um=michaelis_constant_km_um,
            inhibition_constant_ki_nm=inhibition_constant_ki_nm,
        )
        self.session.add(kinetics)
        await self.session.commit()
        await self.session.refresh(kinetics)
        return kinetics

    async def add_chromatin_profile(
        self,
        model_id: uuid.UUID,
        time_point_hours: float,
        nucleosome_occupancy_percent: float,
        atac_seq_peak_intensity_rpm: float,
        brd4_bromodomain_recruitment: float,
    ) -> DBChromatinOpennessProfile:
        """Add time-series chromatin openness profile."""
        profile = DBChromatinOpennessProfile(
            id=uuid.uuid4(),
            model_id=model_id,
            time_point_hours=time_point_hours,
            nucleosome_occupancy_percent=nucleosome_occupancy_percent,
            atac_seq_peak_intensity_rpm=atac_seq_peak_intensity_rpm,
            brd4_bromodomain_recruitment=brd4_bromodomain_recruitment,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
