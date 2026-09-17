from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.toxicity_qsar import (
    DBCompoundToxicityScreen,
    DBStructuralAlertMatch,
)

class ToxicityQSARRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        compound_name: str,
        smiles_string: str,
        molecular_weight: float = 342.4,
        log_p: float = 2.8,
        ames_mutagenicity_status: str = "NEGATIVE",
        ames_probability_pct: float = 12.4,
        herg_ic50_micromolar: float = 24.5,
        herg_cardiotox_risk: str = "LOW",
        dili_hepatotox_risk: str = "LOW",
        ld50_rat_mg_kg: float = 1250.0,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBCompoundToxicityScreen:
        screen = DBCompoundToxicityScreen(
            compound_name=compound_name,
            smiles_string=smiles_string,
            molecular_weight=molecular_weight,
            log_p=log_p,
            ames_mutagenicity_status=ames_mutagenicity_status,
            ames_probability_pct=ames_probability_pct,
            herg_ic50_micromolar=herg_ic50_micromolar,
            herg_cardiotox_risk=herg_cardiotox_risk,
            dili_hepatotox_risk=dili_hepatotox_risk,
            ld50_rat_mg_kg=ld50_rat_mg_kg,
            properties=properties or {},
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def add_structural_alert(
        self,
        screen_id: str,
        alert_name: str,
        smarts_pattern: str,
        toxicophore_category: str = "DNA Alkylating Agent",
        severity_level: str = "HIGH",
    ) -> DBStructuralAlertMatch:
        alert = DBStructuralAlertMatch(
            screen_id=screen_id,
            alert_name=alert_name,
            smarts_pattern=smarts_pattern,
            toxicophore_category=toxicophore_category,
            severity_level=severity_level,
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def get_screen_by_id(self, screen_id: str) -> Optional[DBCompoundToxicityScreen]:
        stmt = (
            select(DBCompoundToxicityScreen)
            .options(selectinload(DBCompoundToxicityScreen.structural_alerts))
            .where(DBCompoundToxicityScreen.id == screen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(self, limit: int = 50) -> List[DBCompoundToxicityScreen]:
        stmt = (
            select(DBCompoundToxicityScreen)
            .options(selectinload(DBCompoundToxicityScreen.structural_alerts))
            .order_by(DBCompoundToxicityScreen.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
