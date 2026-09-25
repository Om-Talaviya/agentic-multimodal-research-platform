"""Repository for Spatial Proteogenomics & Subcellular Co-Localization."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.spatial_proteogenomics import (
    DBSpatialProteogenomicsStudy,
    DBProteinRNACoLocalizationSpot,
    DBMarkerEnrichmentMetric,
)


class SpatialProteogenomicsRepository:
    """Repository handling CRUD operations for Spatial Proteogenomics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        tissue_sample_id: str = "GBM_TME_Slice_04",
        total_spots_analyzed: int = 4,
        mean_pearson_colocalization_r: float = 0.86,
        subcellular_niche_count: int = 3,
        summary_metrics: Optional[Dict[str, Any]] = None,
        spots: Optional[List[Dict[str, Any]]] = None,
        enrichment_metrics: Optional[List[Dict[str, Any]]] = None,
    ) -> DBSpatialProteogenomicsStudy:
        study_id = uuid.uuid4()
        study = DBSpatialProteogenomicsStudy(
            id=study_id,
            study_name=study_name,
            tissue_sample_id=tissue_sample_id,
            total_spots_analyzed=total_spots_analyzed,
            mean_pearson_colocalization_r=mean_pearson_colocalization_r,
            subcellular_niche_count=subcellular_niche_count,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if spots:
            for s in spots:
                spot_row = DBProteinRNACoLocalizationSpot(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    spot_barcode=s["spot_barcode"],
                    x_coord=s["x_coord"],
                    y_coord=s["y_coord"],
                    target_mrna_symbol=s["target_mrna_symbol"],
                    mrna_normalized_count=s["mrna_normalized_count"],
                    target_protein_antibody=s["target_protein_antibody"],
                    protein_adt_signal=s["protein_adt_signal"],
                    colocalization_pearson_r=s["colocalization_pearson_r"],
                    subcellular_niche=s.get("subcellular_niche", "Invasive Tumor Core"),
                )
                self.session.add(spot_row)

        if enrichment_metrics:
            for e in enrichment_metrics:
                metric_row = DBMarkerEnrichmentMetric(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    marker_pair=e["marker_pair"],
                    enrichment_z_score=e["enrichment_z_score"],
                    fdr_q_value=e["fdr_q_value"],
                    biological_relevance=e["biological_relevance"],
                )
                self.session.add(metric_row)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBSpatialProteogenomicsStudy]:
        stmt = (
            select(DBSpatialProteogenomicsStudy)
            .where(DBSpatialProteogenomicsStudy.id == study_id)
            .options(
                selectinload(DBSpatialProteogenomicsStudy.spots),
                selectinload(DBSpatialProteogenomicsStudy.enrichment_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBSpatialProteogenomicsStudy]:
        stmt = (
            select(DBSpatialProteogenomicsStudy)
            .order_by(DBSpatialProteogenomicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBSpatialProteogenomicsStudy.spots),
                selectinload(DBSpatialProteogenomicsStudy.enrichment_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_study(self, study_id: uuid.UUID) -> bool:
        study = await self.get_study(study_id)
        if not study:
            return False
        await self.session.delete(study)
        await self.session.commit()
        return True
