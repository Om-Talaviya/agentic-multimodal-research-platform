"""Drug Repurposing & Synergy Repository (Phase 45)."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.drug_synergy import (
    DBDrugRepurposingScreen,
    DBRepurposedCandidate,
    DBDrugCombinationSynergy,
)

class DrugSynergyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        title: str,
        disease_indication: str,
        screening_library: str = "FDA-Approved & Phase III Clinical Library",
        total_screened: int = 2450,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBDrugRepurposingScreen:
        screen = DBDrugRepurposingScreen(
            title=title,
            disease_indication=disease_indication,
            screening_library=screening_library,
            total_screened=total_screened,
            workspace_id=workspace_id,
            project_id=project_id,
            meta_info=meta_info or {},
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def get_screen(self, screen_id: str) -> Optional[DBDrugRepurposingScreen]:
        stmt = select(DBDrugRepurposingScreen).where(DBDrugRepurposingScreen.id == screen_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(
        self,
        disease_indication: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBDrugRepurposingScreen]:
        stmt = select(DBDrugRepurposingScreen)
        if disease_indication:
            stmt = stmt.where(DBDrugRepurposingScreen.disease_indication.ilike(f"%{disease_indication}%"))
        stmt = stmt.order_by(desc(DBDrugRepurposingScreen.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_candidates(self, screen_id: str, candidates_data: List[Dict[str, Any]]) -> int:
        candidates = [
            DBRepurposedCandidate(
                screen_id=screen_id,
                drug_name=c["drug_name"],
                original_indication=c["original_indication"],
                proposed_mechanism=c["proposed_mechanism"],
                connectivity_score=c["connectivity_score"],
                ic50_um=c.get("ic50_um", 1.85),
                clinical_safety_tier=c.get("clinical_safety_tier", "High (FDA Approved)"),
                evidence_publications_count=c.get("evidence_publications_count", 12),
                meta_info=c.get("meta_info", {}),
            )
            for c in candidates_data
        ]
        self.session.add_all(candidates)
        await self.session.commit()
        return len(candidates)

    async def get_candidates(self, screen_id: str) -> List[DBRepurposedCandidate]:
        stmt = select(DBRepurposedCandidate).where(DBRepurposedCandidate.screen_id == screen_id)
        stmt = stmt.order_by(DBRepurposedCandidate.connectivity_score.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_synergies(self, screen_id: str, synergies_data: List[Dict[str, Any]]) -> int:
        synergies = [
            DBDrugCombinationSynergy(
                screen_id=screen_id,
                drug_a=s["drug_a"],
                drug_b=s["drug_b"],
                zip_synergy_score=s["zip_synergy_score"],
                bliss_excess_score=s.get("bliss_excess_score", 14.5),
                loewe_combination_index=s.get("loewe_combination_index", 0.68),
                synergy_classification=s.get("synergy_classification", "Synergistic"),
                dose_reduction_index=s.get("dose_reduction_index", 3.8),
                ddi_toxicity_risk=s.get("ddi_toxicity_risk", "Low"),
                synergy_matrix_2d=s.get("synergy_matrix_2d", []),
                meta_info=s.get("meta_info", {}),
            )
            for s in synergies_data
        ]
        self.session.add_all(synergies)
        await self.session.commit()
        return len(synergies)

    async def get_synergies(self, screen_id: str) -> List[DBDrugCombinationSynergy]:
        stmt = select(DBDrugCombinationSynergy).where(DBDrugCombinationSynergy.screen_id == screen_id)
        stmt = stmt.order_by(desc(DBDrugCombinationSynergy.zip_synergy_score))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_screen(self, screen_id: str) -> bool:
        screen = await self.get_screen(screen_id)
        if not screen:
            return False
        await self.session.delete(screen)
        await self.session.commit()
        return True
