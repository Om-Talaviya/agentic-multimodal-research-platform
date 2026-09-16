import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.cart_engineering import (
    DBCARTConstructDesign,
    DBCYToxicityScorecard,
    DBCRSToxicityProfile,
)

class CARTRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_construct(
        self,
        construct_name: str,
        target_antigen: str,
        scfv_binder_clone: str,
        costimulatory_domain: str,
        hinge_transmembrane: str = "CD8a",
        signaling_domain: str = "CD3zeta",
        vector_type: str = "Lentiviral",
        full_aa_sequence: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBCARTConstructDesign:
        construct = DBCARTConstructDesign(
            id=str(uuid.uuid4()),
            construct_name=construct_name,
            target_antigen=target_antigen,
            scfv_binder_clone=scfv_binder_clone,
            costimulatory_domain=costimulatory_domain,
            hinge_transmembrane=hinge_transmembrane,
            signaling_domain=signaling_domain,
            vector_type=vector_type,
            full_aa_sequence=full_aa_sequence,
            properties=properties or {},
        )
        self.session.add(construct)
        await self.session.commit()
        await self.session.refresh(construct)
        return construct

    async def get_construct(self, construct_id: str) -> Optional[DBCARTConstructDesign]:
        stmt = (
            select(DBCARTConstructDesign)
            .options(
                selectinload(DBCARTConstructDesign.cytotoxicity_scorecards),
                selectinload(DBCARTConstructDesign.crs_profiles),
            )
            .where(DBCARTConstructDesign.id == construct_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_constructs(self, limit: int = 50) -> List[DBCARTConstructDesign]:
        stmt = (
            select(DBCARTConstructDesign)
            .options(
                selectinload(DBCARTConstructDesign.cytotoxicity_scorecards),
                selectinload(DBCARTConstructDesign.crs_profiles),
            )
            .order_by(DBCARTConstructDesign.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_cytotoxicity_scorecard(
        self,
        construct_id: str,
        target_cell_line: str,
        effector_to_target_ratio: float,
        specific_lysis_pct: float,
        t_cell_persistence_score: float,
        exhaustion_pd1_expression_pct: float,
        exhaustion_tim3_expression_pct: float,
        exhaustion_lag3_expression_pct: float,
        cytotoxicity_grade: str = "HIGH",
    ) -> DBCYToxicityScorecard:
        scorecard = DBCYToxicityScorecard(
            id=str(uuid.uuid4()),
            construct_id=construct_id,
            target_cell_line=target_cell_line,
            effector_to_target_ratio=effector_to_target_ratio,
            specific_lysis_pct=specific_lysis_pct,
            t_cell_persistence_score=t_cell_persistence_score,
            exhaustion_pd1_expression_pct=exhaustion_pd1_expression_pct,
            exhaustion_tim3_expression_pct=exhaustion_tim3_expression_pct,
            exhaustion_lag3_expression_pct=exhaustion_lag3_expression_pct,
            cytotoxicity_grade=cytotoxicity_grade,
        )
        self.session.add(scorecard)
        await self.session.commit()
        await self.session.refresh(scorecard)
        return scorecard

    async def add_crs_toxicity_profile(
        self,
        construct_id: str,
        peak_il6_pg_ml: float,
        peak_ifng_pg_ml: float,
        peak_tnfa_pg_ml: float,
        peak_il1b_pg_ml: float,
        astct_crs_grade_predicted: str,
        icans_neurotoxicity_risk_pct: float,
        tocilizumab_responsive: bool = True,
        dexamethasone_recommended: bool = False,
        safety_summary: Optional[str] = None,
    ) -> DBCRSToxicityProfile:
        profile = DBCRSToxicityProfile(
            id=str(uuid.uuid4()),
            construct_id=construct_id,
            peak_il6_pg_ml=peak_il6_pg_ml,
            peak_ifng_pg_ml=peak_ifng_pg_ml,
            peak_tnfa_pg_ml=peak_tnfa_pg_ml,
            peak_il1b_pg_ml=peak_il1b_pg_ml,
            astct_crs_grade_predicted=astct_crs_grade_predicted,
            icans_neurotoxicity_risk_pct=icans_neurotoxicity_risk_pct,
            tocilizumab_responsive=tocilizumab_responsive,
            dexamethasone_recommended=dexamethasone_recommended,
            safety_summary=safety_summary,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
