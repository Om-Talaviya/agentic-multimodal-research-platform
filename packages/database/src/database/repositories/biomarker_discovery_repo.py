"""Repository for Multi-Modal Biomarker Discovery & Signature Extraction."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.biomarker_discovery import (
    DBBiomarkerDiscoveryStudy,
    DBBiomarkerFeature,
    DBPatientRiskStratification,
)


class BiomarkerDiscoveryRepository:
    """Handles async database operations for multi-modal biomarker discovery."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        study_title: str,
        disease_indication: str,
        cohort_sample_size: int = 100,
        omics_layers_json: Optional[List[str]] = None,
        signature_stability_score: float = 0.85,
        auc_roc_score: float = 0.91,
        study_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBBiomarkerDiscoveryStudy:
        study = DBBiomarkerDiscoveryStudy(
            study_title=study_title,
            disease_indication=disease_indication,
            cohort_sample_size=cohort_sample_size,
            omics_layers_json=omics_layers_json or ["TRANSCRIPTOMICS", "PROTEOMICS"],
            signature_stability_score=signature_stability_score,
            auc_roc_score=auc_roc_score,
            study_metadata_json=study_metadata_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: str) -> Optional[DBBiomarkerDiscoveryStudy]:
        stmt = select(DBBiomarkerDiscoveryStudy).where(DBBiomarkerDiscoveryStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBBiomarkerDiscoveryStudy]:
        stmt = select(DBBiomarkerDiscoveryStudy).order_by(desc(DBBiomarkerDiscoveryStudy.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_features(
        self,
        study_id: str,
        features_data: List[Dict[str, Any]],
    ) -> List[DBBiomarkerFeature]:
        created = []
        for f in features_data:
            item = DBBiomarkerFeature(
                study_id=study_id,
                feature_name=f["feature_name"],
                omics_modality=f["omics_modality"],
                log2_fold_change=f.get("log2_fold_change", 0.0),
                adjusted_p_value=f.get("adjusted_p_value", 0.05),
                feature_importance_weight=f.get("feature_importance_weight", 0.5),
                correlation_direction=f.get("correlation_direction", "POSITIVE"),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_features_by_study(self, study_id: str) -> List[DBBiomarkerFeature]:
        stmt = select(DBBiomarkerFeature).where(DBBiomarkerFeature.study_id == study_id).order_by(desc(DBBiomarkerFeature.feature_importance_weight))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_stratifications(
        self,
        study_id: str,
        stratifications_data: List[Dict[str, Any]],
    ) -> List[DBPatientRiskStratification]:
        created = []
        for s in stratifications_data:
            item = DBPatientRiskStratification(
                study_id=study_id,
                patient_cohort_id=s["patient_cohort_id"],
                prognostic_risk_tier=s.get("prognostic_risk_tier", "INTERMEDIATE"),
                response_probability_score=s.get("response_probability_score", 0.5),
                composite_signature_score=s.get("composite_signature_score", 0.0),
                signature_expression_map_json=s.get("signature_expression_map_json", {}),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_stratifications_by_study(self, study_id: str) -> List[DBPatientRiskStratification]:
        stmt = select(DBPatientRiskStratification).where(DBPatientRiskStratification.study_id == study_id).order_by(desc(DBPatientRiskStratification.response_probability_score))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
