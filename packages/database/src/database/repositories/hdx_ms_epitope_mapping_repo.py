"""Repository for HDX-MS Epitope Mapping."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.hdx_ms_epitope_mapping import (
    DBHDXMSEpitopeStudy,
    DBPeptideDeuterationProfile,
    DBEpitopeProtectionHotspot,
)


class HDXMSEpitopeRepository:
    """Repository handling CRUD operations for HDX-MS Epitope Mapping."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        target_protein_name: str = "Spike RBD / Neutralizing mAb",
        peptides_monitored_count: int = 4,
        mean_deuteration_protection_pct: float = 42.8,
        epitope_region_identified: str = "Residues 470-492 (RBD Receptor Binding Loop)",
        summary_metrics: Optional[Dict[str, Any]] = None,
        peptides: Optional[List[Dict[str, Any]]] = None,
        hotspots: Optional[List[Dict[str, Any]]] = None,
    ) -> DBHDXMSEpitopeStudy:
        study_id = uuid.uuid4()
        study = DBHDXMSEpitopeStudy(
            id=study_id,
            study_name=study_name,
            target_protein_name=target_protein_name,
            peptides_monitored_count=peptides_monitored_count,
            mean_deuteration_protection_pct=mean_deuteration_protection_pct,
            epitope_region_identified=epitope_region_identified,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if peptides:
            for p in peptides:
                pep_row = DBPeptideDeuterationProfile(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    peptide_sequence=p["peptide_sequence"],
                    start_residue=p["start_residue"],
                    end_residue=p["end_residue"],
                    deuterium_uptake_apo_pct=p["deuterium_uptake_apo_pct"],
                    deuterium_uptake_bound_pct=p["deuterium_uptake_bound_pct"],
                    delta_deuterium_protection_pct=p["delta_deuterium_protection_pct"],
                    confidence_p_value=p.get("confidence_p_value", 0.001),
                )
                self.session.add(pep_row)

        if hotspots:
            for h in hotspots:
                hotspot_row = DBEpitopeProtectionHotspot(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    residue_name=h["residue_name"],
                    protection_factor_log2=h["protection_factor_log2"],
                    solvent_accessibility_change=h.get("solvent_accessibility_change", "buried_upon_binding"),
                )
                self.session.add(hotspot_row)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBHDXMSEpitopeStudy]:
        stmt = (
            select(DBHDXMSEpitopeStudy)
            .where(DBHDXMSEpitopeStudy.id == study_id)
            .options(
                selectinload(DBHDXMSEpitopeStudy.peptides),
                selectinload(DBHDXMSEpitopeStudy.hotspots),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBHDXMSEpitopeStudy]:
        stmt = (
            select(DBHDXMSEpitopeStudy)
            .order_by(DBHDXMSEpitopeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBHDXMSEpitopeStudy.peptides),
                selectinload(DBHDXMSEpitopeStudy.hotspots),
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
