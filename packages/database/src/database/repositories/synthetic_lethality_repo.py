from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.synthetic_lethality import (
    DBSyntheticLethalScreen,
    DBSyntheticLethalPartner,
    DBCRISPRDependencyScore,
)

class SyntheticLethalityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        screen_name: str,
        primary_target_gene: str,
        tumor_indication: str = "Ovarian Carcinoma",
        ceres_dependency_threshold: float = -0.5,
        sample_cell_lines_count: int = 320,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBSyntheticLethalScreen:
        screen = DBSyntheticLethalScreen(
            screen_name=screen_name,
            primary_target_gene=primary_target_gene,
            tumor_indication=tumor_indication,
            ceres_dependency_threshold=ceres_dependency_threshold,
            sample_cell_lines_count=sample_cell_lines_count,
            properties=properties or {},
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def add_synthetic_lethal_partner(
        self,
        screen_id: str,
        partner_gene: str,
        interaction_type: str = "DNA Repair Compensation",
        ceres_depmap_delta_score: float = -0.74,
        synthetic_lethal_p_value: float = 1.2e-6,
        is_validated_druggable: bool = True,
        confidence_tier: str = "HIGH",
    ) -> DBSyntheticLethalPartner:
        partner = DBSyntheticLethalPartner(
            screen_id=screen_id,
            partner_gene=partner_gene,
            interaction_type=interaction_type,
            ceres_depmap_delta_score=ceres_depmap_delta_score,
            synthetic_lethal_p_value=synthetic_lethal_p_value,
            is_validated_druggable=is_validated_druggable,
            confidence_tier=confidence_tier,
        )
        self.session.add(partner)
        await self.session.commit()
        await self.session.refresh(partner)
        return partner

    async def add_dependency_score(
        self,
        screen_id: str,
        cell_line_name: str,
        lineage: str,
        primary_gene_dependency_score: float,
        partner_gene_dependency_score: float,
        co_essentiality_correlation: float = 0.68,
    ) -> DBCRISPRDependencyScore:
        score = DBCRISPRDependencyScore(
            screen_id=screen_id,
            cell_line_name=cell_line_name,
            lineage=lineage,
            primary_gene_dependency_score=primary_gene_dependency_score,
            partner_gene_dependency_score=partner_gene_dependency_score,
            co_essentiality_correlation=co_essentiality_correlation,
        )
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        return score

    async def get_screen_by_id(self, screen_id: str) -> Optional[DBSyntheticLethalScreen]:
        stmt = (
            select(DBSyntheticLethalScreen)
            .options(
                selectinload(DBSyntheticLethalScreen.partners),
                selectinload(DBSyntheticLethalScreen.dependency_scores),
            )
            .where(DBSyntheticLethalScreen.id == screen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(self, limit: int = 50) -> List[DBSyntheticLethalScreen]:
        stmt = (
            select(DBSyntheticLethalScreen)
            .options(
                selectinload(DBSyntheticLethalScreen.partners),
                selectinload(DBSyntheticLethalScreen.dependency_scores),
            )
            .order_by(DBSyntheticLethalScreen.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
