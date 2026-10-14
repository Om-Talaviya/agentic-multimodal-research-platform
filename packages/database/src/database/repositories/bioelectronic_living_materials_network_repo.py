"""Repository for Phase 500: Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bioelectronic_living_materials_network import (
    BioelectronicLivingMaterialsNetworkStudy,
    BioelectronicLivingMaterialsNetworkItemProfile,
    BioelectronicLivingMaterialsNetworkMetricTrace,
)


class BioelectronicLivingMaterialsNetworkRepository:
    """Database operations for Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Geobacter sulfurreducens Engineered Electrically Conductive Cytochrome Pili Hydrogel Matrix",
        analytical_modality: str = "bioelectronic-living-materials",
        matrix_electrical_conductivity_S_per_cm: float = 0.85,
        redox_cytochrome_hopping_rate_s_inv: float = 420000.0,
        current_density_production_mA_per_cm2: float = 18.5,
        longitudinal_charge_transfer_efficiency: float = 0.965,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BioelectronicLivingMaterialsNetworkStudy:
        study = BioelectronicLivingMaterialsNetworkStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            matrix_electrical_conductivity_S_per_cm=matrix_electrical_conductivity_S_per_cm,
            redox_cytochrome_hopping_rate_s_inv=redox_cytochrome_hopping_rate_s_inv,
            current_density_production_mA_per_cm2=current_density_production_mA_per_cm2,
            longitudinal_charge_transfer_efficiency=longitudinal_charge_transfer_efficiency,
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
    ) -> BioelectronicLivingMaterialsNetworkItemProfile:
        item = BioelectronicLivingMaterialsNetworkItemProfile(
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
    ) -> BioelectronicLivingMaterialsNetworkMetricTrace:
        trace = BioelectronicLivingMaterialsNetworkMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BioelectronicLivingMaterialsNetworkStudy]:
        result = await self.session.execute(
            select(BioelectronicLivingMaterialsNetworkStudy)
            .options(
                selectinload(BioelectronicLivingMaterialsNetworkStudy.item_profiles),
                selectinload(BioelectronicLivingMaterialsNetworkStudy.metric_traces),
            )
            .where(BioelectronicLivingMaterialsNetworkStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[BioelectronicLivingMaterialsNetworkStudy]:
        result = await self.session.execute(
            select(BioelectronicLivingMaterialsNetworkStudy)
            .options(
                selectinload(BioelectronicLivingMaterialsNetworkStudy.item_profiles),
                selectinload(BioelectronicLivingMaterialsNetworkStudy.metric_traces),
            )
            .order_by(BioelectronicLivingMaterialsNetworkStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
