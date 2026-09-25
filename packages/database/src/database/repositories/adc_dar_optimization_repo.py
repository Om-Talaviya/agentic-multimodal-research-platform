"""Repository for Phase 178: ADC DAR Optimization & Aggregation Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.adc_dar_optimization import ADCDAROptStudy, ADCDARSpeciesDistribution, ADCDARAggregationMetric


class ADCDAROptimizationRepository:
    """Database operations for ADC DAR optimization studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        antibody_name: str,
        payload_name: str,
        linker_type: str = "cleavable_val_cit",
        conjugation_chemistry: str = "cysteine_maleimide",
        target_dar: float = 4.0,
        calculated_mean_dar: float = 3.85,
        aggregation_propensity_score: float = 0.12,
        hydrophobicity_index: float = 2.45,
        unconjugated_antibody_pct: float = 4.2,
        high_dar_overload_pct: float = 6.8,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> ADCDAROptStudy:
        study = ADCDAROptStudy(
            name=name,
            antibody_name=antibody_name,
            payload_name=payload_name,
            linker_type=linker_type,
            conjugation_chemistry=conjugation_chemistry,
            target_dar=target_dar,
            calculated_mean_dar=calculated_mean_dar,
            aggregation_propensity_score=aggregation_propensity_score,
            hydrophobicity_index=hydrophobicity_index,
            unconjugated_antibody_pct=unconjugated_antibody_pct,
            high_dar_overload_pct=high_dar_overload_pct,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_species_distribution(
        self,
        study_id: UUID,
        dar_species: int,
        molar_fraction: float,
        retention_time_min: float,
        mass_shift_da: float,
        relative_clearance_rate: float = 1.0,
    ) -> ADCDARSpeciesDistribution:
        item = ADCDARSpeciesDistribution(
            study_id=study_id,
            dar_species=dar_species,
            molar_fraction=molar_fraction,
            retention_time_min=retention_time_min,
            mass_shift_da=mass_shift_da,
            relative_clearance_rate=relative_clearance_rate,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_aggregation_metric(
        self,
        study_id: UUID,
        incubation_hours: float,
        monomer_percentage: float,
        high_molecular_weight_pct: float,
        low_molecular_weight_pct: float,
        turbidity_od350: float,
    ) -> ADCDARAggregationMetric:
        item = ADCDARAggregationMetric(
            study_id=study_id,
            incubation_hours=incubation_hours,
            monomer_percentage=monomer_percentage,
            high_molecular_weight_pct=high_molecular_weight_pct,
            low_molecular_weight_pct=low_molecular_weight_pct,
            turbidity_od350=turbidity_od350,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[ADCDAROptStudy]:
        stmt = select(ADCDAROptStudy).where(ADCDAROptStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[ADCDAROptStudy]:
        stmt = select(ADCDAROptStudy).order_by(ADCDAROptStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
