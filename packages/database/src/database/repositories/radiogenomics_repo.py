"""Repository for Radiogenomics & 3D Volumetric Medical Imaging AI Feature Extraction."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.radiogenomics import (
    DBRadiogenomicsScan,
    DBVolumetricRadiomicFeature,
    DBImagingGenomicCorrelation,
)


class RadiogenomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_scan(
        self,
        patient_id: str,
        modality: str = "MRI_T1_CONTRAST",
        anatomical_region: str = "BRAIN_GLIOMA",
        voxel_spacing_mm: str = "1.0x1.0x1.0",
        lesion_volume_cm3: float = 24.5,
        segmentation_mask_status: str = "SEGMENTED",
        scan_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBRadiogenomicsScan:
        scan = DBRadiogenomicsScan(
            patient_id=patient_id,
            modality=modality,
            anatomical_region=anatomical_region,
            voxel_spacing_mm=voxel_spacing_mm,
            lesion_volume_cm3=lesion_volume_cm3,
            segmentation_mask_status=segmentation_mask_status,
            scan_metadata_json=scan_metadata_json or {},
        )
        self.session.add(scan)
        await self.session.commit()
        await self.session.refresh(scan)
        return scan

    async def add_radiomic_feature(
        self,
        scan_id: str,
        feature_family: str = "IBSI_SHAPE_3D",
        feature_name: str = "Sphericity",
        feature_value: float = 0.785,
        normalized_z_score: float = 1.24,
    ) -> DBVolumetricRadiomicFeature:
        feat = DBVolumetricRadiomicFeature(
            scan_id=scan_id,
            feature_family=feature_family,
            feature_name=feature_name,
            feature_value=feature_value,
            normalized_z_score=normalized_z_score,
        )
        self.session.add(feat)
        await self.session.commit()
        await self.session.refresh(feat)
        return feat

    async def add_genomic_correlation(
        self,
        scan_id: str,
        predicted_genomic_alteration: str = "IDH1_R132H",
        prediction_probability: float = 0.912,
        feature_importance_json: Optional[Dict[str, Any]] = None,
        clinical_significance: str = "High likelihood of favorable temozolomide response",
    ) -> DBImagingGenomicCorrelation:
        corr = DBImagingGenomicCorrelation(
            scan_id=scan_id,
            predicted_genomic_alteration=predicted_genomic_alteration,
            prediction_probability=prediction_probability,
            feature_importance_json=feature_importance_json or {},
            clinical_significance=clinical_significance,
        )
        self.session.add(corr)
        await self.session.commit()
        await self.session.refresh(corr)
        return corr

    async def get_scan(self, scan_id: str) -> Optional[DBRadiogenomicsScan]:
        stmt = (
            select(DBRadiogenomicsScan)
            .where(DBRadiogenomicsScan.id == scan_id)
            .options(
                selectinload(DBRadiogenomicsScan.radiomic_features),
                selectinload(DBRadiogenomicsScan.genomic_correlations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_scans(self, limit: int = 50) -> List[DBRadiogenomicsScan]:
        stmt = (
            select(DBRadiogenomicsScan)
            .options(
                selectinload(DBRadiogenomicsScan.radiomic_features),
                selectinload(DBRadiogenomicsScan.genomic_correlations),
            )
            .order_by(desc(DBRadiogenomicsScan.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
