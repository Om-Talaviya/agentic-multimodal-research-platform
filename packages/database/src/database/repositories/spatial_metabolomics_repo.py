"""
Repository for Spatial Metabolomics & MALDI Imaging MS (Phase 57).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.spatial_metabolomics import (
    DBSpatialMetabolomicsExperiment,
    DBMetaboliteSpatialProfile,
    DBMetabolicFluxRoute,
)


class SpatialMetabolomicsRepository:
    """Handles CRUD operations for MALDI spatial metabolomics and metabolic flux balances."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_experiment(
        self,
        tissue_sample_id: str,
        organ_type: str,
        matrix_compound: str = "DHB",
        spatial_resolution_um: float = 20.0,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBSpatialMetabolomicsExperiment:
        exp = DBSpatialMetabolomicsExperiment(
            id=str(uuid.uuid4()),
            tissue_sample_id=tissue_sample_id,
            organ_type=organ_type,
            matrix_compound=matrix_compound,
            spatial_resolution_um=spatial_resolution_um,
            metadata_info=metadata_info or {},
        )
        self.session.add(exp)
        await self.session.flush()
        await self.session.commit()
        return exp

    async def add_metabolites_and_flux(
        self,
        experiment_id: str,
        metabolites_data: List[Dict[str, Any]],
        flux_data: List[Dict[str, Any]],
    ) -> DBSpatialMetabolomicsExperiment:
        for m in metabolites_data:
            profile = DBMetaboliteSpatialProfile(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                metabolite_name=m["metabolite_name"],
                kegg_id=m.get("kegg_id", "C00000"),
                mz_ratio=m["mz_ratio"],
                spatial_zone=m.get("spatial_zone", "Tumor Core"),
                mean_intensity_au=m.get("mean_intensity_au", 1500.0),
                fold_change_vs_normal=m.get("fold_change_vs_normal", 2.0),
                spatial_heterogeneity_score=m.get("spatial_heterogeneity_score", 0.8),
            )
            self.session.add(profile)

        for f in flux_data:
            route = DBMetabolicFluxRoute(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                pathway_name=f["pathway_name"],
                estimated_flux_rate=f.get("estimated_flux_rate", 12.5),
                pathway_activity_score=f.get("pathway_activity_score", 0.9),
                limiting_enzyme=f.get("limiting_enzyme", "LDHA"),
            )
            self.session.add(route)

        await self.session.flush()

        exp = await self.get_experiment(experiment_id)
        if exp:
            exp.total_metabolites_identified = len(metabolites_data)
            self.session.add(exp)

        await self.session.commit()
        return exp

    async def get_experiment(self, experiment_id: str) -> Optional[DBSpatialMetabolomicsExperiment]:
        self.session.expire_all()
        query = (
            select(DBSpatialMetabolomicsExperiment)
            .options(
                selectinload(DBSpatialMetabolomicsExperiment.metabolites),
                selectinload(DBSpatialMetabolomicsExperiment.flux_routes),
            )
            .where(DBSpatialMetabolomicsExperiment.id == experiment_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_experiments(self, limit: int = 50) -> List[DBSpatialMetabolomicsExperiment]:
        query = (
            select(DBSpatialMetabolomicsExperiment)
            .options(selectinload(DBSpatialMetabolomicsExperiment.metabolites))
            .order_by(desc(DBSpatialMetabolomicsExperiment.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
