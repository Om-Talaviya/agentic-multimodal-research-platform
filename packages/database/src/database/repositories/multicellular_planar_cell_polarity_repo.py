"""Repository for Phase 459: Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.multicellular_planar_cell_polarity import (
    MulticellularPlanarCellPolarityStudy,
    MulticellularPlanarCellPolarityItemProfile,
    MulticellularPlanarCellPolarityMetricTrace,
)


class MulticellularPlanarCellPolarityRepository:
    """Database operations for Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles",
        analytical_modality: str = "planar-cell-polarity-segregation",
        asymmetric_crescent_enrichment_ratio: float = 4.25,
        nematic_order_director_coherence: float = 0.885,
        junctional_remodeling_strain_rate_per_hr: float = 0.042,
        global_polarization_vector_magnitude: float = 0.942,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MulticellularPlanarCellPolarityStudy:
        study = MulticellularPlanarCellPolarityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            asymmetric_crescent_enrichment_ratio=asymmetric_crescent_enrichment_ratio,
            nematic_order_director_coherence=nematic_order_director_coherence,
            junctional_remodeling_strain_rate_per_hr=junctional_remodeling_strain_rate_per_hr,
            global_polarization_vector_magnitude=global_polarization_vector_magnitude,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> MulticellularPlanarCellPolarityItemProfile:
        item = MulticellularPlanarCellPolarityItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> MulticellularPlanarCellPolarityMetricTrace:
        trace = MulticellularPlanarCellPolarityMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[MulticellularPlanarCellPolarityStudy]:
        result = await self.session.execute(
            select(MulticellularPlanarCellPolarityStudy)
            .options(
                selectinload(MulticellularPlanarCellPolarityStudy.item_profiles),
                selectinload(MulticellularPlanarCellPolarityStudy.metric_traces),
            )
            .where(MulticellularPlanarCellPolarityStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MulticellularPlanarCellPolarityStudy]:
        result = await self.session.execute(
            select(MulticellularPlanarCellPolarityStudy)
            .options(
                selectinload(MulticellularPlanarCellPolarityStudy.item_profiles),
                selectinload(MulticellularPlanarCellPolarityStudy.metric_traces),
            )
            .order_by(MulticellularPlanarCellPolarityStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
