"""Repository for Genome-Scale Metabolic Network Flux Balance Analysis (FBA)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.metabolic_flux_fba import (
    DBMetabolicFluxFBASStudy,
    DBReactionFluxConstraint,
    DBMetabolicVulnerabilityHit,
)


class MetabolicFluxFBARepository:
    """Repository handling CRUD operations for Metabolic Flux FBA."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        organism_model: str = "Human Recon3D",
        cellular_phenotype: str = "Warburg Glycolytic Cancer",
        optimal_growth_rate_hr: float = 0.084,
        objective_reaction: str = "Biomass_Eukaryote_Production",
        summary_metrics: Optional[Dict[str, Any]] = None,
        reactions: Optional[List[Dict[str, Any]]] = None,
        vulnerabilities: Optional[List[Dict[str, Any]]] = None,
    ) -> DBMetabolicFluxFBASStudy:
        study_id = uuid.uuid4()
        study = DBMetabolicFluxFBASStudy(
            id=study_id,
            study_name=study_name,
            organism_model=organism_model,
            cellular_phenotype=cellular_phenotype,
            optimal_growth_rate_hr=optimal_growth_rate_hr,
            objective_reaction=objective_reaction,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if reactions:
            for r in reactions:
                rxn_row = DBReactionFluxConstraint(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    reaction_id=r["reaction_id"],
                    reaction_name=r["reaction_name"],
                    subsystem=r["subsystem"],
                    lower_bound=r["lower_bound"],
                    upper_bound=r["upper_bound"],
                    computed_flux_mmol_gdw_hr=r["computed_flux_mmol_gdw_hr"],
                    shadow_price=r.get("shadow_price", 0.0),
                )
                self.session.add(rxn_row)

        if vulnerabilities:
            for v in vulnerabilities:
                vuln_row = DBMetabolicVulnerabilityHit(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    target_enzyme_gene=v["target_enzyme_gene"],
                    target_reaction=v["target_reaction"],
                    growth_inhibition_percent=v["growth_inhibition_percent"],
                    synthetic_lethal_partner=v.get("synthetic_lethal_partner"),
                    druggability_verdict=v.get("druggability_verdict", "druggable_selective"),
                )
                self.session.add(vuln_row)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBMetabolicFluxFBASStudy]:
        stmt = (
            select(DBMetabolicFluxFBASStudy)
            .where(DBMetabolicFluxFBASStudy.id == study_id)
            .options(
                selectinload(DBMetabolicFluxFBASStudy.reactions),
                selectinload(DBMetabolicFluxFBASStudy.vulnerabilities),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBMetabolicFluxFBASStudy]:
        stmt = (
            select(DBMetabolicFluxFBASStudy)
            .order_by(DBMetabolicFluxFBASStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBMetabolicFluxFBASStudy.reactions),
                selectinload(DBMetabolicFluxFBASStudy.vulnerabilities),
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
