"""Repository for Phase 186: Oncology Radiomics & Habitat Imaging."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.radiomics_deep_phenotyping import RadiomicsDeepImagingStudy, RadiomicsHabitatSubregion, RadiomicsExtractedTextureFeature


class RadiomicsDeepPhenotypingRepository:
    """Database operations for multi-parametric radiomics studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        scan_modality: str = "Multiparametric MRI (T1c, T2, FLAIR, DWI)",
        tumor_type: str = "Glioblastoma Multiforme",
        gross_tumor_volume_cm3: float = 48.5,
        necrotic_core_fraction: float = 0.24,
        active_rim_fraction: float = 0.46,
        edema_infiltrative_fraction: float = 0.30,
        intratumoral_heterogeneity_index: float = 0.89,
        predicted_overall_survival_months: float = 18.4,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> RadiomicsDeepImagingStudy:
        study = RadiomicsDeepImagingStudy(
            name=name,
            scan_modality=scan_modality,
            tumor_type=tumor_type,
            gross_tumor_volume_cm3=gross_tumor_volume_cm3,
            necrotic_core_fraction=necrotic_core_fraction,
            active_rim_fraction=active_rim_fraction,
            edema_infiltrative_fraction=edema_infiltrative_fraction,
            intratumoral_heterogeneity_index=intratumoral_heterogeneity_index,
            predicted_overall_survival_months=predicted_overall_survival_months,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_habitat_subregion(
        self,
        study_id: UUID,
        subregion_name: str,
        volume_cm3: float,
        mean_perfusion_ktrans: float,
        apparent_diffusion_coefficient_adc: float,
        hypoxia_pet_avidity_suv: float,
    ) -> RadiomicsHabitatSubregion:
        item = RadiomicsHabitatSubregion(
            study_id=study_id,
            subregion_name=subregion_name,
            volume_cm3=volume_cm3,
            mean_perfusion_ktrans=mean_perfusion_ktrans,
            apparent_diffusion_coefficient_adc=apparent_diffusion_coefficient_adc,
            hypoxia_pet_avidity_suv=hypoxia_pet_avidity_suv,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_texture_feature(
        self,
        study_id: UUID,
        feature_class: str,
        feature_name: str,
        feature_value: float,
        ibsi_compliance_flag: bool = True,
        radiogenomic_weight: float = 1.0,
    ) -> RadiomicsExtractedTextureFeature:
        item = RadiomicsExtractedTextureFeature(
            study_id=study_id,
            feature_class=feature_class,
            feature_name=feature_name,
            feature_value=feature_value,
            ibsi_compliance_flag=ibsi_compliance_flag,
            radiogenomic_weight=radiogenomic_weight,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[RadiomicsDeepImagingStudy]:
        stmt = select(RadiomicsDeepImagingStudy).where(RadiomicsDeepImagingStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[RadiomicsDeepImagingStudy]:
        stmt = select(RadiomicsDeepImagingStudy).order_by(RadiomicsDeepImagingStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())